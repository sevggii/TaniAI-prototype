#!/usr/bin/env python3
"""
Triyaj Servisi
Semptom analizi ve klinik önerisi
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

class TriageService:
    """Semptom triyajı ve klinik önerisi servisi"""
    
    def __init__(self):
        self.llm_service = None
        self.clinic_data = self._load_clinic_data()
        self.symptom_patterns = self._load_symptom_patterns()
        
        # LLM servisini import et
        try:
            from llm_service import LLMService
            self.llm_service = LLMService()
        except ImportError:
            logging.warning("LLM service not available, using rule-based triage")
    
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
                    "specialties": ["Genel Tıp", "Aile Hekimliği"],
                    "urgency_keywords": ["genel", "rutin", "kontrol"]
                },
                {
                    "id": "cardiology",
                    "name": "Kardiyoloji",
                    "specialties": ["Kalp", "Damar"],
                    "urgency_keywords": ["göğüs", "kalp", "nefes", "çarpıntı", "ağrı"]
                },
                {
                    "id": "neurology",
                    "name": "Nöroloji",
                    "specialties": ["Beyin", "Sinir"],
                    "urgency_keywords": ["baş", "baş ağrısı", "nöroloji", "sinir", "felç"]
                },
                {
                    "id": "emergency",
                    "name": "Acil Servis",
                    "specialties": ["Acil"],
                    "urgency_keywords": ["acil", "kritik", "hayati", "kanama", "travma"]
                }
            ]
        }
    
    def _load_symptom_patterns(self) -> Dict[str, Any]:
        """Semptom kalıplarını yükle"""
        return {
            "high_urgency": [
                "göğüs ağrısı", "nefes darlığı", "bayılma", "şiddetli baş ağrısı",
                "kanama", "travma", "yüksek ateş", "bilinç kaybı", "felç",
                "kalp krizi", "inme", "akut", "kritik"
            ],
            "medium_urgency": [
                "ağrı", "ateş", "bulantı", "kusma", "ishal", "öksürük",
                "halsizlik", "yorgunluk", "uykusuzluk", "stres", "anksiyete"
            ],
            "low_urgency": [
                "kontrol", "rutin", "genel", "check-up", "muayene",
                "soru", "bilgi", "danışmanlık"
            ]
        }
    
    def analyze_symptoms(self, symptoms: str) -> Dict[str, Any]:
        """Semptomları analiz et ve triyaj yap"""
        try:
            symptoms_lower = symptoms.lower()
            
            # Önce LLM ile analiz yapmaya çalış
            if self.llm_service:
                llm_result = self._analyze_with_llm(symptoms)
                if llm_result:
                    return llm_result
            
            # LLM yoksa kural tabanlı analiz
            return self._rule_based_analysis(symptoms_lower)
            
        except Exception as e:
            logging.error(f"Triage analysis error: {e}")
            return self._get_default_response()
    
    def _analyze_with_llm(self, symptoms: str) -> Optional[Dict[str, Any]]:
        """LLM ile semptom analizi"""
        try:
            prompt = f"""Aşağıdaki semptomları analiz et ve JSON formatında yanıt ver:

Semptomlar: {symptoms}

Yanıt formatı:
{{
    "urgency": "high|medium|low",
    "recommended_clinic": "Klinik adı",
    "analysis": "Detaylı analiz",
    "recommendations": ["Öneri 1", "Öneri 2"],
    "confidence": 0.8
}}

Önemli:
- Acil durumlar için urgency: "high"
- Orta öncelikli durumlar için urgency: "medium"  
- Normal durumlar için urgency: "low"
- Türkçe yanıt ver
- Sadece JSON yanıt ver, başka açıklama yapma"""

            response = self.llm_service.get_chat_response(prompt, "triage_analysis")
            
            # JSON parse etmeye çalış
            try:
                # JSON kısmını bul
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != -1:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    
                    # Gerekli alanları kontrol et
                    if all(key in result for key in ['urgency', 'recommended_clinic', 'analysis']):
                        return result
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception as e:
            logging.error(f"LLM triage error: {e}")
            return None
    
    def _rule_based_analysis(self, symptoms: str) -> Dict[str, Any]:
        """Kural tabanlı semptom analizi"""
        urgency = "low"
        recommended_clinic = "Genel Pratisyen"
        analysis = "Genel sağlık kontrolü önerilir."
        recommendations = ["Bol su için", "Dinlenin", "Doktor muayenesi yaptırın"]
        confidence = 0.6
        
        # Acil durum kontrolü
        for pattern in self.symptom_patterns["high_urgency"]:
            if pattern in symptoms:
                urgency = "high"
                recommended_clinic = "Acil Servis"
                analysis = "Acil müdahale gerektirebilecek semptomlar tespit edildi."
                recommendations = [
                    "En kısa sürede acil servise başvurun",
                    "112'yi arayın (gerekirse)",
                    "Yanınızda birisi olsun"
                ]
                confidence = 0.9
                break
        
        # Orta öncelik kontrolü
        if urgency == "low":
            for pattern in self.symptom_patterns["medium_urgency"]:
                if pattern in symptoms:
                    urgency = "medium"
                    recommended_clinic = self._get_clinic_for_symptoms(symptoms)
                    analysis = "Dikkat gerektiren semptomlar tespit edildi."
                    recommendations = [
                        "24-48 saat içinde doktora başvurun",
                        "Semptomları takip edin",
                        "Dinlenin"
                    ]
                    confidence = 0.7
                    break
        
        return {
            "urgency": urgency,
            "recommended_clinic": recommended_clinic,
            "analysis": analysis,
            "recommendations": recommendations,
            "confidence": confidence
        }
    
    def _get_clinic_for_symptoms(self, symptoms: str) -> str:
        """Semptomlara göre uygun kliniği bul"""
        for clinic in self.clinic_data.get("clinics", []):
            for keyword in clinic.get("urgency_keywords", []):
                if keyword in symptoms:
                    return clinic["name"]
        return "Genel Pratisyen"
    
    def _get_default_response(self) -> Dict[str, Any]:
        """Varsayılan yanıt"""
        return {
            "urgency": "normal",
            "recommended_clinic": "Genel Pratisyen",
            "analysis": "Genel sağlık kontrolü önerilir.",
            "recommendations": ["Bol su için", "Dinlenin", "Doktor muayenesi yaptırın"],
            "confidence": 0.5
        }
