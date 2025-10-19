import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os
import logging
from typing import Dict, List, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

from .data_processor import NHANESDataProcessor

logger = logging.getLogger(__name__)

class RealDataVitaminModel:
    """Gerçek NHANES verileriyle eğitilmiş vitamin eksikliği modeli"""
    
    def __init__(self, nutrient_name: str, data_processor: NHANESDataProcessor):
        self.nutrient_name = nutrient_name
        self.data_processor = data_processor
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.model_performance = {}
        
        # Nutrient'e özgü semptomlar
        self.nutrient_symptoms = {
            'vitamin_d': ['fatigue_symptom', 'bone_pain', 'muscle_weakness', 'depression_symptom'],
            'vitamin_b12': ['fatigue_symptom', 'memory_problems', 'numbness_tingling', 'depression_symptom'],
            'folate': ['fatigue_symptom', 'memory_problems', 'depression_symptom'],
            'iron': ['fatigue_symptom', 'hair_loss', 'headache'],
            'zinc': ['hair_loss', 'infection_prone'],
            'magnesium': ['muscle_weakness', 'heart_palpitations', 'headache', 'numbness_tingling'],
            'calcium': ['bone_pain', 'muscle_weakness'],
            'potassium': ['muscle_weakness', 'heart_palpitations'],
            'selenium': ['fatigue_symptom', 'infection_prone'],
            'vitamin_a': ['infection_prone'],
            'vitamin_c': ['infection_prone', 'fatigue_symptom'],
            'vitamin_e': ['muscle_weakness', 'fatigue_symptom']
        }
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Özellikleri hazırla"""
        try:
            # Demografik özellikler
            demographic_features = ['RIDAGEYR', 'RIAGENDR', 'DMDEDUC2', 'INDFMPIR', 'BMXBMI']
            demographic_data = df[demographic_features].copy()
            
            # Belirti özellikleri
            symptom_features = self.nutrient_symptoms.get(self.nutrient_name, [])
            symptom_data = df[symptom_features].copy() if symptom_features else pd.DataFrame()
            
            # Beslenme özellikleri
            diet_features = [col for col in df.columns if col.startswith('DR1T') and col in df.columns]
            diet_data = df[diet_features].copy() if diet_features else pd.DataFrame()
            
            # Tüm özellikleri birleştir
            feature_data = pd.concat([demographic_data, symptom_data, diet_data], axis=1)
            
            # Eksik değerleri doldur
            feature_data = feature_data.fillna(feature_data.median())
            
            # Kategorik değişkenleri encode et
            for col in feature_data.select_dtypes(include=['object']).columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    feature_data[col] = self.label_encoders[col].fit_transform(feature_data[col].astype(str))
                else:
                    feature_data[col] = self.label_encoders[col].transform(feature_data[col].astype(str))
            
            # Hedef değişken
            target_column = f'{self.nutrient_name}_deficiency'
            if target_column not in df.columns:
                logger.error(f"❌ Hedef sütun bulunamadı: {target_column}")
                return pd.DataFrame(), pd.Series()
            
            target_data = df[target_column].copy()
            
            # Eksik değerleri olan satırları kaldır
            valid_indices = ~(feature_data.isnull().any(axis=1) | target_data.isnull())
            feature_data = feature_data[valid_indices]
            target_data = target_data[valid_indices]
            
            self.feature_columns = feature_data.columns.tolist()
            
            logger.info(f"✅ {self.nutrient_name} için {len(feature_data)} kayıt, {len(feature_data.columns)} özellik hazırlandı")
            
            return feature_data, target_data
            
        except Exception as e:
            logger.error(f"❌ Özellik hazırlama hatası: {str(e)}")
            return pd.DataFrame(), pd.Series()
    
    def train_model(self, df: pd.DataFrame) -> float:
        """Modeli eğit"""
        try:
            logger.info(f"🔄 {self.nutrient_name} modeli eğitiliyor...")
            
            # Özellikleri hazırla
            X, y = self.prepare_features(df)
            if X.empty or y.empty:
                logger.error(f"❌ {self.nutrient_name} için veri hazırlanamadı")
                return 0.0
            
            # Eğitim ve test setlerine ayır
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Özellikleri ölçeklendir
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Model oluştur ve eğit
            self.model = GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=6,
                random_state=42
            )
            
            # Cross-validation
            cv_scores = cross_val_score(
                self.model, X_train_scaled, y_train, 
                cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
                scoring='roc_auc'
            )
            
            # Modeli eğit
            self.model.fit(X_train_scaled, y_train)
            
            # Test performansı
            y_pred = self.model.predict(X_test_scaled)
            y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
            
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
                'classification_report': class_report,
                'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
            }
            
            logger.info(f"✅ {self.nutrient_name} modeli eğitildi")
            logger.info(f"   - Doğruluk: {accuracy:.3f}")
            logger.info(f"   - AUC: {auc_score:.3f}")
            logger.info(f"   - CV Ortalama: {cv_scores.mean():.3f} (±{cv_scores.std():.3f})")
            
            return accuracy
            
        except Exception as e:
            logger.error(f"❌ {self.nutrient_name} model eğitimi hatası: {str(e)}")
            return 0.0
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Tahmin yap"""
        try:
            if self.model is None:
                logger.error(f"❌ {self.nutrient_name} modeli eğitilmemiş")
                return {}
            
            # Özellikleri hazırla
            feature_vector = []
            for col in self.feature_columns:
                value = features.get(col, 0)
                feature_vector.append(value)
            
            # Ölçeklendir
            feature_array = np.array(feature_vector).reshape(1, -1)
            feature_scaled = self.scaler.transform(feature_array)
            
            # Tahmin yap
            probability = self.model.predict_proba(feature_scaled)[0]
            prediction = self.model.predict(feature_scaled)[0]
            
            # Risk seviyesi belirle
            risk_level = "Düşük"
            if probability[1] > 0.75:
                risk_level = "Yüksek"
            elif probability[1] > 0.50:
                risk_level = "Orta"
            elif probability[1] > 0.30:
                risk_level = "Düşük Risk"
            
            return {
                'nutrient': self.nutrient_name,
                'deficiency_probability': float(probability[1]),
                'prediction': int(prediction),
                'risk_level': risk_level,
                'confidence': float(max(probability))
            }
            
        except Exception as e:
            logger.error(f"❌ {self.nutrient_name} tahmin hatası: {str(e)}")
            return {}
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Özellik önemini döndür"""
        if hasattr(self, 'model_performance') and 'feature_importance' in self.model_performance:
            return self.model_performance['feature_importance']
        return {}
    
    def save_model(self, filepath: str = None):
        """Modeli kaydet"""
        try:
            if filepath is None:
                filepath = f"models/real_data_{self.nutrient_name}_model.pkl"
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_columns': self.feature_columns,
                'model_performance': self.model_performance,
                'nutrient_name': self.nutrient_name
            }
            
            joblib.dump(model_data, filepath)
            logger.info(f"✅ {self.nutrient_name} modeli kaydedildi: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ {self.nutrient_name} model kaydetme hatası: {str(e)}")
    
    def load_model(self, filepath: str = None):
        """Modeli yükle"""
        try:
            if filepath is None:
                filepath = f"models/real_data_{self.nutrient_name}_model.pkl"
            
            if os.path.exists(filepath):
                model_data = joblib.load(filepath)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                self.feature_columns = model_data['feature_columns']
                self.model_performance = model_data['model_performance']
                logger.info(f"✅ {self.nutrient_name} modeli yüklendi: {filepath}")
                return True
            else:
                logger.warning(f"⚠️ {self.nutrient_name} modeli bulunamadı: {filepath}")
                return False
                
        except Exception as e:
            logger.error(f"❌ {self.nutrient_name} model yükleme hatası: {str(e)}")
            return False

class RealDataModelTrainer:
    """Gerçek verilerle model eğitici"""
    
    def __init__(self, data_path: str = "veri/"):
        self.data_processor = NHANESDataProcessor(data_path)
        self.models = {}
        self.available_nutrients = [
            'vitamin_d', 'vitamin_b12', 'folate', 'iron', 'zinc', 
            'magnesium', 'calcium', 'potassium', 'selenium',
            'vitamin_a', 'vitamin_c', 'vitamin_e'
        ]
    
    def train_all_models(self) -> Dict[str, float]:
        """Tüm modelleri eğit"""
        try:
            logger.info("🚀 Tüm modeller eğitiliyor...")
            
            # Veriyi hazırla
            df = self.data_processor.prepare_training_data()
            if df.empty:
                logger.error("❌ Eğitim verisi hazırlanamadı")
                return {}
            
            results = {}
            
            # Her nutrient için model eğit
            for nutrient in self.available_nutrients:
                try:
                    model = RealDataVitaminModel(nutrient, self.data_processor)
                    accuracy = model.train_model(df)
                    
                    if accuracy > 0:
                        self.models[nutrient] = model
                        results[nutrient] = accuracy
                        model.save_model()
                        logger.info(f"✅ {nutrient} modeli eğitildi (Doğruluk: {accuracy:.3f})")
                    else:
                        logger.warning(f"⚠️ {nutrient} modeli eğitilemedi")
                        
                except Exception as e:
                    logger.error(f"❌ {nutrient} model eğitimi hatası: {str(e)}")
                    continue
            
            logger.info(f"✅ {len(results)} model başarıyla eğitildi")
            return results
            
        except Exception as e:
            logger.error(f"❌ Model eğitimi hatası: {str(e)}")
            return {}
    
    def load_all_models(self) -> bool:
        """Tüm modelleri yükle"""
        try:
            logger.info("📂 Modeller yükleniyor...")
            
            loaded_count = 0
            for nutrient in self.available_nutrients:
                model = RealDataVitaminModel(nutrient, self.data_processor)
                if model.load_model():
                    self.models[nutrient] = model
                    loaded_count += 1
            
            logger.info(f"✅ {loaded_count}/{len(self.available_nutrients)} model yüklendi")
            return loaded_count > 0
            
        except Exception as e:
            logger.error(f"❌ Model yükleme hatası: {str(e)}")
            return False
    
    def predict_deficiency(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Eksiklik tahmini yap"""
        try:
            results = {}
            
            for nutrient, model in self.models.items():
                try:
                    result = model.predict(features)
                    if result:
                        results[nutrient] = result
                except Exception as e:
                    logger.error(f"❌ {nutrient} tahmin hatası: {str(e)}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Tahmin hatası: {str(e)}")
            return {}
    
    def get_model_performance(self) -> Dict[str, Dict[str, Any]]:
        """Model performanslarını döndür"""
        performance = {}
        
        for nutrient, model in self.models.items():
            if hasattr(model, 'model_performance'):
                performance[nutrient] = model.model_performance
        
        return performance
    
    def get_feature_importance(self) -> Dict[str, Dict[str, float]]:
        """Özellik önemlerini döndür"""
        importance = {}
        
        for nutrient, model in self.models.items():
            importance[nutrient] = model.get_feature_importance()
        
        return importance
