import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
import joblib
import os
import logging
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

class NutrientDeficiencyModel:
    def __init__(self, nutrient_name: str):
        self.nutrient_name = nutrient_name
        self.model = None
        self.symptoms = self.get_nutrient_symptoms(nutrient_name)
        
    def get_nutrient_symptoms(self, nutrient_name: str) -> List[str]:
        """Vitamin/mineral'e özgü semptomları döndürür"""
        nutrient_symptoms = {
            # MVP Vitaminler
            'D': [
                'kemik_agrisi', 'mus_zayifligi', 'yorgunluk', 'depresyon', 'bas_agrisi',
                'kas_agrisi', 'eklem_agrisi', 'enfeksiyon_yatkinligi', 'bas_donmesi',
                'halsizlik', 'enerji_dusuklugu', 'odaklanma_sorunu', 'sac_dokulmesi'
            ],
            'B12': [
                'anemi', 'yorgunluk', 'hafiza_sorunlari', 'nopati', 'uyusma',
                'karincalanma', 'depresyon', 'denge_sorunlari', 'sinirlilik',
                'unutkanlik', 'dikkat_sorunu', 'halsizlik', 'sac_dokulmesi', 'tirnak_bozuklugu'
            ],
            # MVP Mineraller
            'Demir': [
                'anemi', 'yorgunluk', 'halsizlik', 'bas_donmesi', 'cilt_solgunlugu',
                'nefes_darligi', 'kalp_carpintisi', 'bas_agrisi', 'enerji_dusuklugu',
                'odaklanma_sorunu', 'kas_guclugu', 'tirnak_kirilganligi', 'sac_dokulmesi', 'tirnak_bozuklugu'
            ],
            'Cinko': [
                'enfeksiyon_yatkinligi', 'yavas_iyilesme', 'tat_bozuklugu', 'koku_bozuklugu',
                'cilt_kurulugu', 'sac_dokulmesi', 'tirnak_kirilganligi', 'yorgunluk',
                'yara_iyilesme_sorunu', 'bas_agrisi', 'depresyon', 'tirnak_bozuklugu'
            ],
            'Magnezyum': [
                'kas_agrisi', 'kas_krampi', 'uyusma', 'karincalanma', 'yorgunluk',
                'bas_agrisi', 'depresyon', 'uyku_bozuklugu', 'kalp_carpintisi',
                'halsizlik', 'sinirlilik', 'konsantrasyon_sorunu'
            ],
            # Genişletilmiş Vitaminler
            'A': [
                'gece_korlugu', 'kuru_cilt', 'enfeksiyon_yatkinligi', 'goz_kurulugu',
                'sagliksiz_sac', 'tirnak_kirilganligi', 'buyume_geriligi', 'goz_yorgunlugu',
                'cilt_kurulugu', 'goz_yanmasi', 'isiga_duyarlilik'
            ],
            'C': [
                'yavas_iyilesme', 'dis_eti_kanamasi', 'cilt_kurulugu', 'yorgunluk',
                'kas_agrisi', 'eklem_agrisi', 'enfeksiyon_yatkinligi', 'sagliksiz_sac',
                'halsizlik', 'bas_agrisi', 'depresyon'
            ],
            'E': [
                'sinir_hasari', 'mus_zayifligi', 'yorgunluk', 'gorme_sorunlari',
                'denge_sorunlari', 'uyusma', 'karincalanma', 'cilt_kurulugu',
                'halsizlik', 'kas_agrisi', 'koordinasyon_bozuklugu'
            ],
            'B9': [
                'anemi', 'yorgunluk', 'hafiza_sorunlari', 'depresyon', 'bas_agrisi',
                'nefes_darligi', 'kalp_ritim_bozuklugu', 'cilt_solgunlugu',
                'halsizlik', 'dikkat_sorunu', 'sinirlilik'
            ],
            # Genişletilmiş Mineraller
            'Kalsiyum': [
                'kemik_agrisi', 'kas_krampi', 'uyusma', 'karincalanma', 'tirnak_kirilganligi',
                'dis_bozuklugu', 'kas_agrisi', 'yorgunluk', 'halsizlik', 'bas_agrisi'
            ],
            'Potasyum': [
                'kas_guclugu', 'kas_krampi', 'kalp_ritim_bozuklugu', 'yorgunluk',
                'halsizlik', 'uyusma', 'karincalanma', 'bas_donmesi', 'mide_bulantisi'
            ],
            'Selenyum': [
                'yorgunluk', 'halsizlik', 'kas_guclugu', 'tirnak_kirilganligi',
                'sac_dokulmesi', 'cilt_kurulugu', 'bas_agrisi', 'depresyon',
                'enfeksiyon_yatkinligi', 'dikkat_sorunu'
            ],
            # Yeni Teşhis Modülleri
            'HepatitB': [
                'sari', 'sari', 'sari', 'yorgunluk', 'halsizlik', 'karin_agrisi', 'bulanti',
                'kusma', 'ates', 'kas_agrisi', 'eklem_agrisi', 'cilt_kasintisi',
                'koyu_idrar', 'acik_renkli_disk', 'istahsizlik', 'kilo_kaybi'
            ],
            'Gebelik': [
                'adet_gecikmesi', 'adet_gecikmesi', 'bulanti', 'kusma', 'meme_hassasiyeti', 'yorgunluk',
                'sik_idrara_cikma', 'karin_agrisi', 'bas_donmesi', 'halsizlik',
                'tat_degisikligi', 'kokulara_hassasiyet', 'mide_yanmasi'
            ],
            'Tiroid': [
                'yorgunluk', 'halsizlik', 'kilo_degisimi', 'kilo_degisimi', 'sac_dokulmesi', 'kalp_carpintisi',
                'terleme', 'titreme', 'uyku_bozuklugu', 'depresyon', 'sinirlilik',
                'kas_agrisi', 'eklem_agrisi', 'cilt_kurulugu', 'kabizlik', 'ishal'
            ]
        }
        return nutrient_symptoms.get(nutrient_name, [])
    
    def create_training_data(self, n_samples: int = 2000) -> pd.DataFrame:
        """Gerçekçi sentetik eğitim verisi oluşturur - tıbbi literatüre dayalı"""
        np.random.seed(42)
        
        # Semptom verileri oluştur
        data = {}
        
        # Gerçekçi eksiklik prevalansı (tıbbi literatüre göre)
        deficiency_prevalence = {
            'D': 0.35,      # D vitamini eksikliği yaygın
            'B12': 0.15,    # B12 eksikliği orta
            'Demir': 0.25,  # Demir eksikliği yaygın
            'Cinko': 0.20,  # Çinko eksikliği orta
            'Magnezyum': 0.30,  # Magnezyum eksikliği yaygın
            'A': 0.10,      # A vitamini eksikliği nadir
            'C': 0.05,      # C vitamini eksikliği nadir
            'E': 0.08,      # E vitamini eksikliği nadir
            'B9': 0.12,     # Folat eksikliği orta
            'Kalsiyum': 0.18,  # Kalsiyum eksikliği orta
            'Potasyum': 0.15,  # Potasyum eksikliği orta
            'Selenyum': 0.10,  # Selenyum eksikliği nadir
            'HepatitB': 0.05,  # Hepatit B nadir
            'Gebelik': 0.08,   # Gebelik durumu
            'Tiroid': 0.12     # Tiroid bozukluğu orta
        }
        
        prevalence = deficiency_prevalence.get(self.nutrient_name, 0.15)
        
        # Her semptom için gerçekçi dağılım
        for symptom in self.symptoms:
            # Eksiklik olan durumlarda semptomlar daha şiddetli görülür
            deficiency_symptoms = np.random.choice([0, 1, 2, 3], n_samples, p=[0.05, 0.15, 0.35, 0.45])
            normal_symptoms = np.random.choice([0, 1, 2, 3], n_samples, p=[0.75, 0.20, 0.04, 0.01])
            
            # Eksiklik durumunu belirle
            deficiency_mask = np.random.random(n_samples) < prevalence
            
            data[symptom] = np.where(deficiency_mask, deficiency_symptoms, normal_symptoms)
        
        # Diğer semptomları da ekle (eksiklik olmayan durumlarda)
        other_symptoms = [
            'ates', 'bulanti', 'kusma', 'ishal', 'kabizlik', 'karin_agrisi',
            'gogus_agrisi', 'nefes_darligi', 'kalp_ritim_bozuklugu', 'bas_donmesi',
            'mide_bulantisi', 'konsantrasyon_sorunu', 'dikkat_sorunu', 'enerji_dusuklugu'
        ]
        
        for symptom in other_symptoms:
            if symptom not in data:
                # Genel popülasyonda semptom prevalansı
                data[symptom] = np.random.choice([0, 1, 2, 3], n_samples, p=[0.80, 0.15, 0.04, 0.01])
        
        # Gerçekçi eksiklik etiketi oluştur
        deficiency_labels = np.random.choice([0, 1], n_samples, p=[1-prevalence, prevalence])
        
        df = pd.DataFrame(data)
        df['deficiency'] = deficiency_labels
        
        return df
    
    def train_model(self):
        """Modeli eğitir - Gelişmiş validasyon ve performans metrikleri ile"""
        print(f"🔄 {self.nutrient_name} için model eğitiliyor...")
        
        # Eğitim verisi oluştur
        df = self.create_training_data()
        
        # Özellikler ve hedef değişken
        X = df.drop('deficiency', axis=1)
        y = df['deficiency']
        
        # Eğitim ve test setlerine ayır (70/15/15)
        X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)
        
        # Model oluştur ve eğit (RandomForest - optimize edilmiş parametreler)
        self.model = RandomForestClassifier(
            n_estimators=300, 
            max_depth=12,
            min_samples_split=3,
            min_samples_leaf=1,
            max_features='sqrt',
            class_weight='balanced',  # Sınıf dengesizliği için
            random_state=42,
            n_jobs=-1
        )
        
        # Cross-validation ile model performansını değerlendir
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42), scoring='roc_auc')
        
        # Modeli eğit
        self.model.fit(X_train, y_train)
        
        # Test performansı
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Performans metrikleri
        accuracy = accuracy_score(y_test, y_pred)
        auc_score = roc_auc_score(y_test, y_pred_proba)
        conf_matrix = confusion_matrix(y_test, y_pred)
        
        # Classification report
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        # Performans bilgilerini sakla
        self.model_performance = {
            'accuracy': accuracy,
            'auc_score': auc_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'confusion_matrix': conf_matrix.tolist(),
            'classification_report': class_report
        }
        
        print(f"✅ {self.nutrient_name} modeli eğitildi.")
        print(f"   - Doğruluk: {accuracy:.3f}")
        print(f"   - AUC: {auc_score:.3f}")
        print(f"   - CV Ortalama: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
        
        return accuracy
    
    def predict(self, symptoms_dict: Dict[str, int]) -> Dict[str, Any]:
        """Semptomlara göre eksiklik tahmini yapar"""
        if self.model is None:
            self.load_model()
        
        # Modelin beklediği feature sayısını al
        expected_features = self.model.n_features_in_
        
        # Tüm olası semptomları topla
        all_possible_symptoms = set(self.symptoms)
        other_symptoms = [
            'ates', 'bulanti', 'kusma', 'ishal', 'kabizlik', 'karin_agrisi',
            'gogus_agrisi', 'nefes_darligi', 'kalp_ritim_bozuklugu', 'bas_donmesi',
            'mide_bulantisi', 'konsantrasyon_sorunu', 'dikkat_sorunu', 'enerji_dusuklugu',
            'sac_dokulmesi', 'tirnak_bozuklugu', 'tirnak_kirilganligi', 'cilt_solgunlugu',
            'anemi', 'hafiza_sorunlari', 'nopati', 'uyusma', 'karincalanma', 'depresyon',
            'denge_sorunlari', 'sinirlilik', 'unutkanlik', 'dikkat_sorunu', 'halsizlik',
            'nefes_darligi', 'kalp_carpintisi', 'bas_agrisi', 'odaklanma_sorunu', 'kas_guclugu',
            'enfeksiyon_yatkinligi', 'yavas_iyilesme', 'tat_bozuklugu', 'koku_bozuklugu',
            'cilt_kurulugu', 'yara_iyilesme_sorunu', 'kas_agrisi', 'kas_krampi', 'uyku_bozuklugu',
            'kalp_carpintisi', 'sinirlilik', 'konsantrasyon_sorunu', 'gece_korlugu', 'kuru_cilt',
            'goz_kurulugu', 'sagliksiz_sac', 'buyume_geriligi', 'goz_yorgunlugu', 'cilt_kurulugu',
            'goz_yanmasi', 'isiga_duyarlilik', 'dis_eti_kanamasi', 'eklem_agrisi', 'sagliksiz_sac',
            'sinir_hasari', 'mus_zayifligi', 'gorme_sorunlari', 'denge_sorunlari', 'uyusma',
            'karincalanma', 'koordinasyon_bozuklugu', 'hafiza_sorunlari', 'kalp_ritim_bozuklugu',
            'kemik_agrisi', 'dis_bozuklugu', 'kas_agrisi', 'mide_bulantisi', 'tiroid_sorunlari'
        ]
        
        all_possible_symptoms.update(other_symptoms)
        
        # Feature vector oluştur - modelin beklediği sırayla
        feature_vector = []
        for symptom in sorted(all_possible_symptoms):
            if len(feature_vector) >= expected_features:
                break
            value = symptoms_dict.get(symptom, 0)
            feature_vector.append(value)
        
        # Eksik feature'ları 0 ile doldur
        while len(feature_vector) < expected_features:
            feature_vector.append(0)
        
        # Sadece gerekli feature'ları al
        feature_vector = feature_vector[:expected_features]
        
        # Tahmin yap
        X = np.array(feature_vector).reshape(1, -1)
        probability = self.model.predict_proba(X)[0]
        prediction = self.model.predict(X)[0]
        
        # Risk seviyesi belirle (tıbbi literatüre dayalı eşikler)
        risk_level = "Düşük"
        if probability[1] > 0.75:  # Yüksek güvenilirlik için %75+
            risk_level = "Yüksek"
        elif probability[1] > 0.50:  # Orta güvenilirlik için %50+
            risk_level = "Orta"
        elif probability[1] > 0.30:  # Düşük risk için %30+
            risk_level = "Düşük Risk"
        
        return {
            'nutrient': self.nutrient_name,
            'deficiency_probability': float(probability[1]),
            'prediction': int(prediction),
            'risk_level': risk_level,
            'confidence': float(max(probability))
        }
    
    def get_recommendations(self, prediction_result: Dict[str, Any]) -> Dict[str, List[str]]:
        """Nutrient'e özgü öneriler döndürür"""
        nutrient = prediction_result['nutrient']
        risk_level = prediction_result['risk_level']
        
        recommendations = {
            'immediate_actions': [],
            'dietary_recommendations': [],
            'supplement_recommendations': [],
            'tests_recommended': []
        }
        
        if risk_level in ["Orta", "Yüksek"]:
            # Nutrient'e özgü öneriler
            if nutrient == 'D':
                recommendations['dietary_recommendations'] = [
                    "Güneş ışığından yararlanın (15-30 dakika/gün)",
                    "Yağlı balık, yumurta sarısı, mantar tüketin",
                    "D vitamini ile zenginleştirilmiş süt ve tahıllar"
                ]
                recommendations['supplement_recommendations'] = [
                    "D3 vitamini takviyesi (günlük 1000-2000 IU)",
                    "Kalsiyum ile birlikte alın"
                ]
                recommendations['tests_recommended'] = [
                    "25(OH)D seviyesi",
                    "Kalsiyum seviyesi",
                    "Paratiroid hormon seviyesi"
                ]
                
            elif nutrient == 'B12':
                recommendations['dietary_recommendations'] = [
                    "Et, balık, süt, yumurta tüketin",
                    "Vejetaryenler için B12 takviyeli besinler",
                    "Karaciğer ve böbrek gibi organ etleri"
                ]
                recommendations['supplement_recommendations'] = [
                    "B12 takviyesi (günlük 2.4 mcg)",
                    "Şiddetli eksiklikte enjeksiyon gerekebilir"
                ]
                recommendations['tests_recommended'] = [
                    "Serum B12 seviyesi",
                    "Methylmalonic asit seviyesi",
                    "Tam kan sayımı"
                ]
                
            elif nutrient == 'Demir':
                recommendations['dietary_recommendations'] = [
                    "Kırmızı et, karaciğer, ıspanak tüketin",
                    "C vitamini ile birlikte alın (emilimi artırır)",
                    "Çay ve kahve yemeklerden 2 saat sonra için"
                ]
                recommendations['supplement_recommendations'] = [
                    "Demir takviyesi (günlük 18 mg)",
                    "Aç karnına alın, C vitamini ile birlikte"
                ]
                recommendations['tests_recommended'] = [
                    "Serum ferritin seviyesi",
                    "Tam kan sayımı",
                    "Transferrin saturasyonu"
                ]
                
            elif nutrient == 'Cinko':
                recommendations['dietary_recommendations'] = [
                    "Et, kabuklu deniz ürünleri, fındık tüketin",
                    "Tam tahıllar ve baklagiller",
                    "Cinko emilimini engelleyen fitatları azaltın"
                ]
                recommendations['supplement_recommendations'] = [
                    "Çinko takviyesi (günlük 8-11 mg)",
                    "Yemeklerle birlikte alın"
                ]
                recommendations['tests_recommended'] = [
                    "Serum çinko seviyesi",
                    "Tam kan sayımı"
                ]
                
            elif nutrient == 'Magnezyum':
                recommendations['dietary_recommendations'] = [
                    "Yeşil yapraklı sebzeler, fındık, tohumlar tüketin",
                    "Tam tahıllar ve baklagiller",
                    "Bitter çikolata (kakao oranı yüksek)"
                ]
                recommendations['supplement_recommendations'] = [
                    "Magnezyum takviyesi (günlük 300-400 mg)",
                    "Yemeklerle birlikte alın"
                ]
                recommendations['tests_recommended'] = [
                    "Serum magnezyum seviyesi",
                    "Eritrosit magnezyum seviyesi"
                ]
                
            elif nutrient == 'HepatitB':
                recommendations['dietary_recommendations'] = [
                    "Bol su için, dinlenin",
                    "Alkol ve yağlı yiyeceklerden kaçının",
                    "Hafif, besleyici yemekler tüketin"
                ]
                recommendations['supplement_recommendations'] = [
                    "Doktor kontrolünde hepatit B aşısı",
                    "Antiviral tedavi gerekebilir"
                ]
                recommendations['tests_recommended'] = [
                    "HBsAg testi",
                    "Anti-HBc testi",
                    "Karaciğer fonksiyon testleri",
                    "Viral yük testi"
                ]
                
            elif nutrient == 'Gebelik':
                recommendations['dietary_recommendations'] = [
                    "Folik asit takviyesi alın",
                    "Demir ve kalsiyum açısından zengin beslenin",
                    "Küçük ve sık öğünler tüketin"
                ]
                recommendations['supplement_recommendations'] = [
                    "Gebelik multivitamini",
                    "Folik asit (400-800 mcg)",
                    "Demir takviyesi (doktor önerisiyle)"
                ]
                recommendations['tests_recommended'] = [
                    "Gebelik testi (idrar/kan)",
                    "Beta-hCG seviyesi",
                    "Ultrasonografi",
                    "Tam kan sayımı"
                ]
                
            elif nutrient == 'Tiroid':
                recommendations['dietary_recommendations'] = [
                    "İyotlu tuz kullanın",
                    "Selenyum açısından zengin besinler tüketin",
                    "Düzenli egzersiz yapın"
                ]
                recommendations['supplement_recommendations'] = [
                    "Tiroid hormonu (doktor reçetesiyle)",
                    "Selenyum takviyesi",
                    "İyot takviyesi (doktor önerisiyle)"
                ]
                recommendations['tests_recommended'] = [
                    "TSH seviyesi",
                    "T3 ve T4 seviyeleri",
                    "Anti-TPO antikorları",
                    "Tiroid ultrasonografisi"
                ]
            
            # Genel öneriler
            recommendations['immediate_actions'] = [
                "Doktor kontrolüne gidin",
                "Beslenme alışkanlıklarınızı gözden geçirin",
                "Stres yönetimi uygulayın"
            ]
        
        return recommendations
    
    def save_model(self, filepath: str = None):
        """Modeli kaydeder"""
        if filepath is None:
            filepath = f"models/{self.nutrient_name}_model.pkl"
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.model, filepath)
        print(f"✅ {self.nutrient_name} modeli kaydedildi: {filepath}")
    
    def load_model(self, filepath: str = None):
        """Modeli yükler veya eğitir"""
        if filepath is None:
            filepath = f"models/{self.nutrient_name}_model.pkl"
        
        if os.path.exists(filepath):
            self.model = joblib.load(filepath)
            print(f"✅ {self.nutrient_name} modeli yüklendi: {filepath}")
        else:
            print(f"⚠️ {self.nutrient_name} modeli bulunamadı, eğitiliyor...")
            self.train_model()
            self.save_model(filepath)