#!/usr/bin/env python3
"""
Semptom Analiz Modülü
Whisper transkripsiyonundan semptom çıkarma
"""

import re
from typing import Dict, List, Any

class SymptomAnalyzer:
    """Sesli transkripsiyondan semptom çıkaran sınıf"""
    
    def __init__(self):
        self.symptom_keywords = {
            'yorgunluk': [
                'yorgun', 'yorgunum', 'halsiz', 'halsizim', 'bitkin', 'bitkinim',
                'enerjim yok', 'güçsüz', 'güçsüzüm', 'tükenmiş', 'tükenmişim'
            ],
            'bulanti': [
                'bulantı', 'bulantım', 'kusacak', 'mide bulanıyor', 'mide bulantısı',
                'kusma', 'kusmak', 'mide bulandırıyor'
            ],
            'ates': [
                'ateş', 'ateşim', 'fever', 'sıcaklık', 'yüksek ateş',
                'ateşim var', 'sıcaklığım yüksek'
            ],
            'bas_agrisi': [
                'baş ağrısı', 'başım ağrıyor', 'kafam ağrıyor', 'baş ağrım',
                'başımda ağrı', 'kafamda ağrı'
            ],
            'karin_agrisi': [
                'karın ağrısı', 'karınım ağrıyor', 'mide ağrısı', 'karın ağrım',
                'mide ağrım', 'karınımda ağrı'
            ],
            'sari': [
                'sarılık', 'sarı', 'sarı renk', 'cilt sararması', 'sarı cilt',
                'sarılık var', 'cildim sarı'
            ],
            'adet_gecikmesi': [
                'adet gecikmesi', 'regl gecikmesi', 'adet olmadım', 'regl olmadım',
                'adet gecikti', 'regl gecikti'
            ],
            'meme_hassasiyeti': [
                'meme ağrısı', 'göğüs ağrısı', 'meme hassasiyeti', 'göğüs hassasiyeti',
                'meme ağrım', 'göğüs ağrım'
            ],
            'sac_dokulmesi': [
                'saç dökülmesi', 'saçlarım dökülüyor', 'kellik', 'saç kaybı',
                'saçlarım azaldı', 'saç dökülüyor'
            ],
            'kilo_degisimi': [
                'kilo aldım', 'kilo verdim', 'kilo değişimi', 'kilo kaybı',
                'kilo artışı', 'zayıfladım', 'şişmanladım'
            ],
            'kas_agrisi': [
                'kas ağrısı', 'kaslarım ağrıyor', 'kas ağrım', 'kaslarımda ağrı',
                'kas sızısı', 'kaslarım sızlıyor'
            ],
            'eklem_agrisi': [
                'eklem ağrısı', 'eklemlerim ağrıyor', 'eklem ağrım', 'eklemlerimde ağrı',
                'eklem sızısı', 'eklemlerim sızlıyor'
            ],
            'uyku_bozuklugu': [
                'uyku bozukluğu', 'uyuyamıyorum', 'uyku sorunu', 'uykusuzluk',
                'uyku problemi', 'uyku düzensizliği'
            ],
            'depresyon': [
                'depresyon', 'depresyondayım', 'moralim bozuk', 'üzgünüm',
                'karamsar', 'motivasyonum yok'
            ],
            'konsantrasyon_bozuklugu': [
                'konsantrasyon bozukluğu', 'odaklanamıyorum', 'dikkat dağınıklığı',
                'konsantre olamıyorum', 'dikkat sorunu'
            ]
        }
        
        # Şiddet belirleyici kelimeler
        self.severity_keywords = {
            'hafif': ['hafif', 'biraz', 'az', 'hafifçe', 'birazcık'],
            'orta': ['orta', 'orta seviye', 'makul', 'normal'],
            'şiddetli': ['çok', 'çok fazla', 'aşırı', 'şiddetli', 'çok şiddetli', 'dayanılmaz']
        }
    
    def analyze_transcript(self, transcript: str) -> Dict[str, Any]:
        """
        Transkripsiyonu analiz eder ve semptomları çıkarır
        
        Args:
            transcript: Transkripsiyon metni
            
        Returns:
            Dict: Analiz sonucu
        """
        transcript_lower = transcript.lower()
        detected_symptoms = {}
        
        # Her semptom için kontrol et
        for symptom, keywords in self.symptom_keywords.items():
            severity = 0
            
            for keyword in keywords:
                if keyword in transcript_lower:
                    # Şiddet belirleme
                    severity = self._determine_severity(transcript_lower, keyword)
                    break
            
            if severity > 0:
                detected_symptoms[symptom] = severity
        
        return {
            "transcript": transcript,
            "detected_symptoms": detected_symptoms,
            "symptom_count": len(detected_symptoms),
            "analysis_success": True
        }
    
    def _determine_severity(self, transcript: str, keyword: str) -> int:
        """
        Semptom şiddetini belirler
        
        Args:
            transcript: Transkripsiyon metni
            keyword: Bulunan anahtar kelime
            
        Returns:
            int: Şiddet seviyesi (1-3)
        """
        # Anahtar kelimenin etrafındaki metni al
        keyword_index = transcript.find(keyword)
        context_start = max(0, keyword_index - 50)
        context_end = min(len(transcript), keyword_index + len(keyword) + 50)
        context = transcript[context_start:context_end]
        
        # Şiddetli kelimeleri kontrol et
        for severity_level, severity_words in self.severity_keywords.items():
            for word in severity_words:
                if word in context:
                    if severity_level == 'hafif':
                        return 1
                    elif severity_level == 'orta':
                        return 2
                    elif severity_level == 'şiddetli':
                        return 3
        
        # Varsayılan şiddet
        return 1
    
    def get_symptom_suggestions(self, partial_text: str) -> List[str]:
        """
        Kısmi metin için semptom önerileri döndürür
        
        Args:
            partial_text: Kısmi metin
            
        Returns:
            List[str]: Önerilen semptomlar
        """
        suggestions = []
        partial_lower = partial_text.lower()
        
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if keyword.startswith(partial_lower) or partial_lower in keyword:
                    suggestions.append(keyword)
                    break
        
        return suggestions[:5]  # En fazla 5 öneri

# Global analyzer instance
symptom_analyzer = SymptomAnalyzer()

def get_symptom_analyzer() -> SymptomAnalyzer:
    """Symptom analyzer instance'ını döndürür"""
    return symptom_analyzer
