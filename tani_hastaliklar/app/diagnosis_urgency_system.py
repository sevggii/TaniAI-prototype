"""
Tanı-Hastalıklar (Vitamin Eksikliği) Aciliyet Sistemi
====================================================

Vitamin ve besin eksikliklerini aciliyet skoruna göre önceliklendirir.
Mevcut risk assessment sistemini genişletir, backward-compatible.

Author: TanıAI Development Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class DiagnosisUrgencyLevel(str, Enum):
    """Tanı aciliyet seviyeleri"""
    CRITICAL = "critical"      # 8-10: Acil tıbbi müdahale (4 saat)
    HIGH = "high"              # 6-8: Yüksek öncelik (24 saat)
    MODERATE = "moderate"      # 4-6: Orta öncelik (1 hafta)
    LOW = "low"                # 1-4: Düşük öncelik (1 ay)


@dataclass
class DiagnosisUrgencyAssessment:
    """Tanı aciliyet değerlendirmesi"""
    urgency_score: float  # 1-10 arası
    urgency_level: DiagnosisUrgencyLevel
    requires_immediate_attention: bool
    response_time: str
    priority_deficiencies: List[Dict[str, Any]]
    risk_factors: Dict[str, float]
    clinical_findings: List[Dict[str, Any]]
    recommendations: List[str]
    doctor_alert_required: bool
    timestamp: datetime


class DiagnosisUrgencySystem:
    """
    Vitamin/besin eksikliği tanıları için aciliyet değerlendirme sistemi.
    
    Mevcut RiskAssessmentService ile entegre çalışır.
    """
    
    def __init__(self):
        # Müdahale süreleri
        self.response_times = {
            DiagnosisUrgencyLevel.CRITICAL: "4 saat içinde",
            DiagnosisUrgencyLevel.HIGH: "24 saat içinde",
            DiagnosisUrgencyLevel.MODERATE: "1 hafta içinde",
            DiagnosisUrgencyLevel.LOW: "1 ay içinde"
        }
        
        # Kritik vitamin/mineral eksiklikleri ve ağırlıkları
        self.critical_deficiencies = {
            # Lebensbedrohlich (hayati tehlike)
            'vitamin_b12': {
                'weight': 0.95,
                'symptoms': ['pernisiyöz anemi', 'nörolojik hasar'],
                'complications': 'Geri dönüşümsüz sinir hasarı'
            },
            'iron': {
                'weight': 0.9,
                'symptoms': ['şiddetli anemi', 'kalp sorunları'],
                'complications': 'Kalp yetmezliği riski'
            },
            'vitamin_d': {
                'weight': 0.75,
                'symptoms': ['osteomalazi', 'kas güçsüzlüğü'],
                'complications': 'Kemik kırılmaları'
            },
            
            # Ciddi (serious)
            'folate': {
                'weight': 0.85,
                'symptoms': ['megaloblastik anemi', 'gebelikte nöral tüp defekti'],
                'complications': 'Doğum defektleri riski'
            },
            'calcium': {
                'weight': 0.7,
                'symptoms': ['osteoporoz', 'tetani'],
                'complications': 'Kemik yoğunluğu kaybı'
            },
            'potassium': {
                'weight': 0.9,
                'symptoms': ['kardiyak aritmiler', 'kas felci'],
                'complications': 'Kalp ritim bozuklukları'
            },
            
            # Orta (moderate)
            'magnesium': {
                'weight': 0.65,
                'symptoms': ['kas krampları', 'kardiyak sorunlar'],
                'complications': 'Elektrolit dengesizliği'
            },
            'zinc': {
                'weight': 0.6,
                'symptoms': ['bağışıklık zayıflığı', 'yara iyileşmesi sorunları'],
                'complications': 'Enfeksiyon riski artışı'
            },
            'vitamin_c': {
                'weight': 0.5,
                'symptoms': ['skorvi', 'yara iyileşmesi sorunları'],
                'complications': 'Doku hasarı'
            },
        }
        
        # Semptom şiddeti ağırlıkları
        self.symptom_severity_weights = {
            'nörolojik': 0.95,        # En ciddi
            'kardiyak': 0.9,
            'hematoljik': 0.85,       # Kan ile ilgili
            'kas_iskelet': 0.7,
            'dermatoljik': 0.5,
            'genel': 0.4
        }
        
        # Yaş grubu risk çarpanları
        self.age_risk_multipliers = {
            'infant': 1.3,      # 0-1 yaş (kritik gelişim dönemi)
            'child': 1.2,       # 1-12 yaş
            'adolescent': 1.1,  # 13-18 yaş
            'adult': 1.0,       # 19-64 yaş
            'elderly': 1.25,    # 65+ yaş (artmış risk)
            'pregnant': 1.4,    # Hamile (en yüksek risk)
        }
    
    def assess_diagnosis_urgency(
        self,
        diagnosis_results: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]] = None,
        symptoms: Optional[List[Dict[str, Any]]] = None
    ) -> DiagnosisUrgencyAssessment:
        """
        Tanı sonuçlarını aciliyet açısından değerlendir
        
        Args:
            diagnosis_results: Tanı sonuçları (deficiency_probability, risk_level vb.)
            user_profile: Kullanıcı profili (yaş, cinsiyet, medical_conditions vb.)
            symptoms: Semptom listesi
            
        Returns:
            DiagnosisUrgencyAssessment
        """
        try:
            # Risk faktörlerini hesapla
            risk_factors = self._calculate_risk_factors(
                diagnosis_results, user_profile, symptoms
            )
            
            # Aciliyet skoru hesapla
            urgency_score = self._calculate_urgency_score(risk_factors, diagnosis_results)
            
            # Aciliyet seviyesi belirle
            urgency_level = self._determine_urgency_level(urgency_score)
            
            # Öncelikli eksiklikleri belirle
            priority_deficiencies = self._identify_priority_deficiencies(
                diagnosis_results, urgency_score
            )
            
            # Klinik bulguları belirle
            clinical_findings = self._identify_clinical_findings(
                diagnosis_results, risk_factors, symptoms
            )
            
            # Öneriler oluştur
            recommendations = self._generate_recommendations(
                urgency_level, priority_deficiencies, clinical_findings
            )
            
            # Doktor uyarısı gerekli mi?
            doctor_alert = urgency_score >= 6.0
            
            assessment = DiagnosisUrgencyAssessment(
                urgency_score=round(urgency_score, 2),
                urgency_level=urgency_level,
                requires_immediate_attention=urgency_score >= 6.0,
                response_time=self.response_times[urgency_level],
                priority_deficiencies=priority_deficiencies,
                risk_factors={k: round(v, 3) for k, v in risk_factors.items()},
                clinical_findings=clinical_findings,
                recommendations=recommendations,
                doctor_alert_required=doctor_alert,
                timestamp=datetime.now()
            )
            
            # Logger - kritik durumlar
            if urgency_level in [DiagnosisUrgencyLevel.CRITICAL, DiagnosisUrgencyLevel.HIGH]:
                logger.warning(
                    f"🚨 ACİL TANI DURUMU - "
                    f"Seviye: {urgency_level.value} - "
                    f"Skor: {urgency_score:.1f}/10"
                )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Tanı aciliyet değerlendirme hatası: {e}")
            raise
    
    def _calculate_risk_factors(
        self,
        diagnosis_results: Dict[str, Any],
        user_profile: Optional[Dict[str, Any]],
        symptoms: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, float]:
        """Risk faktörlerini hesapla"""
        risk_factors = {}
        
        # 1. Eksiklik şiddeti
        deficiency_prob = diagnosis_results.get('deficiency_probability', 0.0)
        risk_factors['deficiency_severity'] = deficiency_prob
        
        # 2. Kritik vitamin eksikliği
        nutrient = diagnosis_results.get('nutrient', '')
        risk_factors['critical_nutrient'] = self.critical_deficiencies.get(
            nutrient, {}
        ).get('weight', 0.0)
        
        # 3. Semptom şiddeti
        risk_factors['symptom_severity'] = self._assess_symptom_severity(symptoms)
        
        # 4. Yaş riski
        risk_factors['age_risk'] = self._assess_age_risk(user_profile)
        
        # 5. Komorbidite riski
        risk_factors['comorbidity_risk'] = self._assess_comorbidity_risk(user_profile)
        
        # 6. Gebelik riski
        risk_factors['pregnancy_risk'] = self._assess_pregnancy_risk(user_profile)
        
        # 7. Mevcut risk seviyesinden (varsa)
        existing_risk = diagnosis_results.get('risk_level', 'Düşük')
        risk_map = {
            'Kritik': 0.95,
            'Yüksek': 0.8,
            'Orta': 0.5,
            'Düşük': 0.2
        }
        risk_factors['existing_risk_level'] = risk_map.get(existing_risk, 0.2)
        
        return risk_factors
    
    def _assess_symptom_severity(
        self,
        symptoms: Optional[List[Dict[str, Any]]]
    ) -> float:
        """Semptom şiddetini değerlendir"""
        if not symptoms:
            return 0.0
        
        max_severity = 0.0
        
        for symptom in symptoms:
            severity = symptom.get('severity', 'mild')
            symptom_type = symptom.get('category', 'genel')
            
            # Şiddet skorlama
            severity_score_map = {
                'mild': 0.3,
                'moderate': 0.6,
                'severe': 0.9,
                'critical': 1.0
            }
            
            severity_score = severity_score_map.get(severity, 0.3)
            
            # Semptom tipi ağırlığı
            type_weight = self.symptom_severity_weights.get(symptom_type, 0.4)
            
            # Toplam skor
            total_score = severity_score * type_weight
            max_severity = max(max_severity, total_score)
        
        return max_severity
    
    def _assess_age_risk(self, user_profile: Optional[Dict[str, Any]]) -> float:
        """Yaş riskini değerlendir"""
        if not user_profile:
            return 0.3  # Varsayılan
        
        age = user_profile.get('age', 30)
        
        # Yaş grubunu belirle
        if age < 1:
            age_group = 'infant'
        elif age < 13:
            age_group = 'child'
        elif age < 19:
            age_group = 'adolescent'
        elif age < 65:
            age_group = 'adult'
        else:
            age_group = 'elderly'
        
        # Risk çarpanı
        multiplier = self.age_risk_multipliers.get(age_group, 1.0)
        
        # Normalize et (0-1 arası)
        return min(1.0, (multiplier - 1.0) * 2.5 + 0.3)
    
    def _assess_comorbidity_risk(
        self,
        user_profile: Optional[Dict[str, Any]]
    ) -> float:
        """Komorbidite (eşlik eden hastalık) riskini değerlendir"""
        if not user_profile:
            return 0.0
        
        medical_conditions = user_profile.get('medical_conditions', [])
        
        if not medical_conditions:
            return 0.0
        
        # Ciddi hastalıklar
        serious_conditions = [
            'diabetes', 'heart_disease', 'kidney_disease', 'liver_disease',
            'cancer', 'autoimmune_disease', 'malabsorption'
        ]
        
        serious_count = sum(
            1 for condition in medical_conditions
            if any(serious in condition.lower() for serious in serious_conditions)
        )
        
        # Risk skoru
        risk = min(1.0, serious_count * 0.3 + len(medical_conditions) * 0.1)
        return risk
    
    def _assess_pregnancy_risk(
        self,
        user_profile: Optional[Dict[str, Any]]
    ) -> float:
        """Gebelik riskini değerlendir"""
        if not user_profile:
            return 0.0
        
        is_pregnant = user_profile.get('is_pregnant', False)
        
        if is_pregnant:
            return 0.95  # Çok yüksek risk (folat, B12, demir eksikliği tehlikeli)
        
        return 0.0
    
    def _calculate_urgency_score(
        self,
        risk_factors: Dict[str, float],
        diagnosis_results: Dict[str, Any]
    ) -> float:
        """Toplam aciliyet skorunu hesapla (1-10)"""
        # Ağırlıklı faktörler
        weights = {
            'deficiency_severity': 2.5,
            'critical_nutrient': 3.0,
            'symptom_severity': 2.5,
            'age_risk': 1.5,
            'comorbidity_risk': 2.0,
            'pregnancy_risk': 3.5,
            'existing_risk_level': 2.0
        }
        
        total_weight = sum(weights.values())
        weighted_sum = sum(
            risk_factors.get(factor, 0.0) * weight
            for factor, weight in weights.items()
        )
        
        # 0-1'den 1-10'a normalize et
        normalized = weighted_sum / total_weight
        urgency_score = 1 + (normalized * 9)
        
        return min(10.0, max(1.0, urgency_score))
    
    def _determine_urgency_level(self, urgency_score: float) -> DiagnosisUrgencyLevel:
        """Aciliyet seviyesini belirle"""
        if urgency_score >= 8.0:
            return DiagnosisUrgencyLevel.CRITICAL
        elif urgency_score >= 6.0:
            return DiagnosisUrgencyLevel.HIGH
        elif urgency_score >= 4.0:
            return DiagnosisUrgencyLevel.MODERATE
        else:
            return DiagnosisUrgencyLevel.LOW
    
    def _identify_priority_deficiencies(
        self,
        diagnosis_results: Dict[str, Any],
        urgency_score: float
    ) -> List[Dict[str, Any]]:
        """Öncelikli eksiklikleri belirle"""
        deficiencies = []
        
        # Ana eksiklik
        nutrient = diagnosis_results.get('nutrient', '')
        deficiency_prob = diagnosis_results.get('deficiency_probability', 0.0)
        
        if deficiency_prob > 0.5:  # %50'den fazla olasılık
            deficiency_info = self.critical_deficiencies.get(nutrient, {})
            
            deficiencies.append({
                'nutrient': nutrient,
                'probability': round(deficiency_prob * 100, 1),
                'severity': 'HIGH' if deficiency_prob > 0.75 else 'MODERATE',
                'symptoms': deficiency_info.get('symptoms', []),
                'complications': deficiency_info.get('complications', 'Bilinmiyor'),
                'urgency': 'priority' if urgency_score >= 6.0 else 'standard'
            })
        
        # Diğer tespit edilen eksiklikler (varsa)
        all_results = diagnosis_results.get('all_nutrients', {})
        for nut, result in all_results.items():
            prob = result.get('probability', 0.0)
            if prob > 0.6 and nut != nutrient:  # Ana eksiklik değilse
                deficiency_info = self.critical_deficiencies.get(nut, {})
                deficiencies.append({
                    'nutrient': nut,
                    'probability': round(prob * 100, 1),
                    'severity': 'MODERATE',
                    'symptoms': deficiency_info.get('symptoms', []),
                    'complications': deficiency_info.get('complications', 'Bilinmiyor'),
                    'urgency': 'standard'
                })
        
        # Aciliyete göre sırala
        deficiencies.sort(key=lambda x: x['probability'], reverse=True)
        
        return deficiencies
    
    def _identify_clinical_findings(
        self,
        diagnosis_results: Dict[str, Any],
        risk_factors: Dict[str, float],
        symptoms: Optional[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Klinik bulguları belirle"""
        findings = []
        
        # Kritik vitamin eksikliği
        if risk_factors.get('critical_nutrient', 0) > 0.8:
            findings.append({
                'type': 'critical_deficiency',
                'severity': 'CRITICAL',
                'title': 'Kritik Vitamin/Mineral Eksikliği',
                'description': f"{diagnosis_results.get('nutrient', 'Bilinmiyor')} eksikliği tespit edildi",
                'action': 'ACİL doktor konsültasyonu gerekli'
            })
        
        # Ciddi semptomlar
        if risk_factors.get('symptom_severity', 0) > 0.8:
            findings.append({
                'type': 'severe_symptoms',
                'severity': 'HIGH',
                'title': 'Şiddetli Semptomlar',
                'description': 'Ciddi klinik belirti ve semptomlar mevcut',
                'action': 'Tıbbi değerlendirme gerekli'
            })
        
        # Gebelik riski
        if risk_factors.get('pregnancy_risk', 0) > 0.5:
            findings.append({
                'type': 'pregnancy_risk',
                'severity': 'HIGH',
                'title': 'Gebelik Dönemi Riski',
                'description': 'Gebelikte vitamin eksikliği tehlikelidir',
                'action': 'Obstetrik konsültasyon önerilir'
            })
        
        # Komorbidite
        if risk_factors.get('comorbidity_risk', 0) > 0.5:
            findings.append({
                'type': 'comorbidity',
                'severity': 'MODERATE',
                'title': 'Eşlik Eden Hastalık Riski',
                'description': 'Mevcut sağlık durumu riski artırıyor',
                'action': 'Kapsamlı tıbbi değerlendirme önerilir'
            })
        
        return findings
    
    def _generate_recommendations(
        self,
        urgency_level: DiagnosisUrgencyLevel,
        priority_deficiencies: List[Dict[str, Any]],
        clinical_findings: List[Dict[str, Any]]
    ) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        # Seviye bazlı genel öneriler
        recommendations.append(
            f"⏱️ Önerilen müdahale süresi: {self.response_times[urgency_level]}"
        )
        
        if urgency_level == DiagnosisUrgencyLevel.CRITICAL:
            recommendations.extend([
                "🚨 KRİTİK DURUM - Acil servise başvurun",
                "📞 112 Acil Servisi aramanız gerekebilir",
                "⛔ Kendi kendine tedavi uygulamayın",
                "🏥 Hastaneye gitmeden önce yakınlarınızı bilgilendirin"
            ])
        elif urgency_level == DiagnosisUrgencyLevel.HIGH:
            recommendations.extend([
                "⚠️ YÜKSEK ÖNCELİK - Bugün içinde doktora başvurun",
                "📋 Kan tahlili ile doğrulama yaptırın",
                "💊 Doktor reçetesi olmadan yüksek doz takviye almayın"
            ])
        elif urgency_level == DiagnosisUrgencyLevel.MODERATE:
            recommendations.extend([
                "⚡ ORTA ÖNCELİK - 1 hafta içinde doktora görünün",
                "🥗 Beslenme programınızı gözden geçirin",
                "📝 Semptomlarınızı kaydedin"
            ])
        else:
            recommendations.extend([
                "✓ DÜŞÜK ÖNCELİK - Rutin kontrol yeterli",
                "🍎 Dengeli beslenmeye devam edin",
                "📅 1 ay sonra tekrar değerlendirme"
            ])
        
        # Eksiklik bazlı özel öneriler
        for deficiency in priority_deficiencies[:2]:  # İlk 2 öncelikli
            if deficiency['urgency'] == 'priority':
                recommendations.append(
                    f"• {deficiency['nutrient'].upper()}: "
                    f"Acil tedavi gerekli - {deficiency['complications']}"
                )
        
        # Klinik bulgu bazlı öneriler
        for finding in clinical_findings:
            if finding['severity'] in ['CRITICAL', 'HIGH']:
                recommendations.append(f"• {finding['title']}: {finding['action']}")
        
        return recommendations
    
    def create_doctor_alert(
        self,
        assessment: DiagnosisUrgencyAssessment,
        patient_info: Dict[str, Any],
        diagnosis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Doktor için uyarı oluştur"""
        alert = {
            'alert_type': 'diagnosis_urgency_alert',
            'urgency_level': assessment.urgency_level.value,
            'urgency_score': assessment.urgency_score,
            'requires_immediate_attention': assessment.requires_immediate_attention,
            'timestamp': assessment.timestamp.isoformat(),
            
            # Hasta bilgileri
            'patient': {
                'id': patient_info.get('user_id'),
                'name': patient_info.get('name'),
                'age': patient_info.get('age'),
                'gender': patient_info.get('gender'),
                'pregnancy_status': patient_info.get('is_pregnant', False)
            },
            
            # Tanı bilgileri
            'diagnosis': {
                'primary_deficiency': diagnosis_results.get('nutrient'),
                'probability': diagnosis_results.get('deficiency_probability'),
                'risk_level': diagnosis_results.get('risk_level')
            },
            
            # Öncelikli eksiklikler
            'priority_deficiencies': assessment.priority_deficiencies,
            
            # Klinik bulgular
            'clinical_findings': assessment.clinical_findings,
            
            # Risk faktörleri
            'risk_factors': assessment.risk_factors,
            
            # Öneriler
            'recommendations': assessment.recommendations,
            
            # Eylem gerektiren durumlar
            'action_required': assessment.requires_immediate_attention,
            'response_time': assessment.response_time
        }
        
        return alert


def format_urgency_assessment(assessment: DiagnosisUrgencyAssessment) -> str:
    """Aciliyet değerlendirmesini okunabilir formata çevir"""
    level_emoji = {
        DiagnosisUrgencyLevel.CRITICAL: "🚨",
        DiagnosisUrgencyLevel.HIGH: "⚠️",
        DiagnosisUrgencyLevel.MODERATE: "⚡",
        DiagnosisUrgencyLevel.LOW: "✓"
    }
    
    output = []
    output.append("=" * 60)
    output.append(f"{level_emoji[assessment.urgency_level]} TANI ACİLİYET DEĞERLENDİRMESİ")
    output.append("=" * 60)
    output.append(f"Aciliyet Skoru: {assessment.urgency_score:.1f}/10")
    output.append(f"Seviye: {assessment.urgency_level.value.upper()}")
    output.append(f"Acil Müdahale: {'EVET' if assessment.requires_immediate_attention else 'HAYIR'}")
    output.append(f"Müdahale Süresi: {assessment.response_time}")
    
    if assessment.priority_deficiencies:
        output.append("\n🔍 ÖNCELİKLİ EKSİKLİKLER:")
        for deficiency in assessment.priority_deficiencies:
            output.append(f"  • {deficiency['nutrient'].upper()}: %{deficiency['probability']:.1f}")
            output.append(f"    Şiddet: {deficiency['severity']}")
            if deficiency.get('complications'):
                output.append(f"    Risk: {deficiency['complications']}")
    
    if assessment.clinical_findings:
        output.append("\n🏥 KLİNİK BULGULAR:")
        for finding in assessment.clinical_findings:
            output.append(f"  • {finding['title']}")
            output.append(f"    {finding['description']}")
            output.append(f"    → {finding['action']}")
    
    output.append("\n💡 ÖNERİLER:")
    for rec in assessment.recommendations:
        output.append(f"  {rec}")
    
    return "\n".join(output)

