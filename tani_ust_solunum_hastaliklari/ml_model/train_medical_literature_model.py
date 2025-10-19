#!/usr/bin/env python3
"""
Train Medical Literature Model
Tıbbi literatür verilerine dayalı model eğitimi
"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, BaggingClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

class MedicalLiteratureModelTrainer:
    def __init__(self, data_file="medical_literature_dataset.csv"):
        """Tıbbi literatür modeli eğitici"""
        print("🏥 Tıbbi Literatür Modeli Eğitici başlatılıyor...")
        
        self.data_file = data_file
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.best_model = None
        
        # Semptom listesi
        self.symptoms = [
            "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
            "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
            "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları",
            "Göğüs Ağrısı", "Titreme", "Gece Terlemesi", "İştahsızlık", "Konsantrasyon Güçlüğü"
        ]
        
        print(f"✅ {len(self.symptoms)} semptom için model eğitici hazır")
    
    def load_data(self):
        """Veri setini yükle"""
        print(f"📂 Veri seti yükleniyor: {self.data_file}")
        
        try:
            self.df = pd.read_csv(self.data_file)
            print(f"✅ {len(self.df):,} hasta verisi yüklendi")
            print(f"📊 Hastalık dağılımı:")
            print(self.df['Hastalik'].value_counts())
            return True
        except FileNotFoundError:
            print(f"❌ Veri dosyası bulunamadı: {self.data_file}")
            return False
    
    def prepare_data(self):
        """Veriyi hazırla"""
        print("🔧 Veri hazırlanıyor...")
        
        # Semptom verilerini al
        X = self.df[self.symptoms].values
        y = self.df['Hastalik'].values
        
        print(f"📊 Veri boyutları: {X.shape}")
        print(f"🎯 Hedef sınıfları: {np.unique(y)}")
        
        # Train-test split
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"✅ Train set: {self.X_train.shape[0]:,} hasta")
        print(f"✅ Test set: {self.X_test.shape[0]:,} hasta")
        
        return True
    
    def create_enhanced_features(self):
        """Gelişmiş özellikler oluştur"""
        print("🚀 Gelişmiş özellikler oluşturuluyor...")
        
        def create_features(data):
            features = []
            
            # Temel semptomlar (18 adet)
            for symptom in self.symptoms:
                features.append(data[self.symptoms.index(symptom)])
            
            # COVID-19 özel özellikler
            covid_features = [
                data[self.symptoms.index("Koku veya Tat Kaybı")],
                data[self.symptoms.index("Nefes Darlığı")],
                data[self.symptoms.index("Koku veya Tat Kaybı")] * data[self.symptoms.index("Nefes Darlığı")],  # Etkileşim
                data[self.symptoms.index("Ateş")] * data[self.symptoms.index("Öksürük")],  # Etkileşim
            ]
            features.extend(covid_features)
            
            # Grip özel özellikler
            flu_features = [
                data[self.symptoms.index("Vücut Ağrıları")],
                data[self.symptoms.index("Titreme")],
                data[self.symptoms.index("Vücut Ağrıları")] * data[self.symptoms.index("Titreme")],  # Etkileşim
                data[self.symptoms.index("Ateş")] * data[self.symptoms.index("Vücut Ağrıları")],  # Etkileşim
            ]
            features.extend(flu_features)
            
            # Soğuk algınlığı özel özellikler
            cold_features = [
                data[self.symptoms.index("Burun Akıntısı veya Tıkanıklığı")],
                data[self.symptoms.index("Hapşırma")],
                data[self.symptoms.index("Burun Akıntısı veya Tıkanıklığı")] * data[self.symptoms.index("Hapşırma")],  # Etkileşim
                data[self.symptoms.index("Boğaz Ağrısı")] * data[self.symptoms.index("Öksürük")],  # Etkileşim
            ]
            features.extend(cold_features)
            
            # Alerji özel özellikler
            allergy_features = [
                data[self.symptoms.index("Göz Kaşıntısı veya Sulanma")],
                data[self.symptoms.index("Göz Kaşıntısı veya Sulanma")] * data[self.symptoms.index("Hapşırma")],  # Etkileşim
                data[self.symptoms.index("Ateş")] == 0,  # Ateş yok (boolean)
                data[self.symptoms.index("Vücut Ağrıları")] == 0,  # Vücut ağrısı yok (boolean)
            ]
            features.extend(allergy_features)
            
            # Genel özellikler
            general_features = [
                np.sum(data),  # Toplam semptom yoğunluğu
                np.sum(data > 0),  # Aktif semptom sayısı
                np.max(data),  # Maksimum semptom yoğunluğu
                np.std(data),  # Semptom yoğunluğu standart sapması
                np.mean(data),  # Ortalama semptom yoğunluğu
            ]
            features.extend(general_features)
            
            return np.array(features)
        
        # Train ve test setleri için özellikler oluştur
        self.X_train_enhanced = np.array([create_features(x) for x in self.X_train])
        self.X_test_enhanced = np.array([create_features(x) for x in self.X_test])
        
        print(f"✅ Gelişmiş özellikler oluşturuldu: {self.X_train_enhanced.shape[1]} özellik")
        
        return True
    
    def scale_features(self):
        """Özellikleri ölçeklendir"""
        print("📏 Özellikler ölçeklendiriliyor...")
        
        self.X_train_scaled = self.scaler.fit_transform(self.X_train_enhanced)
        self.X_test_scaled = self.scaler.transform(self.X_test_enhanced)
        
        print("✅ Özellikler ölçeklendirildi")
        
        return True
    
    def select_features(self):
        """En iyi özellikleri seç"""
        print("🎯 En iyi özellikler seçiliyor...")
        
        # En iyi 25 özelliği seç
        self.feature_selector = SelectKBest(score_func=f_classif, k=25)
        self.X_train_selected = self.feature_selector.fit_transform(self.X_train_scaled, self.y_train)
        self.X_test_selected = self.feature_selector.transform(self.X_test_scaled)
        
        print(f"✅ {self.X_train_selected.shape[1]} en iyi özellik seçildi")
        
        return True
    
    def train_models(self):
        """Modelleri eğit"""
        print("🤖 Modeller eğitiliyor...")
        
        # Model tanımları
        self.models = {
            'RandomForest': RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_leaf=3,
                random_state=42,
                n_jobs=-1
            ),
            'SVM': SVC(
                kernel='rbf',
                C=1.0,
                gamma='scale',
                probability=True,
                random_state=42
            ),
            'NeuralNetwork': MLPClassifier(
                hidden_layer_sizes=(100, 50),
                max_iter=500,
                random_state=42
            ),
            'LogisticRegression': LogisticRegression(
                max_iter=1000,
                random_state=42
            ),
            'Bagging': BaggingClassifier(
                estimator=RandomForestClassifier(n_estimators=100, random_state=42),
                n_estimators=10,
                random_state=42,
                n_jobs=-1
            )
        }
        
        # Her modeli eğit
        model_scores = {}
        
        for name, model in self.models.items():
            print(f"   🔄 {name} eğitiliyor...")
            
            # Modeli eğit
            model.fit(self.X_train_selected, self.y_train)
            
            # Cross-validation skoru
            cv_scores = cross_val_score(model, self.X_train_selected, self.y_train, cv=5)
            model_scores[name] = cv_scores.mean()
            
            print(f"   ✅ {name} CV Skoru: %{cv_scores.mean()*100:.2f}")
        
        # En iyi modelleri seç
        best_models = sorted(model_scores.items(), key=lambda x: x[1], reverse=True)[:4]
        
        print(f"\n🏆 En iyi 4 model:")
        for name, score in best_models:
            print(f"   {name}: %{score*100:.2f}")
        
        # Ensemble model oluştur
        ensemble_models = [(name, self.models[name]) for name, _ in best_models]
        
        self.best_model = VotingClassifier(
            estimators=ensemble_models,
            voting='soft'
        )
        
        # Ensemble modeli eğit
        print(f"\n🎯 Ensemble model eğitiliyor...")
        self.best_model.fit(self.X_train_selected, self.y_train)
        
        # Ensemble CV skoru
        ensemble_cv = cross_val_score(self.best_model, self.X_train_selected, self.y_train, cv=5)
        print(f"✅ Ensemble CV Skoru: %{ensemble_cv.mean()*100:.2f}")
        
        return True
    
    def evaluate_model(self):
        """Modeli değerlendir"""
        print("📊 Model değerlendiriliyor...")
        
        # Test tahminleri
        y_pred = self.best_model.predict(self.X_test_selected)
        y_pred_proba = self.best_model.predict_proba(self.X_test_selected)
        
        # Accuracy
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f"🎯 Test Accuracy: %{accuracy*100:.2f}")
        
        # Classification report
        print(f"\n📋 Classification Report:")
        print(classification_report(self.y_test, y_pred))
        
        # Confusion matrix
        cm = confusion_matrix(self.y_test, y_pred)
        print(f"\n🔢 Confusion Matrix:")
        print(cm)
        
        # Hastalık bazında doğruluk
        diseases = np.unique(self.y_test)
        print(f"\n🏥 Hastalık Bazında Doğruluk:")
        for i, disease in enumerate(diseases):
            disease_accuracy = cm[i, i] / cm[i, :].sum()
            print(f"   {disease}: %{disease_accuracy*100:.2f}")
        
        return accuracy
    
    def save_model(self):
        """Modeli kaydet"""
        print("💾 Model kaydediliyor...")
        
        # Model ve preprocessing nesnelerini kaydet
        model_data = {
            'model': self.best_model,
            'scaler': self.scaler,
            'feature_selector': self.feature_selector,
            'symptoms': self.symptoms,
            'accuracy': self.evaluate_model()
        }
        
        joblib.dump(model_data, 'medical_literature_model.pkl')
        print("✅ Model 'medical_literature_model.pkl' olarak kaydedildi")
        
        return True
    
    def run_training_pipeline(self):
        """Eğitim pipeline'ını çalıştır"""
        print("🚀 TIBBİ LİTERATÜR MODEL EĞİTİMİ BAŞLIYOR...")
        print("="*60)
        
        # Pipeline adımları
        steps = [
            ("Veri Yükleme", self.load_data),
            ("Veri Hazırlama", self.prepare_data),
            ("Gelişmiş Özellikler", self.create_enhanced_features),
            ("Özellik Ölçeklendirme", self.scale_features),
            ("Özellik Seçimi", self.select_features),
            ("Model Eğitimi", self.train_models),
            ("Model Değerlendirme", self.evaluate_model),
            ("Model Kaydetme", self.save_model)
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            if not step_func():
                print(f"❌ {step_name} başarısız!")
                return False
            print(f"✅ {step_name} tamamlandı!")
        
        print(f"\n🎉 TIBBİ LİTERATÜR MODEL EĞİTİMİ TAMAMLANDI!")
        print("="*60)
        
        return True

def main():
    """Ana fonksiyon"""
    trainer = MedicalLiteratureModelTrainer()
    trainer.run_training_pipeline()

if __name__ == "__main__":
    main()
