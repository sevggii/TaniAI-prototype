"""LiteLLM ile aday klinik önerisi üreten katman."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable, List, Tuple, TypedDict

from litellm import completion

DEFAULT_MODEL = "ollama/llama3:8b"
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompt_templates" / "triage_system.txt"


class Candidate(TypedDict, total=False):
    clinic: str
    reason: str
    confidence: float


def _render_system_prompt(allowlist: Iterable[str]) -> str:
    """Allowlist'i sisteme gömerek LLM'i sıkı sınırlar."""
    allowlist_csv = ", ".join(sorted(allowlist))
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("<{{allowlist_csv}}>", allowlist_csv)


def _call_llm(text: str, system_prompt: str) -> str:
    """LiteLLM üzerinden tek çağrı yapar."""
    model_name = os.getenv("LITELLM_MODEL", DEFAULT_MODEL)
    timeout = float(os.getenv("TIMEOUT_S", "30"))
    response = completion(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text.strip()},
        ],
        temperature=0.2,
        max_tokens=256,
        timeout=timeout,
    )
    return response["choices"][0]["message"]["content"]


_JSON_SNIPPET = re.compile(r"\{.*\}", re.DOTALL)


def _extract_json(raw: str) -> dict:
    """LLM yanıtından güvenilir JSON çıkarmayı dener."""
    snippet_match = _JSON_SNIPPET.search(raw)
    snippet = snippet_match.group(0) if snippet_match else raw
    cleaned = snippet.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```[a-zA-Z0-9]*\n", "", cleaned)
        cleaned = cleaned.rstrip("`").strip()
    return json.loads(cleaned)


def _normalise_candidates(payload: dict) -> List[Candidate]:
    """LLM çıktısını aday listesine dönüştürür."""
    candidates = payload.get("candidates", [])
    normalised: List[Candidate] = []
    for raw in candidates[:3]:
        clinic = str(raw.get("clinic", "")).strip()
        if not clinic:
            continue
        reason = str(raw.get("reason", "")) or "Gerekçe belirtilmedi."
        confidence = raw.get("confidence")
        try:
            confidence_val = float(confidence)
        except (TypeError, ValueError):
            confidence_val = 0.5
        normalised.append(
            Candidate(clinic=clinic, reason=reason, confidence=confidence_val)
        )
    return normalised or [Candidate(clinic="", reason="Boş yanıt", confidence=0.5)]


def _fallback_candidates(allowlist: Iterable[str], error_message: str) -> List[Candidate]:
    """JSON çözülemediğinde basit kural tabanlı aday üretir."""
    choices = list(allowlist)
    if choices:
        clinic = choices[0]
    else:
        clinic = "Genel Klinik"
    if error_message:
        reason = (
            "LLM yanıtı değerlendirilemedi; hata notu: " + error_message
        )
    else:
        reason = "LLM yanıtı değerlendirilemedi, allowlist'in ilk kliniği önerildi."
    return [Candidate(clinic=clinic, reason=reason, confidence=0.4)]


def generate_candidates(text: str, allowlist: Iterable[str], retries: int = 1) -> Tuple[List[Candidate], List[str]]:
    """LLM'den aday klinik listesi döndürür, gereğinde fallback kullanır."""
    system_prompt = _render_system_prompt(allowlist)
    attempts = retries + 1
    notes: List[str] = []

    for attempt in range(attempts):
        try:
            raw = _call_llm(text, system_prompt)
        except Exception as exc:  # pragma: no cover - ağ hataları
            notes.append(f"LiteLLM hatası: {exc}")
            continue

        try:
            payload = _extract_json(raw)
            candidates = _normalise_candidates(payload)
            if candidates and candidates[0].get("clinic"):
                return candidates, notes
            notes.append("LLM aday listesi boş geldi.")
        except json.JSONDecodeError as exc:
            notes.append(f"JSON ayrıştırma hatası: {exc}")
            continue

    fallback = _fallback_candidates(allowlist, "; ".join(notes))
    return fallback, notes


__all__ = ["generate_candidates", "Candidate"]
