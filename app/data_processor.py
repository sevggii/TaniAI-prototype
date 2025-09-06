import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple
import logging
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class NHANESDataProcessor:
    """NHANES verilerini işleyen sınıf"""
    
    def __init__(self, data_path: str = "veri/"):
        self.data_path = Path(data_path)
        self.demographic_data = None
        self.examination_data = None
        self.diet_data = None
        self.questionnaire_data = None
        self.medications_data = None
        self.labs_data = None
        self.merged_data = None
        
        # Vitamin/mineral eksikliği eşikleri (NHANES standartları)
        self.deficiency_thresholds = {
            'Vitamin_D': 20,  # ng/mL
            'Vitamin_B12': 200,  # pg/mL
            'Folate': 4,  # ng/mL
            'Iron': 60,  # μg/dL
            'Zinc': 70,  # μg/dL
            'Magnesium': 1.8,  # mg/dL
            'Calcium': 8.5,  # mg/dL
            'Potassium': 3.5,  # mEq/L
            'Selenium': 70,  # μg/L
            'Vitamin_A': 20,  # μg/dL
            'Vitamin_C': 0.2,  # mg/dL
            'Vitamin_E': 5,  # mg/L
        }
    
    def load_all_data(self) -> bool:
        """Tüm CSV dosyalarını yükle"""
        try:
            logger.info("NHANES verileri yukleniyor...")
            
            # Demografik veriler
            self.demographic_data = pd.read_csv(self.data_path / "demographic.csv")
            logger.info(f"OK Demografik veriler: {len(self.demographic_data)} kayit")
            
            # Fiziksel muayene verileri
            self.examination_data = pd.read_csv(self.data_path / "examination.csv")
            logger.info(f"OK Muayene verileri: {len(self.examination_data)} kayit")
            
            # Beslenme verileri
            self.diet_data = pd.read_csv(self.data_path / "diet.csv")
            logger.info(f"OK Beslenme verileri: {len(self.diet_data)} kayit")
            
            # Anket verileri
            self.questionnaire_data = pd.read_csv(self.data_path / "questionnaire.csv")
            logger.info(f"OK Anket verileri: {len(self.questionnaire_data)} kayit")
            
            # İlaç verileri
            self.medications_data = pd.read_csv(self.data_path / "medications.csv", encoding='latin-1')
            logger.info(f"OK Ilac verileri: {len(self.medications_data)} kayit")
            
            # Laboratuvar verileri
            self.labs_data = pd.read_csv(self.data_path / "labs.csv", encoding='latin-1')
            logger.info(f"OK Laboratuvar verileri: {len(self.labs_data)} kayit")
            
            return True
            
        except Exception as e:
            logger.error(f"HATA: Veri yukleme hatasi: {str(e)}")
            return False
    
    def merge_all_data(self) -> pd.DataFrame:
        """Tüm veri setlerini SEQN ile birleştir"""
        try:
            logger.info("Veri setleri birlestiriliyor...")
            
            # SEQN ile tüm verileri birleştir
            merged = self.demographic_data.copy()
            
            # Fiziksel muayene verilerini ekle
            merged = merged.merge(
                self.examination_data, 
                on='SEQN', 
                how='left', 
                suffixes=('', '_exam')
            )
            
            # Beslenme verilerini ekle
            merged = merged.merge(
                self.diet_data, 
                on='SEQN', 
                how='left', 
                suffixes=('', '_diet')
            )
            
            # Anket verilerini ekle
            merged = merged.merge(
                self.questionnaire_data, 
                on='SEQN', 
                how='left', 
                suffixes=('', '_quest')
            )
            
            # İlaç verilerini ekle
            merged = merged.merge(
                self.medications_data, 
                on='SEQN', 
                how='left', 
                suffixes=('', '_med')
            )
            
            # Laboratuvar verilerini ekle
            merged = merged.merge(
                self.labs_data, 
                on='SEQN', 
                how='left', 
                suffixes=('', '_lab')
            )
            
            self.merged_data = merged
            logger.info(f"OK Birlestirilmis veri: {len(merged)} kayit, {len(merged.columns)} sutun")
            
            return merged
            
        except Exception as e:
            logger.error(f"HATA: Veri birlestirme hatasi: {str(e)}")
            return pd.DataFrame()
    
    def create_vitamin_deficiency_labels(self) -> pd.DataFrame:
        """Vitamin/mineral eksikliği etiketleri oluştur"""
        try:
            logger.info("🏷️ Vitamin eksikliği etiketleri oluşturuluyor...")
            
            if self.merged_data is None:
                logger.error("❌ Veri birleştirilmemiş")
                return pd.DataFrame()
            
            df = self.merged_data.copy()
            
            # Laboratuvar değerlerinden eksiklik etiketleri oluştur
            deficiency_columns = {}
            
            # Vitamin D eksikliği (LBXVIDMS - ng/mL)
            if 'LBXVIDMS' in df.columns:
                df['vitamin_d_deficiency'] = (df['LBXVIDMS'] < self.deficiency_thresholds['Vitamin_D']).astype(int)
                deficiency_columns['vitamin_d_deficiency'] = 'LBXVIDMS'
            
            # Vitamin B12 eksikliği (LBXB12 - pg/mL)
            if 'LBXB12' in df.columns:
                df['vitamin_b12_deficiency'] = (df['LBXB12'] < self.deficiency_thresholds['Vitamin_B12']).astype(int)
                deficiency_columns['vitamin_b12_deficiency'] = 'LBXB12'
            
            # Folat eksikliği (LBXFOL - ng/mL)
            if 'LBXFOL' in df.columns:
                df['folate_deficiency'] = (df['LBXFOL'] < self.deficiency_thresholds['Folate']).astype(int)
                deficiency_columns['folate_deficiency'] = 'LBXFOL'
            
            # Demir eksikliği (LBXFER - μg/dL)
            if 'LBXFER' in df.columns:
                df['iron_deficiency'] = (df['LBXFER'] < self.deficiency_thresholds['Iron']).astype(int)
                deficiency_columns['iron_deficiency'] = 'LBXFER'
            
            # Çinko eksikliği (LBXZNS - μg/dL)
            if 'LBXZNS' in df.columns:
                df['zinc_deficiency'] = (df['LBXZNS'] < self.deficiency_thresholds['Zinc']).astype(int)
                deficiency_columns['zinc_deficiency'] = 'LBXZNS'
            
            # Magnezyum eksikliği (LBXMGSI - mg/dL)
            if 'LBXMGSI' in df.columns:
                df['magnesium_deficiency'] = (df['LBXMGSI'] < self.deficiency_thresholds['Magnesium']).astype(int)
                deficiency_columns['magnesium_deficiency'] = 'LBXMGSI'
            
            # Kalsiyum eksikliği (LBXSCA - mg/dL)
            if 'LBXSCA' in df.columns:
                df['calcium_deficiency'] = (df['LBXSCA'] < self.deficiency_thresholds['Calcium']).astype(int)
                deficiency_columns['calcium_deficiency'] = 'LBXSCA'
            
            # Potasyum eksikliği (LBXSKSI - mEq/L)
            if 'LBXSKSI' in df.columns:
                df['potassium_deficiency'] = (df['LBXSKSI'] < self.deficiency_thresholds['Potassium']).astype(int)
                deficiency_columns['potassium_deficiency'] = 'LBXSKSI'
            
            # Selenyum eksikliği (LBXSNASI - μg/L)
            if 'LBXSNASI' in df.columns:
                df['selenium_deficiency'] = (df['LBXSNASI'] < self.deficiency_thresholds['Selenium']).astype(int)
                deficiency_columns['selenium_deficiency'] = 'LBXSNASI'
            
            # Vitamin A eksikliği (LBXRET - μg/dL)
            if 'LBXRET' in df.columns:
                df['vitamin_a_deficiency'] = (df['LBXRET'] < self.deficiency_thresholds['Vitamin_A']).astype(int)
                deficiency_columns['vitamin_a_deficiency'] = 'LBXRET'
            
            # Vitamin C eksikliği (LBXSCA - mg/dL)
            if 'LBXSCA' in df.columns:
                df['vitamin_c_deficiency'] = (df['LBXSCA'] < self.deficiency_thresholds['Vitamin_C']).astype(int)
                deficiency_columns['vitamin_c_deficiency'] = 'LBXSCA'
            
            logger.info(f"✅ {len(deficiency_columns)} vitamin/mineral eksikliği etiketi oluşturuldu")
            
            # Eksiklik sütunlarını kaydet
            self.deficiency_columns = deficiency_columns
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Eksiklik etiketi oluşturma hatası: {str(e)}")
            return pd.DataFrame()
    
    def create_symptom_features(self) -> pd.DataFrame:
        """Belirti özellikleri oluştur"""
        try:
            logger.info("🔍 Belirti özellikleri oluşturuluyor...")
            
            if self.merged_data is None:
                logger.error("❌ Veri birleştirilmemiş")
                return pd.DataFrame()
            
            df = self.merged_data.copy()
            
            # Belirti özellikleri oluştur
            symptom_features = {}
            
            # Yorgunluk belirtileri (anemi, düşük enerji)
            if 'LBXHGB' in df.columns:  # Hemoglobin
                df['fatigue_symptom'] = (df['LBXHGB'] < 12).astype(int)  # Kadınlar için <12, erkekler için <13
                symptom_features['fatigue_symptom'] = 'LBXHGB'
            
            # Kas güçsüzlüğü (düşük potasyum, magnezyum)
            if 'LBXSKSI' in df.columns and 'LBXMGSI' in df.columns:
                df['muscle_weakness'] = ((df['LBXSKSI'] < 3.5) | (df['LBXMGSI'] < 1.8)).astype(int)
                symptom_features['muscle_weakness'] = ['LBXSKSI', 'LBXMGSI']
            
            # Kemik ağrısı (düşük D vitamini, kalsiyum)
            if 'LBXVIDMS' in df.columns and 'LBXSCA' in df.columns:
                df['bone_pain'] = ((df['LBXVIDMS'] < 20) | (df['LBXSCA'] < 8.5)).astype(int)
                symptom_features['bone_pain'] = ['LBXVIDMS', 'LBXSCA']
            
            # Saç dökülmesi (düşük demir, çinko)
            if 'LBXFER' in df.columns and 'LBXZNS' in df.columns:
                df['hair_loss'] = ((df['LBXFER'] < 60) | (df['LBXZNS'] < 70)).astype(int)
                symptom_features['hair_loss'] = ['LBXFER', 'LBXZNS']
            
            # Depresyon (düşük B12, folat)
            if 'LBXB12' in df.columns and 'LBXFOL' in df.columns:
                df['depression_symptom'] = ((df['LBXB12'] < 200) | (df['LBXFOL'] < 4)).astype(int)
                symptom_features['depression_symptom'] = ['LBXB12', 'LBXFOL']
            
            # Enfeksiyon yatkınlığı (düşük çinko, C vitamini)
            if 'LBXZNS' in df.columns and 'LBXSCA' in df.columns:
                df['infection_prone'] = ((df['LBXZNS'] < 70) | (df['LBXSCA'] < 0.2)).astype(int)
                symptom_features['infection_prone'] = ['LBXZNS', 'LBXSCA']
            
            # Hafıza sorunları (düşük B12)
            if 'LBXB12' in df.columns:
                df['memory_problems'] = (df['LBXB12'] < 200).astype(int)
                symptom_features['memory_problems'] = 'LBXB12'
            
            # Uyuşma/karıncalanma (düşük B12, magnezyum)
            if 'LBXB12' in df.columns and 'LBXMGSI' in df.columns:
                df['numbness_tingling'] = ((df['LBXB12'] < 200) | (df['LBXMGSI'] < 1.8)).astype(int)
                symptom_features['numbness_tingling'] = ['LBXB12', 'LBXMGSI']
            
            # Kalp çarpıntısı (düşük potasyum, magnezyum)
            if 'LBXSKSI' in df.columns and 'LBXMGSI' in df.columns:
                df['heart_palpitations'] = ((df['LBXSKSI'] < 3.5) | (df['LBXMGSI'] < 1.8)).astype(int)
                symptom_features['heart_palpitations'] = ['LBXSKSI', 'LBXMGSI']
            
            # Baş ağrısı (düşük magnezyum, demir)
            if 'LBXMGSI' in df.columns and 'LBXFER' in df.columns:
                df['headache'] = ((df['LBXMGSI'] < 1.8) | (df['LBXFER'] < 60)).astype(int)
                symptom_features['headache'] = ['LBXMGSI', 'LBXFER']
            
            logger.info(f"✅ {len(symptom_features)} belirti özelliği oluşturuldu")
            
            # Belirti özelliklerini kaydet
            self.symptom_features = symptom_features
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Belirti özelliği oluşturma hatası: {str(e)}")
            return pd.DataFrame()
    
    def create_demographic_features(self) -> pd.DataFrame:
        """Demografik özellikler oluştur"""
        try:
            logger.info("👥 Demografik özellikler oluşturuluyor...")
            
            if self.merged_data is None:
                logger.error("❌ Veri birleştirilmemiş")
                return pd.DataFrame()
            
            df = self.merged_data.copy()
            
            # Yaş grupları
            if 'RIDAGEYR' in df.columns:
                df['age_group'] = pd.cut(
                    df['RIDAGEYR'], 
                    bins=[0, 18, 35, 50, 65, 100], 
                    labels=['child', 'young_adult', 'middle_aged', 'senior', 'elderly']
                )
            
            # Cinsiyet
            if 'RIAGENDR' in df.columns:
                df['gender'] = df['RIAGENDR'].map({1: 'male', 2: 'female'})
            
            # Eğitim seviyesi
            if 'DMDEDUC2' in df.columns:
                df['education_level'] = df['DMDEDUC2'].map({
                    1: 'less_than_9th',
                    2: '9_11th_grade', 
                    3: 'high_school',
                    4: 'some_college',
                    5: 'college_graduate'
                })
            
            # Gelir seviyesi
            if 'INDFMPIR' in df.columns:
                df['income_level'] = pd.cut(
                    df['INDFMPIR'], 
                    bins=[0, 1, 2, 3, 5], 
                    labels=['low', 'low_middle', 'middle', 'high']
                )
            
            # BMI kategorileri
            if 'BMXBMI' in df.columns:
                df['bmi_category'] = pd.cut(
                    df['BMXBMI'], 
                    bins=[0, 18.5, 25, 30, 100], 
                    labels=['underweight', 'normal', 'overweight', 'obese']
                )
            
            # Kan basıncı kategorileri
            if 'BPXSY1' in df.columns and 'BPXDI1' in df.columns:
                df['bp_category'] = 'normal'
                df.loc[(df['BPXSY1'] >= 140) | (df['BPXDI1'] >= 90), 'bp_category'] = 'high'
                df.loc[(df['BPXSY1'] < 90) & (df['BPXDI1'] < 60), 'bp_category'] = 'low'
            
            logger.info("✅ Demografik özellikler oluşturuldu")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Demografik özellik oluşturma hatası: {str(e)}")
            return pd.DataFrame()
    
    def create_diet_features(self) -> pd.DataFrame:
        """Beslenme özellikleri oluştur"""
        try:
            logger.info("🍎 Beslenme özellikleri oluşturuluyor...")
            
            if self.merged_data is None:
                logger.error("❌ Veri birleştirilmemiş")
                return pd.DataFrame()
            
            df = self.merged_data.copy()
            
            # Günlük kalori alımı kategorileri
            if 'DR1TKCAL' in df.columns:
                df['calorie_intake'] = pd.cut(
                    df['DR1TKCAL'], 
                    bins=[0, 1200, 1800, 2500, 10000], 
                    labels=['low', 'moderate', 'high', 'very_high']
                )
            
            # Protein alımı
            if 'DR1TPROT' in df.columns:
                df['protein_intake'] = pd.cut(
                    df['DR1TPROT'], 
                    bins=[0, 50, 80, 120, 1000], 
                    labels=['low', 'moderate', 'high', 'very_high']
                )
            
            # Vitamin alımı kategorileri
            vitamin_columns = {
                'DR1TVD': 'vitamin_d_intake',
                'DR1TVB12': 'vitamin_b12_intake', 
                'DR1TFOLA': 'folate_intake',
                'DR1TIRON': 'iron_intake',
                'DR1TZINC': 'zinc_intake',
                'DR1TMAGN': 'magnesium_intake',
                'DR1TCALC': 'calcium_intake',
                'DR1TPOTA': 'potassium_intake',
                'DR1TSELE': 'selenium_intake',
                'DR1TRET': 'vitamin_a_intake',
                'DR1TVC': 'vitamin_c_intake',
                'DR1TVE': 'vitamin_e_intake'
            }
            
            for col, new_col in vitamin_columns.items():
                if col in df.columns:
                    # Her vitamin için düşük/orta/yüksek kategorileri
                    df[new_col] = pd.cut(
                        df[col], 
                        bins=[0, df[col].quantile(0.33), df[col].quantile(0.67), df[col].max()], 
                        labels=['low', 'moderate', 'high']
                    )
            
            logger.info("✅ Beslenme özellikleri oluşturuldu")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Beslenme özelliği oluşturma hatası: {str(e)}")
            return pd.DataFrame()
    
    def prepare_training_data(self) -> pd.DataFrame:
        """Eğitim için veri hazırla"""
        try:
            logger.info("🎯 Eğitim verisi hazırlanıyor...")
            
            # Tüm verileri yükle ve birleştir
            if not self.load_all_data():
                return pd.DataFrame()
            
            # Verileri birleştir
            df = self.merge_all_data()
            if df.empty:
                return pd.DataFrame()
            
            # Eksiklik etiketleri oluştur
            df = self.create_vitamin_deficiency_labels()
            if df.empty:
                return pd.DataFrame()
            
            # Belirti özellikleri oluştur
            df = self.create_symptom_features()
            if df.empty:
                return pd.DataFrame()
            
            # Demografik özellikler oluştur
            df = self.create_demographic_features()
            if df.empty:
                return pd.DataFrame()
            
            # Beslenme özellikleri oluştur
            df = self.create_diet_features()
            if df.empty:
                return pd.DataFrame()
            
            # Eksik değerleri temizle
            df = df.dropna(subset=['RIDAGEYR', 'RIAGENDR'])
            
            logger.info(f"✅ Eğitim verisi hazırlandı: {len(df)} kayıt")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Eğitim verisi hazırlama hatası: {str(e)}")
            return pd.DataFrame()
    
    def get_feature_columns(self) -> Dict[str, List[str]]:
        """Özellik sütunlarını döndür"""
        return {
            'demographic': ['RIDAGEYR', 'RIAGENDR', 'DMDEDUC2', 'INDFMPIR', 'BMXBMI', 'BPXSY1', 'BPXDI1'],
            'symptoms': list(self.symptom_features.keys()) if hasattr(self, 'symptom_features') else [],
            'diet': ['DR1TKCAL', 'DR1TPROT', 'DR1TVD', 'DR1TVB12', 'DR1TFOLA', 'DR1TIRON', 'DR1TZINC', 'DR1TMAGN', 'DR1TCALC', 'DR1TPOTA', 'DR1TSELE', 'DR1TRET', 'DR1TVC', 'DR1TVE'],
            'deficiency_labels': list(self.deficiency_columns.keys()) if hasattr(self, 'deficiency_columns') else []
        }
    
    def save_processed_data(self, output_path: str = "processed_data.csv"):
        """İşlenmiş veriyi kaydet"""
        try:
            if self.merged_data is not None:
                self.merged_data.to_csv(output_path, index=False)
                logger.info(f"✅ İşlenmiş veri kaydedildi: {output_path}")
                return True
            else:
                logger.error("❌ İşlenmiş veri bulunamadı")
                return False
        except Exception as e:
            logger.error(f"❌ Veri kaydetme hatası: {str(e)}")
            return False
