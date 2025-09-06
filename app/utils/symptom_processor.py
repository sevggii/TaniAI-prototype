import re
from typing import List, Dict
import unicodedata

class SymptomProcessor:
    def __init__(self):
        # Gelişmiş semptom anahtar kelimeleri - eşanlamlı ve varyantlar
        self.symptom_keywords = {
            # Temel semptomlar
            'yorgunluk': ['yorgun', 'bitkin', 'halsiz', 'güçsüz', 'enerjisiz', 'tükenmiş', 'kırgın', 'bitap'],
            'halsizlik': ['halsiz', 'güçsüz', 'zayıf', 'bitkin', 'tükenmiş', 'kırgın', 'dermansız'],
            'enerji_dusuklugu': ['enerji düşüklüğü', 'enerji azlığı', 'güçsüzlük', 'halsizlik', 'bitkinlik'],
            
            # Ağrı semptomları
            'bas_agrisi': ['baş ağrısı', 'başağrısı', 'baş ağrı', 'kafada ağrı', 'kafa ağrısı', 'migren'],
            'kas_agrisi': ['kas ağrısı', 'kas ağrı', 'kaslarda ağrı', 'kas sızısı', 'kas sancısı', 'adale ağrısı'],
            'eklem_agrisi': ['eklem ağrısı', 'eklem ağrı', 'eklemlerde ağrı', 'romatizma', 'eklem sancısı'],
            'kemik_agrisi': ['kemik ağrısı', 'kemik ağrı', 'osteoporoz', 'kemik erimesi', 'kemik sancısı'],
            'karin_agrisi': ['karın ağrısı', 'karın ağrı', 'mide ağrısı', 'karnım ağrıyor', 'karın sancısı'],
            'gogus_agrisi': ['göğüs ağrısı', 'göğüs ağrı', 'kalp ağrısı', 'göğsüm ağrıyor', 'göğüs sancısı'],
            
            # Mide-bağırsak semptomları
            'mide_bulantisi': ['mide bulantısı', 'bulantı', 'mide bulanması', 'kusma hissi', 'mide bulanması'],
            'kusma': ['kusma', 'kustu', 'kusuyor', 'kustum', 'kusturma'],
            'ishal': ['ishal', 'sulu dışkı', 'dışkı sulu', 'bağırsak bozukluğu', 'sürgün'],
            'kabizlik': ['kabızlık', 'kabizlik', 'dışkı yapamama', 'bağırsak tıkanması', 'konstipasyon'],
            
            # Solunum ve kalp semptomları
            'nefes_darligi': ['nefes darlığı', 'nefes alamama', 'solunum güçlüğü', 'nefes kesilmesi', 'dispne'],
            'kalp_ritim_bozuklugu': ['kalp çarpıntısı', 'kalp ritim bozukluğu', 'aritmi', 'kalp atışı', 'çarpıntı'],
            'kalp_carpintisi': ['kalp çarpıntısı', 'çarpıntı', 'kalp atışı', 'aritmi', 'kalp ritim bozukluğu'],
            
            # Nörolojik semptomlar
            'bas_donmesi': ['baş dönmesi', 'başdönmesi', 'dönme hissi', 'sersemlik', 'vertigo'],
            'hafiza_sorunlari': ['hafıza sorunu', 'unutkanlık', 'hafıza kaybı', 'bellek sorunu', 'unutkan', 'hafıza bozukluğu'],
            'unutkanlik': ['unutkanlık', 'unutkan', 'hafıza sorunu', 'bellek sorunu', 'hafıza kaybı'],
            'uyusma': ['uyuşma', 'uyuşukluk', 'hissizlik', 'karıncalanma', 'uyuşuk', 'hissiz'],
            'karincalanma': ['karıncalanma', 'iğne batması', 'sızı', 'yanma', 'karıncalanma hissi'],
            'nopati': ['nöropati', 'sinir hasarı', 'sinir iltihabı', 'periferik nöropati', 'sinir bozukluğu'],
            'denge_sorunlari': ['denge sorunu', 'dengesizlik', 'yürüme güçlüğü', 'koordinasyon bozukluğu', 'dengesiz'],
            
            # Görme semptomları
            'goz_yorgunlugu': ['göz yorgunluğu', 'göz ağrısı', 'göz yanması', 'göz kuruluğu', 'göz yorgunluğu'],
            'goz_kurulugu': ['göz kuruluğu', 'kuru göz', 'göz yaşı eksikliği', 'göz kuruluğu'],
            'gece_korlugu': ['gece körlüğü', 'gece görme sorunu', 'karanlıkta görememe', 'gece görme bozukluğu'],
            'gorme_sorunlari': ['görme sorunu', 'görme bozukluğu', 'bulanık görme', 'görme kaybı', 'görme bozukluğu'],
            'isiga_duyarlilik': ['ışığa duyarlılık', 'fotofobi', 'göz ışık hassasiyeti', 'ışık hassasiyeti'],
            
            # Cilt ve saç semptomları
            'cilt_kurulugu': ['cilt kuruluğu', 'kuru cilt', 'cilt pullanması', 'deri kuruluğu', 'kuru deri'],
            'kuru_cilt': ['kuru cilt', 'cilt kuruluğu', 'deri kuruluğu', 'kuru deri', 'cilt pullanması'],
            'sac_dokulmesi': ['saç dökülmesi', 'saç kaybı', 'kellik', 'saçlar dökülüyor', 'saç dökülmesi'],
            'sagliksiz_sac': ['sağlıksız saç', 'mat saç', 'kırılgan saç', 'saç kalitesi düşük', 'donuk saç'],
            'tirnak_kirilganligi': ['tırnak kırılganlığı', 'kırılgan tırnak', 'tırnak kırılması', 'tırnak zayıflığı'],
            'tirnak_bozuklugu': ['tırnak bozukluğu', 'tırnak hasarı', 'tırnak şekil bozukluğu', 'tırnak incelmesi', 'tırnak sorunları'],
            
            # Hepatit B semptomları
            'sari': ['sarılık', 'sarı', 'sarı renk', 'cilt sararması', 'göz sararması', 'sarılık'],
            'karin_agrisi': ['karın ağrısı', 'karın sancısı', 'mide ağrısı', 'karın bölgesi ağrısı'],
            'bulanti': ['bulantı', 'mide bulantısı', 'kusacak gibi', 'mide bulanması'],
            'kusma': ['kusma', 'kustum', 'kusuyorum', 'mide kusması'],
            'cilt_kasintisi': ['cilt kaşıntısı', 'kaşıntı', 'deri kaşıntısı', 'cilt kaşınıyor'],
            'koyu_idrar': ['koyu idrar', 'idrar rengi koyu', 'koyu renkli idrar'],
            'acik_renkli_disk': ['açık renkli dışkı', 'beyaz dışkı', 'açık renkli kaka'],
            'istahsizlik': ['iştahsızlık', 'iştah yok', 'yemek yemek istemiyorum'],
            'kilo_kaybi': ['kilo kaybı', 'zayıflama', 'kilo verme', 'kilo düşmesi'],
            
            # Gebelik semptomları
            'adet_gecikmesi': ['adet gecikmesi', 'regl gecikmesi', 'adet olmadım', 'gecikme'],
            'meme_hassasiyeti': ['meme hassasiyeti', 'göğüs ağrısı', 'meme ağrısı', 'göğüs hassasiyeti'],
            'sik_idrara_cikma': ['sık idrara çıkma', 'çok idrara çıkıyorum', 'sık sık tuvalet'],
            'tat_degisikligi': ['tat değişikliği', 'tat alma bozukluğu', 'tat alamıyorum'],
            'kokulara_hassasiyet': ['kokulara hassasiyet', 'koku hassasiyeti', 'kokular rahatsız ediyor'],
            'mide_yanmasi': ['mide yanması', 'mide ekşimesi', 'göğüs yanması'],
            
            # Tiroid semptomları
            'kilo_degisimi': ['kilo değişimi', 'kilo artışı', 'kilo kaybı', 'kilo alma'],
            'terleme': ['terleme', 'çok terliyorum', 'aşırı terleme'],
            'titreme': ['titreme', 'eller titriyor', 'vücut titremesi'],
            'kabizlik': ['kabızlık', 'dışkı yapamıyorum', 'tuvalet sorunu'],
            'ishal': ['ishal', 'sulu dışkı', 'diyare'],
            'cilt_solgunlugu': ['cilt solgunluğu', 'solgun cilt', 'pallor', 'renksiz cilt', 'solgun'],
            'cilt_morarmasi': ['cilt morarması', 'çürük', 'hematom', 'morluk', 'morarma'],
            
            # Ağız semptomları
            'dil_iltihabi': ['dil iltihabı', 'dil yanması', 'dil ağrısı', 'dil şişmesi', 'dil yanması'],
            'agiz_kosesi_catlaklari': ['ağız köşesi çatlakları', 'dudak çatlakları', 'ağız kenarı yarası', 'dudak çatlağı'],
            'dis_eti_kanamasi': ['diş eti kanaması', 'diş eti kanı', 'gingival kanama', 'diş eti kanaması'],
            'burun_kanamasi': ['burun kanaması', 'epistaksis', 'burun kanı', 'burun kanaması'],
            
            # Kanama semptomları
            'kanama_bozuklugu': ['kanama bozukluğu', 'kanama eğilimi', 'kolay kanama', 'pıhtılaşma sorunu'],
            'yavas_iyilesme': ['yavaş iyileşme', 'geç iyileşme', 'yara iyileşmesi gecikmesi', 'geç iyileşme'],
            
            # Enfeksiyon semptomları
            'enfeksiyon_yatkinligi': ['enfeksiyon yatkınlığı', 'sık enfeksiyon', 'bağışıklık düşüklüğü', 'hasta olma'],
            'ates': ['ateş', 'fever', 'yüksek ateş', 'sıcaklık', 'fever'],
            
            # Psikolojik semptomlar
            'depresyon': ['depresyon', 'mutsuzluk', 'üzüntü', 'moral bozukluğu', 'depresif', 'mutsuz'],
            'sinirlilik': ['sinirlilik', 'sinirli', 'gerginlik', 'huzursuzluk', 'gergin'],
            'dikkat_sorunu': ['dikkat sorunu', 'dikkatsizlik', 'konsantrasyon sorunu', 'odaklanma sorunu'],
            'odaklanma_sorunu': ['odaklanma sorunu', 'konsantrasyon sorunu', 'dikkat sorunu', 'dikkatsizlik'],
            'konsantrasyon_sorunu': ['konsantrasyon sorunu', 'odaklanma sorunu', 'dikkat sorunu', 'dikkatsizlik'],
            
            # Kas semptomları
            'mus_zayifligi': ['kas zayıflığı', 'güçsüzlük', 'kas güçsüzlüğü', 'miyopati', 'kas güçsüzlüğü'],
            'kas_krampi': ['kas krampi', 'kramp', 'kas spazmı', 'kasılma', 'kramp'],
            'kas_guclugu': ['kas güçsüzlüğü', 'kas zayıflığı', 'güçsüzlük', 'miyopati'],
            
            # Diğer semptomlar
            'buyume_geriligi': ['büyüme geriliği', 'gelişim geriliği', 'boy kısalığı', 'gelişim bozukluğu'],
            'sinir_hasari': ['sinir hasarı', 'nörolojik hasar', 'sinir bozukluğu', 'nörolojik bozukluk'],
            'dermatit': ['dermatit', 'cilt iltihabı', 'egzama', 'cilt döküntüsü', 'cilt hastalığı'],
            'anemi': ['anemi', 'kansızlık', 'demir eksikliği', 'hemoglobin düşüklüğü', 'kansız'],
            
            # Yeni eklenen semptomlar
            'tat_bozuklugu': ['tat bozukluğu', 'tat kaybı', 'tat alamama', 'tat bozukluğu'],
            'koku_bozuklugu': ['koku bozukluğu', 'koku kaybı', 'koku alamama', 'koku bozukluğu'],
            'yara_iyilesme_sorunu': ['yara iyileşme sorunu', 'geç iyileşme', 'yavaş iyileşme', 'iyileşme gecikmesi'],
            'uyku_bozuklugu': ['uyku bozukluğu', 'uyuyamama', 'uyku sorunu', 'insomnia'],
            'dis_bozuklugu': ['diş bozukluğu', 'diş sorunu', 'diş hastalığı', 'diş problemleri']
        }
        
        # Stopwords listesi
        self.stopwords = {
            'çok', 'fazla', 'çok fazla', 'biraz', 'az', 'hafif', 'orta', 'şiddetli', 'ağır',
            'kritik', 'net', 'belirgin', 'küçük', 'büyük', 'yeni', 'eski', 'günlük', 'haftalık',
            'aylık', 'yıllık', 'sürekli', 'bazen', 'nadiren', 'hiç', 'hiçbir', 'her', 'tüm',
            'bazı', 'bir', 'iki', 'üç', 'dört', 'beş', 'altı', 'yedi', 'sekiz', 'dokuz', 'on',
            've', 'veya', 'ile', 'için', 'gibi', 'kadar', 'daha', 'en', 'çok', 'az', 'biraz'
        }
    
    def normalize_text(self, text: str) -> str:
        """Metni normalize eder - Türkçe karakterleri düzeltir, küçük harfe çevirir"""
        # Türkçe karakterleri düzelt
        replacements = {
            'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c',
            'İ': 'i', 'Ğ': 'g', 'Ü': 'u', 'Ş': 's', 'Ö': 'o', 'Ç': 'c'
        }
        
        normalized = text.lower()
        for tr_char, en_char in replacements.items():
            normalized = normalized.replace(tr_char, en_char)
        
        # Fazla boşlukları temizle
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def remove_stopwords(self, text: str) -> str:
        """Stopwords'leri kaldırır"""
        words = text.split()
        filtered_words = [word for word in words if word not in self.stopwords]
        return ' '.join(filtered_words)
    
    def lemmatize_word(self, word: str) -> str:
        """Basit lemmatization - kelimeleri kök haline indirger"""
        # Türkçe için basit lemmatization kuralları
        lemmatization_rules = {
            # Çoğul ekleri
            'lar': '', 'ler': '', 'ları': '', 'leri': '',
            # İyelik ekleri
            'ım': '', 'im': '', 'ın': '', 'in': '', 'ı': '', 'i': '',
            'ımız': '', 'imiz': '', 'ınız': '', 'iniz': '', 'ları': '', 'leri': '',
            # Hal ekleri
            'da': '', 'de': '', 'ta': '', 'te': '',
            'dan': '', 'den': '', 'tan': '', 'ten': '',
            'ya': '', 'ye': '', 'a': '', 'e': '',
            'yı': '', 'yi': '', 'ı': '', 'i': '',
            # Fiil ekleri
            'yor': '', 'iyor': '', 'uyor': '', 'üyor': '',
            'dı': '', 'di': '', 'du': '', 'dü': '',
            'tı': '', 'ti': '', 'tu': '', 'tü': '',
            'mış': '', 'miş': '', 'muş': '', 'müş': '',
            'acak': '', 'ecek': '', 'ır': '', 'ir': '', 'ur': '', 'ür': '',
            # Sıfat ekleri
            'lı': '', 'li': '', 'lu': '', 'lü': '',
            'sız': '', 'siz': '', 'suz': '', 'süz': '',
            'lık': '', 'lik': '', 'luk': '', 'lük': '',
            'sı': '', 'si': '', 'su': '', 'sü': ''
        }
        
        # En uzun eki bul ve kaldır
        for suffix in sorted(lemmatization_rules.keys(), key=len, reverse=True):
            if word.endswith(suffix):
                return word[:-len(suffix)]
        
        return word
    
    def extract_symptoms_from_text(self, text: str) -> Dict[str, int]:
        """Metinden semptomları çıkarır ve şiddet seviyesini belirler - Gelişmiş NLP"""
        # Metni normalize et
        normalized_text = self.normalize_text(text)
        
        # Stopwords'leri kaldır
        cleaned_text = self.remove_stopwords(normalized_text)
        
        symptoms = {}
        
        for symptom, keywords in self.symptom_keywords.items():
            severity = 0
            
            for keyword in keywords:
                # Anahtar kelimeyi ara (tam eşleşme ve kısmi eşleşme)
                if keyword in cleaned_text:
                    # Şiddet belirten kelimeleri kontrol et
                    severity_indicators = {
                        'çok': 3, 'çok fazla': 3, 'şiddetli': 3, 'ağır': 3, 'kritik': 3,
                        'sürekli': 3, 'sürekli olarak': 3, 'her zaman': 3,
                        'fazla': 2, 'orta': 2, 'belirgin': 2, 'net': 2, 'açık': 2,
                        'biraz': 1, 'hafif': 1, 'az': 1, 'küçük': 1, 'nadiren': 1
                    }
                    
                    # Şiddet seviyesini belirle
                    max_severity = 1  # Varsayılan
                    for indicator, level in severity_indicators.items():
                        if indicator in cleaned_text:
                            max_severity = max(max_severity, level)
                    
                    # En yüksek şiddeti al
                    if max_severity > symptoms.get(symptom, 0):
                        symptoms[symptom] = max_severity
        
        return symptoms
    
    def normalize_symptom_name(self, symptom: str) -> str:
        """Semptom adını normalize eder"""
        # Türkçe karakterleri düzelt
        replacements = {
            'ı': 'i', 'ğ': 'g', 'ü': 'u', 'ş': 's', 'ö': 'o', 'ç': 'c'
        }
        
        normalized = symptom.lower()
        for tr_char, en_char in replacements.items():
            normalized = normalized.replace(tr_char, en_char)
        
        # Boşlukları alt çizgi ile değiştir
        normalized = re.sub(r'\s+', '_', normalized)
        
        return normalized
    
    def get_symptom_suggestions(self, partial_text: str) -> List[str]:
        """Kısmi metne göre semptom önerileri döndürür"""
        partial_text = partial_text.lower()
        suggestions = []
        
        for symptom, keywords in self.symptom_keywords.items():
            for keyword in keywords:
                if partial_text in keyword:
                    suggestions.append(symptom)
                    break
        
        return suggestions[:10]  # En fazla 10 öneri
    
    def validate_symptoms(self, symptoms: Dict[str, int]) -> Dict[str, str]:
        """Semptomları doğrular ve hata mesajları döndürür"""
        errors = {}
        
        for symptom, severity in symptoms.items():
            if not isinstance(severity, int):
                errors[symptom] = "Şiddet seviyesi sayı olmalı"
            elif severity < 0 or severity > 3:
                errors[symptom] = "Şiddet seviyesi 0-3 arasında olmalı"
        
        return errors