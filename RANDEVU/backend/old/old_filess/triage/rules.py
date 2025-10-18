"""
MHRS Ön-koşul Kuralları (Gatekeeping) Sistemi
Bazı yan dallara randevu almadan önce ana branştan geçme zorunluluğu
"""

from typing import Dict, List, NamedTuple, Optional, Tuple
from dataclasses import dataclass


@dataclass
class AppliedGate:
    """Uygulanan gatekeeping kuralı"""
    requires_prior: bool
    prior_list: List[str]
    gate_note: str
    reason: str


# MHRS Gatekeeping Kuralları
GATE_RULES = {
    # İç Hastalıkları yan dalları
    "Kardiyoloji": {
        "requires_prior": True,
        "prior_list": ["İç Hastalıkları (Dahiliye)"],
        "gate_note": "Kardiyoloji randevusu için önce İç Hastalıkları (Dahiliye) muayenesi gereklidir.",
        "reason": "Kalp hastalıklarının genel değerlendirmesi için"
    },
    "Gastroenteroloji": {
        "requires_prior": True,
        "prior_list": ["İç Hastalıkları (Dahiliye)"],
        "gate_note": "Gastroenteroloji randevusu için önce İç Hastalıkları (Dahiliye) muayenesi gereklidir.",
        "reason": "Sindirim sistemi hastalıklarının genel değerlendirmesi için"
    },
    "Endokrinoloji": {
        "requires_prior": True,
        "prior_list": ["İç Hastalıkları (Dahiliye)"],
        "gate_note": "Endokrinoloji randevusu için önce İç Hastalıkları (Dahiliye) muayenesi gereklidir.",
        "reason": "Hormon hastalıklarının genel değerlendirmesi için"
    },
    "Romatoloji": {
        "requires_prior": True,
        "prior_list": ["İç Hastalıkları (Dahiliye)"],
        "gate_note": "Romatoloji randevusu için önce İç Hastalıkları (Dahiliye) muayenesi gereklidir.",
        "reason": "Romatizmal hastalıkların genel değerlendirmesi için"
    },
    "Nefroloji": {
        "requires_prior": True,
        "prior_list": ["İç Hastalıkları (Dahiliye)"],
        "gate_note": "Nefroloji randevusu için önce İç Hastalıkları (Dahiliye) muayenesi gereklidir.",
        "reason": "Böbrek hastalıklarının genel değerlendirmesi için"
    },
    "Hematoloji": {
        "requires_prior": True,
        "prior_list": ["İç Hastalıkları (Dahiliye)"],
        "gate_note": "Hematoloji randevusu için önce İç Hastalıkları (Dahiliye) muayenesi gereklidir.",
        "reason": "Kan hastalıklarının genel değerlendirmesi için"
    },
    
    # Çocuk yan dalları
    "Çocuk Kardiyolojisi": {
        "requires_prior": True,
        "prior_list": ["Çocuk Sağlığı ve Hastalıkları"],
        "gate_note": "Çocuk Kardiyolojisi randevusu için önce Çocuk Sağlığı ve Hastalıkları muayenesi gereklidir.",
        "reason": "Çocuk kalp hastalıklarının genel değerlendirmesi için"
    },
    "Çocuk Nörolojisi": {
        "requires_prior": True,
        "prior_list": ["Çocuk Sağlığı ve Hastalıkları"],
        "gate_note": "Çocuk Nörolojisi randevusu için önce Çocuk Sağlığı ve Hastalıkları muayenesi gereklidir.",
        "reason": "Çocuk sinir sistemi hastalıklarının genel değerlendirmesi için"
    },
    "Çocuk Endokrinolojisi": {
        "requires_prior": True,
        "prior_list": ["Çocuk Sağlığı ve Hastalıkları"],
        "gate_note": "Çocuk Endokrinolojisi randevusu için önce Çocuk Sağlığı ve Hastalıkları muayenesi gereklidir.",
        "reason": "Çocuk hormon hastalıklarının genel değerlendirmesi için"
    },
    
    # Göz yan dalları
    "Retina Hastalıkları": {
        "requires_prior": True,
        "prior_list": ["Göz Hastalıkları"],
        "gate_note": "Retina Hastalıkları randevusu için önce Göz Hastalıkları muayenesi gereklidir.",
        "reason": "Retina hastalıklarının genel göz muayenesi için"
    },
    "Glokom": {
        "requires_prior": True,
        "prior_list": ["Göz Hastalıkları"],
        "gate_note": "Glokom randevusu için önce Göz Hastalıkları muayenesi gereklidir.",
        "reason": "Glokom hastalığının genel göz muayenesi için"
    },
    "Kornea Hastalıkları": {
        "requires_prior": True,
        "prior_list": ["Göz Hastalıkları"],
        "gate_note": "Kornea Hastalıkları randevusu için önce Göz Hastalıkları muayenesi gereklidir.",
        "reason": "Kornea hastalıklarının genel göz muayenesi için"
    },
    
    # KBB yan dalları
    "Baş Boyun Cerrahisi": {
        "requires_prior": True,
        "prior_list": ["Kulak Burun Boğaz Hastalıkları"],
        "gate_note": "Baş Boyun Cerrahisi randevusu için önce KBB muayenesi gereklidir.",
        "reason": "Baş boyun cerrahi girişimlerinin genel KBB değerlendirmesi için"
    },
    "Otoloji": {
        "requires_prior": True,
        "prior_list": ["Kulak Burun Boğaz Hastalıkları"],
        "gate_note": "Otoloji randevusu için önce KBB muayenesi gereklidir.",
        "reason": "Kulak hastalıklarının genel KBB değerlendirmesi için"
    },
    
    # Ortopedi yan dalları
    "Spor Hekimliği": {
        "requires_prior": True,
        "prior_list": ["Ortopedi ve Travmatoloji"],
        "gate_note": "Spor Hekimliği randevusu için önce Ortopedi ve Travmatoloji muayenesi gereklidir.",
        "reason": "Spor yaralanmalarının genel ortopedi değerlendirmesi için"
    },
    "El Cerrahisi": {
        "requires_prior": True,
        "prior_list": ["Ortopedi ve Travmatoloji"],
        "gate_note": "El Cerrahisi randevusu için önce Ortopedi ve Travmatoloji muayenesi gereklidir.",
        "reason": "El cerrahi girişimlerinin genel ortopedi değerlendirmesi için"
    },
    
    # Kadın Hastalıkları yan dalları
    "Üreme Endokrinolojisi": {
        "requires_prior": True,
        "prior_list": ["Kadın Hastalıkları ve Doğum"],
        "gate_note": "Üreme Endokrinolojisi randevusu için önce Kadın Hastalıkları ve Doğum muayenesi gereklidir.",
        "reason": "Üreme hormon hastalıklarının genel jinekoloji değerlendirmesi için"
    },
    "Maternal Fetal Tıp": {
        "requires_prior": True,
        "prior_list": ["Kadın Hastalıkları ve Doğum"],
        "gate_note": "Maternal Fetal Tıp randevusu için önce Kadın Hastalıkları ve Doğum muayenesi gereklidir.",
        "reason": "Yüksek riskli gebeliklerin genel jinekoloji değerlendirmesi için"
    },
    
    # Üroloji yan dalları
    "Çocuk Ürolojisi": {
        "requires_prior": True,
        "prior_list": ["Üroloji", "Çocuk Sağlığı ve Hastalıkları"],
        "gate_note": "Çocuk Ürolojisi randevusu için önce Üroloji veya Çocuk Sağlığı ve Hastalıkları muayenesi gereklidir.",
        "reason": "Çocuk üroloji hastalıklarının genel değerlendirmesi için"
    },
    "Androloji": {
        "requires_prior": True,
        "prior_list": ["Üroloji"],
        "gate_note": "Androloji randevusu için önce Üroloji muayenesi gereklidir.",
        "reason": "Erkek üreme sağlığı hastalıklarının genel üroloji değerlendirmesi için"
    },
    
    # Psikiyatri yan dalları
    "Çocuk ve Ergen Psikiyatrisi": {
        "requires_prior": True,
        "prior_list": ["Psikiyatri", "Çocuk Sağlığı ve Hastalıkları"],
        "gate_note": "Çocuk ve Ergen Psikiyatrisi randevusu için önce Psikiyatri veya Çocuk Sağlığı ve Hastalıkları muayenesi gereklidir.",
        "reason": "Çocuk ruh sağlığı hastalıklarının genel değerlendirmesi için"
    },
    "Geriatrik Psikiyatri": {
        "requires_prior": True,
        "prior_list": ["Psikiyatri", "İç Hastalıkları (Dahiliye)"],
        "gate_note": "Geriatrik Psikiyatri randevusu için önce Psikiyatri veya İç Hastalıkları (Dahiliye) muayenesi gereklidir.",
        "reason": "Yaşlılık dönemi ruh sağlığı hastalıklarının genel değerlendirmesi için"
    }
}


