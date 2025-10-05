"""Allowlist verisini okuma ve sorgu yardımcıları."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Iterable, List

# Dataset yolu ortam değişkeni ile özelleştirilebilir.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_RELATIVE = "RANDEVU/tum_klinikler_jsonl"


def _resolve_default_path() -> Path:
    """Ortam değişkeni yoksa proje içindeki dataset yolunu döndürür."""
    env_path = os.getenv("CLINIC_DATA_PATH")
    if env_path:
        return Path(env_path)
    return _PROJECT_ROOT / _DEFAULT_RELATIVE


DEFAULT_DATA_PATH = _resolve_default_path()


def _iter_dataset_files(dataset_path: Path) -> list[Path]:
    """Verilen yol dosya veya klasör olabilir, uygun JSONL kaynaklarını döndür."""
    if dataset_path.is_dir():
        files = sorted(dataset_path.glob("*.jsonl"))
        if not files:
            raise FileNotFoundError(
                f"Allowlist klasörü boş: {dataset_path}"
            )
        return files

    if dataset_path.is_file():
        return [dataset_path]

    raise FileNotFoundError(
        f"Allowlist dosyası/klasörü bulunamadı: {dataset_path}"
    )


def _clean_text(value: object) -> str | None:
    """Ham klinik adlarını sadeleştirir."""
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _normalize_basic(text: str) -> str:
    """Basit karşılaştırmalar için Türkçe karakter bağımsız normalize et."""
    translation = str.maketrans({
        "ç": "c",
        "ğ": "g",
        "ı": "i",
        "i": "i",
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
    return text.translate(translation).lower()


@lru_cache(maxsize=1)
def load_clinics(path: str | Path = DEFAULT_DATA_PATH) -> List[str]:
    """JSONL klinik listesini okur ve alfabetik sırayla döndürür."""
    dataset_path = Path(path)
    sources = _iter_dataset_files(dataset_path)

    clinics: set[str] = set()
    for source in sources:
        with source.open("r", encoding="utf-8-sig") as stream:
            for line_no, raw_line in enumerate(stream, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError as exc:  # pragma: no cover - veri hatası
                    raise ValueError(
                        f"{source} satır {line_no} JSON hatası: {exc}"
                    ) from exc

                clinic_value = (
                    payload.get("clinic")
                    or payload.get("klinik")
                )
                clinic_name = _clean_text(clinic_value)
                if not clinic_name:
                    continue
                clinics.add(clinic_name)

    return sorted(clinics, key=lambda name: _normalize_basic(name))


def has_acil(clinics: Iterable[str]) -> bool:
    """Allowlist içinde ACİL varyasyonlarını kontrol eder."""
    for clinic in clinics:
        if _normalize_basic(clinic) == "acil":
            return True
    return False


__all__ = ["load_clinics", "has_acil"]
