import re
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class EnhancedSymptomParser:
    def __init__(self):
        # Gelişmiş semptom sözlüğü - daha kapsamlı ve hassas
        self.symptom_dict = {
            "Ateş": {
                "keywords": [
                    "ateşim", "ateş", "yanıyorum", "sıcaktan kavruluyorum", "hararetim var",
                    "sıcaklık", "yüksek ateş", "düşük ateş", "hafif ateş", "şiddetli ateş",
                    "ateşleniyorum", "ateşlendim", "sıcaklığım yüksek", "termometre",
                    "39 derece", "40 derece", "fever", "hot", "temperature"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "yüksek": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "düşük": 0.2, "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["ateşim yok", "ateş olmadan", "ateşsiz"]
            },
            
            "Baş Ağrısı": {
                "keywords": [
                    "başım ağrıyor", "kafam ağrıyor", "baş ağrısı", "kafa ağrısı",
                    "başım zonkluyor", "kafam zonkluyor", "başım çatlıyor", "kafam çatlıyor",
                    "başım sızlıyor", "kafam sızlıyor", "migren", "başım dönüyor",
                    "kafam karışık", "başım dolu", "headache", "head pain", "migraine"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "korkunç": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["başım ağrımıyor", "baş ağrısı yok"]
            },
            
            "Bitkinlik": {
                "keywords": [
                    "yorgunum", "halsizim", "enerjim yok", "bitkinim", "tükenmişim",
                    "çok yorgunum", "aşırı yorgunum", "kendimi yorgun hissediyorum",
                    "gücüm yok", "halsizlik", "bitkinlik", "yorgunluk", "enerji kaybı",
                    "tired", "exhausted", "fatigue", "weak", "lethargic", "drained"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "korkunç": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["yorgun değilim", "enerjim var", "bitkin değilim"]
            },
            
            "Boğaz Ağrısı": {
                "keywords": [
                    "boğazım ağrıyor", "boğazımda ağrı", "boğaz ağrısı", "boğazımda batma",
                    "boğazım şişti", "boğazım gıcık yapıyor", "boğazımda yanma",
                    "boğazımda kaşıntı", "boğazımda kuruluk", "boğazımda takılma",
                    "throat pain", "sore throat", "throat ache", "throat burning"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "korkunç": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["boğazım ağrımıyor", "boğaz ağrısı yok"]
            },
            
            "Bulantı veya Kusma": {
                "keywords": [
                    "midem bulanıyor", "kusacak gibiyim", "bulantım var", "mide bulantısı",
                    "istifra ettim", "kusma", "kusma hissi", "mide rahatsızlığı",
                    "midem kalkıyor", "mide bulandırıcı", "nausea", "vomiting", "throw up",
                    "nauseous", "queasy", "sick to stomach"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "sürekli": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["bulantım yok", "kusma yok", "midem iyi"]
            },
            
            "Burun Akıntısı veya Tıkanıklığı": {
                "keywords": [
                    "burnum akıyor", "burun akıntısı", "burnum tıkanık", "burun tıkanıklığı",
                    "nefesim burnumdan zor geliyor", "burun dolu", "burun akması",
                    "burnumda akıntı", "burun tıkanması", "runny nose", "stuffy nose",
                    "nasal congestion", "nose running", "blocked nose"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "sürekli": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["burnum açık", "burun akıntısı yok", "burun tıkanıklığı yok"]
            },
            
            "Göz Kaşıntısı veya Sulanma": {
                "keywords": [
                    "gözüm kaşınıyor", "göz kaşıntısı", "gözüm sulanıyor", "göz sulanması",
                    "gözlerim yanıyor", "göz yanması", "gözlerim kızarık", "göz kızarıklığı",
                    "gözlerim şişti", "göz şişliği", "gözlerim sulu", "göz tahrişi",
                    "gözlerim kaşınıyor", "gözlerim sulanıyor", "göz kaşıntısı var",
                    "itchy eyes", "watery eyes", "eye irritation", "eye burning", "red eyes"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "sürekli": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["gözlerim iyi", "göz kaşıntısı yok", "göz sulanması yok"]
            },
            
            "Hapşırma": {
                "keywords": [
                    "hapşırıyorum", "hapşırma", "durmadan hapşırıyorum", "sürekli hapşırıyorum",
                    "hapşırık krizi", "hapşırık tuttu", "sneezing", "sneeze", "achoo"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "sürekli": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["hapşırma yok", "hapşırıyorum yok"]
            },
            
            "İshal": {
                "keywords": [
                    "ishalim", "ishal", "sürekli tuvalete gidiyorum", "sık sık tuvalete gidiyorum",
                    "sıvı dışkı", "cıvık dışkı", "sulu dışkı", "bağırsak rahatsızlığı",
                    "diarrhea", "loose stool", "frequent bathroom", "bowel problems"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "sürekli": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["ishal yok", "bağırsaklarım iyi", "ishal değilim"]
            },
            
            "Koku veya Tat Kaybı": {
                "keywords": [
                    "koku alamıyorum", "tat alamıyorum", "kokusuz", "tatsız",
                    "koku kaybı", "tat kaybı", "anosmi", "ageusia", "koku duyusu yok",
                    "tat duyusu yok", "burnum koku almıyor", "dilim tat almıyor",
                    "loss of smell", "loss of taste", "no smell", "no taste", "anosmia"
                ],
                "intensity_modifiers": {
                    "tamamen": 1.0, "hiç": 1.0, "çok": 0.8, "aşırı": 0.8,
                    "fazla": 0.6, "orta": 0.4, "biraz": 0.3, "hafif": 0.2,
                    "az": 0.1, "kısmen": 0.5, "yok": 0.0
                },
                "negative_words": ["koku alabiliyorum", "tat alabiliyorum", "koku kaybı yok"]
            },
            
            "Nefes Darlığı": {
                "keywords": [
                    "nefes alamıyorum", "nefes almakta zorlanıyorum", "zor nefes alıyorum",
                    "nefes darlığı", "nefesim daralıyor", "boğuluyorum", "hava yetmiyor",
                    "nefesim kesiliyor", "göğsüm sıkışıyor", "nefesim yetmiyor",
                    "shortness of breath", "breathing difficulty", "can't breathe", "dyspnea",
                    "breathless", "out of breath", "labored breathing"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "korkunç": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["nefesim iyi", "nefes darlığı yok", "rahat nefes alıyorum"]
            },
            
            "Öksürük": {
                "keywords": [
                    "öksürüyorum", "öksürük", "çok fena öksürüyorum", "öksürük krizi",
                    "hafif öksürüğüm var", "biraz öksürüyorum", "kuru öksürük",
                    "balgamlı öksürük", "sürekli öksürüyorum", "öksürük tuttu",
                    "cough", "coughing", "dry cough", "wet cough", "persistent cough"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "sürekli": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["öksürük yok", "öksürüyorum yok", "öksürme yok"]
            },
            
            "Vücut Ağrıları": {
                "keywords": [
                    "her yerim ağrıyor", "vücudum ağrıyor", "vücut ağrısı", "vücudum sızlıyor",
                    "kemiklerim ağrıyor", "kaslarım ağrıyor", "vücudum çok ağrıyor",
                    "tüm vücudum ağrıyor", "eklem ağrısı", "kas ağrısı", "vücut sızlaması",
                    "body ache", "muscle pain", "joint pain", "body pain", "ache all over"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "korkunç": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3,
                    "az": 0.2, "hiç": 0.0, "yok": 0.0
                },
                "negative_words": ["vücut ağrısı yok", "vücudum ağrımıyor", "ağrı yok"]
            }
        }
        
        # Ek semptomlar (yeni veri seti için)
        self.additional_symptoms = {
            "Göğüs Ağrısı": {
                "keywords": [
                    "göğsüm ağrıyor", "göğüs ağrısı", "göğsümde ağrı", "göğsümde sıkışma",
                    "göğsümde yanma", "göğsümde basınç", "chest pain", "chest ache"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "fazla": 0.8,
                    "orta": 0.6, "biraz": 0.4, "hafif": 0.3, "az": 0.2, "hiç": 0.0
                },
                "negative_words": ["göğüs ağrısı yok", "göğsüm ağrımıyor"]
            },
            
            "Titreme": {
                "keywords": [
                    "titriyorum", "titremeden duramıyorum", "titrıyorum", "titremeden",
                    "shaking", "tremor", "chills", "shivering"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "sürekli": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3, "az": 0.2, "hiç": 0.0
                },
                "negative_words": ["titreme yok", "titrıyorum yok"]
            },
            
            "Gece Terlemesi": {
                "keywords": [
                    "gece terliyorum", "gece terlemesi", "uyurken terliyorum",
                    "night sweats", "sweating at night"
                ],
                "intensity_modifiers": {
                    "çok": 1.0, "aşırı": 1.0, "şiddetli": 1.0, "sürekli": 1.0,
                    "fazla": 0.8, "orta": 0.6, "biraz": 0.4, "hafif": 0.3, "az": 0.2, "hiç": 0.0
                },
                "negative_words": ["gece terlemesi yok", "terleme yok"]
            },
            
            "İştahsızlık": {
                "keywords": [
                    "iştahım yok", "yemek yiyemiyorum", "yemek istemiyorum", "aç değilim",
                    "iştahsızlık", "yemek yemek istemiyorum", "appetite loss", "no appetite"
                ],
                "intensity_modifiers": {
                    "tamamen": 1.0, "hiç": 1.0, "çok": 0.8, "aşırı": 0.8,
                    "fazla": 0.6, "orta": 0.4, "biraz": 0.3, "hafif": 0.2, "az": 0.1, "yok": 0.0
                },
                "negative_words": ["iştahım var", "yemek yiyebiliyorum"]
            },
            
            "Konsantrasyon Güçlüğü": {
                "keywords": [
                    "odaklanamıyorum", "konsantre olamıyorum", "dikkatim dağınık",
                    "kafam karışık", "düşünemiyorum", "concentration problem", "can't focus"
                ],
                "intensity_modifiers": {
                    "tamamen": 1.0, "hiç": 1.0, "çok": 0.8, "aşırı": 0.8,
                    "fazla": 0.6, "orta": 0.4, "biraz": 0.3, "hafif": 0.2, "az": 0.1, "yok": 0.0
                },
                "negative_words": ["odaklanabiliyorum", "konsantre olabiliyorum"]
            }
        }
        
        # Tüm semptomları birleştir
        self.all_symptoms = {**self.symptom_dict, **self.additional_symptoms}
        
        # Zaman ifadeleri
        self.time_modifiers = {
            "sürekli": 1.0, "durmadan": 1.0, "aralıksız": 1.0, "hiç durmadan": 1.0,
            "bazen": 0.6, "ara sıra": 0.5, "nadiren": 0.3, "hiç": 0.0, "yok": 0.0
        }
        
        # Olumsuzluk ifadeleri
        self.negation_words = [
            "değil", "yok", "olmadan", "olmaz", "hiç", "asla", "ne...ne",
            "not", "no", "without", "never", "none"
        ]

    def clean_text(self, text: str) -> str:
        """Metni temizler ve normalize eder"""
        # Küçük harfe çevir
        text = text.lower()
        
        # Özel karakterleri temizle
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Fazla boşlukları temizle
        text = re.sub(r'\s+', ' ', text)
        
        # Başta ve sonda boşlukları temizle
        text = text.strip()
        
        return text

    def detect_negation(self, text: str, symptom_text: str) -> bool:
        """Olumsuzluk tespiti yapar"""
        # Semptom metninin pozisyonunu bul
        symptom_pos = text.find(symptom_text)
        if symptom_pos == -1:
            return False
        
        # Semptom metninden önceki 50 karakteri kontrol et
        before_text = text[max(0, symptom_pos - 50):symptom_pos]
        
        # Olumsuzluk kelimelerini kontrol et
        for neg_word in self.negation_words:
            if neg_word in before_text:
                return True
        
        return False

    def extract_intensity(self, text: str, symptom_text: str) -> float:
        """Şiddet seviyesini çıkarır"""
        # Semptom metninin pozisyonunu bul
        symptom_pos = text.find(symptom_text)
        if symptom_pos == -1:
            return 1.0
        
        # Semptom metninden önceki ve sonraki 30 karakteri kontrol et
        context_start = max(0, symptom_pos - 30)
        context_end = min(len(text), symptom_pos + len(symptom_text) + 30)
        context = text[context_start:context_end]
        
        # Şiddet belirteçlerini ara
        max_intensity = 1.0
        for modifier, intensity in self.all_symptoms[symptom_text]["intensity_modifiers"].items():
            if modifier in context:
                max_intensity = max(max_intensity, intensity)
        
        # Zaman belirteçlerini kontrol et
        for time_mod, intensity in self.time_modifiers.items():
            if time_mod in context:
                max_intensity = max_intensity * intensity
        
        return max_intensity

    def parse_symptoms(self, text: str) -> Dict[str, float]:
        """Ana parsing fonksiyonu"""
        text = self.clean_text(text)
        symptom_scores = {}
        
        # Her semptom için kontrol et
        for symptom_name, symptom_data in self.all_symptoms.items():
            max_score = 0.0
            
            # Her keyword için kontrol et
            for keyword in symptom_data["keywords"]:
                if keyword in text:
                    # Olumsuzluk kontrolü
                    if self.detect_negation(text, keyword):
                        continue
                    
                    # Şiddet seviyesini al
                    intensity = self.extract_intensity(text, symptom_name)
                    
                    # Negatif kelime kontrolü
                    is_negative = False
                    for neg_word in symptom_data.get("negative_words", []):
                        if neg_word in text:
                            is_negative = True
                            break
                    
                    if not is_negative:
                        max_score = max(max_score, intensity)
            
            symptom_scores[symptom_name] = max_score
        
        return symptom_scores

    def create_symptom_vector(self, text: str, symptom_order: List[str]) -> List[float]:
        """Semptom vektörü oluşturur"""
        parsed_symptoms = self.parse_symptoms(text)
        
        # Semptom sırasına göre vektör oluştur
        vector = []
        for symptom in symptom_order:
            if symptom in parsed_symptoms:
                vector.append(parsed_symptoms[symptom])
            else:
                vector.append(0.0)
        
        return vector

    def get_diagnostic_confidence(self, symptom_vector: List[float]) -> Dict[str, float]:
        """Tanısal güven skorları hesaplar"""
        confidence_scores = {}
        
        # COVID-19 güven skoru
        covid_key_symptoms = ["Koku veya Tat Kaybı", "Nefes Darlığı", "Ateş"]
        covid_score = 0
        for symptom in covid_key_symptoms:
            if symptom in self.all_symptoms:
                idx = list(self.all_symptoms.keys()).index(symptom)
                if idx < len(symptom_vector):
                    covid_score += symptom_vector[idx]
        confidence_scores["COVID-19"] = min(1.0, covid_score / 3.0)
        
        # Grip güven skoru
        flu_key_symptoms = ["Ateş", "Vücut Ağrıları", "Titreme"]
        flu_score = 0
        for symptom in flu_key_symptoms:
            if symptom in self.all_symptoms:
                idx = list(self.all_symptoms.keys()).index(symptom)
                if idx < len(symptom_vector):
                    flu_score += symptom_vector[idx]
        confidence_scores["Grip"] = min(1.0, flu_score / 3.0)
        
        # Soğuk algınlığı güven skoru
        cold_key_symptoms = ["Burun Akıntısı veya Tıkanıklığı", "Hapşırma", "Boğaz Ağrısı"]
        cold_score = 0
        for symptom in cold_key_symptoms:
            if symptom in self.all_symptoms:
                idx = list(self.all_symptoms.keys()).index(symptom)
                if idx < len(symptom_vector):
                    cold_score += symptom_vector[idx]
        confidence_scores["Soğuk Algınlığı"] = min(1.0, cold_score / 3.0)
        
        # Alerji güven skoru
        allergy_key_symptoms = ["Göz Kaşıntısı veya Sulanma", "Hapşırma", "Burun Akıntısı veya Tıkanıklığı"]
        allergy_score = 0
        for symptom in allergy_key_symptoms:
            if symptom in self.all_symptoms:
                idx = list(self.all_symptoms.keys()).index(symptom)
                if idx < len(symptom_vector):
                    allergy_score += symptom_vector[idx]
        confidence_scores["Mevsimsel Alerji"] = min(1.0, allergy_score / 3.0)
        
        return confidence_scores

# Kullanım örneği
if __name__ == "__main__":
    parser = EnhancedSymptomParser()
    
    # Test metinleri
    test_cases = [
        "Çok yüksek ateşim var, nefes alamıyorum, koku alamıyorum ve öksürüyorum",
        "Ateşim var, vücudum ağrıyor, titreme tuttu, çok yorgunum",
        "Burnum akıyor, hapşırıyorum, boğazım ağrıyor ama ateşim yok",
        "Gözlerim kaşınıyor, hapşırıyorum, burnum tıkanık ama ateşim yok"
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {text}")
        
        # Semptom vektörü oluştur
        symptom_order = list(parser.all_symptoms.keys())
        vector = parser.create_symptom_vector(text, symptom_order)
        
        # Sonuçları göster
        print("📊 Tespit edilen semptomlar:")
        for j, (symptom, score) in enumerate(zip(symptom_order, vector)):
            if score > 0:
                print(f"  {symptom}: {score:.2f}")
        
        # Tanısal güven skorları
        confidence = parser.get_diagnostic_confidence(vector)
        print("\n🎯 Tanısal güven skorları:")
        for disease, score in confidence.items():
            print(f"  {disease}: {score:.2f}")
