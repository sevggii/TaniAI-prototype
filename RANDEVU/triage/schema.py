"""
Deterministik JSON Sözleşmesi ve Validasyon Sistemi
LLM çıktısını temizler, doğrular ve eksikleri doldurur
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ClinicRecommendation:
    """Klinik önerisi veri yapısı"""
    name: str
    reason: str
    confidence: float


@dataclass
class TriageResponse:
    """Triage yanıt veri yapısı"""
    primary_clinic: ClinicRecommendation
    secondary_clinics: List[ClinicRecommendation]
    strategy: str
    model_version: str
    latency_ms: int
    requires_prior: bool
    prior_list: List[str]
    gate_note: str


def clean_json_string(json_str: str) -> str:
    """
    JSON string'ini temizler:
    - Markdown backtick'leri kaldırır
    - Yorumları temizler
    - Trailing comma'ları düzeltir
    - Fazla boşlukları temizler
    """
    if not json_str:
        return "{}"
    
    # Markdown backtick'leri kaldır
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```\s*', '', json_str)
    json_str = re.sub(r'`', '', json_str)
    
    # Yorumları kaldır (// ve /* */)
    json_str = re.sub(r'//.*$', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    
    # Trailing comma'ları düzeltir
    json_str = re.sub(r',\s*}', '}', json_str)
    json_str = re.sub(r',\s*]', ']', json_str)
    
    # Fazla boşlukları temizle
    json_str = re.sub(r'\s+', ' ', json_str)
    json_str = json_str.strip()
    
    return json_str


def extract_json_from_text(text: str) -> Optional[str]:
    """
    Metinden JSON'u çıkarır
    """
    if not text:
        return None
    
    # JSON pattern'ini ara
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, text)
    
    if matches:
        # En uzun match'i al (muhtemelen en kapsamlı)
        return max(matches, key=len)
    
    return None


def validate_or_fix(payload_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    JSON payload'ını doğrular ve eksikleri doldurur
    
    Args:
        payload_dict: Ham JSON dict
    
    Returns:
        Dict: Doğrulanmış ve düzeltilmiş JSON
    """
    if not isinstance(payload_dict, dict):
        payload_dict = {}
    
    # Varsayılan değerler
    default_response = {
        "primary_clinic": {
            "name": "Aile Hekimliği",
            "reason": "Genel değerlendirme için",
            "confidence": 0.7
        },
        "secondary_clinics": [
            {
                "name": "İç Hastalıkları (Dahiliye)",
                "reason": "Detaylı değerlendirme için alternatif",
                "confidence": 0.6
            }
        ],
        "strategy": "fallback",
        "model_version": "unknown",
        "latency_ms": 0,
        "requires_prior": False,
        "prior_list": [],
        "gate_note": ""
    }
    
    # Primary clinic doğrulama
    if "primary_clinic" not in payload_dict or not isinstance(payload_dict["primary_clinic"], dict):
        payload_dict["primary_clinic"] = default_response["primary_clinic"]
    else:
        primary = payload_dict["primary_clinic"]
        if "name" not in primary or not isinstance(primary["name"], str):
            primary["name"] = default_response["primary_clinic"]["name"]
        if "reason" not in primary or not isinstance(primary["reason"], str):
            primary["reason"] = default_response["primary_clinic"]["reason"]
        if "confidence" not in primary or not isinstance(primary["confidence"], (int, float)):
            primary["confidence"] = default_response["primary_clinic"]["confidence"]
        else:
            # Confidence'ı [0,1] aralığına sınırla
            primary["confidence"] = max(0.0, min(1.0, float(primary["confidence"])))
    
    # Secondary clinics doğrulama
    if "secondary_clinics" not in payload_dict or not isinstance(payload_dict["secondary_clinics"], list):
        payload_dict["secondary_clinics"] = default_response["secondary_clinics"]
    else:
        secondary_list = []
        for clinic in payload_dict["secondary_clinics"]:
            if isinstance(clinic, dict):
                if "name" not in clinic or not isinstance(clinic["name"], str):
                    clinic["name"] = "Aile Hekimliği"
                if "reason" not in clinic or not isinstance(clinic["reason"], str):
                    clinic["reason"] = "Alternatif öneri"
                if "confidence" not in clinic or not isinstance(clinic["confidence"], (int, float)):
                    clinic["confidence"] = 0.6
                else:
                    clinic["confidence"] = max(0.0, min(1.0, float(clinic["confidence"])))
                secondary_list.append(clinic)
        
        if not secondary_list:
            secondary_list = default_response["secondary_clinics"]
        
        payload_dict["secondary_clinics"] = secondary_list
    
    # Diğer alanlar
    if "strategy" not in payload_dict or not isinstance(payload_dict["strategy"], str):
        payload_dict["strategy"] = default_response["strategy"]
    
    if "model_version" not in payload_dict or not isinstance(payload_dict["model_version"], str):
        payload_dict["model_version"] = default_response["model_version"]
    
    if "latency_ms" not in payload_dict or not isinstance(payload_dict["latency_ms"], (int, float)):
        payload_dict["latency_ms"] = default_response["latency_ms"]
    else:
        payload_dict["latency_ms"] = max(0, int(payload_dict["latency_ms"]))
    
    if "requires_prior" not in payload_dict or not isinstance(payload_dict["requires_prior"], bool):
        payload_dict["requires_prior"] = default_response["requires_prior"]
    
    if "prior_list" not in payload_dict or not isinstance(payload_dict["prior_list"], list):
        payload_dict["prior_list"] = default_response["prior_list"]
    else:
        # String listesi olduğundan emin ol
        prior_list = []
        for item in payload_dict["prior_list"]:
            if isinstance(item, str):
                prior_list.append(item)
        payload_dict["prior_list"] = prior_list
    
    if "gate_note" not in payload_dict or not isinstance(payload_dict["gate_note"], str):
        payload_dict["gate_note"] = default_response["gate_note"]
    
    return payload_dict


