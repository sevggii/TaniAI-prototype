#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Klinik Önerisi Servisi
Eğitilmiş Ollama modelini kullanarak klinik önerisi yapar
"""

import requests
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ClinicRecommenderService:
    """Eğitilmiş klinik önerisi servisi"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "clinic-recommender"
        
    def recommend_clinic(self, complaint: str) -> Dict[str, Any]:
        """Hasta şikayetine göre klinik önerisi al"""
        try:
            # Ollama API'sine istek gönder
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": f"Hasta Şikayeti: {complaint}",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "top_k": 40
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                # JSON parse etmeye çalış
                try:
                    # JSON kısmını bul
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    
                    if start != -1 and end != -1:
                        json_str = response_text[start:end]
                        clinic_data = json.loads(json_str)
                        
                        return {
                            "success": True,
                            "recommended_clinic": clinic_data.get("clinic", "Aile Hekimliği"),
                            "confidence": clinic_data.get("confidence", 0.8),
                            "reasoning": clinic_data.get("reasoning", "Eğitilmiş model önerisi"),
                            "urgency": self._determine_urgency(clinic_data.get("clinic", "")),
                            "alternatives": self._get_alternatives(clinic_data.get("clinic", ""))
                        }
                    else:
                        # JSON parse edilemezse fallback
                        return self._fallback_recommendation(complaint)
                        
                except json.JSONDecodeError:
                    logger.warning(f"JSON parse hatası: {response_text}")
                    return self._fallback_recommendation(complaint)
            else:
                logger.error(f"Ollama API hatası: {response.status_code}")
                return self._fallback_recommendation(complaint)
                
        except Exception as e:
            logger.error(f"Klinik önerisi hatası: {e}")
            return self._fallback_recommendation(complaint)
    
    def _determine_urgency(self, clinic: str) -> str:
        """Klinik türüne göre aciliyet belirle"""
        urgent_clinics = ["Acil Servis", "Kardiyoloji", "Nöroloji"]
        
        if clinic in urgent_clinics:
            return "high"
        elif clinic in ["Aile Hekimliği", "İç Hastalıkları"]:
            return "low"
        else:
            return "medium"
    
    def _get_alternatives(self, recommended_clinic: str) -> list:
        """Alternatif klinikleri öner"""
        alternatives = {
            "Acil Servis": ["Aile Hekimliği", "İç Hastalıkları"],
            "Kardiyoloji": ["Aile Hekimliği", "İç Hastalıkları"],
            "Nöroloji": ["Aile Hekimliği", "İç Hastalıkları"],
            "Göz Hastalıkları": ["Aile Hekimliği"],
            "Aile Hekimliği": ["İç Hastalıkları", "Genel Cerrahi"]
        }
        
        return alternatives.get(recommended_clinic, ["Aile Hekimliği", "İç Hastalıkları"])
    
    def _fallback_recommendation(self, complaint: str) -> Dict[str, Any]:
        """Fallback önerisi"""
        complaint_lower = complaint.lower()
        
        # Basit kural tabanlı fallback
        if any(word in complaint_lower for word in ["acil", "kırık", "kanama", "travma"]):
            clinic = "Acil Servis"
            urgency = "high"
        elif any(word in complaint_lower for word in ["göğüs", "kalp", "nefes", "çarpıntı"]):
            clinic = "Kardiyoloji"
            urgency = "high"
        elif any(word in complaint_lower for word in ["baş", "migren", "nöroloji"]):
            clinic = "Nöroloji"
            urgency = "medium"
        elif any(word in complaint_lower for word in ["göz", "görme", "bulanık"]):
            clinic = "Göz Hastalıkları"
            urgency = "medium"
        else:
            clinic = "Aile Hekimliği"
            urgency = "low"
        
        return {
            "success": True,
            "recommended_clinic": clinic,
            "confidence": 0.7,
            "reasoning": "Fallback kural tabanlı öneri",
            "urgency": urgency,
            "alternatives": self._get_alternatives(clinic)
        }

def test_service():
    """Servisi test et"""
    service = ClinicRecommenderService()
    
    test_cases = [
        "Başım çok ağrıyor, migren ataklarım arttı",
        "Göğsümde sıkışma var, nefes almakta zorlanıyorum",
        "Gözlerim bulanık görüyor, numara büyümüş olabilir"
    ]
    
    print("=" * 60)
    print("KLİNİK ÖNERİSİ SERVİSİ TEST")
    print("=" * 60)
    
    for complaint in test_cases:
        result = service.recommend_clinic(complaint)
        print(f"\nŞikayet: {complaint}")
        print(f"Önerilen Klinik: {result['recommended_clinic']}")
        print(f"Güven: {result['confidence']:.2f}")
        print(f"Aciliyet: {result['urgency']}")
        print(f"Açıklama: {result['reasoning']}")
        print("-" * 40)

if __name__ == "__main__":
    test_service()
