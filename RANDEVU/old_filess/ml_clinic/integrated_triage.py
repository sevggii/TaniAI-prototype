"""
Entegre Triage Sistemi
Tüm bileşenleri birleştiren ana triage motoru
"""

import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Triage bileşenlerini import et
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from triage.canonical import canonicalize, load_mhrs_canonical
from triage.rules import apply_gatekeeping
from triage.redflags import detect_red_flags
from triage.schema import parse_llm_response, create_emergency_response, validate_or_fix
from triage.rag import load_jsonl_embeddings, retrieve_similar, calculate_rag_confidence


@dataclass
class TriageConfig:
    """Triage konfigürasyonu"""
    ollama_url: str = "http://localhost:11434/api/generate"
    dataset_path: str = "/Users/sevgi/TaniAI-prototype/RANDEVU/mobile_flutter/klinik_dataset.jsonl"
    canonical_path: str = "/Users/sevgi/TaniAI-prototype/RANDEVU/data/mhrs_canonical.json"
    llm_timeout: int = 15
    model_name: str = "tinyllama"
    rag_enabled: bool = True
    cache_enabled: bool = True


class IntegratedTriage:
    """Entegre triage sistemi"""
    
    def __init__(self, config: TriageConfig = None):
        self.config = config or TriageConfig()
        self.canonical_table = {}
        self.rag_loaded = False
        self._dataset_cache: Optional[List[Dict[str, Any]]] = None
        self._initialize()

    def _initialize(self):
        """Sistemi başlatır"""
        try:
            # Kanonik tabloyu yükle
            self.canonical_table = load_mhrs_canonical(self.config.canonical_path)
            logging.info(f"✅ Kanonik tablo yüklendi: {len(self.canonical_table)} klinik")
            
            # RAG sistemini yükle
            if self.config.rag_enabled:
                self.rag_loaded = load_jsonl_embeddings(self.config.dataset_path)
                if self.rag_loaded:
                    logging.info("✅ RAG sistemi yüklendi")
                else:
                    logging.warning("⚠️ RAG sistemi yüklenemedi")
            
        except Exception as e:
            logging.error(f"❌ Triage başlatma hatası: {e}")

    def _get_dataset_examples(self) -> List[Dict[str, Any]]:
        """JSONL veri kümesini bellek içine alır"""
        if self._dataset_cache is not None:
            return self._dataset_cache

        dataset: List[Dict[str, Any]] = []
        try:
            with open(self.config.dataset_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    complaint = data.get('complaint')
                    clinic = data.get('clinic')
                    if complaint and clinic:
                        dataset.append({'complaint': complaint, 'clinic': clinic})
        except FileNotFoundError:
            logging.warning("Dataset dosyası bulunamadı: %s", self.config.dataset_path)
        except Exception as exc:
            logging.warning("Dataset okunurken hata: %s", exc)

        self._dataset_cache = dataset
        return dataset

    def _keyword_dataset_lookup(self, complaint: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Anahtar kelime eşleşmesi ile benzer vakaları döndürür"""
        dataset = self._get_dataset_examples()
        if not dataset or not complaint:
            return []

        complaint_lower = complaint.lower()
        keywords = [word for word in complaint_lower.split() if len(word) > 2]
        if not keywords:
            return []

        medical_terms = {
            'baş': 3, 'ağrı': 3, 'ağrısı': 3, 'bulanıyor': 3, 'bulantı': 3,
            'kusma': 3, 'istifra': 3, 'mide': 2, 'göğüs': 2, 'kalp': 2,
            'nefes': 2, 'darlığı': 2, 'çarpıntı': 2, 'terleme': 2,
            'ateş': 4, 'ateşi': 4, 'ateşim': 4, 'ateşli': 4, 'öksürük': 3,
            'öksürüyor': 3, 'çocuk': 2, 'çocuğum': 2, 'çocuğumun': 2
        }

        results: List[Dict[str, Any]] = []
        for item in dataset:
            example_lower = item['complaint'].lower()
            score = 0

            for keyword in keywords:
                if keyword in example_lower:
                    score += medical_terms.get(keyword, 1)

            # Kombinasyon bonusları
            if any(key in example_lower for key in ['baş', 'migren']) and \
               any(key in example_lower for key in ['kus', 'bulantı', 'bulanıyor', 'istifra']):
                score += 4

            if 'ateş' in example_lower or 'ates' in example_lower:
                if any(key in example_lower for key in ['çocuk', 'çocuğum', 'çocuğumun']):
                    score += 3

            if score > 0:
                results.append({
                    'complaint': item['complaint'],
                    'clinic': item['clinic'],
                    'score': score
                })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]

    def _create_llm_prompt(self, complaint: str, similar_cases: List[Dict] = None) -> str:
        """LLM için prompt oluşturur"""
        similar_text = ""
        if similar_cases:
            similar_text = "\nBenzer hasta örnekleri:\n"
            for case in similar_cases[:3]:  # En fazla 3 örnek
                similar_text += f"- Şikayet: {case['complaint']} → Klinik: {case['clinic']}\n"
        
        prompt = f"""ROLE: You are a careful triage assistant for Turkish MHRS clinics.
TASK: Given a Turkish complaint text, return ONLY the following JSON as a single line (no markdown, no extra text).
SCHEMA: {{"primary_clinic":{{"name":"string","reason":"string","confidence":0.0}},"secondary_clinics":[{{"name":"string","reason":"string","confidence":0.0}}],"strategy":"llm","model_version":"{self.config.model_name}","latency_ms":0,"requires_prior":false,"prior_list":[],"gate_note":""}}
RULES:
- If red-flag/urgent (crushing chest pain with cold sweat, acute neuro deficit, uncontrolled bleeding), set primary_clinic.name="ACİL" with a very short reason.
- Use only real MHRS-like specialties; do NOT invent names. If unsure, choose the nearest parent specialty.
- Output valid compact JSON on ONE LINE. No markdown. No commentary.
INPUT: {complaint}{similar_text}
OUTPUT: <JSON ONLY>"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> Tuple[Optional[str], int]:
        """LLM'yi çağırır"""
        try:
            payload = {
                "model": self.config.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 150
                }
            }
            
            start_time = time.time()
            response = requests.post(
                self.config.ollama_url, 
                json=payload, 
                timeout=self.config.llm_timeout
            )
            latency_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '').strip()
                return llm_response, latency_ms
            else:
                logging.error(f"LLM API hatası: {response.status_code}")
                return None, latency_ms
                
        except requests.exceptions.Timeout:
            logging.error("LLM timeout")
            return None, 0
        except Exception as e:
            logging.error(f"LLM çağrı hatası: {e}")
            return None, 0
    
    def _dataset_fallback(self, complaint: str, similar_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Dataset tabanlı fallback analizi"""
        effective_cases = [case for case in similar_cases if case.get("score", 0.0) >= 1.5]
        if not effective_cases:
            effective_cases = self._keyword_dataset_lookup(complaint, top_k=8)

        if effective_cases:
            clinic_scores: Dict[str, float] = {}
            clinic_examples: Dict[str, Dict[str, Any]] = {}
            for case in effective_cases:
                clinic_name = case.get('clinic')
                if not clinic_name:
                    continue
                clinic_scores[clinic_name] = clinic_scores.get(clinic_name, 0.0) + case.get('score', 0.0)
                clinic_examples.setdefault(clinic_name, case)

            ranked_clinics = sorted(clinic_scores.items(), key=lambda item: item[1], reverse=True)
            primary_clinic, primary_score = ranked_clinics[0]
            primary_case = clinic_examples[primary_clinic]
            primary_reason = f"Benzer vaka: {primary_case.get('complaint', '')[:80]}..."
            primary_confidence = min(0.9, 0.5 + (primary_score / (primary_score + 6)))

            secondary_clinics: List[Dict[str, Any]] = []
            for clinic_name, score in ranked_clinics[1:3]:
                case = clinic_examples[clinic_name]
                secondary_clinics.append({
                    "name": clinic_name,
                    "reason": f"Benzer vaka: {case.get('complaint', '')[:80]}...",
                    "confidence": min(0.8, 0.4 + (score / (score + 8)))
                })

            return {
                "primary_clinic": {
                    "name": primary_clinic,
                    "reason": primary_reason,
                    "confidence": round(primary_confidence, 2)
                },
                "secondary_clinics": secondary_clinics,
                "strategy": "dataset_fallback",
                "model_version": "rag_tfidf",
                "latency_ms": 0,
                "requires_prior": False,
                "prior_list": [],
                "gate_note": ""
            }

        # Benzer örnek bulunamazsa nötr varsayılan
        return {
            "primary_clinic": {
                "name": "Aile Hekimliği",
                "reason": "Benzer vaka bulunamadı, genel değerlendirme önerildi",
                "confidence": 0.6
            },
            "secondary_clinics": [],
            "strategy": "dataset_fallback",
            "model_version": "rag_tfidf",
            "latency_ms": 0,
            "requires_prior": False,
            "prior_list": [],
            "gate_note": ""
        }
    
    def analyze_complaint(self, complaint: str) -> Dict[str, Any]:
        """
        Ana triage analizi
        
        Args:
            complaint: Hasta şikayeti
        
        Returns:
            Dict: Triage sonucu
        """
        if not complaint or not complaint.strip():
            return self._dataset_fallback("", [])
        
        complaint = complaint.strip()
        
        # 1. Red-flag kontrolü (en yüksek öncelik)
        red_flag = detect_red_flags(complaint)
        if red_flag.urgent:
            logging.info("🚨 Red-flag tespit edildi")
            return create_emergency_response(red_flag.reason, red_flag.message, red_flag.confidence)
        
        # 2. RAG ile benzer vakaları bul
        similar_cases = []
        rag_confidence = 0.0
        if self.rag_loaded:
            similar_cases = retrieve_similar(complaint, top_k=3)
            rag_confidence = calculate_rag_confidence(complaint, similar_cases)
        
        # 3. LLM analizi
        llm_result = None
        llm_latency = 0
        
        try:
            prompt = self._create_llm_prompt(complaint, similar_cases)
            llm_response, llm_latency = self._call_llm(prompt)
            
            if llm_response:
                llm_result = parse_llm_response(
                    llm_response, 
                    strategy="llm", 
                    model_version=self.config.model_name,
                    latency_ms=llm_latency
                )
                logging.info("🤖 LLM analizi başarılı")
            else:
                logging.warning("⚠️ LLM yanıt alınamadı, fallback kullanılacak")
                
        except Exception as e:
            logging.error(f"❌ LLM analiz hatası: {e}")
        
        # 4. LLM başarısızsa fallback
        if not llm_result:
            if not similar_cases and self.config.rag_enabled:
                similar_cases = retrieve_similar(complaint, top_k=3)
            llm_result = self._dataset_fallback(complaint, similar_cases)
            logging.info("🔄 Fallback analizi kullanıldı")
        
        # 5. Kanonikleştirme
        canonical_name, matched, similarity = canonicalize(
            llm_result["primary_clinic"]["name"], 
            self.canonical_table
        )
        
        if matched:
            llm_result["primary_clinic"]["name"] = canonical_name
            logging.info(f"✅ Kanonikleştirme: {canonical_name} (benzerlik: {similarity:.2f})")
        
        # 6. Gatekeeping kontrolü
        gate = apply_gatekeeping(canonical_name)
        if gate.requires_prior:
            llm_result["requires_prior"] = gate.requires_prior
            llm_result["prior_list"] = gate.prior_list
            llm_result["gate_note"] = gate.gate_note
            logging.info(f"🔐 Gatekeeping: {gate.gate_note}")
        
        # 7. Güven skorunu harmanla
        if self.config.rag_enabled and similar_cases:
            # final_confidence = 0.5*llm + 0.3*rag + 0.2*rule
            llm_confidence = llm_result["primary_clinic"]["confidence"]
            rule_confidence = 0.8 if gate.requires_prior else 0.9
            
            final_confidence = (
                0.5 * llm_confidence + 
                0.3 * rag_confidence + 
                0.2 * rule_confidence
            )
            
            llm_result["primary_clinic"]["confidence"] = min(1.0, final_confidence)
            logging.info(f"🎯 Harmanlanmış güven: {final_confidence:.2f}")
        
        # 8. Son doğrulama
        final_result = validate_or_fix(llm_result)
        
        return final_result


def test_integrated_triage():
    """Test fonksiyonu"""
    print("🧪 Entegre Triage Test Sonuçları:")
    
    # Test konfigürasyonu
    config = TriageConfig()
    config.dataset_path = "/Users/sevgi/TaniAI-prototype/RANDEVU/mobile_flutter/klinik_dataset.jsonl"
    
    triage = IntegratedTriage(config)
    
    # Test senaryoları
    test_cases = [
        "Başım çok ağrıyor ve mide bulantım var",
        "Aniden göğsümde ezici ağrı var, soğuk terliyorum",
        "Çocuğumda ateş ve öksürük var",
        "Romatizma şikayetlerim var; eklemde şişlik",
        "düştüm başımı çarptım",
        "garip bir ağrım var ne olduğunu bilmiyorum"
    ]
    
    for complaint in test_cases:
        print(f"\n🔍 Şikayet: '{complaint}'")
        result = triage.analyze_complaint(complaint)
        
        print(f"  🏥 Ana Klinik: {result['primary_clinic']['name']}")
        print(f"  📝 Sebep: {result['primary_clinic']['reason']}")
        print(f"  🎯 Güven: {result['primary_clinic']['confidence']:.2f}")
        print(f"  🔧 Strateji: {result['strategy']}")
        
        if result['requires_prior']:
            print(f"  🔐 Ön-koşul: {result['gate_note']}")
        
        if result['secondary_clinics']:
            print(f"  🔄 Alternatif: {result['secondary_clinics'][0]['name']}")


if __name__ == "__main__":
    test_integrated_triage()