def parse_llm_response(response_text: str, strategy: str = "llm", model_version: str = "tinyllama", latency_ms: int = 0) -> Dict[str, Any]:
    """
    LLM yanıtını parse eder ve doğrular
    
    Args:
        response_text: LLM'den gelen ham yanıt
        strategy: Kullanılan strateji
        model_version: Model versiyonu
        latency_ms: Yanıt süresi
    
    Returns:
        Dict: Doğrulanmış JSON yanıtı
    """
    if not response_text:
        return validate_or_fix({})
    
    # JSON'u çıkar
    json_str = extract_json_from_text(response_text)
    if not json_str:
        json_str = response_text
    
    # JSON'u temizle
    json_str = clean_json_string(json_str)
    
    try:
        # Parse et
        payload_dict = json.loads(json_str)
    except json.JSONDecodeError:
        # Parse hatası - varsayılan döndür
        payload_dict = {}
    
    # Doğrula ve düzelt
    validated = validate_or_fix(payload_dict)
    
    # Metadata ekle
    validated["strategy"] = strategy
    validated["model_version"] = model_version
    validated["latency_ms"] = latency_ms
    
    return validated


def create_emergency_response(reason: str, message: str, confidence: float = 0.95) -> Dict[str, Any]:
    """
    Acil durum yanıtı oluşturur
    """
    return {
        "primary_clinic": {
            "name": "ACİL",
            "reason": reason,
            "confidence": confidence
        },
        "secondary_clinics": [
            {
                "name": "Acil Servis",
                "reason": "Acil durumlar için",
                "confidence": 0.9
            }
        ],
        "strategy": "redflag",
        "model_version": "redflag_detector",
        "latency_ms": 0,
        "requires_prior": False,
        "prior_list": [],
        "gate_note": message
    }


def test_schema():
    """Test fonksiyonu"""
    print("🧪 Schema Test Sonuçları:")
    
    # Test 1: Geçerli JSON
    valid_json = '''
    {
        "primary_clinic": {
            "name": "Nöroloji",
            "reason": "Baş ağrısı için",
            "confidence": 0.85
        },
        "secondary_clinics": [
            {
                "name": "İç Hastalıkları (Dahiliye)",
                "reason": "Alternatif",
                "confidence": 0.7
            }
        ]
    }
    '''
    
    result = parse_llm_response(valid_json)
    print(f"✅ Geçerli JSON: {result['primary_clinic']['name']}")
    
    # Test 2: Markdown ile JSON
    markdown_json = '''
    ```json
    {
        "primary_clinic": {
            "name": "Kardiyoloji",
            "reason": "Kalp şikayetleri",
            "confidence": 0.9
        }
    }
    ```
    '''
    
    result = parse_llm_response(markdown_json)
    print(f"✅ Markdown JSON: {result['primary_clinic']['name']}")
    
    # Test 3: Eksik alanlar
    incomplete_json = '''
    {
        "primary_clinic": {
            "name": "Göz Hastalıkları"
        }
    }
    '''
    
    result = parse_llm_response(incomplete_json)
    print(f"✅ Eksik alanlar düzeltildi: {result['primary_clinic']['reason']}")
    
    # Test 4: Geçersiz JSON
    invalid_json = "Bu bir JSON değil"
    
    result = parse_llm_response(invalid_json)
    print(f"✅ Geçersiz JSON fallback: {result['primary_clinic']['name']}")
    
    # Test 5: Acil durum
    emergency = create_emergency_response("Kalp krizi şüphesi", "112'yi arayın")
    print(f"✅ Acil durum: {emergency['primary_clinic']['name']}")


if __name__ == "__main__":
    test_schema()
