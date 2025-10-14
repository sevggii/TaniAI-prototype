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

# XGBoost için
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost kurulu değil. pip install xgboost ile kurabilirsiniz.")

class AdvancedDiseasePredictor:
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
        print("📊 Veri seti yükleniyor...")
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
    
    def create_advanced_features(self, X):
        """Gelişmiş özellik mühendisliği"""
        print("🔧 Gelişmiş özellik mühendisliği yapılıyor...")
        
        X_enhanced = X.copy()
        
        # 1. Semptom kombinasyon skorları
        if "Ateş" in X.columns and "Koku veya Tat Kaybı" in X.columns:
            X_enhanced["COVID_Indicator"] = X["Ateş"] * X["Koku veya Tat Kaybı"] * X["Nefes Darlığı"]
        
        if "Ateş" in X.columns and "Vücut Ağrıları" in X.columns:
            X_enhanced["Grip_Indicator"] = X["Ateş"] * X["Vücut Ağrıları"] * X["Bitkinlik"]
        
        if "Burun Akıntısı veya Tıkanıklığı" in X.columns and "Hapşırma" in X.columns:
            X_enhanced["Cold_Indicator"] = X["Burun Akıntısı veya Tıkanıklığı"] * X["Hapşırma"] * (1 - X.get("Ateş", 0))
        
        if "Göz Kaşıntısı veya Sulanma" in X.columns and "Hapşırma" in X.columns:
            X_enhanced["Allergy_Indicator"] = X["Göz Kaşıntısı veya Sulanma"] * X["Hapşırma"] * (1 - X.get("Ateş", 0))
        
        # 2. Toplam semptom şiddeti
        X_enhanced["Total_Symptom_Severity"] = X.sum(axis=1)
        
        # 3. Semptom sayısı
        X_enhanced["Symptom_Count"] = (X > 0.1).sum(axis=1)
        
        # 4. Solunum sistemi skoru
        respiratory_symptoms = ["Nefes Darlığı", "Öksürük", "Burun Akıntısı veya Tıkanıklığı"]
        available_resp = [s for s in respiratory_symptoms if s in X.columns]
        if available_resp:
            X_enhanced["Respiratory_Score"] = X[available_resp].mean(axis=1)
        
        # 5. Sistemik semptom skoru
        systemic_symptoms = ["Ateş", "Bitkinlik", "Vücut Ağrıları", "Baş Ağrısı"]
        available_syst = [s for s in systemic_symptoms if s in X.columns]
        if available_syst:
            X_enhanced["Systemic_Score"] = X[available_syst].mean(axis=1)
        
        # 6. Gastrointestinal semptom skoru
        gi_symptoms = ["Bulantı veya Kusma", "İshal", "İştahsızlık"]
        available_gi = [s for s in gi_symptoms if s in X.columns]
        if available_gi:
            X_enhanced["GI_Score"] = X[available_gi].mean(axis=1)
        
        print(f"✅ Özellik sayısı {X.shape[1]}'den {X_enhanced.shape[1]}'e çıkarıldı")
        
        return X_enhanced
    
    def train_individual_models(self, X, y):
        """Bireysel modelleri eğitir"""
        print("🤖 Bireysel modeller eğitiliyor...")
        
        # 1. Random Forest (Optimized)
        print("🌲 Random Forest eğitiliyor...")
        rf_params = {
            'n_estimators': 200,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'max_features': 'sqrt',
            'bootstrap': True,
            'random_state': 42,
            'n_jobs': -1
        }
        self.models['RandomForest'] = RandomForestClassifier(**rf_params)
        
        # 2. XGBoost (if available)
        if XGBOOST_AVAILABLE:
            print("🚀 XGBoost eğitiliyor...")
            xgb_params = {
                'n_estimators': 200,
                'max_depth': 6,
                'learning_rate': 0.1,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'random_state': 42,
                'eval_metric': 'mlogloss'
            }
            self.models['XGBoost'] = xgb.XGBClassifier(**xgb_params)
        
        # 3. SVM
        print("⚡ SVM eğitiliyor...")
        self.models['SVM'] = SVC(
            kernel='rbf',
            C=10,
            gamma='scale',
            probability=True,
            random_state=42
        )
        
        # 4. Neural Network
        print("🧠 Neural Network eğitiliyor...")
        self.models['NeuralNetwork'] = MLPClassifier(
            hidden_layer_sizes=(100, 50, 25),
            activation='relu',
            solver='adam',
            alpha=0.001,
            learning_rate='adaptive',
            max_iter=500,
            random_state=42
        )
        
        # 5. Logistic Regression
        print("📈 Logistic Regression eğitiliyor...")
        self.models['LogisticRegression'] = LogisticRegression(
            C=10,
            max_iter=1000,
            random_state=42,
            multi_class='ovr'
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
    
    def create_ensemble_model(self, X, y):
        """Ensemble model oluşturur"""
        print("🎭 Ensemble model oluşturuluyor...")
        
        # En iyi modelleri seç
        best_models = []
        for name, result in self.results.items():
            if result['cv_mean'] > 0.85:  # %85'ten yüksek performans gösteren modeller
                best_models.append((name, self.models[name]))
                print(f"✅ {name} ensemble'a eklendi")
        
        if len(best_models) < 2:
            print("⚠️ Yeterli model yok, tüm modelleri kullanıyor...")
            best_models = [(name, model) for name, model in self.models.items()]
        
        # Voting Classifier
        self.ensemble_model = VotingClassifier(
            estimators=best_models,
            voting='soft',  # Olasılık tabanlı voting
            n_jobs=-1
        )
        
        print(f"🎯 {len(best_models)} model ile ensemble oluşturuldu")
        return self.ensemble_model
    
    def hyperparameter_tuning(self, X, y):
        """Hiperparametre optimizasyonu"""
        print("🎛️ Hiperparametre optimizasyonu başlıyor...")
        
        # Random Forest için grid search
        rf_params = {
            'n_estimators': [100, 200, 300],
            'max_depth': [8, 10, 12, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        print("🌲 Random Forest hiperparametre optimizasyonu...")
        rf_grid = GridSearchCV(
            RandomForestClassifier(random_state=42),
            rf_params,
            cv=3,
            scoring='accuracy',
            n_jobs=-1,
            verbose=1
        )
        rf_grid.fit(X, y)
        
        print(f"✅ En iyi RF parametreleri: {rf_grid.best_params_}")
        print(f"✅ En iyi RF skoru: {rf_grid.best_score_:.4f}")
        
        # En iyi Random Forest'i güncelle
        self.models['RandomForest_Optimized'] = rf_grid.best_estimator_
        
        # XGBoost optimizasyonu (if available)
        if XGBOOST_AVAILABLE:
            print("🚀 XGBoost hiperparametre optimizasyonu...")
            xgb_params = {
                'n_estimators': [100, 200],
                'max_depth': [4, 6, 8],
                'learning_rate': [0.05, 0.1, 0.2],
                'subsample': [0.8, 0.9]
            }
            
            xgb_grid = GridSearchCV(
                xgb.XGBClassifier(random_state=42, eval_metric='mlogloss'),
                xgb_params,
                cv=3,
                scoring='accuracy',
                n_jobs=-1,
                verbose=1
            )
            xgb_grid.fit(X, y)
            
            print(f"✅ En iyi XGB parametreleri: {xgb_grid.best_params_}")
            print(f"✅ En iyi XGB skoru: {xgb_grid.best_score_:.4f}")
            
            self.models['XGBoost_Optimized'] = xgb_grid.best_estimator_
        
        return self.models
    
    def train_complete_system(self, csv_path):
        """Tüm sistemi eğitir"""
        print("🚀 Gelişmiş hastalık tanı sistemi eğitimi başlıyor...\n")
        
        # 1. Veri yükle
        X, y = self.load_data(csv_path)
        
        # 2. Train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 3. Özellik mühendisliği
        X_train_enhanced = self.create_advanced_features(X_train)
        X_test_enhanced = self.create_advanced_features(X_test)
        
        # 4. Ölçeklendirme
        X_train_scaled = self.scaler.fit_transform(X_train_enhanced)
        X_test_scaled = self.scaler.transform(X_test_enhanced)
        
        # 5. Özellik seçimi
        self.feature_selector = SelectKBest(f_classif, k=min(20, X_train_scaled.shape[1]))
        X_train_selected = self.feature_selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = self.feature_selector.transform(X_test_scaled)
        
        print(f"🎯 Özellik seçimi: {X_train_scaled.shape[1]} -> {X_train_selected.shape[1]}")
        
        # 6. Bireysel modelleri eğit
        self.train_individual_models(X_train_selected, y_train)
        
        # 7. Hiperparametre optimizasyonu
        self.hyperparameter_tuning(X_train_selected, y_train)
        
        # 8. Ensemble model oluştur
        self.create_ensemble_model(X_train_selected, y_train)
        
        # 9. Final değerlendirme
        print("\n🎯 Final değerlendirme:")
        
        # En iyi bireysel modeli bul
        best_individual = max(self.results.items(), key=lambda x: x[1]['cv_mean'])
        print(f"🏆 En iyi bireysel model: {best_individual[0]} ({best_individual[1]['cv_mean']:.4f})")
        
        # Ensemble modeli test et
        if self.ensemble_model:
            ensemble_cv = cross_val_score(self.ensemble_model, X_train_selected, y_train, cv=5)
            print(f"🎭 Ensemble CV Score: {ensemble_cv.mean():.4f} (±{ensemble_cv.std():.4f})")
            
            # Test seti üzerinde değerlendir
            self.ensemble_model.fit(X_train_selected, y_train)
            y_pred = self.ensemble_model.predict(X_test_selected)
            y_pred_proba = self.ensemble_model.predict_proba(X_test_selected)
            
            test_accuracy = accuracy_score(y_test, y_pred)
            print(f"🎯 Test Accuracy: {test_accuracy:.4f}")
            
            print("\n📊 Detaylı Sınıflandırma Raporu:")
            print(classification_report(y_test, y_pred, target_names=self.label_encoder.classes_))
            
            # En iyi modeli kaydet
            self.best_model = self.ensemble_model
            
        return {
            'best_individual': best_individual,
            'ensemble_cv': ensemble_cv.mean() if self.ensemble_model else None,
            'test_accuracy': test_accuracy if self.ensemble_model else None,
            'models': self.models,
            'feature_names': self.feature_names
        }
    
    def save_model(self, model_path="advanced_disease_model.pkl"):
        """Modeli kaydeder"""
        if self.best_model:
            model_data = {
                'model': self.best_model,
                'scaler': self.scaler,
                'label_encoder': self.label_encoder,
                'feature_selector': self.feature_selector,
                'feature_names': self.feature_names
            }
            joblib.dump(model_data, model_path)
            print(f"💾 Model kaydedildi: {model_path}")
        else:
            print("⚠️ Kaydedilecek model yok!")

# Kullanım örneği
if __name__ == "__main__":
    # Gelişmiş veri seti üret (eğer yoksa)
    try:
        df = pd.read_csv("enhanced_hastalik_veriseti.csv")
        print("✅ Gelişmiş veri seti bulundu")
    except FileNotFoundError:
        print("⚠️ Gelişmiş veri seti bulunamadı, önce enhanced_data_generation.py çalıştırın")
        exit(1)
    
    # Sistem eğitimi
    predictor = AdvancedDiseasePredictor()
    results = predictor.train_complete_system("enhanced_hastalik_veriseti.csv")
    
    # Modeli kaydet
    predictor.save_model("advanced_disease_model.pkl")
    
    print("\n🎉 Sistem eğitimi tamamlandı!")
    print(f"🏆 En iyi performans: {results['test_accuracy']:.4f}")
