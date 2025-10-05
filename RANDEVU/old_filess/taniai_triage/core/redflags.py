"""Acil uyarı kriterlerini kontrol eden kurallar."""
from __future__ import annotations

import re
from typing import Tuple

# Anahtar desenler; metin küçük harfe dönüştürülüp kontrol edilir.
_CHEST_TERMS = [
    r"ezici göğüs ağr",
    r"göğsüm",  # genel göğüs şikayeti
    r"göğüs ağr",
    r"göğüste sıkış",
]

_COLD_SWEAT_TERMS = [r"soğuk ter", r"soğuk terleme"]
_RADIATION_TERMS = [r"sol kol", r"sol omuz", r"çeneye yay", r"sırta vur", r"nefes darlığı"]

_NEURO_TERMS = [
    r"ani konuşma bozul",
    r"konuşmam bozul",
    r"yüz[üı]m kay",
    r"yüz kay",
    r"kol(um)? güçs",  # kol güçsüzlüğü
    r"bacak(larım)? güçs",
    r"kolumu kaldır",
    r"bilinç kayb",
    r"bayıld",
]

_BLEEDING_TERMS = [
    r"durmayan kanama",
    r"kontrolsüz kanama",
    r"şiddetli kanama",
    r"kan(.*)durmuyor",
]

_SEVERE_PAIN_TERMS = [
    r"inanılmaz.*ağrı",
    r"dayanamıyorum",
    r"çok şiddetli.*ağrı",
    r"korkunç.*ağrı",
    r"aniden.*şiddetli",
    r"aniden.*korkunç",
    r"aniden.*inanılmaz",
    r"aniden.*dayanamıyorum",
    r"aniden.*çok.*ağrı",
    r"aniden.*çok.*şiddetli",
]

_NIGHT_PAIN_TERMS = [
    r"gece.*ağrı",
    r"gece.*tuttu",
    r"gece.*başladı",
    r"gece.*uyuyamıyorum",
    r"gece.*uyutmadı",
    r"gece.*dayanamıyorum",
    r"gece.*çok ağrı",
    r"gece.*şiddetli",
    r"gece.*diş ağrı",
    r"gece.*baş ağrı",
    r"gece.*karın ağrı",
    r"gece.*bel ağrı",
]


def _contains_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def detect_red_flag(text: str) -> Tuple[bool, str]:
    """Metinde acil uyarı kriteri varsa döner."""
    lowered = text.lower()

    chest_issue = _contains_any(lowered, _CHEST_TERMS)
    cold_sweat = _contains_any(lowered, _COLD_SWEAT_TERMS)
    radiation = _contains_any(lowered, _RADIATION_TERMS)

    if chest_issue and (cold_sweat or radiation):
        return True, "Göğüs ağrısı yüksek risk bulgularıyla tarifleniyor."

    if _contains_any(lowered, _NEURO_TERMS):
        return True, "Ani nörolojik defisit belirtileri tarifleniyor."

    if _contains_any(lowered, _BLEEDING_TERMS):
        return True, "Kontrolsüz kanama belirtileri mevcut."

    if _contains_any(lowered, _SEVERE_PAIN_TERMS):
        return True, "Şiddetli ani ağrı belirtileri mevcut."

    if _contains_any(lowered, _NIGHT_PAIN_TERMS):
        return True, "Gece ağrısı acil müdahale gerektirebilir."

    return False, ""


__all__ = ["detect_red_flag"]
