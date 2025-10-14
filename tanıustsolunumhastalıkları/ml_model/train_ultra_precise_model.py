#!/usr/bin/env python3
"""
Ultra Hassas Model Eğitimi - 4 Hastalığı Mükemmel Ayırt Etmek İçin
"""

import pandas as pd
import numpy as np
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, BaggingClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

class UltraPreciseDiseasePredictor:
    def __init__(self):
        self.models = {}
        self.ensemble_model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_selector = None
        self.feature_names = None
        self.best_model = None
        self.results = {}
        
    def load_data(self, csv_path):
        """Veri setini yükler ve hazırlar"""
        print("📊 Ultra hassas veri seti yükleniyor...")
        self.df = pd.read_csv(csv_path)
        
        # X ve y ayır
        self.X = self.df.drop("Etiket", axis=1)
        self.y = self.df["Etiket"]
        
        # Etiketleri encode et
        self.y_encoded = self.label_encoder.fit_transform(self.y)
        
        # Özellik isimlerini sakla
        self.feature_names = self.X.columns.tolist()
        
        print(f"✅ Veri yüklendi: {self.X.shape[0]} örnek, {self.X.shape[1]} özellik")
        print(f"📋 Sınıflar: {list(self.label_encoder.classes_)}")
        
        return self.X, self.y_encoded
    
    def create_ultra_precise_features(self, X):
        """Ultra hassas özellik mühendisliği"""
        print("🔧 Ultra hassas özellik mühendisliği yapılıyor...")
        
        X_enhanced = X.copy()
        
        # 1. COVID-19 ayırıcı kombinasyonları
        if "Ateş" in X.columns and "Koku veya Tat Kaybı" in X.columns and "Nefes Darlığı" in X.columns:
            X_enhanced["COVID_Unique_Signature"] = (
                X["Ateş"] * X["Koku veya Tat Kaybı"] * X["Nefes Darlığı"]
            )
        
        if "Koku veya Tat Kaybı" in X.columns and "Nefes Darlığı" in X.columns:
            X_enhanced["COVID_Core_Signature"] = (
                X["Koku veya Tat Kaybı"] * X["Nefes Darlığı"]
            )
        
        # 2. Grip ayırıcı kombinasyonları
        if "Ateş" in X.columns and "Vücut Ağrıları" in X.columns and "Titreme" in X.columns:
            X_enhanced["Flu_Unique_Signature"] = (
                X["Ateş"] * X["Vücut Ağrıları"] * X["Titreme"]
            )
        
        if "Vücut Ağrıları" in X.columns and "Ateş" in X.columns:
            X_enhanced["Flu_Core_Signature"] = (
                X["Vücut Ağrıları"] * X["Ateş"]
            )
        
        # 3. Soğuk algınlığı ayırıcı kombinasyonları
        if "Burun Akıntısı veya Tıkanıklığı" in X.columns and "Hapşırma" in X.columns:
            X_enhanced["Cold_Unique_Signature"] = (
                X["Burun Akıntısı veya Tıkanıklığı"] * X["Hapşırma"]
            )
        
        # Ateş olmadan soğuk algınlığı
        if "Burun Akıntısı veya Tıkanıklığı" in X.columns and "Hapşırma" in X.columns and "Ateş" in X.columns:
            X_enhanced["Cold_No_Fever"] = (
                X["Burun Akıntısı veya Tıkanıklığı"] * X["Hapşırma"] * (1 - X["Ateş"])
            )
        
        # 4. Alerji ayırıcı kombinasyonları
        if "Göz Kaşıntısı veya Sulanma" in X.columns and "Hapşırma" in X.columns:
            X_enhanced["Allergy_Unique_Signature"] = (
                X["Göz Kaşıntısı veya Sulanma"] * X["Hapşırma"]
            )
        
        # Ateş olmadan alerji
        if "Göz Kaşıntısı veya Sulanma" in X.columns and "Hapşırma" in X.columns and "Ateş" in X.columns:
            X_enhanced["Allergy_No_Fever"] = (
                X["Göz Kaşıntısı veya Sulanma"] * X["Hapşırma"] * (1 - X["Ateş"])
            )
        
        # 5. Ayırıcı tanı skorları
        # COVID-19 vs Grip
        if "Koku veya Tat Kaybı" in X.columns and "Vücut Ağrıları" in X.columns:
            X_enhanced["COVID_vs_Flu"] = (
                X["Koku veya Tat Kaybı"] - X["Vücut Ağrıları"]
            )
        
        # Alerji vs Soğuk algınlığı
        if "Göz Kaşıntısı veya Sulanma" in X.columns and "Boğaz Ağrısı" in X.columns:
            X_enhanced["Allergy_vs_Cold"] = (
                X["Göz Kaşıntısı veya Sulanma"] - X["Boğaz Ağrısı"]
            )
        
        # 6. Sistemik vs Lokal semptom ayrımı
        systemic_symptoms = ["Ateş", "Bitkinlik", "Vücut Ağrıları", "Baş Ağrısı", "Titreme"]
        available_systemic = [s for s in systemic_symptoms if s in X.columns]
        if available_systemic:
            X_enhanced["Systemic_Score"] = X[available_systemic].mean(axis=1)
        
        local_symptoms = ["Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma", "Boğaz Ağrısı"]
        available_local = [s for s in local_symptoms if s in X.columns]
        if available_local:
            X_enhanced["Local_Score"] = X[available_local].mean(axis=1)
        
        # 7. Semptom yoğunluğu
        X_enhanced["Symptom_Intensity"] = X.sum(axis=1)
        X_enhanced["Active_Symptom_Count"] = (X > 0.1).sum(axis=1)
        
        # 8. Ayırıcı tanı indeksi
        X_enhanced["Diagnostic_Index"] = (
            X_enhanced.get("COVID_Unique_Signature", 0) * 4 +
            X_enhanced.get("Flu_Unique_Signature", 0) * 4 +
            X_enhanced.get("Cold_Unique_Signature", 0) * 3 +
            X_enhanced.get("Allergy_Unique_Signature", 0) * 3
        )
        
        print(f"✅ Özellik sayısı {X.shape[1]}'den {X_enhanced.shape[1]}'e çıkarıldı")
        
        return X_enhanced
    
    def train_ultra_precise_models(self, X, y):
        """Ultra hassas modelleri eğitir"""
        print("🤖 Ultra hassas modeller eğitiliyor...")
        
        # 1. Ultra hassas Random Forest
        print("🌲 Ultra hassas Random Forest eğitiliyor...")
        rf_params = {
            'n_estimators': 300,
            'max_depth': 12,
            'min_samples_split': 3,
            'min_samples_leaf': 1,
            'max_features': 'sqrt',
            'bootstrap': True,
            'random_state': 42,
            'n_jobs': -1,
            'class_weight': 'balanced'
        }
        self.models['Ultra_RandomForest'] = RandomForestClassifier(**rf_params)
        
        # 2. Ultra hassas SVM
        print("⚡ Ultra hassas SVM eğitiliyor...")
        self.models['Ultra_SVM'] = SVC(
            kernel='rbf',
            C=100,
            gamma='scale',
            probability=True,
            random_state=42,
            class_weight='balanced'
        )
        
        # 3. Ultra hassas Neural Network
        print("🧠 Ultra hassas Neural Network eğitiliyor...")
        self.models['Ultra_NeuralNetwork'] = MLPClassifier(
            hidden_layer_sizes=(200, 100, 50),
            activation='relu',
            solver='adam',
            alpha=0.0001,
            learning_rate='adaptive',
            max_iter=1000,
            random_state=42
        )
        
        # 4. Ultra hassas Logistic Regression
        print("📈 Ultra hassas Logistic Regression eğitiliyor...")
        self.models['Ultra_LogisticRegression'] = LogisticRegression(
            C=100,
            max_iter=2000,
            random_state=42,
            multi_class='ovr',
            class_weight='balanced'
        )
        
        # 5. Bagging Classifier
        print("🎒 Bagging Classifier eğitiliyor...")
        self.models['Ultra_Bagging'] = BaggingClassifier(
            estimator=RandomForestClassifier(n_estimators=100, random_state=42),
            n_estimators=10,
            random_state=42,
            n_jobs=-1
        )
        
        # Her modeli eğit ve değerlendir
        for name, model in self.models.items():
            print(f"🔄 {name} eğitiliyor...")
            
            # Cross validation
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
            self.results[name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'cv_scores': cv_scores
            }
            
            print(f"✅ {name} - CV Score: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        return self.results
    
    def create_ultra_ensemble(self, X, y):
        """Ultra hassas ensemble model oluşturur"""
        print("🎭 Ultra hassas ensemble model oluşturuluyor...")
        
        # En iyi modelleri seç (%95'ten yüksek performans gösteren modeller)
        best_models = []
        for name, result in self.results.items():
            if result['cv_mean'] > 0.95:  # %95'ten yüksek performans
                best_models.append((name, self.models[name]))
                print(f"✅ {name} ultra ensemble'a eklendi")
        
        if len(best_models) < 2:
            print("⚠️ Yeterli model yok, tüm modelleri kullanıyor...")
            best_models = [(name, model) for name, model in self.models.items()]
        
        # Ultra hassas Voting Classifier
        self.ensemble_model = VotingClassifier(
            estimators=best_models,
            voting='soft',  # Olasılık tabanlı voting
            n_jobs=-1
        )
        
        print(f"🎯 {len(best_models)} model ile ultra ensemble oluşturuldu")
        return self.ensemble_model
    
    def train_complete_ultra_system(self, csv_path):
        """Ultra hassas sistemi eğitir"""
        print("🚀 Ultra hassas hastalık tanı sistemi eğitimi başlıyor...\n")
        
        # 1. Veri yükle
        X, y = self.load_data(csv_path)
        
        # 2. Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 3. Ultra hassas özellik mühendisliği
        X_train_enhanced = self.create_ultra_precise_features(X_train)
        X_test_enhanced = self.create_ultra_precise_features(X_test)
        
        # 4. Ölçeklendirme
        X_train_scaled = self.scaler.fit_transform(X_train_enhanced)
        X_test_scaled = self.scaler.transform(X_test_enhanced)
        
        # 5. Özellik seçimi
        self.feature_selector = SelectKBest(f_classif, k=min(25, X_train_scaled.shape[1]))
        X_train_selected = self.feature_selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = self.feature_selector.transform(X_test_scaled)
        
        print(f"🎯 Özellik seçimi: {X_train_scaled.shape[1]} -> {X_train_selected.shape[1]}")
        
        # 6. Ultra hassas modelleri eğit
        self.train_ultra_precise_models(X_train_selected, y_train)
        
        # 7. Ultra ensemble model oluştur
        self.create_ultra_ensemble(X_train_selected, y_train)
        
        # 8. Final değerlendirme
        print("\n🎯 Ultra hassas final değerlendirme:")
        
        # En iyi bireysel modeli bul
        best_individual = max(self.results.items(), key=lambda x: x[1]['cv_mean'])
        print(f"🏆 En iyi bireysel model: {best_individual[0]} ({best_individual[1]['cv_mean']:.4f})")
        
        # Ensemble modeli test et
        if self.ensemble_model:
            ensemble_cv = cross_val_score(self.ensemble_model, X_train_selected, y_train, cv=5)
            print(f"🎭 Ultra Ensemble CV Score: {ensemble_cv.mean():.4f} (±{ensemble_cv.std():.4f})")
            
            # Test seti üzerinde değerlendir
            self.ensemble_model.fit(X_train_selected, y_train)
            y_pred = self.ensemble_model.predict(X_test_selected)
            y_pred_proba = self.ensemble_model.predict_proba(X_test_selected)
            
            test_accuracy = accuracy_score(y_test, y_pred)
            print(f"🎯 Test Accuracy: {test_accuracy:.4f}")
            
            print("\n📊 Detaylı Sınıflandırma Raporu:")
            print(classification_report(y_test, y_pred, target_names=self.label_encoder.classes_))
            
            # Confusion Matrix
            cm = confusion_matrix(y_test, y_pred)
            print("\n📊 Confusion Matrix:")
            print(cm)
            
            # En iyi modeli kaydet
            self.best_model = self.ensemble_model
            
        return {
            'best_individual': best_individual,
            'ensemble_cv': ensemble_cv.mean() if self.ensemble_model else None,
            'test_accuracy': test_accuracy if self.ensemble_model else None,
            'models': self.models,
            'feature_names': self.feature_names
        }
    
    def save_ultra_model(self, model_path="ultra_precise_disease_model.pkl"):
        """Ultra hassas modeli kaydeder"""
        if self.best_model:
            model_data = {
                'model': self.best_model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'feature_selector': self.feature_selector,
                'feature_names': self.feature_names
            }
            joblib.dump(model_data, model_path)
            print(f"💾 Ultra hassas model kaydedildi: {model_path}")
        else:
            print("⚠️ Kaydedilecek model yok!")

# Kullanım
if __name__ == "__main__":
    predictor = UltraPreciseDiseasePredictor()
    
    # Ultra hassas sistem eğitimi
    results = predictor.train_complete_ultra_system("ultra_precise_hastalik_veriseti.csv")
    
    # Modeli kaydet
    predictor.save_ultra_model("ultra_precise_disease_model.pkl")
    
    print("\n🎉 Ultra hassas sistem eğitimi tamamlandı!")
    print(f"🏆 En iyi performans: {results['test_accuracy']:.4f}")
    
    if results['test_accuracy'] >= 0.95:
        print("🎉 HEDEF BAŞARILDI! %95+ doğruluk elde edildi!")
    elif results['test_accuracy'] >= 0.90:
        print("✅ İyi performans! %90+ doğruluk elde edildi.")
    else:
        print("⚠️ Performans hedefin altında.")
