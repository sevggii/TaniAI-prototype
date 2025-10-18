"""Klinik isimlerini allowlist'e kanonik bağlayan yardımcılar."""
from __future__ import annotations

import unicodedata
from typing import Iterable, Tuple

from rapidfuzz import fuzz, process

# Türkçe karakterleri ASCII temsile indirgemek için dönüşüm tablosu.
_TURKISH_TRANSLATION = str.maketrans({
    "ç": "c",
    "ğ": "g",
    "ı": "i",
    "ö": "o",
    "ş": "s",
    "ü": "u",
    "Ç": "c",
    "Ğ": "g",
    "İ": "i",
    "Ö": "o",
    "Ş": "s",
    "Ü": "u",
    "I": "i",
})


def _fold(text: str) -> str:
    """Türkçe büyük/küçük farkını minimize eden sadeleştirme."""
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(char for char in normalized if not unicodedata.combining(char))
    return stripped.translate(_TURKISH_TRANSLATION).lower()


def canonicalize(name: str, allowlist: Iterable[str]) -> Tuple[str | None, bool]:
    """Girilen klinik adını allowlist'teki en yakın eşleşmeye çeker."""
    if not name:
        return None, False

    candidate = name.strip()
    if not candidate:
        return None, False

    choices = list(allowlist)
    if not choices:
        return None, False

    folded_candidate = _fold(candidate)
    folded_choices = {choice: _fold(choice) for choice in choices}

    match = process.extractOne(
        folded_candidate,
        folded_choices,
        scorer=fuzz.WRatio,
        score_cutoff=80,
        processor=None,
    )
    if not match:
        return None, False

    matched_value = match[0]
    return matched_value, True


__all__ = ["canonicalize"]
