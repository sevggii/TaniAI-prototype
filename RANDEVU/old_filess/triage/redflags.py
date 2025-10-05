"""
Acil Durum (Red-Flag) Tespiti Sistemi
Kritik durumları tespit edip ACİL yönlendirmesi yapar
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class RedFlagResult:
    """Red-flag tespit sonucu"""
    urgent: bool
    label: str
    reason: str
    message: str
    confidence: float


# Acil durum desenleri
RED_FLAG_PATTERNS = {
    "kalp_krizi": {
        "patterns": [
            r"göğüs\s+ağrısı.*soğuk\s+ter",
            r"soğuk\s+ter.*göğüs\s+ağrısı",
            r"ezici\s+ağrı.*göğüs",
            r"göğüs.*ezici\s+ağrı",
            r"kalp\s+krizi",
            r"miyokard\s+enfarkt",
            r"göğüs\s+ağrısı.*soğuk\s+terleme",
            r"soğuk\s+terleme.*göğüs\s+ağrısı",
            r"aniden.*gogsumde.*ezici.*agri.*soguk.*terliyorum"
        ],
        "keywords": ["ezici ağrı", "kalp krizi", "soğuk terleme", "aniden göğsümde"],
        "label": "ACİL",
        "reason": "Kalp krizi şüphesi",
        "message": "112'yi arayın veya en yakın acile başvurun. Kalp krizi belirtileri tespit edildi.",
        "confidence": 0.95
    },
    
    "inme": {
        "patterns": [
            r"ani.*yuzum.*kaydi",
            r"yuzum.*kaydi.*ani",
            r"ani.*konusma.*bozuklugu",
            r"konusma.*bozuklugu.*ani",
            r"ani.*kol.*gucsuzlugu",
            r"ani.*bacak.*gucsuzlugu",
            r"ani.*felc",
            r"inme",
            r"stroke",
            r"ani.*yuz.*felci",
            r"ani.*dil.*felci"
        ],
        "keywords": ["ani", "yüz kayması", "konuşma bozukluğu", "kol güçsüzlüğü", "bacak güçsüzlüğü", "felç", "inme"],
        "label": "ACİL",
        "reason": "İnme şüphesi",
        "message": "112'yi arayın veya en yakın acile başvurun. İnme belirtileri tespit edildi.",
        "confidence": 0.95
    },
    
    "bilinc_kaybi": {
        "patterns": [
            r"bilinç\s+kaybı",
            r"bayılma",
            r"bayıldım",
            r"bilinçsiz",
            r"koma",
            r"şuur\s+kaybı",
            r"bilinç\s+bulanıklığı",
            r"kendinden\s+geçme"
        ],
        "keywords": ["bilinç kaybı", "bayılma", "bilinçsiz", "koma", "şuur kaybı"],
        "label": "ACİL",
        "reason": "Bilinç kaybı",
        "message": "112'yi arayın veya en yakın acile başvurun. Bilinç kaybı durumu tespit edildi.",
        "confidence": 0.90
    },
    
    "kontrolsuz_kanama": {
        "patterns": [
            r"kontrolsüz\s+kanama",
            r"durmayan\s+kanama",
            r"aşırı\s+kanama",
            r"çok\s+kan\s+kaybı",
            r"kanama\s+durmayor",
            r"kan\s+akıyor.*durmayor",
            r"hemoraji",
            r"masif\s+kanama"
        ],
        "keywords": ["kontrolsüz kanama", "durmayan kanama", "aşırı kanama", "çok kan kaybı", "hemoraji"],
        "label": "ACİL",
        "reason": "Kontrolsüz kanama",
        "message": "112'yi arayın veya en yakın acile başvurun. Kontrolsüz kanama durumu tespit edildi.",
        "confidence": 0.90
    },
    
    "nefes_darligi": {
        "patterns": [
            r"nefes\s+alamıyorum",
            r"nefes\s+darlığı.*şiddetli",
            r"şiddetli.*nefes\s+darlığı",
            r"boğuluyorum",
            r"nefes\s+kesilmesi",
            r"solunum\s+yetmezliği",
            r"astım\s+krizi",
            r"nefes\s+alma\s+güçlüğü.*şiddetli"
        ],
        "keywords": ["nefes alamıyorum", "şiddetli nefes darlığı", "boğuluyorum", "nefes kesilmesi", "solunum yetmezliği"],
        "label": "ACİL",
        "reason": "Şiddetli nefes darlığı",
        "message": "112'yi arayın veya en yakın acile başvurun. Şiddetli nefes darlığı durumu tespit edildi.",
        "confidence": 0.85
    },
    
    "siddetli_agri": {
        "patterns": [
            r"dayanılmaz\s+ağrı",
            r"çok\s+şiddetli\s+ağrı",
            r"ağrı.*dayanılmaz",
            r"ağrı.*çok\s+şiddetli",
            r"ağrı.*10.*10",
            r"ağrı.*10\s+üzerinden\s+10",
            r"en\s+şiddetli\s+ağrı",
            r"ağrı.*ölüyorum"
        ],
        "keywords": ["dayanılmaz ağrı", "çok şiddetli ağrı", "ağrı 10/10", "en şiddetli ağrı"],
        "label": "ACİL",
        "reason": "Dayanılmaz ağrı",
        "message": "112'yi arayın veya en yakın acile başvurun. Dayanılmaz ağrı durumu tespit edildi.",
        "confidence": 0.80
    },
    
    "travma": {
        "patterns": [
            r"kafa\s+travması",
            r"kafa.*yaralandı",
            r"kafa.*çarptı.*kanama",
            r"travma.*kafa",
            r"kafa.*travma.*bilinç",
            r"düştüm.*kafa.*kanama",
            r"çarptım.*kafa.*kanama"
        ],
        "keywords": ["kafa travması", "kafa yaralandı", "kafa çarptı kanama", "travma kafa"],
        "label": "ACİL",
        "reason": "Kafa travması",
        "message": "112'yi arayın veya en yakın acile başvurun. Kafa travması durumu tespit edildi.",
        "confidence": 0.85
    },
    
    "zehirlenme": {
        "patterns": [
            r"zehirlendim",
            r"zehir.*içtim",
            r"ilaç.*fazla.*aldım",
            r"fazla.*ilaç.*aldım",
            r"overdose",
            r"aşırı\s+doz",
            r"kimyasal.*zehirlenme",
            r"gaz.*zehirlenmesi"
        ],
        "keywords": ["zehirlendim", "zehir içtim", "fazla ilaç", "overdose", "aşırı doz", "kimyasal zehirlenme"],
        "label": "ACİL",
        "reason": "Zehirlenme şüphesi",
        "message": "112'yi arayın veya en yakın acile başvurun. Zehirlenme şüphesi tespit edildi.",
        "confidence": 0.90
    }
}


def normalize_text_for_redflags(text: str) -> str:
    """Red-flag tespiti için metni normalize eder"""
    if not text:
        return ""
    
    # Küçük harfe çevir
    text = text.lower().strip()
    
    # Diakritik karakterleri sadeleştir
    replacements = {
        'ğ': 'g', 'Ğ': 'g',
        'ş': 's', 'Ş': 's', 
        'ı': 'i', 'İ': 'i', 'I': 'i',
        'ö': 'o', 'Ö': 'o',
        'ü': 'u', 'Ü': 'u',
        'ç': 'c', 'Ç': 'c'
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Fazla boşlukları temizle
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def detect_red_flags(text: str) -> RedFlagResult:
    """
    Verilen metinde acil durum (red-flag) tespiti yapar
    
    Args:
        text: Hasta şikayeti metni
    
    Returns:
        RedFlagResult: Tespit sonucu
    """
    if not text:
        return RedFlagResult(
            urgent=False,
            label="",
            reason="",
            message="",
            confidence=0.0
        )
    
    normalized_text = normalize_text_for_redflags(text)
    
    # Her red-flag kategorisi için kontrol et
    for category, config in RED_FLAG_PATTERNS.items():
        # Regex pattern kontrolü
        for pattern in config["patterns"]:
            if re.search(pattern, normalized_text, re.IGNORECASE):
                return RedFlagResult(
                    urgent=True,
                    label=config["label"],
                    reason=config["reason"],
                    message=config["message"],
                    confidence=config["confidence"]
                )
        
        # Keyword kontrolü (daha esnek) - sadece kritik durumlar için
        if category in ["kalp_krizi", "inme", "bilinc_kaybi", "kontrolsuz_kanama"]:
            keyword_count = 0
            for keyword in config["keywords"]:
                if keyword in normalized_text:
                    keyword_count += 1
            
            # En az 2 keyword varsa red-flag
            if keyword_count >= 2:
                return RedFlagResult(
                    urgent=True,
                    label=config["label"],
                    reason=config["reason"],
                    message=config["message"],
                    confidence=config["confidence"] * 0.8  # Keyword tabanlı daha düşük güven
                )

    # Kombine belirtiler: şiddetli baş ağrısı + mide bulantısı/kusma
    headache_terms = ["bas", "migren", "kafa"]
    nausea_terms = ["kus", "istifra", "bulant"]
    if any(term in normalized_text for term in headache_terms) and \
       any(term in normalized_text for term in nausea_terms):
        return RedFlagResult(
            urgent=True,
            label="ACİL",
            reason="Şiddetli baş ağrısı ve mide belirtileri",
            message="112'yi arayın veya en yakın acile başvurun. Baş ağrısına eşlik eden mide bulantısı/kusma acil değerlendirme gerektirebilir.",
            confidence=0.85
        )

    # Red-flag tespit edilmedi
    return RedFlagResult(
        urgent=False,
        label="",
        reason="",
        message="",
        confidence=0.0
    )


def get_emergency_keywords() -> List[str]:
    """Acil durum anahtar kelimelerini döndürür"""
    keywords = []
    for config in RED_FLAG_PATTERNS.values():
        keywords.extend(config["keywords"])
    return list(set(keywords))  # Tekrarları kaldır


def test_red_flags():
    """Test fonksiyonu"""
    print("🚨 Red-Flag Test Sonuçları:")
    
    test_cases = [
        ("Göğsümde ezici ağrı var, soğuk terliyorum", True, "Kalp krizi"),
        ("Aniden yüzüm kaydı, konuşamıyorum", True, "İnme"),
        ("Bayıldım, bilincimi kaybettim", True, "Bilinç kaybı"),
        ("Kontrolsüz kanama var, durmuyor", True, "Kontrolsüz kanama"),
        ("Nefes alamıyorum, boğuluyorum", True, "Nefes darlığı"),
        ("Dayanılmaz ağrım var, 10/10", True, "Şiddetli ağrı"),
        ("Kafa travması geçirdim, kanama var", True, "Kafa travması"),
        ("Fazla ilaç aldım, zehirlendim", True, "Zehirlenme"),
        ("Başım ağrıyor", False, ""),
        ("Mide bulantım var", False, ""),
        ("Hafif öksürük", False, ""),
    ]
    
    for complaint, expected_urgent, expected_type in test_cases:
        result = detect_red_flags(complaint)
        status = "✅" if result.urgent == expected_urgent else "❌"
        print(f"{status} '{complaint[:30]}...' → Urgent: {result.urgent}")
        if result.urgent:
            print(f"   🚨 {result.label}: {result.reason}")
            print(f"   📝 {result.message}")
            print(f"   🎯 Confidence: {result.confidence:.2f}")


if __name__ == "__main__":
    test_red_flags()
