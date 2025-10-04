"""LLM tabanlı klinik öneri analizörü.

Bu modül hem HTTP sunucusu (clinic_llm_server.py) hem de FastAPI katmanı
(mobile_flutter/api/randevu_api.py) tarafından paylaşılır. LLM çağrıları
litellm aracılığıyla yönetilir; başarısız durumlarda kural tabanlı fallback
çalışır.
"""

import json
import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from litellm import completion

from triage.schema import parse_llm_response

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


DEFAULT_DATASET_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "mobile_flutter",
    "klinik_dataset.jsonl",
)


@dataclass
class AnalyzerConfig:
    """LLM ve veri kümesi yapılandırması."""

    dataset_path: str = os.getenv("CLINIC_DATASET_PATH", DEFAULT_DATASET_PATH)
    model: str = os.getenv("LITELLM_MODEL", "ollama/tinyllama")
    api_base: Optional[str] = os.getenv("LITELLM_API_BASE")
    api_key: Optional[str] = os.getenv("LITELLM_API_KEY")
    temperature: float = float(os.getenv("LITELLM_TEMPERATURE", "0.1"))
    max_tokens: int = int(os.getenv("LITELLM_MAX_TOKENS", "256"))


class ClinicLLMAnalyzer:
    """Litellm destekli klinik öneri analizörü."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        self.config = config or AnalyzerConfig()
        self.clinic_examples: Dict[str, List[str]] = {}
        self._load_dataset()

    # ------------------------------------------------------------------
    # Veri işlemleri
    # ------------------------------------------------------------------
    def _load_dataset(self) -> None:
        """Klinik örneklerini bellek içine alır."""
        dataset_path = self.config.dataset_path
        if not os.path.exists(dataset_path):
            logger.warning("Klinik veri kümesi bulunamadı: %s", dataset_path)
            return

        loaded = 0
        with open(dataset_path, "r", encoding="utf-8") as dataset_file:
            for line in dataset_file:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                clinic = data.get("clinic")
                complaint = data.get("complaint")
                if not clinic or not complaint:
                    continue
                self.clinic_examples.setdefault(clinic, []).append(complaint)
                loaded += 1
        logger.info("Klinik veri kümesi yüklendi: %s örnek", loaded)

    def _retrieve_similar_examples(self, complaint: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Basit anahtar kelime eşleşmesi ile benzer örnekleri bulur."""
        complaint_lower = complaint.lower()
        keywords = [word for word in complaint_lower.split() if len(word) > 2]
        if not keywords:
            return []

        scored: List[Dict[str, Any]] = []
        for clinic, examples in self.clinic_examples.items():
            for example in examples:
                score = sum(1 for keyword in keywords if keyword in example.lower())
                if score > 0:
                    scored.append({
                        "clinic": clinic,
                        "complaint": example,
                        "score": score,
                    })
        scored.sort(key=lambda item: item["score"], reverse=True)
        return scored[:top_k]

    # ------------------------------------------------------------------
    # LLM ve fallback analizi
    # ------------------------------------------------------------------
    def analyze_complaint(self, complaint: str) -> Dict[str, Any]:
        """LLM ile klinik analizi yapar; gerekirse fallback kullanır."""
        complaint = (complaint or "").strip()
        if not complaint:
            return {
                "success": False,
                "error": "Boş şikayet metni",
                "analysis": self._fallback_analysis(""),
            }

        similar_examples = self._retrieve_similar_examples(complaint)
        prompt_messages = self._build_prompt(complaint, similar_examples)

        # LLM'i geçici olarak bypass et - sadece fallback kullan
        logger.info("LLM bypass edildi, sadece fallback kullanılıyor")
        fallback_result = self._fallback_analysis(complaint)
        return {
            "success": True,
            "analysis": fallback_result,
        }

        return {
            "success": True,
            "analysis": self._fallback_analysis(complaint),
            "method": "fallback",
            "model": "rule_based",
        }

    def _call_llm(self, messages: List[Dict[str, str]]) -> Optional[str]:
        """litellm aracılığıyla modeli çağırır ve düz metin döndürür."""
        request_kwargs: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        if self.config.api_base:
            request_kwargs["api_base"] = self.config.api_base
        if self.config.api_key:
            request_kwargs["api_key"] = self.config.api_key

        response = completion(**request_kwargs)
        choices = response.get("choices") or []
        if not choices:
            return None
        message = choices[0].get("message", {})
        content = message.get("content")
        return content.strip() if isinstance(content, str) else None

    def _build_prompt(
        self,
        complaint: str,
        similar_examples: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """LLM için sistem ve kullanıcı mesajlarını oluşturur."""
        schema_description = (
            '{"primary_clinic":{"name":"Ortopedi ve Travmatoloji","reason":"El yaralanması için","confidence":0.9},'
            '"secondary_clinics":[{"name":"Acil Servis","reason":"Kanama kontrolü için","confidence":0.8}]}'
        )
        system_prompt = (
            "Sen Türk MHRS sistemi için triage asistanısın. "
            "Hasta şikayetini analiz et ve en uygun kliniği öner. "
            "ÖNEMLİ: Kanama, yaralanma, kırık → Ortopedi ve Travmatoloji veya Acil Servis. "
            "Baş ağrısı, nörolojik belirtiler → Nöroloji. "
            "Göğüs ağrısı, kalp belirtileri → Kardiyoloji. "
            "Mide, karın ağrısı → İç Hastalıkları. "
            "Sadece JSON formatında yanıt ver: "
            + schema_description +
            " Acil durumlarda (kontrolsüz kanama, göğüs ağrısı, felç belirtileri) primary_clinic.name='ACİL' yap."
        )

        similar_text = ""
        if similar_examples:
            formatted = [
                f"- Şikayet: {item['complaint']} → Klinik: {item['clinic']}"
                for item in similar_examples
            ]
            similar_text = "Benzer örnekler:\n" + "\n".join(formatted)

        user_prompt = (
            f"Hasta şikayeti: {complaint}\n"
            f"{similar_text}\n"
            "Bu şikayet için en uygun klinik hangisidir? Sadece JSON formatında yanıt ver:"
        )

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    # ------------------------------------------------------------------
    # Fallback analizi
    # ------------------------------------------------------------------
    def _fallback_analysis(self, complaint: str) -> Dict[str, Any]:
        """Basit kural tabanlı öneriler üretir."""
        complaint_lower = complaint.lower()

        rules = [
            # ÖNCE: Kombine belirtiler (acil durumlar) - EN YÜKSEK ÖNCELİK
            (
                ["bulanıyor", "dönüyor", "bayıl", "baygın", "halsiz", "terleme"],
                {
                    "primary_clinic": {
                        "name": "Acil Servis",
                        "reason": "Çoklu belirti - acil değerlendirme gerekli",
                        "confidence": 0.95,
                    },
                    "secondary_clinics": [
                        {
                            "name": "İç Hastalıkları (Dahiliye)",
                            "reason": "Genel değerlendirme",
                            "confidence": 0.7,
                        }
                    ],
                },
            ),
            (
                ["göğüs", "ağrı", "nefes", "darlığı", "çarpıntı", "terleme"],
                {
                    "primary_clinic": {
                        "name": "Acil Servis",
                        "reason": "Kalp krizi belirtileri - acil müdahale",
                        "confidence": 0.95,
                    },
                    "secondary_clinics": [
                        {
                            "name": "Kardiyoloji",
                            "reason": "Kalp değerlendirmesi",
                            "confidence": 0.8,
                        }
                    ],
                },
            ),
            (
                ["baş", "ağrı", "bulanıyor", "kusma", "mide"],
                {
                    "primary_clinic": {
                        "name": "Acil Servis",
                        "reason": "Çoklu belirti - acil değerlendirme",
                        "confidence": 0.9,
                    },
                    "secondary_clinics": [
                        {
                            "name": "Nöroloji",
                            "reason": "Nörolojik değerlendirme",
                            "confidence": 0.7,
                        }
                    ],
                },
            ),
            (
                ["düştüm", "çarptım", "travma", "yaralandım", "kırık", "çıkık", "kanıyor", "kanama", "kesik", "el", "kol", "bacak"],
                {
                    "primary_clinic": {
                        "name": "Ortopedi ve Travmatoloji",
                        "reason": "Travma ve yaralanma şikayetleri",
                        "confidence": 0.9,
                    },
                    "secondary_clinics": [
                        {
                            "name": "Acil Servis",
                            "reason": "Acil değerlendirme",
                            "confidence": 0.8,
                        }
                    ],
                },
            ),
            (
                ["baş", "kafa", "migren", "baş ağrısı"],
                {
                    "primary_clinic": {
                        "name": "Nöroloji",
                        "reason": "Baş ağrısı ve nörolojik belirtiler",
                        "confidence": 0.8,
                    },
                    "secondary_clinics": [
                        {
                            "name": "İç Hastalıkları (Dahiliye)",
                            "reason": "Genel değerlendirme",
                            "confidence": 0.6,
                        }
                    ],
                },
            ),
            (
                ["mide", "karın", "bulantı", "kusma"],
                {
                    "primary_clinic": {
                        "name": "İç Hastalıkları (Dahiliye)",
                        "reason": "Sindirim sistemi şikayetleri",
                        "confidence": 0.8,
                    },
                    "secondary_clinics": [
                        {
                            "name": "Gastroenteroloji",
                            "reason": "Uzman değerlendirme",
                            "confidence": 0.7,
                        }
                    ],
                },
            ),
            (
                ["kalp", "göğüs", "çarpıntı", "nefes darlığı"],
                {
                    "primary_clinic": {
                        "name": "Kardiyoloji",
                        "reason": "Kalp ve damar sistemi belirtileri",
                        "confidence": 0.85,
                    },
                    "secondary_clinics": [
                        {
                            "name": "İç Hastalıkları (Dahiliye)",
                            "reason": "Ön değerlendirme",
                            "confidence": 0.7,
                        }
                    ],
                },
            ),
            (
                ["çocuk", "bebek", "oğlum", "kızım"],
                {
                    "primary_clinic": {
                        "name": "Çocuk Sağlığı ve Hastalıkları",
                        "reason": "Pediatrik şikayet",
                        "confidence": 0.85,
                    },
                    "secondary_clinics": [
                        {
                            "name": "Aile Hekimliği",
                            "reason": "Genel rehberlik",
                            "confidence": 0.65,
                        }
                    ],
                },
            ),
        ]

        for keywords, recommendation in rules:
            if any(keyword in complaint_lower for keyword in keywords):
                recommendation.setdefault("strategy", "fallback")
                recommendation.setdefault("model_version", "rule_based")
                recommendation.setdefault("latency_ms", 0)
                recommendation.setdefault("requires_prior", False)
                recommendation.setdefault("prior_list", [])
                recommendation.setdefault("gate_note", "")
                return recommendation

        default_response = {
            "primary_clinic": {
                "name": "Aile Hekimliği",
                "reason": "Genel sağlık değerlendirmesi",
                "confidence": 0.7,
            },
            "secondary_clinics": [
                {
                    "name": "İç Hastalıkları (Dahiliye)",
                    "reason": "Detaylı inceleme",
                    "confidence": 0.6,
                }
            ],
            "strategy": "fallback",
            "model_version": "rule_based",
            "latency_ms": 0,
            "requires_prior": False,
            "prior_list": [],
            "gate_note": "",
        }
        return default_response


_analyzer_instance: Optional[ClinicLLMAnalyzer] = None


def get_clinic_analyzer() -> ClinicLLMAnalyzer:
    """Tekil analizör örneğini döndürür."""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = ClinicLLMAnalyzer()
    return _analyzer_instance
