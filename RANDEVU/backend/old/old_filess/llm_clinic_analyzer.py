"""LLM tabanlı klinik öneri analizörü.

Bu modül hem HTTP sunucusu (clinic_llm_server.py) hem de FastAPI katmanı
(mobile_flutter/api/randevu_api.py) tarafından paylaşılır. LLM çağrıları
litellm aracılığıyla yönetilir; başarısız durumlarda kural tabanlı fallback
çalışır.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from litellm import completion
from llm_config import get_llm_config, get_litellm_params, set_llm_model

from triage.schema import parse_llm_response

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "mobile_flutter",
    "klinik_dataset.jsonl",
)


@dataclass
class AnalyzerConfig:
    """LLM ve veri kümesi yapılandırması."""

    dataset_path: str = os.getenv("CLINIC_DATASET_PATH", DEFAULT_DATASET_PATH)
    model_config_name: str = os.getenv("LITELLM_MODEL_CONFIG", "ollama_llama3.2_3b")
    temperature: float = float(os.getenv("LITELLM_TEMPERATURE", "0.1"))
    max_tokens: int = int(os.getenv("LITELLM_MAX_TOKENS", "256"))


class ClinicLLMAnalyzer:
    """Litellm destekli klinik öneri analizörü."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        self.config = config or AnalyzerConfig()
        self.clinic_examples: Dict[str, List[str]] = {}
        self._load_dataset()

    # ------------------------------------------------------------------
    # Veri işlemleri
    # ------------------------------------------------------------------
    def _load_dataset(self) -> None:
        """Klinik örneklerini bellek içine alır."""
        dataset_path = self.config.dataset_path
        if not os.path.exists(dataset_path):
            logger.warning("Klinik veri kümesi bulunamadı: %s", dataset_path)
            return

        loaded = 0
        with open(dataset_path, "r", encoding="utf-8") as dataset_file:
            for line in dataset_file:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                clinic = data.get("clinic")
                complaint = data.get("complaint")
                if not clinic or not complaint:
                    continue
                self.clinic_examples.setdefault(clinic, []).append(complaint)
                loaded += 1
        logger.info("Klinik veri kümesi yüklendi: %s örnek", loaded)

    def _retrieve_similar_examples(self, complaint: str, top_k: int = 5) -> List[Dict[str, str]]:
        """Çok daha akıllı benzer örnek bulma algoritması."""
        complaint_lower = complaint.lower()
        
        # Anahtar kelimeleri çıkar (2+ karakter)
        keywords = [word for word in complaint_lower.split() if len(word) > 2]
        
        # Tıbbi terimler için özel ağırlık - ÇOK DETAYLI
        medical_terms = {
            # ACİL BELİRTİLER (en yüksek öncelik)
            'kan': 10, 'kanama': 10, 'kanıyor': 10, 'kan geliyor': 10,
            'bayıl': 8, 'baygın': 8, 'bilinç': 8, 'bilinçsiz': 8,
            'göğüs': 6, 'kalp': 6, 'nefes': 6, 'darlığı': 6, 'çarpıntı': 6, 'terleme': 6,
            
            # VÜCUT BÖLÜMLERİ (çok önemli!)
            'bacak': 8, 'bacağım': 8, 'bacak ağrısı': 8, 'bacak şişti': 8,
            'kol': 7, 'kolu': 7, 'kol ağrısı': 7,
            'sırt': 7, 'sırtım': 7, 'sırt ağrısı': 7,
            'bel': 7, 'belim': 7, 'bel ağrısı': 7,
            'boyun': 7, 'boynum': 7, 'boyun ağrısı': 7,
            'omuz': 6, 'omuzum': 6, 'omuz ağrısı': 6,
            'diz': 6, 'dizim': 6, 'diz ağrısı': 6,
            'el': 6, 'elim': 6, 'el ağrısı': 6,
            'ayak': 6, 'ayağım': 6, 'ayak ağrısı': 6,
            
            # BAŞ AĞRISI ÖZEL TERİMLERİ
            'baş ağrısı': 8, 'baş ağrım': 8, 'başım ağrıyor': 8, 'migren': 8,
            'baş ağrı': 7, 'baş ağrısı var': 7, 'baş ağrısı oluyor': 7,
            'baş dönmesi': 5, 'başım dönüyor': 5, 'dönüyor': 4,
            
            # TRAVMA VE YARALANMA
            'düştüm': 8, 'düştü': 8, 'düşme': 8, 'travma': 8,
            'yaralandım': 7, 'yaralandı': 7, 'yaralanma': 7,
            'kırık': 8, 'kırıldı': 8, 'çıkık': 7, 'çıktı': 7,
            'şişti': 6, 'şişme': 6, 'şişmiş': 6,
            
            # NORMAL BELİRTİLER
            'ağrı': 3, 'ağrısı': 3, 'ağrıyor': 3, 'ağrıyor': 3,
            'bulanıyor': 3, 'bulantı': 3, 'kusma': 3, 'istifra': 3,
            'mide': 2, 'ateş': 4, 'ateşi': 4, 'ateşli': 4,
            'öksürük': 3, 'öksürüyor': 3, 'nezle': 3
        }
        
        if not keywords:
            return []

        scored: List[Dict[str, Any]] = []
        for clinic, examples in self.clinic_examples.items():
            for example in examples:
                example_lower = example.lower()
                score = 0
                
                # 1. Tam ifade eşleşmesi (en yüksek puan)
                for term, weight in medical_terms.items():
                    if term in complaint_lower and term in example_lower:
                        score += weight * 3  # Tam eşleşme bonusu
                
                # 2. Normal kelime eşleşmesi
                for keyword in keywords:
                    if keyword in example_lower:
                        weight = medical_terms.get(keyword, 1)
                        score += weight
                
                # 3. VÜCUT BÖLÜMÜ UYUMSUZLUĞU CEZASI
                body_parts = ['baş', 'bacak', 'kol', 'sırt', 'bel', 'boyun', 'omuz', 'diz', 'el', 'ayak', 'göğüs', 'mide']
                complaint_body = [part for part in body_parts if part in complaint_lower]
                example_body = [part for part in body_parts if part in example_lower]
                
                if complaint_body and example_body:
                    # Farklı vücut bölümleri için büyük ceza
                    if not any(part in example_body for part in complaint_body):
                        score -= 15  # Farklı vücut bölümü cezası
                
                # 4. TRAVMA vs NORMAL AĞRI AYRIMI
                if 'düştüm' in complaint_lower or 'travma' in complaint_lower:
                    if 'düştüm' not in example_lower and 'travma' not in example_lower:
                        score -= 10  # Travma olmayan örnekler için ceza
                
                # 5. ŞİŞME vs NORMAL AĞRI AYRIMI
                if 'şişti' in complaint_lower or 'şişme' in complaint_lower:
                    if 'şişti' not in example_lower and 'şişme' not in example_lower:
                        score -= 8  # Şişme olmayan örnekler için ceza
                
                if score > 0:
                    scored.append({
                        "clinic": clinic,
                        "complaint": example,
                        "score": score,
                    })
        
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    # ------------------------------------------------------------------
    # LLM ve fallback analizi
    # ------------------------------------------------------------------
    def analyze_complaint(self, complaint: str) -> Dict[str, Any]:
        """LLM ile klinik analizi yapar; gerekirse fallback kullanır."""
        complaint = (complaint or "").strip()
        if not complaint:
            return {
                "success": False,
                "error": "Boş şikayet metni",
                "analysis": self._fallback_analysis("", []),
            }

        # Benzer örnekleri kullanma - LLM'i karıştırıyor
        # similar_examples = self._retrieve_similar_examples(complaint, top_k=5)
        similar_examples = []  # Boş bırak - LLM kendi bilgisiyle karar versin
        prompt_messages = self._build_prompt(complaint, similar_examples)

        # SADECE LLM kullan - fallback yok!
        try:
            llm_response = self._call_llm(prompt_messages)
            if llm_response:
                try:
                    # JSON parse et - daha esnek
                    start_idx = llm_response.find('{')
                    end_idx = llm_response.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != -1:
                        json_str = llm_response[start_idx:end_idx]
                        
                        # JSON'u temizle - yaygın LLM hatalarını düzelt
                        json_str = json_str.replace('being,', '')  # "being" kelimesi
                        json_str = json_str.replace('being', '')  # "being" kelimesi
                        json_str = json_str.replace('beingi', '')  # "beingi" kelimesi
                        json_str = json_str.replace('beingi,', '')  # "beingi," kelimesi
                        json_str = json_str.replace('"confidence":0.9}', '"confidence":0.9}')  # Eksik tırnak
                        json_str = json_str.replace('"confidence":0.8}', '"confidence":0.8}')  # Eksik tırnak
                        
                        parsed_result = json.loads(json_str)
                        
                        # Klinik adlarını kontrol et - sadece dataset'teki klinikleri kabul et
                        validated_result = self._validate_clinic_names(parsed_result)
                        
                        # LLM sonucunu döndür - güven eşiği yok!
                        return {
                            "success": True,
                            "analysis": validated_result,
                            "method": "llm",
                            "model": self.config.model_config_name,
                            "raw_response": llm_response,
                        }
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"LLM JSON parse hatası: {e}")
                    logger.error(f"Raw response: {llm_response}")
                    # JSON parse hatası - LLM'den tekrar iste
                    return self._retry_llm_with_simpler_prompt(complaint, similar_examples)
            
            # LLM yanıt vermedi - tekrar dene
            logger.warning("LLM yanıt vermedi, tekrar deneniyor...")
            return self._retry_llm_with_simpler_prompt(complaint, similar_examples)
            
        except Exception as e:
            logger.error(f"LLM çağrısı hatası: {e}")
            # LLM hatası - tekrar dene
            return self._retry_llm_with_simpler_prompt(complaint, similar_examples)

    def _call_llm(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """litellm aracılığıyla modeli çağırır ve düz metin döndürür."""
        # Yeni konfigürasyon sistemini kullan
        llm_params = get_litellm_params(self.config.model_config_name)
        
        request_kwargs: Dict[str, Any] = {
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            **llm_params  # model, api_base, api_key vs. buradan gelir
        }

        try:
            response = completion(**request_kwargs)
            choices = response.get("choices") or []
            if not choices:
                return None
            message = choices[0].get("message", {})
            content = message.get("content")
            return content.strip() if isinstance(content, str) else None
        except Exception as e:
            logger.error(f"LLM çağrısı hatası: {e}")
            return None

    def _build_prompt(
        self,
        complaint: str,
        similar_examples: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """LLM için sistem ve kullanıcı mesajlarını oluşturur."""
        schema_description = (
            '{"primary_clinic":{"name":"Ortopedi ve Travmatoloji","reason":"El yaralanması için","confidence":0.9},'
            '"secondary_clinics":[{"name":"Acil Servis","reason":"Kanama kontrolü için","confidence":0.8}]}'
        )
        # Dataset'teki tüm klinikleri al
        available_clinics = list(self.clinic_examples.keys())
        clinics_text = ", ".join(available_clinics[:20])  # İlk 20 kliniği göster
        
        system_prompt = (
            "Sen deneyimli bir tıbbi triage asistanısın. Hasta şikayetini dikkatlice analiz et ve en uygun kliniği öner. "
            "ÖNEMLİ: SADECE aşağıdaki kliniklerden birini öner: " + clinics_text + "... "
            "BAŞKA KLİNİK ÖNERME! Sadece bu listedeki klinikleri kullan. "
            "KRİTİK KURALLAR: "
            "- ÇOKLU BELİRTİLER varsa (baş ağrısı + mide bulantısı + kalp sıkışması gibi) → Acil Servis "
            "- KALP, GÖĞÜS, NEFES problemleri → Acil Servis veya Kardiyoloji "
            "- KANAMA, BAYILMA, BİLİNÇ kaybı → Acil Servis "
            "- TEK BELİRTİ varsa (sadece baş ağrısı) → Nöroloji "
            "- TEK BELİRTİ varsa (sadece mide ağrısı) → İç Hastalıkları "
            "- TRAVMA, DÜŞME, KIRIK → Ortopedi ve Travmatoloji "
            "ÖNCE ACİL DURUM kontrolü yap, sonra spesifik kliniği seç. "
            "SADECE JSON formatında yanıt ver. Başka hiçbir şey yazma. "
            "Örnek format: " + schema_description
        )

        similar_text = ""
        if similar_examples:
            formatted = [
                f"- Şikayet: {item['complaint']} → Klinik: {item['clinic']}"
                for item in similar_examples
            ]
            similar_text = "Benzer örnekler:\n" + "\n".join(formatted)

        # Few-shot examples ekle
        few_shot_examples = """
ÖRNEKLER:
- "Ateşim var, burnum tıkalı, nezleyim" → Kulak Burun Boğaz Hastalıkları
- "Başım ağrıyor, migrenim var" → Nöroloji  
- "Göğsümde ağrı var, nefes alamıyorum" → Acil Servis
- "Mide ağrım var, bulantım oluyor" → İç Hastalıkları (Dahiliye)
- "Çocuğumun ateşi var" → Çocuk Sağlığı ve Hastalıkları
- "Ağzımdan kan geliyor" → Acil Servis
- "Gözlerim yanıyor, bulanık görüyorum" → Göz Hastalıkları
"""
        
        user_prompt = (
            f"Hasta şikayeti: '{complaint}'\n\n"
            f"ÖNEMLİ: Bu şikayette kaç farklı belirti var? "
            f"Eğer 2 veya daha fazla belirti varsa (baş ağrısı + mide bulantısı + kalp sıkışması gibi) → Acil Servis öner! "
            f"Eğer sadece 1 belirti varsa → spesifik kliniği öner. "
            f"JSON formatında yanıt ver:"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    
    def _validate_clinic_names(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """LLM yanıtındaki klinik adlarını dataset ile kontrol et"""
        available_clinics = set(self.clinic_examples.keys())
        
        # Primary clinic kontrolü
        if "primary_clinic" in result:
            primary_name = result["primary_clinic"].get("name", "")
            if primary_name not in available_clinics:
                logger.warning(f"Geçersiz primary clinic: {primary_name}")
                # En yakın kliniği bul veya Aile Hekimliği kullan
                result["primary_clinic"]["name"] = "Aile Hekimliği"
                result["primary_clinic"]["reason"] = f"Geçersiz klinik adı düzeltildi: {primary_name}"
        
        # Secondary clinics kontrolü
        if "secondary_clinics" in result:
            for i, secondary in enumerate(result["secondary_clinics"]):
                secondary_name = secondary.get("name", "")
                if secondary_name not in available_clinics:
                    logger.warning(f"Geçersiz secondary clinic: {secondary_name}")
                    # Geçersiz kliniği kaldır
                    result["secondary_clinics"][i]["name"] = "Aile Hekimliği"
                    result["secondary_clinics"][i]["reason"] = f"Geçersiz klinik adı düzeltildi: {secondary_name}"
        
        return result

    def _retry_llm_with_simpler_prompt(
        self,
        complaint: str,
        similar_examples: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """LLM'den basit prompt ile tekrar iste"""
        try:
            # Çok basit prompt
            simple_messages = [
                {
                    "role": "system", 
                    "content": "Sen tıbbi triage uzmanısın. Hasta şikayetini analiz et ve uygun kliniği öner. SADECE JSON formatında yanıt ver."
                },
                {
                    "role": "user", 
                    "content": f"Hasta şikayeti: '{complaint}'\n\nUygun kliniği belirle ve JSON formatında yanıt ver:\n{{\"primary_clinic\": {{\"name\": \"Klinik Adı\", \"reason\": \"Neden\", \"confidence\": 0.9}}, \"secondary_clinics\": []}}"
                }
            ]
            
            llm_response = self._call_llm(simple_messages)
            if llm_response:
                # JSON parse et
                start_idx = llm_response.find('{')
                end_idx = llm_response.rfind('}') + 1
                
                if start_idx != -1 and end_idx != -1:
                    json_str = llm_response[start_idx:end_idx]
                    parsed_result = json.loads(json_str)
                    validated_result = self._validate_clinic_names(parsed_result)
                    
                    return {
                        "success": True,
                        "analysis": validated_result,
                        "method": "llm_retry",
                        "model": self.config.model_config_name,
                        "raw_response": llm_response,
                    }
            
            # Son çare - basit LLM yanıtı
            return {
                "success": False,
                "error": "LLM yanıt veremedi",
                "analysis": {
                    "primary_clinic": {
                        "name": "Aile Hekimliği",
                        "reason": "LLM yanıt veremedi - genel değerlendirme önerildi",
                        "confidence": 0.5,
                    },
                    "secondary_clinics": [],
                    "strategy": "llm_failed",
                    "model_version": "failed",
                    "latency_ms": 0,
                    "requires_prior": False,
                    "prior_list": [],
                    "gate_note": "LLM başarısız",
                },
                "method": "llm_failed",
                "model": self.config.model_config_name,
            }
            
        except Exception as e:
            logger.error(f"LLM retry hatası: {e}")
            return {
                "success": False,
                "error": f"LLM retry hatası: {e}",
                "analysis": {
                    "primary_clinic": {
                        "name": "Aile Hekimliği",
                        "reason": "LLM hatası - genel değerlendirme önerildi",
                        "confidence": 0.3,
                    },
                    "secondary_clinics": [],
                    "strategy": "llm_error",
                    "model_version": "error",
                    "latency_ms": 0,
                    "requires_prior": False,
                    "prior_list": [],
                    "gate_note": "LLM hatası",
                },
                "method": "llm_error",
                "model": self.config.model_config_name,
            }

    # ------------------------------------------------------------------
    # Fallback fonksiyonları KALDIRILDI - SADECE LLM kullanılıyor
    # ------------------------------------------------------------------


_analyzer_instance: Optional[ClinicLLMAnalyzer] = None


def get_clinic_analyzer() -> ClinicLLMAnalyzer:
    """Tekil analizör örneğini döndürür."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ClinicLLMAnalyzer()
    return _analyzer_instance
