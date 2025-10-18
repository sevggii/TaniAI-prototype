#!/usr/bin/env python3
"""
Klinik Servisi
Klinik önerileri ve randevu yönlendirmesi
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

class ClinicService:
    """Klinik önerisi ve randevu yönlendirme servisi"""
    
    def __init__(self):
        self.clinic_data = self._load_clinic_data()
        self.llm_service = None
        
        # LLM servisini import et
        try:
            from llm_service import LLMService
            self.llm_service = LLMService()
        except ImportError:
            logging.warning("LLM service not available, using rule-based clinic recommendation")
    
    def _load_clinic_data(self) -> Dict[str, Any]:
        """Klinik verilerini yükle"""
        try:
            clinics_file = "clinics/clinics.json"
            if os.path.exists(clinics_file):
                with open(clinics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logging.error(f"Error loading clinic data: {e}")
        
        # Varsayılan klinik verileri
        return {
            "clinics": [
                {
                    "id": "general",
                    "name": "Genel Pratisyen",
                    "description": "Genel sağlık kontrolü ve rutin muayeneler",
                    "specialties": ["Genel Tıp", "Aile Hekimliği"],
                    "keywords": ["genel", "rutin", "kontrol", "check-up"],
                    "urgency_level": "low"
                },
                {
                    "id": "cardiology",
                    "name": "Kardiyoloji",
                    "description": "Kalp ve damar hastalıkları",
                    "specialties": ["Kardiyoloji", "Kalp Cerrahisi"],
                    "keywords": ["göğüs", "kalp", "nefes", "çarpıntı", "ağrı", "tansiyon"],
                    "urgency_level": "high"
                },
                {
                    "id": "neurology",
                    "name": "Nöroloji",
                    "description": "Sinir sistemi hastalıkları",
                    "specialties": ["Nöroloji", "Beyin Cerrahisi"],
                    "keywords": ["baş", "baş ağrısı", "nöroloji", "sinir", "felç", "titreme"],
                    "urgency_level": "high"
                },
                {
                    "id": "orthopedics",
                    "name": "Ortopedi",
                    "description": "Kemik, eklem ve kas hastalıkları",
                    "specialties": ["Ortopedi", "Travmatoloji"],
                    "keywords": ["kemik", "eklem", "kas", "ağrı", "travma", "kırık"],
                    "urgency_level": "medium"
                },
                {
                    "id": "dermatology",
                    "name": "Dermatoloji",
                    "description": "Cilt hastalıkları",
                    "specialties": ["Dermatoloji"],
                    "keywords": ["cilt", "deri", "döküntü", "kaşıntı", "ben", "leke"],
                    "urgency_level": "low"
                },
                {
                    "id": "emergency",
                    "name": "Acil Servis",
                    "description": "Acil müdahale gerektiren durumlar",
                    "specialties": ["Acil Tıp"],
                    "keywords": ["acil", "kritik", "hayati", "kanama", "travma", "bayılma"],
                    "urgency_level": "critical"
                }
            ]
        }
    
    def recommend_clinic(self, symptoms: str) -> Dict[str, Any]:
        """Semptomlara göre klinik önerisi yap"""
        try:
            symptoms_lower = symptoms.lower()
            
            # Önce LLM ile analiz yapmaya çalış
            if self.llm_service:
                llm_result = self._recommend_with_llm(symptoms)
                if llm_result:
                    return llm_result
            
            # LLM yoksa kural tabanlı öneri
            return self._rule_based_recommendation(symptoms_lower)
            
        except Exception as e:
            logging.error(f"Clinic recommendation error: {e}")
            return self._get_default_recommendation()
    
    def _recommend_with_llm(self, symptoms: str) -> Optional[Dict[str, Any]]:
        """LLM ile klinik önerisi"""
        try:
            prompt = f"""Aşağıdaki semptomlara göre en uygun kliniği öner:

Semptomlar: {symptoms}

Mevcut klinikler:
- Genel Pratisyen: Genel sağlık kontrolü
- Kardiyoloji: Kalp ve damar hastalıkları
- Nöroloji: Sinir sistemi hastalıkları
- Ortopedi: Kemik, eklem ve kas hastalıkları
- Dermatoloji: Cilt hastalıkları
- Acil Servis: Acil müdahale gerektiren durumlar

JSON formatında yanıt ver:
{{
    "recommended_clinic": "Klinik adı",
    "urgency": "critical|high|medium|low",
    "reasoning": "Neden bu klinik önerildi",
    "alternatives": ["Alternatif 1", "Alternatif 2"]
}}

Önemli:
- Acil durumlar için "Acil Servis" öner
- Türkçe yanıt ver
- Sadece JSON yanıt ver"""

            response = self.llm_service.get_chat_response(prompt, "clinic_recommendation")
            
            # JSON parse etmeye çalış
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    
                    if all(key in result for key in ['recommended_clinic', 'urgency', 'reasoning']):
                        return result
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception as e:
            logging.error(f"LLM clinic recommendation error: {e}")
            return None
    
    def _rule_based_recommendation(self, symptoms: str) -> Dict[str, Any]:
        """Kural tabanlı klinik önerisi"""
        best_match = None
        best_score = 0
        
        # Her klinik için skor hesapla
        for clinic in self.clinic_data.get("clinics", []):
            score = 0
            keywords = clinic.get("keywords", [])
            
            # Anahtar kelime eşleşmelerini say
            for keyword in keywords:
                if keyword in symptoms:
                    score += 1
            
            # En yüksek skorlu kliniği seç
            if score > best_score:
                best_score = score
                best_match = clinic
        
        # Eşleşme bulunamazsa varsayılan
        if not best_match:
            best_match = {
                "name": "Genel Pratisyen",
                "urgency_level": "low",
                "description": "Genel sağlık kontrolü"
            }
        
        # Alternatifleri bul
        alternatives = self._get_alternatives(best_match["name"])
        
        return {
            "recommended_clinic": best_match["name"],
            "urgency": best_match.get("urgency_level", "low"),
            "reasoning": f"Semptomlarınız {best_match['name']} bölümüne uygun görünüyor.",
            "alternatives": alternatives
        }
    
    def _get_alternatives(self, recommended_clinic: str) -> List[str]:
        """Alternatif klinikleri bul"""
        alternatives = []
        
        for clinic in self.clinic_data.get("clinics", []):
            if clinic["name"] != recommended_clinic:
                alternatives.append(clinic["name"])
        
        # En fazla 3 alternatif döndür
        return alternatives[:3]
    
    def get_clinic_info(self, clinic_id: str) -> Optional[Dict[str, Any]]:
        """Klinik bilgilerini al"""
        for clinic in self.clinic_data.get("clinics", []):
            if clinic["id"] == clinic_id:
                return clinic
        return None
    
    def get_all_clinics(self) -> List[Dict[str, Any]]:
        """Tüm klinikleri listele"""
        return self.clinic_data.get("clinics", [])
    
    def _get_default_recommendation(self) -> Dict[str, Any]:
        """Varsayılan öneri"""
        return {
            "recommended_clinic": "Genel Pratisyen",
            "urgency": "low",
            "reasoning": "Genel sağlık kontrolü için uygun",
            "alternatives": ["İç Hastalıkları", "Aile Hekimi"]
        }
