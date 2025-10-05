"""
MHRS Kanonik Klinik Adları Mapping Sistemi
Türkçe normalize ve benzerlik tabanlı eşleştirme
"""

import json
import re
from typing import Dict, Tuple, List, Optional
from difflib import SequenceMatcher


def normalize_turkish(text: str) -> str:
    """
    Türkçe metni normalize eder:
    - Küçük harfe çevir
    - Diakritik karakterleri sadeleştir (ğ→g, ş→s, ı→i, ö→o, ü→u, ç→c)
    - Fazla boşlukları temizle
    """
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


def tokenize(text: str) -> List[str]:
    """Metni tokenlara ayırır"""
    normalized = normalize_turkish(text)
    # Kelime sınırlarına göre böl
    tokens = re.findall(r'\b\w+\b', normalized)
    return [token for token in tokens if len(token) > 1]  # Tek karakterli tokenları atla


def jaccard_similarity(tokens1: List[str], tokens2: List[str]) -> float:
    """Jaccard benzerlik skoru hesaplar"""
    if not tokens1 or not tokens2:
        return 0.0
    
    set1, set2 = set(tokens1), set(tokens2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    
    return intersection / union if union > 0 else 0.0


def levenshtein_similarity(text1: str, text2: str) -> float:
    """Levenshtein benzerlik skoru hesaplar"""
    if not text1 or not text2:
        return 0.0
    
    return SequenceMatcher(None, text1, text2).ratio()


def load_mhrs_canonical(path: str) -> Dict[str, Dict]:
    """
    MHRS kanonik klinik listesini yükler
    Format: {"canonical_name": {"variants": [...], "parent": "...", "gate_required": bool}}
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Varsayılan MHRS kanonik listesi
        return {
            "Aile Hekimliği": {
                "variants": ["aile hekimligi", "aile hekimi", "genel pratisyen", "gp"],
                "parent": None,
                "gate_required": False
            },
            "İç Hastalıkları (Dahiliye)": {
                "variants": ["ic hastaliklari", "dahiliye", "internal medicine", "ic"],
                "parent": None,
                "gate_required": False
            },
            "Nöroloji": {
                "variants": ["noroloji", "neurology", "beyin sinir", "sinir sistemi"],
                "parent": None,
                "gate_required": False
            },
            "Kardiyoloji": {
                "variants": ["kardiyoloji", "cardiology", "kalp damar", "kalp"],
                "parent": "İç Hastalıkları (Dahiliye)",
                "gate_required": True
            },
            "Gastroenteroloji": {
                "variants": ["gastroenteroloji", "gastro", "mide bagirsak", "sindirim"],
                "parent": "İç Hastalıkları (Dahiliye)",
                "gate_required": True
            },
            "Endokrinoloji": {
                "variants": ["endokrinoloji", "endokrin", "hormon", "tiroit"],
                "parent": "İç Hastalıkları (Dahiliye)",
                "gate_required": True
            },
            "Romatoloji": {
                "variants": ["romatoloji", "romatizma", "eklem", "artrit"],
                "parent": "İç Hastalıkları (Dahiliye)",
                "gate_required": True
            },
            "Nefroloji": {
                "variants": ["nefroloji", "bobrek", "diyaliz", "nefrit"],
                "parent": "İç Hastalıkları (Dahiliye)",
                "gate_required": True
            },
            "Hematoloji": {
                "variants": ["hematoloji", "kan hastaliklari", "lösemi", "anemi"],
                "parent": "İç Hastalıkları (Dahiliye)",
                "gate_required": True
            },
            "Göz Hastalıkları": {
                "variants": ["goz hastaliklari", "oftalmoloji", "goz", "görme"],
                "parent": None,
                "gate_required": False
            },
            "Kulak Burun Boğaz Hastalıkları": {
                "variants": ["kbb", "kulak burun bogaz", "ent", "otolaringoloji"],
                "parent": None,
                "gate_required": False
            },
            "Dermatoloji": {
                "variants": ["dermatoloji", "cilt hastaliklari", "deri", "cilt"],
                "parent": None,
                "gate_required": False
            },
            "Ortopedi ve Travmatoloji": {
                "variants": ["ortopedi", "travmatoloji", "kemik", "eklem", "travma"],
                "parent": None,
                "gate_required": False
            },
            "Genel Cerrahi": {
                "variants": ["genel cerrahi", "cerrahi", "ameliyat", "surgery"],
                "parent": None,
                "gate_required": False
            },
            "Çocuk Sağlığı ve Hastalıkları": {
                "variants": ["cocuk sagligi", "pediatri", "cocuk", "pediatric"],
                "parent": None,
                "gate_required": False
            },
            "Kadın Hastalıkları ve Doğum": {
                "variants": ["kadin hastaliklari", "jinekoloji", "dogum", "obstetrik"],
                "parent": None,
                "gate_required": False
            },
            "Üroloji": {
                "variants": ["uroloji", "idrar yolu", "bobrek", "prostat"],
                "parent": None,
                "gate_required": False
            },
            "Psikiyatri": {
                "variants": ["psikiyatri", "ruh sagligi", "psikoloji", "mental"],
                "parent": None,
                "gate_required": False
            },
            "Göğüs Hastalıkları": {
                "variants": ["gogus hastaliklari", "pulmonoloji", "akciger", "solunum"],
                "parent": None,
                "gate_required": False
            },
            "ACİL": {
                "variants": ["acil", "emergency", "112", "kritik", "acil servis"],
                "parent": None,
                "gate_required": False
            }
        }


def canonicalize(name: str, canonical_table: Dict[str, Dict]) -> Tuple[str, bool, float]:
    """
    Verilen klinik adını kanonik forma çevirir
    
    Returns:
        (canonical_name, matched: bool, similarity: float)
    """
    if not name or not canonical_table:
        return "Aile Hekimliği", False, 0.0
    
    normalized_input = normalize_turkish(name)
    input_tokens = tokenize(name)
    
    best_match = None
    best_similarity = 0.0
    best_canonical = "Aile Hekimliği"
    
    # 1. Tam eşleşme kontrolü (normalize edilmiş)
    for canonical, data in canonical_table.items():
        canonical_normalized = normalize_turkish(canonical)
        if canonical_normalized == normalized_input:
            return canonical, True, 1.0
        
        # Varyant kontrolü
        for variant in data.get("variants", []):
            variant_normalized = normalize_turkish(variant)
            if variant_normalized == normalized_input:
                return canonical, True, 0.95
    
    # 2. Token benzerliği kontrolü
    for canonical, data in canonical_table.items():
        canonical_tokens = tokenize(canonical)
        jaccard_sim = jaccard_similarity(input_tokens, canonical_tokens)
        
        # Varyant tokenları da kontrol et
        for variant in data.get("variants", []):
            variant_tokens = tokenize(variant)
            variant_jaccard = jaccard_similarity(input_tokens, variant_tokens)
            jaccard_sim = max(jaccard_sim, variant_jaccard)
        
        if jaccard_sim > best_similarity:
            best_similarity = jaccard_sim
            best_canonical = canonical
            best_match = True
    
    # 3. Levenshtein benzerliği kontrolü (düşük threshold)
    if best_similarity < 0.3:
        for canonical, data in canonical_table.items():
            levenshtein_sim = levenshtein_similarity(normalized_input, normalize_turkish(canonical))
            
            # Varyant kontrolü
            for variant in data.get("variants", []):
                variant_levenshtein = levenshtein_similarity(normalized_input, normalize_turkish(variant))
                levenshtein_sim = max(levenshtein_sim, variant_levenshtein)
            
            if levenshtein_sim > best_similarity and levenshtein_sim > 0.6:
                best_similarity = levenshtein_sim
                best_canonical = canonical
                best_match = True
    
    # Threshold kontrolü
    if best_similarity < 0.3:
        return "Aile Hekimliği", False, best_similarity
    
    return best_canonical, best_match, best_similarity


def test_canonicalize():
    """Test fonksiyonu"""
    canonical_table = load_mhrs_canonical("")
    
    test_cases = [
        ("Nöroloji", "Nöroloji", True, 1.0),
        ("noroloji", "Nöroloji", True, 0.95),
        ("beyin sinir", "Nöroloji", True, 0.8),
        ("Kardiyoloji", "Kardiyoloji", True, 1.0),
        ("kalp", "Kardiyoloji", True, 0.8),
        ("bilinmeyen klinik", "Aile Hekimliği", False, 0.0),
    ]
    
    print("🧪 Canonicalize Test Sonuçları:")
    for input_name, expected_canonical, expected_match, expected_sim in test_cases:
        canonical, matched, similarity = canonicalize(input_name, canonical_table)
        status = "✅" if canonical == expected_canonical else "❌"
        print(f"{status} '{input_name}' → '{canonical}' (match: {matched}, sim: {similarity:.2f})")


if __name__ == "__main__":
    test_canonicalize()
