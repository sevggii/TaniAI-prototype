import json
import os
import re
from typing import List, Dict, Any
from collections import Counter
try:
    from .triage_direct import suggest as direct_suggest, RED_FLAGS
except ImportError:
    # Fallback: direkt import
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from triage_direct import suggest as direct_suggest, RED_FLAGS

class SimpleTriageSystem:
    """Basit ama etkili triage sistemi - 40 klinik"""
    
    def __init__(self):
        # Tüm 40 klinik için anahtar kelimeler
        self.medical_keywords = {
            'Aile Hekimliği': ['genel', 'check-up', 'rutin', 'kontrol', 'muayene', 'ateş', 'halsizlik'],
            'İç Hastalıkları': ['mide', 'bulantı', 'kusma', 'karın', 'ağrı', 'ateş', 'halsizlik', 'yorgunluk', 'iştahsızlık'],
            'Nöroloji': ['baş', 'ağrı', 'baş ağrısı', 'migren', 'baş dönmesi', 'bulantı', 'kusma', 'görme', 'göz', 'bulanık', 'titreme'],
            'Kardiyoloji': ['kalp', 'göğüs', 'ağrı', 'nefes', 'darlığı', 'çarpıntı', 'tansiyon', 'göğüs ağrısı', 'kalp ağrısı'],
            'Gastroenteroloji': ['mide', 'karın', 'ağrı', 'bulantı', 'kusma', 'ishal', 'kabızlık', 'karın ağrısı', 'mide ağrısı'],
            'Ortopedi': ['kemik', 'eklem', 'ağrı', 'sırt', 'bel', 'boyun', 'omuz', 'diz', 'bacak', 'kol', 'kırık', 'çıkık'],
            'Dermatoloji': ['cilt', 'deri', 'kaşıntı', 'döküntü', 'lekeler', 'yara', 'kızarıklık', 'egzama', 'sedef'],
            'Göz Hastalıkları': ['göz', 'görme', 'bulanık', 'ağrı', 'kızarıklık', 'yaşarma', 'göz ağrısı', 'görme bozukluğu'],
            'Kulak Burun Boğaz': ['kulak', 'burun', 'boğaz', 'ağrı', 'tıkanıklık', 'ses', 'işitme', 'burun tıkanıklığı', 'boğaz ağrısı'],
            'Üroloji': ['idrar', 'böbrek', 'ağrı', 'yanma', 'sık idrara çıkma', 'kan', 'idrar yolu', 'böbrek ağrısı'],
            'Kadın Hastalıkları': ['adet', 'hamilelik', 'rahim', 'yumurtalık', 'ağrı', 'kanama', 'gebelik', 'doğum'],
            'Çocuk Sağlığı': ['çocuk', 'bebek', 'ateş', 'öksürük', 'ishal', 'kusma', 'çocuk hastalığı', 'bebek hastalığı'],
            'Psikiyatri': ['depresyon', 'anksiyete', 'stres', 'panik', 'uyku', 'iştah', 'kaygı', 'endişe', 'mutsuzluk'],
            'Endokrinoloji': ['şeker', 'diyabet', 'tiroid', 'hormon', 'kilo', 'şişmanlık', 'zayıflık', 'guatr'],
            'Göğüs Hastalıkları': ['akciğer', 'nefes', 'öksürük', 'balgam', 'astım', 'bronşit', 'nefes darlığı'],
            'Romatoloji': ['romatizma', 'eklem', 'ağrı', 'şişlik', 'sertlik', 'artrit', 'lupus', 'fibromiyalji'],
            'Onkoloji': ['kanser', 'tümör', 'kitle', 'biyopsi', 'kemoterapi', 'radyoterapi', 'onkoloji'],
            'Nefroloji': ['böbrek', 'diyaliz', 'idrar', 'protein', 'kreatinin', 'böbrek yetmezliği'],
            'Hematoloji': ['kan', 'anemi', 'lösemi', 'lenfoma', 'kanama', 'pıhtı', 'hemoglobin'],
            'Plastik Cerrahi': ['estetik', 'yanık', 'yara', 'skarlar', 'doğumsal', 'travma', 'rekonstrüksiyon'],
            'Genel Cerrahi': ['apandisit', 'fıtık', 'safra', 'karın', 'ameliyat', 'cerrahi', 'operasyon'],
            'Beyin Cerrahisi': ['beyin', 'kafa', 'travma', 'tümör', 'anevrizma', 'hidrosefali', 'beyin cerrahisi'],
            'Kalp Damar Cerrahisi': ['kalp', 'damar', 'bypass', 'kapak', 'anevrizma', 'kalp cerrahisi'],
            'Ortopedi ve Travmatoloji': ['kemik', 'eklem', 'ağrı', 'sırt', 'bel', 'boyun', 'omuz', 'diz', 'kırık', 'çıkık'],
            'Üroloji': ['idrar', 'böbrek', 'ağrı', 'yanma', 'sık idrara çıkma', 'kan', 'idrar yolu', 'böbrek ağrısı'],
            'Kadın Hastalıkları ve Doğum': ['adet', 'hamilelik', 'rahim', 'yumurtalık', 'ağrı', 'kanama', 'gebelik', 'doğum'],
            'Çocuk Cerrahisi': ['çocuk', 'bebek', 'cerrahi', 'doğumsal', 'travma', 'çocuk ameliyatı'],
            'Çocuk Nörolojisi': ['çocuk', 'bebek', 'nöroloji', 'epilepsi', 'gelişim', 'çocuk nörolojisi'],
            'Çocuk Kardiyolojisi': ['çocuk', 'bebek', 'kalp', 'doğumsal', 'kalp hastalığı', 'çocuk kalp'],
            'Çocuk Gastroenterolojisi': ['çocuk', 'bebek', 'mide', 'karın', 'ishal', 'kusma', 'çocuk mide'],
            'Çocuk Endokrinolojisi': ['çocuk', 'bebek', 'şeker', 'diyabet', 'büyüme', 'çocuk hormon'],
            'Çocuk Hematolojisi': ['çocuk', 'bebek', 'kan', 'anemi', 'lösemi', 'çocuk kan'],
            'Çocuk Onkolojisi': ['çocuk', 'bebek', 'kanser', 'tümör', 'çocuk kanser', 'pediatrik onkoloji'],
            'Çocuk Romatolojisi': ['çocuk', 'bebek', 'romatizma', 'eklem', 'çocuk romatizma'],
            'Çocuk Nefrolojisi': ['çocuk', 'bebek', 'böbrek', 'idrar', 'çocuk böbrek'],
            'Çocuk Göğüs Hastalıkları': ['çocuk', 'bebek', 'akciğer', 'nefes', 'öksürük', 'çocuk akciğer'],
            'Çocuk Dermatolojisi': ['çocuk', 'bebek', 'cilt', 'deri', 'kaşıntı', 'çocuk cilt'],
            'Çocuk Göz Hastalıkları': ['çocuk', 'bebek', 'göz', 'görme', 'çocuk göz'],
            'Çocuk Kulak Burun Boğaz': ['çocuk', 'bebek', 'kulak', 'burun', 'boğaz', 'çocuk KBB'],
            'Çocuk Psikiyatrisi': ['çocuk', 'bebek', 'psikiyatri', 'davranış', 'çocuk psikiyatri']
        }
    
    def suggest(self, complaint: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Şikayete göre klinik öner - Acil durum kontrolü ile"""
        try:
            # Önce acil durum kontrolü yap
            direct_result = direct_suggest(complaint, top_k)
            
            # Eğer acil durum varsa
            if isinstance(direct_result, dict) and direct_result.get("action") == "ACIL":
                return [{
                    'clinic': 'ACİL',
                    'confidence': 1.0,
                    'reason': f"ACİL DURUM: {direct_result.get('red_flag', 'Bilinmeyen')}",
                    'rank': 1,
                    'urgent': True,
                    'message': direct_result.get('message', 'Acil durum tespit edildi!')
                }]
            
            # Normal triage işlemi
            clinic_scores = {}
            complaint_lower = complaint.lower()
            
            for clinic, keywords in self.medical_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in complaint_lower:
                        score += 1
                clinic_scores[clinic] = score
            
            # En yüksek skorlu klinikleri al
            sorted_clinics = sorted(clinic_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Sonuçları formatla
            suggestions = []
            for i, (clinic, score) in enumerate(sorted_clinics[:top_k]):
                if score > 0:
                    suggestions.append({
                        'clinic': clinic,
                        'confidence': score / len(self.medical_keywords[clinic]),
                        'reason': f"{score} anahtar kelime eşleşmesi",
                        'rank': i + 1,
                        'urgent': False
                    })
            
            # Eğer hiç eşleşme yoksa, direct_suggest'ten fallback al
            if not suggestions:
                if isinstance(direct_result, dict) and 'suggestions' in direct_result:
                    for i, clinic in enumerate(direct_result['suggestions'][:top_k]):
                        suggestions.append({
                            'clinic': clinic,
                            'confidence': 0.3,
                            'reason': 'Fallback öneri',
                            'rank': i + 1,
                            'urgent': False
                        })
            
            return suggestions
            
        except Exception as e:
            return [{'clinic': 'Aile Hekimliği', 'confidence': 0.5, 'reason': 'Hata durumunda varsayılan', 'rank': 1, 'urgent': False}]
    
    def learn_from_dataset(self, dataset_path: str):
        """Veri setinden öğren"""
        try:
            print("🔄 Veri setinden öğreniliyor...")
            
            # Veri setini oku
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = []
                for line in f:
                    if line.strip():
                        try:
                            data.append(json.loads(line.strip()))
                        except:
                            continue
            
            print(f"✅ {len(data)} şikayet yüklendi!")
            
            # Her klinik için anahtar kelimeleri güncelle
            clinic_keywords = {}
            for item in data:
                clinic = item.get('clinic', '')
                complaint = item.get('complaint', '')
                
                if clinic and complaint:
                    if clinic not in clinic_keywords:
                        clinic_keywords[clinic] = []
                    
                    # Şikayetten anahtar kelimeleri çıkar
                    words = re.findall(r'\w+', complaint.lower())
                    clinic_keywords[clinic].extend(words)
            
            # En sık kullanılan kelimeleri al
            for clinic, words in clinic_keywords.items():
                word_counts = Counter(words)
                top_words = [word for word, count in word_counts.most_common(20)]
                
                # Mevcut anahtar kelimelerle birleştir
                if clinic in self.medical_keywords:
                    self.medical_keywords[clinic].extend(top_words)
                    # Tekrarları kaldır
                    self.medical_keywords[clinic] = list(set(self.medical_keywords[clinic]))
            
            print("✅ Veri setinden öğrenme tamamlandı!")
            return True
            
        except Exception as e:
            print(f"❌ Veri seti öğrenme hatası: {e}")
            return False

# Global instance
_simple_triage = None

def get_simple_triage():
    """Simple triage sistemini al"""
    global _simple_triage
    if _simple_triage is None:
        _simple_triage = SimpleTriageSystem()
    return _simple_triage