#!/usr/bin/env python3
"""
LLM Tabanlı Klinik Analiz Sistemi
Klinik dataset'i kullanarak akıllı klinik önerileri
"""

import json
import os
import logging
from typing import List, Dict, Any
import litellm
from litellm import completion

logger = logging.getLogger(__name__)

class LLMClinicAnalyzer:
    """LLM tabanlı klinik analiz sınıfı"""
    
    def __init__(self, dataset_path: str = None):
        """
        Args:
            dataset_path: Klinik dataset dosya yolu
        """
        self.dataset_path = dataset_path or "/Users/sevgi/Desktop/TaniAI-prototype/RANDEVU/mobile_flutter/klinik_dataset.jsonl"
        self.dataset = self._load_dataset()
        self.clinic_examples = self._prepare_examples()
        
    def _load_dataset(self) -> List[Dict[str, str]]:
        """Klinik dataset'ini yükler"""
        try:
            dataset = []
            if os.path.exists(self.dataset_path):
                with open(self.dataset_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line.strip())
                            dataset.append(data)
                logger.info(f"Klinik dataset yüklendi: {len(dataset)} örnek")
            else:
                logger.warning(f"Dataset dosyası bulunamadı: {self.dataset_path}")
            return dataset
        except Exception as e:
            logger.error(f"Dataset yükleme hatası: {e}")
            return []
    
    def _prepare_examples(self) -> str:
        """LLM için örnekleri hazırlar"""
        if not self.dataset:
            return ""
        
        # Her klinikten örnekler al - daha fazla örnek
        clinic_examples = {}
        for item in self.dataset:
            clinic = item.get('clinic', '')
            complaint = item.get('complaint', '')
            if clinic and complaint:
                if clinic not in clinic_examples:
                    clinic_examples[clinic] = []
                if len(clinic_examples[clinic]) < 5:  # Her klinikten max 5 örnek
                    clinic_examples[clinic].append(complaint)
        
        # Örnekleri formatla
        examples_text = "Klinik örnekleri (şikayet → klinik eşleştirmeleri):\n"
        for clinic, complaints in clinic_examples.items():
            examples_text += f"\n{clinic}:\n"
            for complaint in complaints:
                examples_text += f"- '{complaint}' → {clinic}\n"
        
        return examples_text
    
    def analyze_complaint(self, complaint: str) -> Dict[str, Any]:
        """
        Şikayeti LLM ile analiz eder ve klinik önerileri döndürür
        
        Args:
            complaint: Hasta şikayeti
            
        Returns:
            Dict: Analiz sonucu ve klinik önerileri
        """
        try:
            # LLM prompt'u hazırla
            prompt = f"""
Sen bir tıbbi triaj uzmanısın. Hasta şikayetlerini analiz edip en uygun klinikleri öneriyorsun.

{self.clinic_examples}

Mevcut klinikler ve uzmanlık alanları:
- Aile Hekimliği: Genel sağlık sorunları, rutin kontroller, basit hastalıklar, genel muayene
- İç Hastalıkları: Yetişkin hastalıkları, kronik hastalıklar, metabolik bozukluklar, diyabet, hipertansiyon
- Nöroloji: Beyin, sinir sistemi, baş ağrısı, migren, baş dönmesi, epilepsi, felç
- Kardiyoloji: Kalp ve damar hastalıkları, göğüs ağrısı, çarpıntı, nefes darlığı
- Gastroenteroloji: Mide, bağırsak, karın ağrısı, sindirim sorunları, bulantı, kusma
- Göğüs Hastalıkları: Akciğer, nefes darlığı, öksürük, solunum sorunları, astım
- Kulak Burun Boğaz: KBB organları, boğaz ağrısı, burun tıkanıklığı, kulak ağrısı
- Dermatoloji: Cilt hastalıkları, döküntü, kaşıntı, egzama, sedef
- Ortopedi: Kemik, eklem, kas, sırt ağrısı, bel ağrısı, kırık, burkulma
- Jinekoloji: Kadın hastalıkları, üreme sağlığı, adet sorunları, hamilelik
- Üroloji: Erkek hastalıkları, böbrek, idrar yolları, prostat
- Endokrinoloji: Hormon hastalıkları, şeker hastalığı, tiroid, obezite
- Psikiyatri: Ruh sağlığı, depresyon, anksiyete, stres, uyku bozuklukları
- Çocuk Hastalıkları: 0-18 yaş çocuk hastalıkları, çocuk gelişimi

Hasta şikayeti: "{complaint}"

Bu şikayet için en uygun 2-3 kliniği öner. Yukarıdaki örnekleri referans al.
Her öneri için:
1. Klinik adı (tam olarak yukarıdaki listeden)
2. Öneri nedeni (kısa ve açık açıklama)
3. Güven oranı (0.0-1.0 arası)

SADECE JSON formatında yanıtla, başka açıklama ekleme:
{{
    "primary_clinic": {{
        "name": "Klinik Adı",
        "reason": "Öneri nedeni",
        "confidence": 0.85
    }},
    "secondary_clinics": [
        {{
            "name": "Klinik Adı",
            "reason": "Öneri nedeni", 
            "confidence": 0.70
        }}
    ]
}}
"""
            
            # LLM çağrısı yap - En iyi model kullan
            try:
                # Önce en iyi model dene
                response = completion(
                    model="ollama/llama3.2:3b",  # En iyi model
                    messages=[
                        {"role": "system", "content": "Sen bir tıbbi triaj uzmanısın. Hasta şikayetlerini analiz edip en uygun klinikleri öneriyorsun. Sadece JSON formatında yanıt ver."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,  # Daha düşük temperature
                    max_tokens=800
                )
            except Exception as e:
                logger.warning(f"Llama3.2 modeli kullanılamadı: {e}")
                try:
                    # Fallback: tinyllama
                    response = completion(
                        model="ollama/tinyllama",
                        messages=[
                            {"role": "system", "content": "Sen bir tıbbi triaj uzmanısın. Sadece JSON formatında yanıt ver."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=600
                    )
                except Exception as e2:
                    logger.warning(f"Tinyllama modeli de kullanılamadı: {e2}")
                    # Fallback: basit analiz
                    return self._fallback_analysis(complaint)
            
            # Yanıtı parse et
            response_text = response.choices[0].message.content.strip()
            logger.info(f"LLM yanıtı: {response_text}")
            
            # JSON parse et - daha esnek parsing
            try:
                # JSON kısmını bul
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_text = response_text[json_start:json_end]
                    result = json.loads(json_text)
                    
                    # Sonucu validate et
                    if "primary_clinic" in result and "name" in result["primary_clinic"]:
                        return {
                            "success": True,
                            "analysis": result,
                            "method": "llm"
                        }
                    else:
                        logger.warning("LLM yanıtı eksik bilgi içeriyor")
                        return self._fallback_analysis(complaint)
                else:
                    logger.warning("LLM yanıtında JSON bulunamadı")
                    return self._fallback_analysis(complaint)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parse hatası: {e}")
                return self._fallback_analysis(complaint)
                
        except Exception as e:
            logger.error(f"LLM analiz hatası: {e}")
            return self._fallback_analysis(complaint)
    
    def _fallback_analysis(self, complaint: str) -> Dict[str, Any]:
        """LLM başarısız olursa basit analiz"""
        complaint_lower = complaint.lower()
        
        # Gelişmiş anahtar kelime analizi
        if any(word in complaint_lower for word in ['baş', 'kafa', 'migren', 'başağrısı', 'baş ağrısı', 'başım', 'kafam', 'baş dönmesi', 'dönüyor']):
            return {
                "success": True,
                "analysis": {
                    "primary_clinic": {
                        "name": "Nöroloji",
                        "reason": "Baş ağrısı ve nörolojik şikayetler için",
                        "confidence": 0.85
                    },
                    "secondary_clinics": [
                        {
                            "name": "Aile Hekimliği",
                            "reason": "Genel değerlendirme için",
                            "confidence": 0.70
                        }
                    ]
                },
                "method": "fallback"
            }
        elif any(word in complaint_lower for word in ['göğüs', 'kalp', 'nefes', 'çarpıntı', 'kalbim', 'göğsüm', 'nefes darlığı', 'çarpıntım']):
            return {
                "success": True,
                "analysis": {
                    "primary_clinic": {
                        "name": "Kardiyoloji",
                        "reason": "Kalp ve göğüs şikayetleri için",
                        "confidence": 0.85
                    },
                    "secondary_clinics": [
                        {
                            "name": "Göğüs Hastalıkları",
                            "reason": "Nefes darlığı değerlendirmesi için",
                            "confidence": 0.75
                        }
                    ]
                },
                "method": "fallback"
            }
        elif any(word in complaint_lower for word in ['karın', 'mide', 'bulantı', 'kusma', 'karın ağrısı', 'mide ağrısı', 'bulantım', 'kusuyorum']):
            return {
                "success": True,
                "analysis": {
                    "primary_clinic": {
                        "name": "Gastroenteroloji",
                        "reason": "Mide ve karın şikayetleri için",
                        "confidence": 0.85
                    },
                    "secondary_clinics": [
                        {
                            "name": "Aile Hekimliği",
                            "reason": "Genel değerlendirme için",
                            "confidence": 0.70
                        }
                    ]
                },
                "method": "fallback"
            }
        elif any(word in complaint_lower for word in ['öksürük', 'boğaz', 'burun', 'nefes', 'solunum', 'öksürüyorum', 'boğazım']):
            return {
                "success": True,
                "analysis": {
                    "primary_clinic": {
                        "name": "Göğüs Hastalıkları",
                        "reason": "Solunum yolu şikayetleri için",
                        "confidence": 0.85
                    },
                    "secondary_clinics": [
                        {
                            "name": "Kulak Burun Boğaz",
                            "reason": "Boğaz ve burun şikayetleri için",
                            "confidence": 0.75
                        }
                    ]
                },
                "method": "fallback"
            }
        elif any(word in complaint_lower for word in ['cilt', 'deri', 'kaşıntı', 'döküntü', 'kızarıklık', 'cildim', 'kaşınıyor']):
            return {
                "success": True,
                "analysis": {
                    "primary_clinic": {
                        "name": "Dermatoloji",
                        "reason": "Cilt hastalıkları için",
                        "confidence": 0.85
                    },
                    "secondary_clinics": [
                        {
                            "name": "Aile Hekimliği",
                            "reason": "Genel değerlendirme için",
                            "confidence": 0.70
                        }
                    ]
                },
                "method": "fallback"
            }
        elif any(word in complaint_lower for word in ['eklem', 'kas', 'sırt', 'bel', 'boyun', 'ağrı', 'sırtım', 'belim', 'boynum']):
            return {
                "success": True,
                "analysis": {
                    "primary_clinic": {
                        "name": "Ortopedi",
                        "reason": "Kas ve eklem şikayetleri için",
                        "confidence": 0.85
                    },
                    "secondary_clinics": [
                        {
                            "name": "Aile Hekimliği",
                            "reason": "Genel değerlendirme için",
                            "confidence": 0.70
                        }
                    ]
                },
                "method": "fallback"
            }
        else:
            return {
                "success": True,
                "analysis": {
                    "primary_clinic": {
                        "name": "Aile Hekimliği",
                        "reason": "Genel değerlendirme için",
                        "confidence": 0.70
                    },
                    "secondary_clinics": [
                        {
                            "name": "İç Hastalıkları",
                            "reason": "Genel muayene için",
                            "confidence": 0.60
                        }
                    ]
                },
                "method": "fallback"
            }

# Global instance
clinic_analyzer = None

def get_clinic_analyzer() -> LLMClinicAnalyzer:
    """Clinic analyzer instance'ını döndürür"""
    global clinic_analyzer
    if clinic_analyzer is None:
        clinic_analyzer = LLMClinicAnalyzer()
    return clinic_analyzer
