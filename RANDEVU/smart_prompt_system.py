#!/usr/bin/env python3
"""
Akıllı Prompt Engineering Sistemi
En basit ama etkili yöntem
"""

import json
import requests
import logging
from collections import Counter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartPromptSystem:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.dataset_path = '/Users/sevgi/TaniAI-prototype/RANDEVU/mobile_flutter/klinik_dataset.jsonl'
        
    def load_clinic_examples(self):
        """Her klinikten örnek şikayetler yükle"""
        clinic_examples = {}
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    clinic = data['clinic']
                    complaint = data['complaint']
                    
                    if clinic not in clinic_examples:
                        clinic_examples[clinic] = []
                    clinic_examples[clinic].append(complaint)
        
        # Her klinikten en fazla 5 örnek al
        for clinic in clinic_examples:
            clinic_examples[clinic] = clinic_examples[clinic][:5]
        
        return clinic_examples
    
    def create_smart_prompt(self, complaint: str):
        """Akıllı prompt oluştur"""
        clinic_examples = self.load_clinic_examples()
        
        # En çok kullanılan klinikleri al
        all_clinics = []
        for examples in clinic_examples.values():
            all_clinics.extend(examples)
        
        clinic_counts = Counter()
        for examples in clinic_examples.values():
            for example in examples:
                # Her örnek için klinik sayısını artır
                clinic_counts[list(clinic_examples.keys())[list(clinic_examples.values()).index(examples)]] += 1
        
        # En popüler 10 kliniği al
        top_clinics = [clinic for clinic, count in clinic_counts.most_common(10)]
        
        # Prompt oluştur
        prompt = f"""Sen bir tıbbi asistan AI'sın. 8000 hasta verisi ile eğitilmişsin.

Kullanıcı Şikayeti: "{complaint}"

Mevcut Klinikler ve Örnek Şikayetler:

"""
        
        # Her klinik için örnekler ekle
        for clinic in top_clinics:
            if clinic in clinic_examples:
                prompt += f"\n{clinic}:\n"
                for example in clinic_examples[clinic]:
                    prompt += f"  - {example}\n"
        
        prompt += f"""

Bu verilere dayanarak en uygun kliniği öner. Sadece JSON formatında yanıt ver:

{{
    "primary_clinic": {{
        "name": "Klinik Adı",
        "reason": "Neden bu klinik öneriliyor",
        "confidence": 0.85
    }},
    "secondary_clinics": [
        {{
            "name": "Alternatif Klinik",
            "reason": "Alternatif neden",
            "confidence": 0.70
        }}
    ]
}}"""
        
        return prompt
    
    def analyze_complaint(self, complaint: str):
        """Şikayeti analiz et"""
        try:
            prompt = self.create_smart_prompt(complaint)
            
            response = requests.post(
                self.ollama_url,
                json={
                    "model": "tinyllama",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "max_tokens": 400
                    }
                },
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', '')
                
                # JSON parse et
                try:
                    start_idx = llm_response.find('{')
                    end_idx = llm_response.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx != -1:
                        json_str = llm_response[start_idx:end_idx]
                        parsed_result = json.loads(json_str)
                        return parsed_result
                    else:
                        raise ValueError("JSON bulunamadı")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"JSON parse hatası: {e}")
                    return self._fallback_analysis(complaint)
            else:
                return self._fallback_analysis(complaint)
                
        except Exception as e:
            logger.error(f"Analiz hatası: {e}")
            return self._fallback_analysis(complaint)
    
    def _fallback_analysis(self, complaint: str):
        """Fallback analiz"""
        complaint_lower = complaint.lower()
        
        if any(word in complaint_lower for word in ['baş', 'kafa', 'migren']):
            return {
                'primary_clinic': {
                    'name': 'Nöroloji',
                    'reason': 'Baş ağrısı şikayetleri için en uygun klinik',
                    'confidence': 0.80
                },
                'secondary_clinics': [
                    {
                        'name': 'Aile Hekimliği',
                        'reason': 'Genel değerlendirme için alternatif',
                        'confidence': 0.60
                    }
                ]
            }
        elif any(word in complaint_lower for word in ['mide', 'karın', 'bulantı']):
            return {
                'primary_clinic': {
                    'name': 'İç Hastalıkları (Dahiliye)',
                    'reason': 'Mide ve sindirim sistemi şikayetleri için uygun klinik',
                    'confidence': 0.80
                },
                'secondary_clinics': [
                    {
                        'name': 'Aile Hekimliği',
                        'reason': 'Genel değerlendirme için alternatif',
                        'confidence': 0.60
                    }
                ]
            }
        else:
            return {
                'primary_clinic': {
                    'name': 'Aile Hekimliği',
                    'reason': 'Genel sağlık sorunları için ilk başvuru noktası',
                    'confidence': 0.75
                },
                'secondary_clinics': [
                    {
                        'name': 'İç Hastalıkları (Dahiliye)',
                        'reason': 'Detaylı değerlendirme için alternatif',
                        'confidence': 0.65
                    }
                ]
            }

if __name__ == "__main__":
    system = SmartPromptSystem()
    
    print("🎯 Akıllı Prompt Sistemi")
    print("=" * 50)
    
    # Test et
    test_complaints = [
        "başım ağrıyor midem de bulanıyor",
        "kalp çarpıntım oluyor",
        "gözlerim bulanık görüyor"
    ]
    
    for complaint in test_complaints:
        print(f"\nŞikayet: {complaint}")
        result = system.analyze_complaint(complaint)
        
        if result:
            print(f"Ana Öneri: {result['primary_clinic']['name']}")
            print(f"Neden: {result['primary_clinic']['reason']}")
            print(f"Güven: {result['primary_clinic']['confidence']*100:.0f}%")
        else:
            print("Analiz başarısız!")
        
        print("-" * 30)
