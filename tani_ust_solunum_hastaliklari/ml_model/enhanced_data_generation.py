import pandas as pd
import random
import numpy as np
from sklearn.utils import resample
import warnings
warnings.filterwarnings('ignore')

class EnhancedDiseaseDataGenerator:
    def __init__(self):
        # Gelişmiş semptom tanımları - daha detaylı ve gerçekçi
        self.symptoms = [
            "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
            "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
            "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları",
            "Göğüs Ağrısı", "Titreme", "Gece Terlemesi", "İştahsızlık", "Konsantrasyon Güçlüğü"
        ]
        
        # Hastalık bazlı semptom profilleri - tıbbi literatüre dayalı
        self.disease_profiles = {
            "COVID-19": {
                "core_symptoms": {
                    "Ateş": 0.85, "Koku veya Tat Kaybı": 0.70, "Nefes Darlığı": 0.60,
                    "Öksürük": 0.75, "Bitkinlik": 0.80, "Baş Ağrısı": 0.60
                },
                "common_symptoms": {
                    "Vücut Ağrıları": 0.65, "Boğaz Ağrısı": 0.50, "Bulantı veya Kusma": 0.30,
                    "İshal": 0.25, "Göğüs Ağrısı": 0.40
                },
                "rare_symptoms": {
                    "Burun Akıntısı veya Tıkanıklığı": 0.20, "Hapşırma": 0.15,
                    "Göz Kaşıntısı veya Sulanma": 0.10
                },
                "duration_pattern": "acute",
                "severity_variation": 0.3
            },
            
            "Grip": {
                "core_symptoms": {
                    "Ateş": 0.90, "Vücut Ağrıları": 0.85, "Bitkinlik": 0.80,
                    "Baş Ağrısı": 0.75, "Öksürük": 0.70, "Titreme": 0.60
                },
                "common_symptoms": {
                    "Boğaz Ağrısı": 0.60, "Bulantı veya Kusma": 0.40,
                    "Burun Akıntısı veya Tıkanıklığı": 0.50
                },
                "rare_symptoms": {
                    "Koku veya Tat Kaybı": 0.05, "Nefes Darlığı": 0.10,
                    "Göz Kaşıntısı veya Sulanma": 0.05, "İshal": 0.15
                },
                "duration_pattern": "acute",
                "severity_variation": 0.25
            },
            
            "Soğuk Algınlığı": {
                "core_symptoms": {
                    "Burun Akıntısı veya Tıkanıklığı": 0.90, "Boğaz Ağrısı": 0.70,
                    "Öksürük": 0.65, "Hapşırma": 0.60
                },
                "common_symptoms": {
                    "Baş Ağrısı": 0.40, "Bitkinlik": 0.50, "Göz Kaşıntısı veya Sulanma": 0.30
                },
                "rare_symptoms": {
                    "Ateş": 0.10, "Vücut Ağrıları": 0.20, "Bulantı veya Kusma": 0.15,
                    "Koku veya Tat Kaybı": 0.02, "Nefes Darlığı": 0.05, "İshal": 0.10
                },
                "duration_pattern": "mild_chronic",
                "severity_variation": 0.2
            },
            
            "Mevsimsel Alerji": {
                "core_symptoms": {
                    "Göz Kaşıntısı veya Sulanma": 0.85, "Hapşırma": 0.80,
                    "Burun Akıntısı veya Tıkanıklığı": 0.75, "Boğaz Ağrısı": 0.45
                },
                "common_symptoms": {
                    "Bitkinlik": 0.40, "Baş Ağrısı": 0.35, "Öksürük": 0.30
                },
                "rare_symptoms": {
                    "Ateş": 0.01, "Vücut Ağrıları": 0.05, "Bulantı veya Kusma": 0.02,
                    "Koku veya Tat Kaybı": 0.03, "Nefes Darlığı": 0.15, "İshal": 0.01
                },
                "duration_pattern": "chronic",
                "severity_variation": 0.15
            }
        }
        
        # Semptom kombinasyonları - hastalıkların ayırıcı tanısı için
        self.diagnostic_patterns = {
            "COVID-19": {
                "key_combinations": [
                    ("Koku veya Tat Kaybı", "Nefes Darlığı"),
                    ("Ateş", "Koku veya Tat Kaybı"),
                    ("Nefes Darlığı", "Göğüs Ağrısı")
                ],
                "exclusion_patterns": [
                    ("Göz Kaşıntısı veya Sulanma", "Hapşırma")
                ]
            },
            "Grip": {
                "key_combinations": [
                    ("Ateş", "Vücut Ağrıları", "Titreme"),
                    ("Yüksek Ateş", "Şiddetli Bitkinlik")
                ],
                "exclusion_patterns": [
                    ("Göz Kaşıntısı veya Sulanma", "Koku veya Tat Kaybı")
                ]
            },
            "Soğuk Algınlığı": {
                "key_combinations": [
                    ("Burun Akıntısı veya Tıkanıklığı", "Hapşırma"),
                    ("Boğaz Ağrısı", "Hafif Öksürük")
                ],
                "exclusion_patterns": [
                    ("Yüksek Ateş", "Nefes Darlığı")
                ]
            },
            "Mevsimsel Alerji": {
                "key_combinations": [
                    ("Göz Kaşıntısı veya Sulanma", "Hapşırma", "Burun Akıntısı veya Tıkanıklığı"),
                    ("Mevsimsel Pattern", "Göz Belirtileri")
                ],
                "exclusion_patterns": [
                    ("Ateş", "Vücut Ağrıları")
                ]
            }
        }

    def generate_realistic_symptom_vector(self, disease_name, sample_id):
        """Gerçekçi semptom vektörü üretir"""
        profile = self.disease_profiles[disease_name]
        vector = {}
        
        # Core semptomları yüksek olasılıkla ekle
        for symptom, base_prob in profile["core_symptoms"].items():
            if random.random() < base_prob:
                vector[symptom] = self._get_severity_score("high", profile["severity_variation"])
            else:
                vector[symptom] = 0.0
        
        # Common semptomları orta olasılıkla ekle
        for symptom, base_prob in profile["common_symptoms"].items():
            if random.random() < base_prob:
                vector[symptom] = self._get_severity_score("medium", profile["severity_variation"])
            else:
                vector[symptom] = 0.0
        
        # Rare semptomları düşük olasılıkla ekle
        for symptom, base_prob in profile["rare_symptoms"].items():
            if random.random() < base_prob:
                vector[symptom] = self._get_severity_score("low", profile["severity_variation"])
            else:
                vector[symptom] = 0.0
        
        # Tanısal kombinasyonları güçlendir
        self._apply_diagnostic_patterns(vector, disease_name)
        
        # Diğer semptomları 0 yap
        for symptom in self.symptoms:
            if symptom not in vector:
                vector[symptom] = 0.0
        
        return [vector.get(symptom, 0.0) for symptom in self.symptoms]

    def _get_severity_score(self, level, variation):
        """Şiddet seviyesine göre skor üretir"""
        base_scores = {
            "high": (0.7, 1.0),
            "medium": (0.4, 0.7),
            "low": (0.1, 0.4)
        }
        
        min_score, max_score = base_scores[level]
        noise = random.uniform(-variation, variation)
        score = random.uniform(min_score, max_score) + noise
        
        return max(0.0, min(1.0, round(score, 2)))

    def _apply_diagnostic_patterns(self, vector, disease_name):
        """Tanısal kombinasyonları uygular"""
        patterns = self.diagnostic_patterns[disease_name]
        
        # Key combinations - bu kombinasyonlar varsa güçlendir
        for combination in patterns["key_combinations"]:
            if len(combination) == 2:
                s1, s2 = combination
                if vector.get(s1, 0) > 0 and vector.get(s2, 0) > 0:
                    vector[s1] = min(1.0, vector[s1] + 0.2)
                    vector[s2] = min(1.0, vector[s2] + 0.2)
        
        # Exclusion patterns - bu kombinasyonlar varsa zayıflat
        for combination in patterns["exclusion_patterns"]:
            if len(combination) == 2:
                s1, s2 = combination
                if vector.get(s1, 0) > 0 and vector.get(s2, 0) > 0:
                    vector[s1] = max(0.0, vector[s1] - 0.3)
                    vector[s2] = max(0.0, vector[s2] - 0.3)

    def generate_enhanced_dataset(self, samples_per_disease=1500):
        """Gelişmiş veri seti üretir"""
        all_samples = []
        all_labels = []
        
        print("🚀 Gelişmiş veri seti üretimi başlıyor...")
        
        for disease_name in self.disease_profiles.keys():
            print(f"📊 {disease_name} için {samples_per_disease} örnek üretiliyor...")
            
            disease_samples = []
            for i in range(samples_per_disease):
                sample = self.generate_realistic_symptom_vector(disease_name, i)
                disease_samples.append(sample)
            
            # Veri çeşitliliği için SMOTE benzeri augmentasyon
            augmented_samples = self._augment_disease_data(disease_samples, disease_name)
            
            all_samples.extend(augmented_samples)
            all_labels.extend([disease_name] * len(augmented_samples))
        
        # Veri setini oluştur
        df = pd.DataFrame(all_samples, columns=self.symptoms)
        df["Etiket"] = all_labels
        
        # Sınıf dengesizliğini düzelt
        df_balanced = self._balance_dataset(df)
        
        print(f"✅ Toplam {len(df_balanced)} örnek üretildi")
        print(f"📈 Sınıf dağılımı:")
        print(df_balanced["Etiket"].value_counts())
        
        return df_balanced

    def _augment_disease_data(self, samples, disease_name):
        """Hastalık verilerini çeşitlendirir"""
        augmented = samples.copy()
        
        # Her hastalık için özel augmentasyon
        if disease_name == "COVID-19":
            # COVID-19 için varyasyonlar
            for _ in range(len(samples) // 4):
                base_sample = random.choice(samples)
                variant = base_sample.copy()
                
                # Koku kaybı olmadan COVID varyantları
                if random.random() < 0.3:
                    variant[self.symptoms.index("Koku veya Tat Kaybı")] = 0.0
                
                augmented.append(variant)
        
        elif disease_name == "Grip":
            # Grip için şiddet varyasyonları
            for _ in range(len(samples) // 3):
                base_sample = random.choice(samples)
                variant = base_sample.copy()
                
                # Hafif grip vakaları
                if random.random() < 0.4:
                    for i in range(len(variant)):
                        if variant[i] > 0.5:
                            variant[i] = max(0.2, variant[i] - 0.3)
                
                augmented.append(variant)
        
        return augmented

    def _balance_dataset(self, df):
        """Veri setini dengeler"""
        # Her sınıf için aynı sayıda örnek
        min_samples = df["Etiket"].value_counts().min()
        
        balanced_samples = []
        for disease in df["Etiket"].unique():
            disease_data = df[df["Etiket"] == disease]
            if len(disease_data) > min_samples:
                sampled = resample(disease_data, n_samples=min_samples, random_state=42)
            else:
                sampled = disease_data
            balanced_samples.append(sampled)
        
        return pd.concat(balanced_samples, ignore_index=True)

    def save_enhanced_dataset(self, df, filename="enhanced_hastalik_veriseti.csv"):
        """Gelişmiş veri setini kaydeder"""
        df.to_csv(filename, index=False)
        print(f"💾 Veri seti kaydedildi: {filename}")
        return filename

# Kullanım
if __name__ == "__main__":
    generator = EnhancedDiseaseDataGenerator()
    
    # Gelişmiş veri seti üret
    enhanced_df = generator.generate_enhanced_dataset(samples_per_disease=1500)
    
    # Kaydet
    output_file = generator.save_enhanced_dataset(enhanced_df)
    
    print("\n🎯 Veri seti özellikleri:")
    print(f"- Toplam örnek sayısı: {len(enhanced_df)}")
    print(f"- Özellik sayısı: {len(enhanced_df.columns) - 1}")
    print(f"- Sınıf sayısı: {enhanced_df['Etiket'].nunique()}")
    
    # Her sınıf için istatistikler
    print("\n📊 Sınıf bazlı istatistikler:")
    for disease in enhanced_df["Etiket"].unique():
        subset = enhanced_df[enhanced_df["Etiket"] == disease]
        print(f"\n{disease}:")
        print(f"  - Örnek sayısı: {len(subset)}")
        
        # Ortalama semptom şiddetleri
        symptom_means = subset.iloc[:, :-1].mean()
        top_symptoms = symptom_means.nlargest(5)
        print(f"  - En yaygın semptomlar:")
        for symptom, mean_val in top_symptoms.items():
            if mean_val > 0.1:
                print(f"    {symptom}: {mean_val:.2f}")
