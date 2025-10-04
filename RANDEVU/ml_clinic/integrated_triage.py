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
    
    def _fallback_analysis(self, complaint: str) -> Dict[str, Any]:
        """Fallback analizi"""
        complaint_lower = complaint.lower()
        
        # Travma durumları
        if any(phrase in complaint_lower for phrase in ['düştüm', 'çarptım', 'travma', 'yaralandım', 'kırık', 'çıkık']):
            return {
                "primary_clinic": {
                    "name": "Ortopedi ve Travmatoloji",
                    "reason": "Travma ve yaralanma durumları için en uygun klinik",
                    "confidence": 0.95
                },
                "secondary_clinics": [
                    {
                        "name": "Acil Servis",
                        "reason": "Acil durumlar için alternatif",
                        "confidence": 0.85
                    }
                ],
                "strategy": "fallback",
                "model_version": "fallback_trauma",
                "latency_ms": 0,
                "requires_prior": False,
                "prior_list": [],
                "gate_note": ""
            }
        
        # Baş ağrısı
        elif any(word in complaint_lower for word in ['baş', 'kafa', 'migren', 'baş ağrısı']):
            return {
                "primary_clinic": {
                    "name": "Nöroloji",
                    "reason": "Baş ağrısı şikayetleri için en uygun klinik",
                    "confidence": 0.80
                },
                "secondary_clinics": [
                    {
                        "name": "İç Hastalıkları (Dahiliye)",
                        "reason": "Genel değerlendirme için alternatif",
                        "confidence": 0.60
                    }
                ],
                "strategy": "fallback",
                "model_version": "fallback_neurology",
                "latency_ms": 0,
                "requires_prior": False,
                "prior_list": [],
                "gate_note": ""
            }
        
        # Mide sorunları
        elif any(word in complaint_lower for word in ['mide', 'karın', 'bulantı', 'kusma']):
            return {
                "primary_clinic": {
                    "name": "İç Hastalıkları (Dahiliye)",
                    "reason": "Mide ve sindirim sistemi şikayetleri için uygun klinik",
                    "confidence": 0.80
                },
                "secondary_clinics": [
                    {
                        "name": "Gastroenteroloji",
                        "reason": "Sindirim sistemi uzmanı",
                        "confidence": 0.70
                    }
                ],
                "strategy": "fallback",
                "model_version": "fallback_gastro",
                "latency_ms": 0,
                "requires_prior": False,
                "prior_list": [],
                "gate_note": ""
            }
        
        # Kalp sorunları
        elif any(word in complaint_lower for word in ['kalp', 'çarpıntı', 'göğüs ağrısı']):
            return {
                "primary_clinic": {
                    "name": "Kardiyoloji",
                    "reason": "Kalp ve damar sistemi şikayetleri için en uygun klinik",
                    "confidence": 0.85
                },
                "secondary_clinics": [
                    {
                        "name": "İç Hastalıkları (Dahiliye)",
                        "reason": "Genel değerlendirme için alternatif",
                        "confidence": 0.65
                    }
                ],
                "strategy": "fallback",
                "model_version": "fallback_cardio",
                "latency_ms": 0,
                "requires_prior": True,
                "prior_list": ["İç Hastalıkları (Dahiliye)"],
                "gate_note": "Kardiyoloji randevusu için önce İç Hastalıkları (Dahiliye) muayenesi gereklidir."
            }
        
        # Varsayılan
        else:
            return {
                "primary_clinic": {
                    "name": "Aile Hekimliği",
                    "reason": "Genel sağlık sorunları için ilk başvuru noktası",
                    "confidence": 0.75
                },
                "secondary_clinics": [
                    {
                        "name": "İç Hastalıkları (Dahiliye)",
                        "reason": "Detaylı değerlendirme için alternatif",
                        "confidence": 0.65
                    }
                ],
                "strategy": "fallback",
                "model_version": "fallback_general",
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
            return self._fallback_analysis("")
        
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
            llm_result = self._fallback_analysis(complaint)
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