def apply_gatekeeping(canonical_name: str, rules: Dict[str, Dict] = None) -> AppliedGate:
    """
    Verilen kanonik klinik adı için gatekeeping kuralını uygular
    
    Args:
        canonical_name: Kanonik klinik adı
        rules: Gatekeeping kuralları (varsayılan: GATE_RULES)
    
    Returns:
        AppliedGate: Uygulanan gatekeeping kuralı
    """
    if rules is None:
        rules = GATE_RULES
    
    # Kural var mı kontrol et
    if canonical_name in rules:
        rule = rules[canonical_name]
        return AppliedGate(
            requires_prior=rule["requires_prior"],
            prior_list=rule["prior_list"],
            gate_note=rule["gate_note"],
            reason=rule["reason"]
        )
    
    # Kural yoksa gatekeeping gerekmez
    return AppliedGate(
        requires_prior=False,
        prior_list=[],
        gate_note="",
        reason="Bu klinik için ön-koşul kuralı bulunmamaktadır."
    )


def get_parent_specialty(canonical_name: str) -> Optional[str]:
    """
    Verilen klinik adının ana branşını döndürür
    """
    gate = apply_gatekeeping(canonical_name)
    if gate.requires_prior and gate.prior_list:
        return gate.prior_list[0]  # İlk ön-koşul ana branş
    return None


