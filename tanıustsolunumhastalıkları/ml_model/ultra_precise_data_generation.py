#!/usr/bin/env python3
"""
Ultra Hassas Veri Üretimi - 4 Hastalığı Mükemmel Ayırt Etmek İçin
Bu script hastalıklar arasındaki farkları maksimize eder.
"""

import pandas as pd
import numpy as np
import random
from sklearn.utils import resample
import warnings
warnings.filterwarnings('ignore')

class UltraPreciseDiseaseDataGenerator:
    def __init__(self):
        # Ultra hassas semptom tanımları - hastalıklar arası farkları maksimize eder
        self.symptoms = [
            "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
            "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
            "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları",
            "Göğüs Ağrısı", "Titreme", "Gece Terlemesi", "İştahsızlık", "Konsantrasyon Güçlüğü"
        ]
        
        # Ultra hassas hastalık profilleri - ayırıcı tanı odaklı
        self.disease_profiles = {
            "COVID-19": {
                # COVID-19'a özgü ayırıcı semptomlar
                "unique_signatures": {
                    "Koku veya Tat Kaybı": 0.85,  # COVID-19'un en ayırıcı semptomu
                    "Nefes Darlığı": 0.80,        # Ciddi COVID-19 işareti
                    "Göğüs Ağrısı": 0.45          # COVID-19 komplikasyonu
                },
                "core_symptoms": {
                    "Ateş": 0.75, "Öksürük": 0.70, "Bitkinlik": 0.65
                },
                "rare_symptoms": {
                    "Vücut Ağrıları": 0.30, "Baş Ağrısı": 0.40,
                    "Burun Akıntısı veya Tıkanıklığı": 0.15,
                    "Göz Kaşıntısı veya Sulanma": 0.05, "Hapşırma": 0.05
                },
                "exclusion_patterns": [
                    ("Göz Kaşıntısı veya Sulanma", "Hapşırma"),  # Alerji semptomları
                    ("Burun Akıntısı veya Tıkanıklığı", "Hapşırma")  # Soğuk algınlığı
                ]
            },
            
            "Grip": {
                # Grip'e özgü ayırıcı semptomlar
                "unique_signatures": {
                    "Vücut Ağrıları": 0.90,       # Grip'in en ayırıcı semptomu
                    "Titreme": 0.75,              # Grip'e özgü
                    "Yüksek Ateş": 0.85           # Grip'te genelde yüksek
                },
                "core_symptoms": {
                    "Ateş": 0.85, "Bitkinlik": 0.80, "Baş Ağrısı": 0.70,
                    "Öksürük": 0.60, "Boğaz Ağrısı": 0.50
                },
                "rare_symptoms": {
                    "Koku veya Tat Kaybı": 0.05, "Nefes Darlığı": 0.10,
                    "Göz Kaşıntısı veya Sulanma": 0.02, "Hapşırma": 0.15,
                    "Burun Akıntısı veya Tıkanıklığı": 0.25
                },
                "exclusion_patterns": [
                    ("Koku veya Tat Kaybı", "Nefes Darlığı"),  # COVID-19 semptomları
                    ("Göz Kaşıntısı veya Sulanma", "Hapşırma")  # Alerji semptomları
                ]
            },
            
            "Soğuk Algınlığı": {
                # Soğuk algınlığına özgü ayırıcı semptomlar
                "unique_signatures": {
                    "Burun Akıntısı veya Tıkanıklığı": 0.95,  # En ayırıcı semptom
                    "Hapşırma": 0.80,                         # Soğuk algınlığı işareti
                    "Düşük Ateş": 0.30                        # Hafif ateş
                },
                "core_symptoms": {
                    "Boğaz Ağrısı": 0.70, "Öksürük": 0.65, "Baş Ağrısı": 0.40,
                    "Bitkinlik": 0.35
                },
                "rare_symptoms": {
                    "Ateş": 0.20, "Vücut Ağrıları": 0.15, "Koku veya Tat Kaybı": 0.02,
                    "Nefes Darlığı": 0.05, "Göz Kaşıntısı veya Sulanma": 0.10,
                    "Titreme": 0.05
                },
                "exclusion_patterns": [
                    ("Koku veya Tat Kaybı", "Nefes Darlığı"),  # COVID-19
                    ("Vücut Ağrıları", "Titreme"),            # Grip
                    ("Göz Kaşıntısı veya Sulanma", "Hapşırma")  # Alerji (hafif)
                ]
            },
            
            "Mevsimsel Alerji": {
                # Alerjiye özgü ayırıcı semptomlar
                "unique_signatures": {
                    "Göz Kaşıntısı veya Sulanma": 0.90,  # En ayırıcı semptom
                    "Hapşırma": 0.85,                    # Alerji işareti
                    "Ateş Yok": 0.95                     # Alerjide ateş olmaz
                },
                "core_symptoms": {
                    "Burun Akıntısı veya Tıkanıklığı": 0.75, "Boğaz Ağrısı": 0.40,
                    "Öksürük": 0.30, "Baş Ağrısı": 0.35
                },
                "rare_symptoms": {
                    "Ateş": 0.01, "Vücut Ağrıları": 0.05, "Koku veya Tat Kaybı": 0.03,
                    "Nefes Darlığı": 0.15, "Titreme": 0.02, "Bitkinlik": 0.25
                },
                "exclusion_patterns": [
                    ("Ateş", "Vücut Ağrıları"),              # Grip semptomları
                    ("Koku veya Tat Kaybı", "Nefes Darlığı"),  # COVID-19
                    ("Titreme", "Bitkinlik")                 # Grip sistemik
                ]
            }
        }
        
        # Ayırıcı tanı kuralları
        self.diagnostic_rules = {
            "COVID-19": {
                "must_have": ["Koku veya Tat Kaybı", "Nefes Darlığı"],
                "must_not_have": ["Göz Kaşıntısı veya Sulanma", "Titreme"],
                "high_probability": ["Ateş", "Öksürük", "Bitkinlik"]
            },
            "Grip": {
                "must_have": ["Vücut Ağrıları", "Ateş"],
                "must_not_have": ["Koku veya Tat Kaybı", "Göz Kaşıntısı veya Sulanma"],
                "high_probability": ["Titreme", "Bitkinlik", "Baş Ağrısı"]
            },
            "Soğuk Algınlığı": {
                "must_have": ["Burun Akıntısı veya Tıkanıklığı", "Hapşırma"],
                "must_not_have": ["Koku veya Tat Kaybı", "Titreme", "Vücut Ağrıları"],
                "high_probability": ["Boğaz Ağrısı", "Öksürük"]
            },
            "Mevsimsel Alerji": {
                "must_have": ["Göz Kaşıntısı veya Sulanma", "Hapşırma"],
                "must_not_have": ["Ateş", "Vücut Ağrıları", "Titreme"],
                "high_probability": ["Burun Akıntısı veya Tıkanıklığı"]
            }
        }

    def generate_ultra_precise_sample(self, disease_name, sample_id):
        """Ultra hassas semptom vektörü üretir"""
        profile = self.disease_profiles[disease_name]
        vector = {}
        
        # 1. Unique signatures - hastalığa özgü semptomları güçlendir
        for symptom, prob in profile["unique_signatures"].items():
            if random.random() < prob:
                vector[symptom] = random.uniform(0.7, 1.0)  # Yüksek şiddet
            else:
                vector[symptom] = 0.0
        
        # 2. Core symptoms - temel semptomları ekle
        for symptom, prob in profile["core_symptoms"].items():
            if symptom not in vector:  # Eğer unique signature değilse
                if random.random() < prob:
                    vector[symptom] = random.uniform(0.4, 0.8)
                else:
                    vector[symptom] = 0.0
        
        # 3. Rare symptoms - nadir semptomları kontrol et
        for symptom, prob in profile["rare_symptoms"].items():
            if symptom not in vector:
                if random.random() < prob:
                    vector[symptom] = random.uniform(0.1, 0.4)
                else:
                    vector[symptom] = 0.0
        
        # 4. Diagnostic rules uygula
        self._apply_diagnostic_rules(vector, disease_name)
        
        # 5. Diğer semptomları 0 yap
        for symptom in self.symptoms:
            if symptom not in vector:
                vector[symptom] = 0.0
        
        return [vector.get(symptom, 0.0) for symptom in self.symptoms]

    def _apply_diagnostic_rules(self, vector, disease_name):
        """Tanısal kuralları uygular"""
        rules = self.diagnostic_rules[disease_name]
        
        # Must have - mutlaka olması gerekenler
        for symptom in rules["must_have"]:
            if symptom in self.symptoms:
                idx = self.symptoms.index(symptom)
                if idx < len(vector):
                    vector[symptom] = random.uniform(0.6, 1.0)
        
        # Must not have - kesinlikle olmaması gerekenler
        for symptom in rules["must_not_have"]:
            if symptom in self.symptoms:
                vector[symptom] = 0.0
        
        # High probability - yüksek olasılıklı semptomları güçlendir
        for symptom in rules["high_probability"]:
            if symptom in self.symptoms and symptom in vector:
                if vector[symptom] > 0:
                    vector[symptom] = min(1.0, vector[symptom] + 0.2)

    def generate_ultra_precise_dataset(self, samples_per_disease=2000):
        """Ultra hassas veri seti üretir"""
        all_samples = []
        all_labels = []
        
        print("🚀 Ultra hassas veri seti üretimi başlıyor...")
        print("🎯 Hedef: 4 hastalığı mükemmel ayırt etme")
        
        for disease_name in self.disease_profiles.keys():
            print(f"📊 {disease_name} için {samples_per_disease} ultra hassas örnek üretiliyor...")
            
            disease_samples = []
            for i in range(samples_per_disease):
                sample = self.generate_ultra_precise_sample(disease_name, i)
                disease_samples.append(sample)
            
            # Veri çeşitliliği için augmentasyon
            augmented_samples = self._augment_for_precision(disease_samples, disease_name)
            
            all_samples.extend(augmented_samples)
            all_labels.extend([disease_name] * len(augmented_samples))
        
        # Veri setini oluştur
        df = pd.DataFrame(all_samples, columns=self.symptoms)
        df["Etiket"] = all_labels
        
        # Sınıf dengesini kontrol et
        df_balanced = self._balance_for_precision(df)
        
        print(f"✅ Toplam {len(df_balanced)} ultra hassas örnek üretildi")
        print(f"📈 Sınıf dağılımı:")
        print(df_balanced["Etiket"].value_counts())
        
        return df_balanced

    def _augment_for_precision(self, samples, disease_name):
        """Hassasiyet için augmentasyon"""
        augmented = samples.copy()
        
        # Her hastalık için özel augmentasyon
        if disease_name == "COVID-19":
            # COVID-19 varyantları
            for _ in range(len(samples) // 3):
                base_sample = random.choice(samples)
                variant = base_sample.copy()
                
                # Koku kaybı olmadan COVID varyantları (nadir)
                if random.random() < 0.1:
                    variant[self.symptoms.index("Koku veya Tat Kaybı")] = 0.0
                
                # Nefes darlığı olmadan COVID varyantları (nadir)
                if random.random() < 0.05:
                    variant[self.symptoms.index("Nefes Darlığı")] = 0.0
                
                augmented.append(variant)
        
        elif disease_name == "Grip":
            # Grip varyantları
            for _ in range(len(samples) // 4):
                base_sample = random.choice(samples)
                variant = base_sample.copy()
                
                # Hafif grip vakaları
                if random.random() < 0.3:
                    for i in range(len(variant)):
                        if variant[i] > 0.7:
                            variant[i] = max(0.3, variant[i] - 0.4)
                
                augmented.append(variant)
        
        elif disease_name == "Soğuk Algınlığı":
            # Soğuk algınlığı varyantları
            for _ in range(len(samples) // 5):
                base_sample = random.choice(samples)
                variant = base_sample.copy()
                
                # Ateşli soğuk algınlığı (nadir)
                if random.random() < 0.2:
                    variant[self.symptoms.index("Ateş")] = random.uniform(0.3, 0.6)
                
                augmented.append(variant)
        
        elif disease_name == "Mevsimsel Alerji":
            # Alerji varyantları
            for _ in range(len(samples) // 6):
                base_sample = random.choice(samples)
                variant = base_sample.copy()
                
                # Hafif ateşli alerji (çok nadir)
                if random.random() < 0.05:
                    variant[self.symptoms.index("Ateş")] = random.uniform(0.1, 0.3)
                
                augmented.append(variant)
        
        return augmented

    def _balance_for_precision(self, df):
        """Hassasiyet için dengeleme"""
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

    def save_ultra_precise_dataset(self, df, filename="ultra_precise_hastalik_veriseti.csv"):
        """Ultra hassas veri setini kaydeder"""
        df.to_csv(filename, index=False)
        print(f"💾 Ultra hassas veri seti kaydedildi: {filename}")
        return filename

    def analyze_disease_separation(self, df):
        """Hastalık ayrımını analiz eder"""
        print("\n🔍 HASTALIK AYIRIM ANALİZİ")
        print("="*60)
        
        for disease in df["Etiket"].unique():
            subset = df[df["Etiket"] == disease]
            print(f"\n📊 {disease} Profili:")
            
            # Ortalama semptom şiddetleri
            symptom_means = subset.iloc[:, :-1].mean()
            top_symptoms = symptom_means.nlargest(8)
            
            print("🎯 En belirgin semptomlar:")
            for symptom, mean_val in top_symptoms.items():
                if mean_val > 0.1:
                    print(f"   {symptom}: {mean_val:.3f}")
            
            # Ayırıcı semptomları kontrol et
            rules = self.diagnostic_rules[disease]
            print(f"\n✅ Must-have semptomlar: {rules['must_have']}")
            print(f"❌ Must-not-have semptomlar: {rules['must_not_have']}")
            print(f"🔥 High-probability semptomlar: {rules['high_probability']}")

# Kullanım
if __name__ == "__main__":
    generator = UltraPreciseDiseaseDataGenerator()
    
    # Ultra hassas veri seti üret
    ultra_df = generator.generate_ultra_precise_dataset(samples_per_disease=2000)
    
    # Kaydet
    output_file = generator.save_ultra_precise_dataset(ultra_df)
    
    # Analiz et
    generator.analyze_disease_separation(ultra_df)
    
    print("\n🎯 Ultra hassas veri seti özellikleri:")
    print(f"- Toplam örnek sayısı: {len(ultra_df)}")
    print(f"- Özellik sayısı: {len(ultra_df.columns) - 1}")
    print(f"- Sınıf sayısı: {ultra_df['Etiket'].nunique()}")
    print(f"- Sınıf dengesi: {ultra_df['Etiket'].value_counts().to_dict()}")
