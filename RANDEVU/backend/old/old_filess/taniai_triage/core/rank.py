"""LLM adaylarını kural tabanlı olarak sonuca dönüştürür."""
from __future__ import annotations

from typing import Iterable, List

from .canonical import canonicalize


def _default_candidate(clinic: str) -> dict:
    return {"clinic": clinic, "confidence": 0.4, "reason": "Kural tabanlı seçim."}


def _select_acil_name(allowlist: Iterable[str]) -> str | None:
    acil_name, success = canonicalize("ACİL", allowlist)
    return acil_name if success else None


def determine_triage(
    text: str,
    candidates: Iterable[dict],
    allowlist: Iterable[str],
    red_flag: bool,
    red_flag_reason: str,
    llm_notes: Iterable[str],
) -> dict:
    """Kandideleri puanlayıp son klinik kararını döndürür."""
    allowlist_list = list(allowlist)
    candidate_view: List[dict] = []
    explanations: List[str] = []
    best_name: str | None = None
    best_conf = -1.0
    canonicalized_flag = False
    fallback_explanation = "Allowlist ile eşleşen aday bulunamadı."

    for item in candidates:
        raw_name = str(item.get("clinic", "")).strip()
        if not raw_name:
            continue
        canonical_name, matched = canonicalize(raw_name, allowlist_list)
        if not canonical_name:
            continue
        confidence = item.get("confidence", 0.5)
        try:
            confidence_val = float(confidence)
        except (TypeError, ValueError):
            confidence_val = 0.5
        reason = str(item.get("reason", "")) or "LLM gerekçesi verilmedi."
        candidate_row = {
            "clinic": canonical_name,
            "confidence": confidence_val,
            "reason": reason,
        }
        candidate_view.append(candidate_row)
        if confidence_val > best_conf:
            best_conf = confidence_val
            best_name = canonical_name
            canonicalized_flag = matched
            fallback_explanation = reason

    if red_flag:
        explanations.append(red_flag_reason or "Acil uyarı kriteri tetiklendi.")
        acil_name = _select_acil_name(allowlist_list)
        if acil_name:
            best_name = acil_name
            canonicalized_flag = True
            if not any(row["clinic"] == acil_name for row in candidate_view):
                candidate_view.insert(0, _default_candidate(acil_name))
        # ACİL yoksa mevcut en yüksek skorla devam edilir.

    if best_name is None:
        if not allowlist_list:
            raise ValueError("Allowlist boş, seçim yapılamıyor.")
        best_name = allowlist_list[0]
        canonicalized_flag = True
        candidate_view = candidate_view or [_default_candidate(best_name)]
        explanations.append("LLM adayları kullanılamadı, varsayılan klinik seçildi.")
    else:
        explanations.append(fallback_explanation)

    for note in llm_notes:
        explanations.append(f"LLM notu: {note}")

    return {
        "clinic": best_name,
        "candidates": candidate_view,
        "red_flag": red_flag,
        "explanations": explanations,
        "canonicalized": canonicalized_flag,
    }


__all__ = ["determine_triage"]