def is_specialty_accessible(canonical_name: str, has_prior_visit: List[str] = None) -> Tuple[bool, str]:
    """
    Verilen klinik için randevu alınabilir mi kontrol eder
    
    Args:
        canonical_name: Klinik adı
        has_prior_visit: Daha önce muayene olunan klinikler listesi
    
    Returns:
        (accessible: bool, message: str)
    """
    if has_prior_visit is None:
        has_prior_visit = []
    
    gate = apply_gatekeeping(canonical_name)
    
    if not gate.requires_prior:
        return True, "Bu klinik için ön-koşul bulunmamaktadır."
    
    # Ön-koşul kliniklerinden herhangi birine muayene olmuş mu?
    for required_clinic in gate.prior_list:
        if required_clinic in has_prior_visit:
            return True, f"Ön-koşul karşılandı: {required_clinic} muayenesi mevcut."
    
    return False, gate.gate_note


def test_gatekeeping():
    """Test fonksiyonu"""
    print("🧪 Gatekeeping Test Sonuçları:")
    
    test_cases = [
        ("Kardiyoloji", True, ["İç Hastalıkları (Dahiliye)"]),
        ("Nöroloji", False, []),
        ("Çocuk Kardiyolojisi", True, ["Çocuk Sağlığı ve Hastalıkları"]),
        ("Retina Hastalıkları", True, ["Göz Hastalıkları"]),
        ("Aile Hekimliği", False, []),
    ]
    
    for clinic, expected_requires, expected_prior in test_cases:
        gate = apply_gatekeeping(clinic)
        status = "✅" if gate.requires_prior == expected_requires else "❌"
        print(f"{status} {clinic}: requires_prior={gate.requires_prior}, prior_list={gate.prior_list}")
        if gate.gate_note:
            print(f"   📝 {gate.gate_note}")
    
    # Erişilebilirlik testi
    print("\n🔐 Erişilebilirlik Testi:")
    accessible, message = is_specialty_accessible("Kardiyoloji", ["İç Hastalıkları (Dahiliye)"])
    print(f"✅ Kardiyoloji (İç Hastalıkları mevcut): {accessible} - {message}")
    
    accessible, message = is_specialty_accessible("Kardiyoloji", [])
    print(f"❌ Kardiyoloji (İç Hastalıkları yok): {accessible} - {message}")


if __name__ == "__main__":
    test_gatekeeping()
