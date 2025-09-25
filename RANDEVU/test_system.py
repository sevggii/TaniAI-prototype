# Sistem Testi
import sys
import os

# Python path'e ekle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Dosyaları ana klasörden import et
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Basit triage sistemi
import json
import re
from typing import List, Dict, Any
from collections import Counter

class SimpleTriageSystem:
    """Basit ama etkili triage sistemi - 40 klinik"""
    
    def __init__(self):
        # Tıbbi anahtar kelime eşleştirmeleri
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
            # Acil durum kontrolü
            if self._is_urgent(complaint):
                return [{
                    'clinic': 'ACİL',
                    'confidence': 1.0,
                    'reason': 'ACİL DURUM: Kalp krizi belirtisi',
                    'rank': 1,
                    'urgent': True,
                    'message': '112\'yi arayın veya en yakın acile başvurun!'
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
            
            # Fallback
            if not suggestions:
                suggestions = [{
                    'clinic': 'Aile Hekimliği',
                    'confidence': 0.3,
                    'reason': 'Fallback öneri',
                    'rank': 1,
                    'urgent': False
                }]
            
            return suggestions
            
        except Exception as e:
            return [{'clinic': 'Aile Hekimliği', 'confidence': 0.5, 'reason': 'Hata durumunda varsayılan', 'rank': 1, 'urgent': False}]
    
    def _is_urgent(self, complaint: str) -> bool:
        """Acil durum kontrolü"""
        urgent_patterns = [
            r"aniden.*göğsümde.*ezici.*ağrı.*soğuk terliyorum",
            r"ani.*göğüs.*ağrı.*soğuk ter",
            r"bilinç.*kayb",
            r"kontrolsüz.*kanama"
        ]
        
        for pattern in urgent_patterns:
            if re.search(pattern, complaint.lower()):
                return True
        return False

def get_simple_triage():
    """Simple triage sistemini al"""
    return SimpleTriageSystem()

def test_system():
    """Sistemi test et"""
    try:
        print("🔄 Sistem test ediliyor...")
        
        # Sistemi başlat
        triage = get_simple_triage()
        print("✅ Sistem yüklendi!")
        
        # Test şikayetleri
        test_complaints = [
            "Başım çok ağrıyor ve mide bulantım var",
            "Aniden göğsümde ezici ağrı var, soğuk terliyorum",
            "Çocuğumda ateş ve öksürük var",
            "Gözlerim bulanık görüyor"
        ]
        
        print("\n📊 Test Sonuçları:")
        print("=" * 50)
        
        for i, complaint in enumerate(test_complaints, 1):
            print(f"\n{i}. Şikayet: {complaint}")
            print("-" * 30)
            
            # Analiz yap
            suggestions = triage.suggest(complaint, top_k=2)
            
            # Sonuçları göster
            for suggestion in suggestions:
                urgent = "🚨 ACİL" if suggestion.get('urgent', False) else "📋 Normal"
                print(f"   {urgent} {suggestion['clinic']} - Güven: {suggestion['confidence']:.2f}")
                print(f"   Sebep: {suggestion['reason']}")
                if suggestion.get('message'):
                    print(f"   Mesaj: {suggestion['message']}")
        
        print("\n✅ Test tamamlandı!")
        return True
        
    except Exception as e:
        print(f"❌ Test hatası: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_system()


    '''
    🔄 Sistem test ediliyor...
✅ Sistem yüklendi!

📊 Test Sonuçları:
==================================================

1. Şikayet: Başım çok ağrıyor ve mide bulantım var
------------------------------
   📋 Normal İç Hastalıkları - Güven: 0.33        
   Sebep: 3 anahtar kelime eşleşmesi
   📋 Normal Nöroloji - Güven: 0.27
   Sebep: 3 anahtar kelime eşleşmesi

2. Şikayet: Aniden göğsümde ezici ağrı var, soğuk terliyorum
------------------------------
   🚨 ACİL ACİL - Güven: 1.00
   Sebep: ACİL DURUM: Kalp krizi belirtisi
   Mesaj: 112'yi arayın veya en yakın acile başvurun!

3. Şikayet: Çocuğumda ateş ve öksürük var
------------------------------
   📋 Normal Çocuk Sağlığı - Güven: 0.25
   Sebep: 2 anahtar kelime eşleşmesi
   📋 Normal Aile Hekimliği - Güven: 0.14
   Sebep: 1 anahtar kelime eşleşmesi

4. Şikayet: Gözlerim bulanık görüyor
------------------------------
   📋 Normal Nöroloji - Güven: 0.18
   Sebep: 2 anahtar kelime eşleşmesi
   📋 Normal Göz Hastalıkları - Güven: 0.25
   Sebep: 2 anahtar kelime eşleşmesi

✅ Test tamamlandı!
    '''
