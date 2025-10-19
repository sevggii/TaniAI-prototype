"""
İlaç Takibi Aciliyet Sistemi
==============================

Profesyonel aciliyet skorlama ve doktora bildirim sistemi.
Mevcut sisteme eklenti olarak çalışır, hiçbir kodu bozmaz.

Author: TanıAI Development Team
Version: 1.0.0
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

logger = logging.getLogger(__name__)


class UrgencyLevel(str, Enum):
    """Aciliyet seviyeleri"""
    CRITICAL = "critical"      # 8-10: Acil müdahale (15 dakika)
    HIGH = "high"              # 6-8: Yüksek öncelik (30 dakika)
    MODERATE = "moderate"      # 4-6: Orta öncelik (2 saat)
    LOW = "low"                # 1-4: Düşük öncelik (24 saat)


@dataclass
class UrgencyAssessment:
    """Aciliyet değerlendirmesi sonucu"""
    urgency_score: float  # 1-10 arası skor
    urgency_level: UrgencyLevel
    requires_immediate_attention: bool
    response_time: str
    risk_factors: Dict[str, float]
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    timestamp: datetime


class MedicationUrgencySystem:
    """
    İlaç takibi için kapsamlı aciliyet değerlendirme sistemi.
    
    Backward-compatible: Mevcut sisteme eklenti olarak çalışır.
    """
    
    def __init__(self, db: Session = None):
        self.db = db
        
        # Aciliyet eşik değerleri
        self.urgency_thresholds = {
            'critical_drug_missed': 0.9,           # Kritik ilaç kaçırma
            'severe_interaction': 0.85,            # Şiddetli etkileşim
            'critical_side_effect': 0.8,           # Kritik yan etki
            'overdose_risk': 0.75,                 # Doz aşımı riski
            'compliance_critical': 0.7,            # Kritik uyumsuzluk
            'refill_urgent': 0.6,                  # Acil reçete yenileme
        }
        
        # Müdahale süreleri
        self.response_times = {
            UrgencyLevel.CRITICAL: "15 dakika",
            UrgencyLevel.HIGH: "30 dakika",
            UrgencyLevel.MODERATE: "2 saat",
            UrgencyLevel.LOW: "24 saat"
        }
        
        # Kritik ilaç kategorileri ve risk ağırlıkları
        self.critical_medications = {
            # Kardiyovasküler (en yüksek risk)
            "WARFARIN": 1.0,
            "HEPARIN": 1.0,
            "ENOXAPARIN": 0.95,
            "DIGOXIN": 0.9,
            "CLOPIDOGREL": 0.85,
            
            # Nörolojik
            "LITHIUM": 0.95,
            "PHENYTOIN": 0.9,
            "CARBAMAZEPINE": 0.85,
            "VALPROIC_ACID": 0.85,
            
            # Metabolik
            "INSULIN": 1.0,
            "METFORMIN": 0.7,
            
            # İmmunosuppressif
            "METHOTREXATE": 0.9,
            "CYCLOSPORINE": 0.95,
            "TACROLIMUS": 0.95,
            
            # Antibiyotik (kritik durumlar)
            "VANCOMYCIN": 0.8,
        }
        
        # Şiddetli etkileşim matrisi
        self.severe_interactions = {
            ("WARFARIN", "ASPIRIN"): 0.95,
            ("WARFARIN", "IBUPROFEN"): 0.9,
            ("WARFARIN", "CLOPIDOGREL"): 0.95,
            ("DIGOXIN", "FUROSEMIDE"): 0.85,
            ("LITHIUM", "FUROSEMIDE"): 0.9,
            ("LITHIUM", "IBUPROFEN"): 0.85,
            ("METHOTREXATE", "ASPIRIN"): 0.9,
            ("ACE_INHIBITOR", "POTASSIUM"): 0.8,
        }
    
    def assess_medication_urgency(
        self,
        user_id: int,
        medication_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> UrgencyAssessment:
        """
        İlaç durumu için kapsamlı aciliyet değerlendirmesi
        
        Args:
            user_id: Hasta ID
            medication_data: İlaç bilgileri
            context: Ek bağlam (yan etkiler, etkileşimler vb.)
            
        Returns:
            UrgencyAssessment: Detaylı aciliyet değerlendirmesi
        """
        try:
            # Risk faktörlerini hesapla
            risk_factors = self._calculate_risk_factors(
                user_id, medication_data, context
            )
            
            # Aciliyet skoru hesapla (1-10)
            urgency_score = self._calculate_urgency_score(risk_factors)
            
            # Aciliyet seviyesi belirle
            urgency_level = self._determine_urgency_level(urgency_score)
            
            # Bulgular ve öneriler
            findings = self._identify_urgent_findings(risk_factors, medication_data)
            recommendations = self._generate_recommendations(
                urgency_level, findings, medication_data
            )
            
            # Değerlendirme
            assessment = UrgencyAssessment(
                urgency_score=round(urgency_score, 2),
                urgency_level=urgency_level,
                requires_immediate_attention=urgency_score >= 6.0,
                response_time=self.response_times[urgency_level],
                risk_factors={k: round(v, 3) for k, v in risk_factors.items()},
                findings=findings,
                recommendations=recommendations,
                timestamp=datetime.now()
            )
            
            # Kritik durum logu
            if urgency_level in [UrgencyLevel.CRITICAL, UrgencyLevel.HIGH]:
                logger.warning(
                    f"🚨 ACİL İLAÇ DURUMU - Kullanıcı: {user_id} - "
                    f"Seviye: {urgency_level.value} - Skor: {urgency_score:.1f}/10"
                )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Aciliyet değerlendirme hatası: {e}")
            raise
    
    def _calculate_risk_factors(
        self,
        user_id: int,
        medication_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Risk faktörlerini hesapla"""
        risk_factors = {}
        
        # 1. Kritik ilaç riski
        med_name = medication_data.get('medication_name', '').upper()
        risk_factors['critical_medication'] = self.critical_medications.get(
            med_name, 0.0
        )
        
        # 2. İlaç etkileşim riski
        risk_factors['drug_interaction'] = self._assess_interaction_risk(
            user_id, med_name, context
        )
        
        # 3. Kaçırılan doz riski
        risk_factors['missed_dose'] = self._assess_missed_dose_risk(
            medication_data, context
        )
        
        # 4. Doz aşımı riski
        risk_factors['overdose'] = self._assess_overdose_risk(
            medication_data, context
        )
        
        # 5. Yan etki riski
        risk_factors['side_effect'] = self._assess_side_effect_risk(context)
        
        # 6. Uyum (compliance) riski
        risk_factors['compliance'] = self._assess_compliance_risk(
            user_id, medication_data, context
        )
        
        # 7. Reçete bitme riski
        risk_factors['refill_urgency'] = self._assess_refill_urgency(
            medication_data, context
        )
        
        # 8. Hastalık ciddiyeti faktörü
        risk_factors['disease_severity'] = self._assess_disease_severity(
            medication_data, context
        )
        
        return risk_factors
    
    def _assess_interaction_risk(
        self,
        user_id: int,
        current_med: str,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """İlaç etkileşim riskini değerlendir"""
        if not context or 'active_medications' not in context:
            return 0.0
        
        max_risk = 0.0
        active_meds = context.get('active_medications', [])
        
        for med in active_meds:
            med_name = med.get('medication_name', '').upper()
            
            # Bilinen şiddetli etkileşimleri kontrol et
            interaction_key = tuple(sorted([current_med, med_name]))
            risk = self.severe_interactions.get(interaction_key, 0.0)
            
            max_risk = max(max_risk, risk)
        
        return max_risk
    
    def _assess_missed_dose_risk(
        self,
        medication_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Kaçırılan doz riskini değerlendir"""
        if not context or 'missed_doses' not in context:
            return 0.0
        
        missed_count = context.get('missed_doses', 0)
        med_name = medication_data.get('medication_name', '').upper()
        
        # Kritik ilaçta kaçırılan doz çok riskli
        is_critical = med_name in self.critical_medications
        
        if missed_count == 0:
            return 0.0
        elif missed_count == 1:
            return 0.4 if is_critical else 0.2
        elif missed_count == 2:
            return 0.7 if is_critical else 0.4
        else:  # 3+
            return 0.95 if is_critical else 0.6
    
    def _assess_overdose_risk(
        self,
        medication_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Doz aşımı riskini değerlendir"""
        if not context or 'daily_doses_taken' not in context:
            return 0.0
        
        daily_limit = medication_data.get('max_daily_dose', float('inf'))
        taken_today = context.get('daily_doses_taken', 0)
        
        if daily_limit == float('inf'):
            return 0.0
        
        ratio = taken_today / daily_limit
        
        if ratio < 0.8:
            return 0.0
        elif ratio < 1.0:
            return 0.3
        elif ratio < 1.2:
            return 0.7
        else:  # Ciddi aşım
            return 0.95
    
    def _assess_side_effect_risk(self, context: Optional[Dict[str, Any]]) -> float:
        """Yan etki riskini değerlendir"""
        if not context or 'side_effects' not in context:
            return 0.0
        
        side_effects = context.get('side_effects', [])
        if not side_effects:
            return 0.0
        
        # En yüksek şiddetli yan etkiyi bul
        max_severity = 0.0
        for effect in side_effects:
            severity = effect.get('severity', 'mild')
            
            severity_map = {
                'mild': 0.2,
                'moderate': 0.5,
                'severe': 0.8,
                'critical': 0.95
            }
            
            max_severity = max(max_severity, severity_map.get(severity, 0.0))
        
        return max_severity
    
    def _assess_compliance_risk(
        self,
        user_id: int,
        medication_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Uyum (compliance) riskini değerlendir"""
        if not context or 'compliance_rate' not in context:
            return 0.0
        
        compliance_rate = context.get('compliance_rate', 1.0)
        med_name = medication_data.get('medication_name', '').upper()
        is_critical = med_name in self.critical_medications
        
        # Uyum oranı düşükse risk yüksek
        if compliance_rate >= 0.9:
            return 0.0
        elif compliance_rate >= 0.7:
            return 0.3 if is_critical else 0.2
        elif compliance_rate >= 0.5:
            return 0.6 if is_critical else 0.4
        else:  # < 50%
            return 0.9 if is_critical else 0.6
    
    def _assess_refill_urgency(
        self,
        medication_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Reçete yenileme aciliyetini değerlendir"""
        if not context or 'remaining_doses' not in context:
            return 0.0
        
        remaining = context.get('remaining_doses', 999)
        frequency_per_day = context.get('frequency_per_day', 1)
        
        # Kaç günlük ilaç kaldı
        days_remaining = remaining / frequency_per_day if frequency_per_day > 0 else 999
        
        if days_remaining > 7:
            return 0.0
        elif days_remaining > 3:
            return 0.3
        elif days_remaining > 1:
            return 0.6
        else:  # 1 gün veya daha az
            return 0.9
    
    def _assess_disease_severity(
        self,
        medication_data: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> float:
        """Hastalık ciddiyetini değerlendir"""
        if not context or 'disease_severity' not in context:
            return 0.0
        
        severity = context.get('disease_severity', 'mild')
        
        severity_map = {
            'mild': 0.2,
            'moderate': 0.4,
            'severe': 0.7,
            'critical': 0.95,
            'life_threatening': 1.0
        }
        
        return severity_map.get(severity, 0.0)
    
    def _calculate_urgency_score(self, risk_factors: Dict[str, float]) -> float:
        """Toplam aciliyet skorunu hesapla (1-10)"""
        # Ağırlıklı faktörler
        weights = {
            'critical_medication': 3.0,
            'drug_interaction': 3.5,
            'missed_dose': 2.5,
            'overdose': 4.0,
            'side_effect': 3.0,
            'compliance': 2.0,
            'refill_urgency': 1.5,
            'disease_severity': 2.5
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
    
    def _determine_urgency_level(self, urgency_score: float) -> UrgencyLevel:
        """Aciliyet seviyesini belirle"""
        if urgency_score >= 8.0:
            return UrgencyLevel.CRITICAL
        elif urgency_score >= 6.0:
            return UrgencyLevel.HIGH
        elif urgency_score >= 4.0:
            return UrgencyLevel.MODERATE
        else:
            return UrgencyLevel.LOW
    
    def _identify_urgent_findings(
        self,
        risk_factors: Dict[str, float],
        medication_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Acil bulguları belirle"""
        findings = []
        
        # Doz aşımı
        if risk_factors.get('overdose', 0) > self.urgency_thresholds['overdose_risk']:
            findings.append({
                'type': 'overdose_risk',
                'severity': 'CRITICAL',
                'title': 'Doz Aşımı Riski',
                'description': 'Günlük maksimum doz limiti aşılmış veya aşılmak üzere',
                'action': 'ACİL - Doktora danışmadan ilave doz almayın'
            })
        
        # Kritik etkileşim
        if risk_factors.get('drug_interaction', 0) > self.urgency_thresholds['severe_interaction']:
            findings.append({
                'type': 'severe_interaction',
                'severity': 'CRITICAL',
                'title': 'Şiddetli İlaç Etkileşimi',
                'description': 'Tehlikeli ilaç etkileşimi tespit edildi',
                'action': 'ACİL - Eczacınıza veya doktorunuza danışın'
            })
        
        # Kritik yan etki
        if risk_factors.get('side_effect', 0) > self.urgency_thresholds['critical_side_effect']:
            findings.append({
                'type': 'critical_side_effect',
                'severity': 'HIGH',
                'title': 'Ciddi Yan Etki',
                'description': 'Şiddetli yan etki bildirildi',
                'action': 'Doktorunuza hemen bildirin'
            })
        
        # Kritik ilaç kaçırma
        if risk_factors.get('missed_dose', 0) > self.urgency_thresholds['critical_drug_missed']:
            findings.append({
                'type': 'critical_missed_dose',
                'severity': 'HIGH',
                'title': 'Kritik İlaç Kaçırıldı',
                'description': f"{medication_data.get('medication_name')} kritik bir ilaçtır",
                'action': 'Doktorunuza danışarak kaçırılan dozu telafi edin'
            })
        
        # İlaç bitmek üzere
        if risk_factors.get('refill_urgency', 0) > self.urgency_thresholds['refill_urgent']:
            findings.append({
                'type': 'refill_urgent',
                'severity': 'MODERATE',
                'title': 'İlaç Stoku Azalıyor',
                'description': 'İlaç birkaç gün içinde bitecek',
                'action': 'Reçete yenilemesi için doktorunuza başvurun'
            })
        
        # Uyum sorunu
        if risk_factors.get('compliance', 0) > self.urgency_thresholds['compliance_critical']:
            findings.append({
                'type': 'compliance_issue',
                'severity': 'MODERATE',
                'title': 'Düşük İlaç Uyumu',
                'description': 'İlaç düzenli kullanılmıyor',
                'action': 'Tedavi planınızı gözden geçirmek için doktorunuzla görüşün'
            })
        
        return findings
    
    def _generate_recommendations(
        self,
        urgency_level: UrgencyLevel,
        findings: List[Dict[str, Any]],
        medication_data: Dict[str, Any]
    ) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        # Seviye bazlı genel öneriler
        recommendations.append(
            f"⏱️ Önerilen müdahale süresi: {self.response_times[urgency_level]}"
        )
        
        if urgency_level == UrgencyLevel.CRITICAL:
            recommendations.extend([
                "🚨 ACİL DURUM - Derhal doktorunuza veya acil servise başvurun",
                "📞 Acil sağlık hattını (112) aramaktan çekinmeyin",
                "⛔ Yeni ilaç almayın, doktor onayı bekleyin"
            ])
        elif urgency_level == UrgencyLevel.HIGH:
            recommendations.extend([
                "⚠️ YÜKSEK ÖNCELİK - Bugün içinde doktorunuza ulaşın",
                "📱 Eczacınıza danışın",
                "📋 İlaç listesi ve yan etkileri kaydedin"
            ])
        elif urgency_level == UrgencyLevel.MODERATE:
            recommendations.extend([
                "⚡ ORTA ÖNCELİK - 2 saat içinde değerlendirme yapın",
                "📝 İlaç kullanım saatlerinizi düzenleyin",
                "💊 Hatırlatıcıları aktif edin"
            ])
        else:
            recommendations.extend([
                "✓ DÜŞÜK ÖNCELİK - Rutin takip yeterli",
                "📅 Planlı kontrollere devam edin"
            ])
        
        # Bulgu bazlı özel öneriler
        for finding in findings:
            if finding['severity'] in ['CRITICAL', 'HIGH']:
                recommendations.append(f"• {finding['title']}: {finding['action']}")
        
        return recommendations
    
    def create_doctor_notification(
        self,
        assessment: UrgencyAssessment,
        patient_info: Dict[str, Any],
        medication_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Doktor için bildirim oluştur"""
        notification = {
            'notification_type': 'medication_urgency_alert',
            'urgency_level': assessment.urgency_level.value,
            'urgency_score': assessment.urgency_score,
            'requires_immediate_attention': assessment.requires_immediate_attention,
            'timestamp': assessment.timestamp.isoformat(),
            
            # Hasta bilgileri
            'patient': {
                'id': patient_info.get('user_id'),
                'name': patient_info.get('name'),
                'age': patient_info.get('age'),
                'gender': patient_info.get('gender')
            },
            
            # İlaç bilgileri
            'medication': {
                'name': medication_data.get('medication_name'),
                'dosage': f"{medication_data.get('dosage_amount')} {medication_data.get('dosage_unit')}",
                'frequency': medication_data.get('frequency_type')
            },
            
            # Bulgular
            'findings': assessment.findings,
            
            # Risk faktörleri
            'risk_factors': assessment.risk_factors,
            
            # Öneriler
            'recommendations': assessment.recommendations,
            
            # Eylem gerektiren durumlar
            'action_required': assessment.requires_immediate_attention,
            'response_time': assessment.response_time
        }
        
        return notification


# Yardımcı fonksiyonlar
def format_urgency_assessment(assessment: UrgencyAssessment) -> str:
    """Aciliyet değerlendirmesini okunabilir formata çevir"""
    level_emoji = {
        UrgencyLevel.CRITICAL: "🚨",
        UrgencyLevel.HIGH: "⚠️",
        UrgencyLevel.MODERATE: "⚡",
        UrgencyLevel.LOW: "✓"
    }
    
    output = []
    output.append("=" * 60)
    output.append(f"{level_emoji[assessment.urgency_level]} ACİLİYET DEĞERLENDİRMESİ")
    output.append("=" * 60)
    output.append(f"Aciliyet Skoru: {assessment.urgency_score:.1f}/10")
    output.append(f"Seviye: {assessment.urgency_level.value.upper()}")
    output.append(f"Acil Müdahale: {'EVET' if assessment.requires_immediate_attention else 'HAYIR'}")
    output.append(f"Müdahale Süresi: {assessment.response_time}")
    
    if assessment.findings:
        output.append("\n🔍 BULGULAR:")
        for finding in assessment.findings:
            output.append(f"  • {finding['title']}")
            output.append(f"    {finding['description']}")
            output.append(f"    → {finding['action']}")
    
    output.append("\n💡 ÖNERİLER:")
    for rec in assessment.recommendations:
        output.append(f"  {rec}")
    
    return "\n".join(output)

