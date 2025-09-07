from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import logging
from sqlalchemy.orm import Session

from .models.nutrient_models import NutrientDeficiencyModel
from .real_data_models import RealDataModelTrainer
from .models import User, UserProfile, DiagnosisHistory, Notification
from .schemas import (
    DiagnosisResult, RiskAssessment, NutritionRecommendations,
    UserProfileCreate, SymptomInput
)

logger = logging.getLogger(__name__)

class VitaminDiagnosisService:
    """Vitamin eksikliği teşhis servisi"""
    
    def __init__(self):
        self.nutrient_models = {}
        self.real_data_trainer = None
        self.use_real_data = True  # Gerçek veri kullanımını etkinleştir
        
        # Gerçek veri modelleri
        self.available_nutrients = [
            'vitamin_d', 'vitamin_b12', 'folate', 'iron', 'zinc', 
            'magnesium', 'calcium', 'potassium', 'selenium',
            'vitamin_a', 'vitamin_c', 'vitamin_e'
        ]
        
        # Eski sentetik modeller (yedek)
        self.synthetic_nutrients = [
            'D', 'B12', 'Demir', 'Cinko', 'Magnezyum', 'A', 'C', 'E', 'B9',
            'Kalsiyum', 'Potasyum', 'Selenyum', 'HepatitB', 'Gebelik', 'Tiroid'
        ]
        
        self._initialize_models()
    
    def _initialize_models(self):
        """Nutrient modellerini başlat"""
        try:
            if self.use_real_data:
                # Gerçek veri modellerini yükle
                self.real_data_trainer = RealDataModelTrainer("veri/")
                if self.real_data_trainer.load_all_models():
                    logger.info("✅ Gerçek veri modelleri yüklendi")
                else:
                    logger.warning("⚠️ Gerçek veri modelleri yüklenemedi, sentetik modellere geçiliyor")
                    self.use_real_data = False
            
            if not self.use_real_data:
                # Sentetik modelleri yükle (yedek)
                for nutrient in self.synthetic_nutrients:
                    try:
                        model = NutrientDeficiencyModel(nutrient)
                        model.load_model()
                        self.nutrient_models[nutrient] = model
                        logger.info(f"✅ {nutrient} sentetik modeli yüklendi")
                    except Exception as e:
                        logger.error(f"❌ {nutrient} sentetik modeli yüklenemedi: {str(e)}")
                        
        except Exception as e:
            logger.error(f"❌ Model başlatma hatası: {str(e)}")
    
    async def analyze_symptoms(
        self, 
        symptoms: List[SymptomInput], 
        user_profile: Optional[UserProfileCreate] = None
    ) -> Dict[str, Any]:
        """Belirtilere göre kapsamlı analiz yap"""
        try:
            if self.use_real_data and self.real_data_trainer:
                # Gerçek veri modelleri ile analiz
                return await self._analyze_with_real_data(symptoms, user_profile)
            else:
                # Sentetik modeller ile analiz
                return await self._analyze_with_synthetic_data(symptoms, user_profile)
                
        except Exception as e:
            logger.error(f"Semptom analizi başarısız: {str(e)}")
            raise
    
    async def _analyze_with_real_data(
        self, 
        symptoms: List[SymptomInput], 
        user_profile: Optional[UserProfileCreate] = None
    ) -> Dict[str, Any]:
        """Gerçek veri modelleri ile analiz"""
        try:
            # Belirtileri ve kullanıcı profilini özellik formatına çevir
            features = self._convert_to_real_data_features(symptoms, user_profile)
            
            # Tüm nutrient'ler için tahmin yap
            all_results = self.real_data_trainer.predict_deficiency(features)
            
            # En yüksek riskli nutrient'i bul
            highest_risk = self._find_highest_risk_real_data(all_results)
            
            # Klinik uyarıları oluştur
            clinical_warnings = self._generate_clinical_warnings(highest_risk, user_profile)
            
            return {
                'primary_diagnosis': highest_risk,
                'all_results': all_results,
                'clinical_warnings': clinical_warnings,
                'analysis_timestamp': datetime.now().isoformat(),
                'model_type': 'real_data'
            }
            
        except Exception as e:
            logger.error(f"Gerçek veri analizi başarısız: {str(e)}")
            raise
    
    async def _analyze_with_synthetic_data(
        self, 
        symptoms: List[SymptomInput], 
        user_profile: Optional[UserProfileCreate] = None
    ) -> Dict[str, Any]:
        """Sentetik modeller ile analiz"""
        try:
            # Belirtileri dictionary formatına çevir
            symptoms_dict = {s.symptom_name: s.severity for s in symptoms}
            
            # Her nutrient için analiz yap
            all_results = {}
            for nutrient, model in self.nutrient_models.items():
                try:
                    result = model.predict(symptoms_dict)
                    recommendations = model.get_recommendations(result)
                    
                    all_results[nutrient] = {
                        'result': result,
                        'recommendations': recommendations
                    }
                except Exception as e:
                    logger.error(f"{nutrient} analizi başarısız: {str(e)}")
                    continue
            
            # En yüksek riskli nutrient'i bul
            highest_risk = self._find_highest_risk(all_results)
            
            # Klinik uyarıları oluştur
            clinical_warnings = self._generate_clinical_warnings(highest_risk, user_profile)
            
            return {
                'primary_diagnosis': highest_risk,
                'all_results': all_results,
                'clinical_warnings': clinical_warnings,
                'analysis_timestamp': datetime.now().isoformat(),
                'model_type': 'synthetic'
            }
            
        except Exception as e:
            logger.error(f"Sentetik veri analizi başarısız: {str(e)}")
            raise
    
    def _convert_to_real_data_features(
        self, 
        symptoms: List[SymptomInput], 
        user_profile: Optional[UserProfileCreate] = None
    ) -> Dict[str, Any]:
        """Belirtileri ve kullanıcı profilini gerçek veri özellik formatına çevir"""
        features = {}
        
        # Demografik özellikler
        if user_profile:
            features['RIDAGEYR'] = getattr(user_profile, 'age', 30)
            features['RIAGENDR'] = 1 if getattr(user_profile, 'gender', 'male') == 'male' else 2
            features['DMDEDUC2'] = 3  # Varsayılan eğitim seviyesi
            features['INDFMPIR'] = 2.5  # Varsayılan gelir seviyesi
            features['BMXBMI'] = 25.0  # Varsayılan BMI
        
        # Belirti özellikleri
        symptom_mapping = {
            'yorgunluk': 'fatigue_symptom',
            'halsizlik': 'fatigue_symptom',
            'kemik_agrisi': 'bone_pain',
            'kas_agrisi': 'muscle_weakness',
            'kas_guclugu': 'muscle_weakness',
            'depresyon': 'depression_symptom',
            'hafiza_sorunlari': 'memory_problems',
            'unutkanlik': 'memory_problems',
            'uyusma': 'numbness_tingling',
            'karincalanma': 'numbness_tingling',
            'sac_dokulmesi': 'hair_loss',
            'kalp_carpintisi': 'heart_palpitations',
            'bas_agrisi': 'headache',
            'enfeksiyon_yatkinligi': 'infection_prone'
        }
        
        for symptom in symptoms:
            mapped_symptom = symptom_mapping.get(symptom.symptom_name)
            if mapped_symptom:
                features[mapped_symptom] = symptom.severity
        
        # Beslenme özellikleri (varsayılan değerler)
        diet_features = {
            'DR1TKCAL': 2000, 'DR1TPROT': 80, 'DR1TVD': 15, 'DR1TVB12': 300,
            'DR1TFOLA': 400, 'DR1TIRON': 18, 'DR1TZINC': 12, 'DR1TMAGN': 350,
            'DR1TCALC': 1000, 'DR1TPOTA': 3500, 'DR1TSELE': 55, 'DR1TRET': 800,
            'DR1TVC': 90, 'DR1TVE': 15
        }
        
        features.update(diet_features)
        
        return features
    
    def _find_highest_risk_real_data(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """Gerçek veri sonuçlarından en yüksek riskli teşhisi bul"""
        highest_risk = None
        highest_probability = 0.0
        
        for nutrient, result in all_results.items():
            probability = result.get('deficiency_probability', 0.0)
            
            if probability > highest_probability:
                highest_probability = probability
                highest_risk = {
                    'nutrient': nutrient,
                    'deficiency_probability': probability,
                    'risk_level': result.get('risk_level', 'Düşük'),
                    'confidence': result.get('confidence', 0.0),
                    'recommendations': self._get_real_data_recommendations(nutrient, result)
                }
        
        return highest_risk or {
            'nutrient': 'bilinmiyor',
            'deficiency_probability': 0.0,
            'risk_level': 'Düşük',
            'confidence': 0.0,
            'recommendations': {}
        }
    
    def _get_real_data_recommendations(self, nutrient: str, result: Dict[str, Any]) -> Dict[str, List[str]]:
        """Gerçek veri modelleri için öneriler oluştur"""
        recommendations = {
            'immediate_actions': [],
            'dietary_recommendations': [],
            'supplement_recommendations': [],
            'tests_recommended': []
        }
        
        risk_level = result.get('risk_level', 'Düşük')
        
        if risk_level in ["Orta", "Yüksek"]:
            # Nutrient'e özgü öneriler
            nutrient_recommendations = {
                'vitamin_d': {
                    'dietary': ["Güneş ışığından yararlanın", "Yağlı balık tüketin", "D vitamini ile zenginleştirilmiş süt"],
                    'supplement': ["D3 vitamini takviyesi (1000-2000 IU)"],
                    'tests': ["25(OH)D seviyesi", "Kalsiyum seviyesi"]
                },
                'vitamin_b12': {
                    'dietary': ["Et, balık, süt, yumurta tüketin", "Vejetaryenler için B12 takviyeli besinler"],
                    'supplement': ["B12 takviyesi (2.4 mcg/gün)"],
                    'tests': ["Serum B12 seviyesi", "Methylmalonic asit seviyesi"]
                },
                'iron': {
                    'dietary': ["Kırmızı et, karaciğer, ıspanak tüketin", "C vitamini ile birlikte alın"],
                    'supplement': ["Demir takviyesi (18 mg/gün)"],
                    'tests': ["Serum ferritin seviyesi", "Tam kan sayımı"]
                }
            }
            
            if nutrient in nutrient_recommendations:
                rec = nutrient_recommendations[nutrient]
                recommendations['dietary_recommendations'] = rec.get('dietary', [])
                recommendations['supplement_recommendations'] = rec.get('supplement', [])
                recommendations['tests_recommended'] = rec.get('tests', [])
            
            recommendations['immediate_actions'] = [
                "Doktor kontrolüne gidin",
                "Beslenme alışkanlıklarınızı gözden geçirin"
            ]
        
        return recommendations
    
    def _find_highest_risk(self, all_results: Dict[str, Any]) -> Dict[str, Any]:
        """En yüksek riskli teşhisi bul"""
        highest_risk = None
        highest_probability = 0.0
        
        for nutrient, data in all_results.items():
            result = data['result']
            probability = result.get('deficiency_probability', 0.0)
            
            if probability > highest_probability:
                highest_probability = probability
                highest_risk = {
                    'nutrient': nutrient,
                    'deficiency_probability': probability,
                    'risk_level': result.get('risk_level', 'Düşük'),
                    'confidence': result.get('confidence', 0.0),
                    'recommendations': data['recommendations']
                }
        
        return highest_risk or {
            'nutrient': 'Bilinmiyor',
            'deficiency_probability': 0.0,
            'risk_level': 'Düşük',
            'confidence': 0.0,
            'recommendations': {}
        }
    
    def _generate_clinical_warnings(
        self, 
        diagnosis: Dict[str, Any], 
        user_profile: Optional[UserProfileCreate] = None
    ) -> List[str]:
        """Klinik uyarıları oluştur"""
        warnings = [
            "⚠️ Bu sonuçlar ön tanı niteliğindedir ve kesin teşhis değildir.",
            "🏥 Kesin teşhis için mutlaka doktor kontrolü gereklidir.",
            "🧪 Laboratuvar testleri ile doğrulama yapılmalıdır.",
            "🚨 Acil durumlarda derhal tıbbi yardım alın."
        ]
        
        # Risk seviyesine göre ek uyarılar
        risk_level = diagnosis.get('risk_level', 'Düşük')
        if risk_level in ['Yüksek', 'Kritik']:
            warnings.extend([
                "🔴 Yüksek risk tespit edildi - acil doktor kontrolü önerilir.",
                "📞 En kısa sürede sağlık kuruluşuna başvurun.",
                "💊 Kendi kendinize ilaç kullanmayın."
            ])
        
        # Gebelik durumu için özel uyarılar
        if user_profile and user_profile.is_pregnant:
            warnings.extend([
                "🤱 Gebelik durumunuz nedeniyle özel dikkat gereklidir.",
                "👩‍⚕️ Kadın doğum uzmanına danışın.",
                "💊 Gebelik sırasında takviye kullanımı doktor kontrolünde olmalıdır."
            ])
        
        return warnings

class RiskAssessmentService:
    """Risk değerlendirme servisi"""
    
    def __init__(self):
        self.risk_factors = {
            'age': {
                'young': (0, 18, 0.1),
                'adult': (19, 65, 0.3),
                'elderly': (66, 120, 0.6)
            },
            'gender': {
                'female': 0.4,  # Kadınlarda daha yüksek risk
                'male': 0.2,
                'other': 0.3
            },
            'diet': {
                'vegan': 0.7,
                'vegetarian': 0.5,
                'omnivore': 0.2,
                'keto': 0.4
            },
            'lifestyle': {
                'sedentary': 0.5,
                'light': 0.3,
                'moderate': 0.2,
                'active': 0.1,
                'very_active': 0.15
            }
        }
    
    async def assess_risk(
        self, 
        diagnosis_result: Dict[str, Any], 
        user_profile: Optional[UserProfileCreate] = None
    ) -> RiskAssessment:
        """Kapsamlı risk değerlendirmesi"""
        try:
            # Temel risk skorları
            age_risk = self._calculate_age_risk(user_profile)
            gender_risk = self._calculate_gender_risk(user_profile)
            lifestyle_risk = self._calculate_lifestyle_risk(user_profile)
            medical_risk = self._calculate_medical_risk(user_profile)
            
            # Teşhis riski
            diagnosis_risk = diagnosis_result.get('deficiency_probability', 0.0) * 100
            
            # Toplam risk skoru
            total_risk = (age_risk + gender_risk + lifestyle_risk + medical_risk + diagnosis_risk) / 5
            
            # Risk seviyesi belirle
            risk_level = self._determine_risk_level(total_risk)
            
            # Risk faktörleri
            risk_factors = {
                'age_risk': age_risk,
                'gender_risk': gender_risk,
                'lifestyle_risk': lifestyle_risk,
                'medical_risk': medical_risk,
                'diagnosis_risk': diagnosis_risk
            }
            
            # Yaşam tarzı faktörleri
            lifestyle_factors = self._get_lifestyle_factors(user_profile)
            
            # Öneriler
            recommendations = self._generate_risk_recommendations(risk_level, risk_factors)
            urgent_actions = self._generate_urgent_actions(risk_level)
            
            return RiskAssessment(
                overall_risk_level=risk_level,
                risk_score=total_risk,
                risk_factors=risk_factors,
                lifestyle_factors=lifestyle_factors,
                recommendations=recommendations,
                urgent_actions=urgent_actions
            )
            
        except Exception as e:
            logger.error(f"Risk değerlendirmesi başarısız: {str(e)}")
            raise
    
    def _calculate_age_risk(self, user_profile: Optional[UserProfileCreate]) -> float:
        """Yaş riskini hesapla"""
        if not user_profile:
            return 0.3  # Varsayılan risk
        
        age = getattr(user_profile, 'age', 30)  # Varsayılan yaş
        
        for age_group, (min_age, max_age, risk) in self.risk_factors['age'].items():
            if min_age <= age <= max_age:
                return risk * 100
        
        return 0.3 * 100
    
    def _calculate_gender_risk(self, user_profile: Optional[UserProfileCreate]) -> float:
        """Cinsiyet riskini hesapla"""
        if not user_profile:
            return 0.3 * 100
        
        gender = getattr(user_profile, 'gender', 'other')
        return self.risk_factors['gender'].get(gender, 0.3) * 100
    
    def _calculate_lifestyle_risk(self, user_profile: Optional[UserProfileCreate]) -> float:
        """Yaşam tarzı riskini hesapla"""
        if not user_profile:
            return 0.3 * 100
        
        # Diyet riski
        diet_type = getattr(user_profile, 'diet_type', 'omnivore')
        diet_risk = self.risk_factors['diet'].get(diet_type, 0.2) * 100
        
        # Aktivite riski
        activity_level = getattr(user_profile, 'activity_level', 'moderate')
        activity_risk = self.risk_factors['lifestyle'].get(activity_level, 0.2) * 100
        
        return (diet_risk + activity_risk) / 2
    
    def _calculate_medical_risk(self, user_profile: Optional[UserProfileCreate]) -> float:
        """Tıbbi riski hesapla"""
        if not user_profile:
            return 0.2 * 100
        
        medical_conditions = getattr(user_profile, 'medical_conditions', [])
        medications = getattr(user_profile, 'medications', [])
        
        risk = 0.2  # Temel risk
        
        # Tıbbi durumlar riski artırır
        if medical_conditions:
            risk += len(medical_conditions) * 0.1
        
        # İlaç kullanımı riski artırır
        if medications:
            risk += len(medications) * 0.05
        
        return min(risk, 1.0) * 100  # Maksimum %100
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Risk seviyesini belirle"""
        if risk_score >= 80:
            return "Kritik"
        elif risk_score >= 60:
            return "Yüksek"
        elif risk_score >= 40:
            return "Orta"
        else:
            return "Düşük"
    
    def _get_lifestyle_factors(self, user_profile: Optional[UserProfileCreate]) -> Dict[str, Any]:
        """Yaşam tarzı faktörlerini getir"""
        if not user_profile:
            return {}
        
        return {
            'diet_type': getattr(user_profile, 'diet_type', 'omnivore'),
            'activity_level': getattr(user_profile, 'activity_level', 'moderate'),
            'smoking_status': getattr(user_profile, 'smoking_status', 'never'),
            'alcohol_consumption': getattr(user_profile, 'alcohol_consumption', 'none'),
            'medical_conditions': getattr(user_profile, 'medical_conditions', []),
            'medications': getattr(user_profile, 'medications', [])
        }
    
    def _generate_risk_recommendations(self, risk_level: str, risk_factors: Dict[str, float]) -> List[str]:
        """Risk azaltma önerileri oluştur"""
        recommendations = []
        
        if risk_level in ["Orta", "Yüksek", "Kritik"]:
            recommendations.extend([
                "Doktor kontrolüne gidin",
                "Beslenme alışkanlıklarınızı gözden geçirin",
                "Düzenli egzersiz yapın",
                "Stres yönetimi uygulayın"
            ])
        
        if risk_factors.get('lifestyle_risk', 0) > 50:
            recommendations.extend([
                "Yaşam tarzınızı iyileştirin",
                "Daha aktif olun",
                "Sağlıklı beslenme alışkanlıkları edinin"
            ])
        
        if risk_factors.get('medical_risk', 0) > 50:
            recommendations.extend([
                "Mevcut tıbbi durumlarınızı kontrol altında tutun",
                "İlaç kullanımınızı doktorunuzla gözden geçirin"
            ])
        
        return recommendations
    
    def _generate_urgent_actions(self, risk_level: str) -> List[str]:
        """Acil eylemler oluştur"""
        if risk_level == "Kritik":
            return [
                "Derhal tıbbi yardım alın",
                "Acil servise başvurun",
                "Doktorunuzu acil olarak arayın"
            ]
        elif risk_level == "Yüksek":
            return [
                "En kısa sürede doktor kontrolüne gidin",
                "Sağlık kuruluşuna başvurun"
            ]
        else:
            return []

class NutritionRecommendationService:
    """Beslenme öneri servisi"""
    
    def __init__(self):
        self.nutrient_foods = {
            'D': ['somon', 'uskumru', 'ton balığı', 'yumurta sarısı', 'mantar', 'süt', 'peynir'],
            'B12': ['et', 'balık', 'süt', 'yumurta', 'karaciğer', 'böbrek'],
            'Demir': ['kırmızı et', 'karaciğer', 'ıspanak', 'mercimek', 'fasulye', 'kuru üzüm'],
            'Cinko': ['et', 'kabuklu deniz ürünleri', 'fındık', 'tam tahıllar', 'baklagiller'],
            'Magnezyum': ['yeşil yapraklı sebzeler', 'fındık', 'tohumlar', 'tam tahıllar', 'bitter çikolata']
        }
    
    async def get_recommendations(
        self, 
        diagnosis_result: Dict[str, Any], 
        user_profile: Optional[UserProfileCreate] = None
    ) -> NutritionRecommendations:
        """Kişiselleştirilmiş beslenme önerileri"""
        try:
            nutrient = diagnosis_result.get('nutrient', '')
            risk_level = diagnosis_result.get('risk_level', 'Düşük')
            
            # Temel öneriler
            dietary_recommendations = self._get_dietary_recommendations(nutrient, user_profile)
            supplement_recommendations = self._get_supplement_recommendations(nutrient, risk_level)
            meal_plan_suggestions = self._get_meal_plan_suggestions(nutrient, user_profile)
            foods_to_avoid = self._get_foods_to_avoid(nutrient, user_profile)
            foods_to_include = self._get_foods_to_include(nutrient)
            daily_intake_goals = self._get_daily_intake_goals(nutrient)
            
            return NutritionRecommendations(
                dietary_recommendations=dietary_recommendations,
                supplement_recommendations=supplement_recommendations,
                meal_plan_suggestions=meal_plan_suggestions,
                foods_to_avoid=foods_to_avoid,
                foods_to_include=foods_to_include,
                daily_intake_goals=daily_intake_goals
            )
            
        except Exception as e:
            logger.error(f"Beslenme önerileri oluşturulamadı: {str(e)}")
            raise
    
    def _get_dietary_recommendations(self, nutrient: str, user_profile: Optional[UserProfileCreate]) -> List[str]:
        """Diyet önerileri"""
        recommendations = []
        
        if nutrient in self.nutrient_foods:
            foods = self.nutrient_foods[nutrient]
            recommendations.append(f"{nutrient} vitamini açısından zengin besinler tüketin: {', '.join(foods)}")
        
        # Diyet tipine göre öneriler
        if user_profile and user_profile.diet_type:
            if user_profile.diet_type == 'vegan':
                recommendations.append("Vegan diyet için uygun alternatifler araştırın")
            elif user_profile.diet_type == 'vegetarian':
                recommendations.append("Vejetaryen kaynaklardan yararlanın")
        
        return recommendations
    
    def _get_supplement_recommendations(self, nutrient: str, risk_level: str) -> List[str]:
        """Takviye önerileri"""
        recommendations = []
        
        if risk_level in ["Orta", "Yüksek", "Kritik"]:
            recommendations.append(f"{nutrient} takviyesi doktor kontrolünde alınabilir")
            recommendations.append("Takviye kullanmadan önce doktor onayı alın")
        
        return recommendations
    
    def _get_meal_plan_suggestions(self, nutrient: str, user_profile: Optional[UserProfileCreate]) -> List[Dict[str, Any]]:
        """Öğün planı önerileri"""
        suggestions = []
        
        if nutrient in self.nutrient_foods:
            foods = self.nutrient_foods[nutrient]
            suggestions.append({
                'meal': 'Kahvaltı',
                'suggestions': [f"{food} içeren kahvaltı seçenekleri" for food in foods[:2]]
            })
            suggestions.append({
                'meal': 'Öğle Yemeği',
                'suggestions': [f"{food} içeren ana yemek seçenekleri" for food in foods[:2]]
            })
        
        return suggestions
    
    def _get_foods_to_avoid(self, nutrient: str, user_profile: Optional[UserProfileCreate]) -> List[str]:
        """Kaçınılması gereken besinler"""
        avoid_foods = []
        
        if nutrient == 'Demir':
            avoid_foods.extend(['çay', 'kahve', 'süt (yemeklerle birlikte)'])
        
        if user_profile and user_profile.allergies:
            avoid_foods.extend(user_profile.allergies)
        
        return avoid_foods
    
    def _get_foods_to_include(self, nutrient: str) -> List[str]:
        """Tüketilmesi gereken besinler"""
        return self.nutrient_foods.get(nutrient, [])
    
    def _get_daily_intake_goals(self, nutrient: str) -> Dict[str, str]:
        """Günlük alım hedefleri"""
        goals = {
            'D': '15-20 mcg/gün',
            'B12': '2.4 mcg/gün',
            'Demir': '18 mg/gün (kadın), 8 mg/gün (erkek)',
            'Cinko': '8-11 mg/gün',
            'Magnezyum': '300-400 mg/gün'
        }
        
        return {nutrient: goals.get(nutrient, 'Doktor önerisiyle belirlenmelidir')}

class NotificationService:
    """Bildirim servisi"""
    
    def __init__(self):
        self.notification_templates = {
            'reminder': {
                'title': 'Vitamin Takip Hatırlatması',
                'message': 'Vitamin seviyelerinizi kontrol etme zamanı geldi.'
            },
            'urgent': {
                'title': 'Acil Tıbbi Kontrol Gerekli',
                'message': 'Yüksek risk tespit edildi. Derhal doktor kontrolüne gidin.'
            },
            'follow_up': {
                'title': 'Takip Kontrolü',
                'message': 'Önceki teşhisinizin takibi için kontrol zamanı.'
            },
            'tip': {
                'title': 'Sağlık İpucu',
                'message': 'Günlük sağlık ipucu: Düzenli egzersiz yapın.'
            }
        }
    
    async def schedule_notification(
        self, 
        user_id: int, 
        notification_type: str, 
        scheduled_time: datetime, 
        message: str
    ):
        """Bildirim planla"""
        try:
            template = self.notification_templates.get(notification_type, {})
            
            # Veritabanına kaydet (gerçek uygulamada)
            logger.info(f"Bildirim planlandı: User {user_id}, Type: {notification_type}, Time: {scheduled_time}")
            
        except Exception as e:
            logger.error(f"Bildirim planlanamadı: {str(e)}")
            raise
    
    async def schedule_urgent_notification(self, user_id: int, risk_level: str):
        """Acil bildirim planla"""
        try:
            message = f"Yüksek risk seviyesi ({risk_level}) tespit edildi. Acil doktor kontrolü önerilir."
            
            await self.schedule_notification(
                user_id=user_id,
                notification_type='urgent',
                scheduled_time=datetime.now() + timedelta(minutes=5),
                message=message
            )
            
        except Exception as e:
            logger.error(f"Acil bildirim planlanamadı: {str(e)}")
            raise
    
    async def get_user_notifications(self, user_id: int) -> List[Dict[str, Any]]:
        """Kullanıcı bildirimlerini getir"""
        try:
            # Gerçek uygulamada veritabanından çekilecek
            notifications = [
                {
                    'id': 1,
                    'title': 'Vitamin Takip Hatırlatması',
                    'message': 'Vitamin seviyelerinizi kontrol etme zamanı geldi.',
                    'type': 'reminder',
                    'scheduled_time': (datetime.now() + timedelta(hours=24)).isoformat(),
                    'is_sent': False,
                    'is_read': False
                }
            ]
            
            return notifications
            
        except Exception as e:
            logger.error(f"Bildirimler getirilemedi: {str(e)}")
            raise
