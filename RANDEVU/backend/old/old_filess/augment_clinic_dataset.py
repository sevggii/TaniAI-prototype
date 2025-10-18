#!/usr/bin/env python3
"""Generate additional clinic complaint samples using litellm.

This script reads `klinik_dataset.jsonl`, determines how many examples exist
per clinic, and asks an LLM (through litellm) to synthesize new Turkish
anamnez metinleri until each klinik reaches the desired target count.

Usage
-----
    python augment_clinic_dataset.py \
        --dataset mobile_flutter/klinik_dataset.jsonl \
        --output mobile_flutter/klinik_dataset_augmented.jsonl \
        --target-per-clinic 300 \
        --batch-size 5

Set the following environment variables before running:
    LITELLM_MODEL           (ör. `openai/gpt-4o-mini` veya `ollama/phi3`)
    LITELLM_API_KEY         (gerekiyorsa)
    LITELLM_API_BASE        (gerekiyorsa)

The script only appends novel complaints that are not already present in the
input file to avoid duplicates. Newly generated entries inherit the `clinic`
field and a synthetic `complaint` text.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

from litellm import completion

LOG = logging.getLogger("augment_clinic_dataset")


@dataclass
class Config:
    dataset_path: Path
    output_path: Path
    target_per_clinic: int
    batch_size: int
    temperature: float
    max_tokens: int
    retry_limit: int
    sleep_between_calls: float
    offline: bool
    skip_clinics: Set[str]


SYSTEM_PROMPT = (
    "You are a careful Turkish medical triage assistant. Given a clinic name, "
    "produce diverse, realistic Turkish patient complaints (anamnez metinleri). "
    "Complaints should describe symptoms, duration, context, and optionally patient "
    "intent (e.g., check-up, referral) in no more than 35 words. Use natural, "
    "colloquial Turkish. Return ONLY valid JSON with the schema: "
    "{\"complaints\":[{\"complaint\":\"...\",\"clinic\":\"...\"}]}"
)

USER_PROMPT_TEMPLATE = (
    "Klinik: {clinic}\n"
    "Üretilecek şikayet sayısı: {count}\n"
    "Kurallar:\n"
    "- Her şikayet benzersiz ve makul derecede farklı olsun.\n"
    "- Klinik adı alanına tam olarak \"{clinic}\" yaz.\n"
    "- Metinlerde kişisel veri, isim veya yaş belirtme.\n"
    "- Şikayetler yalnızca belirtilen kliniğe uygun olsun.\n"
    "JSON dışında hiçbir şey yazma."
)


def parse_args() -> Config:
    parser = argparse.ArgumentParser(description="Augment clinic dataset with LLM-generated complaints")
    parser.add_argument("--dataset", type=Path, default=Path("mobile_flutter/klinik_dataset.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("mobile_flutter/klinik_dataset_augmented.jsonl"))
    parser.add_argument("--target-per-clinic", type=int, default=300)
    parser.add_argument("--batch-size", type=int, default=5, help="How many complaints to request per LLM call")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=512)
    parser.add_argument("--retry-limit", type=int, default=3)
    parser.add_argument("--sleep-between-calls", type=float, default=0.5)
    parser.add_argument("--offline", action='store_true', help="LLM yerine yerel kural tabanlı üretici kullan")
    parser.add_argument("--skip-clinic", action='append', default=[], help="Augment aşamasında atlanacak klinik")

    args = parser.parse_args()
    return Config(
        dataset_path=args.dataset,
        output_path=args.output,
        target_per_clinic=args.target_per_clinic,
        batch_size=args.batch_size,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        retry_limit=args.retry_limit,
        sleep_between_calls=args.sleep_between_calls,
        offline=args.offline,
        skip_clinics=set(args.skip_clinic),
    )


def load_dataset(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        LOG.error("Dataset bulunamadı: %s", path)
        sys.exit(1)

    samples: List[Dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            try:
                data = json.loads(line)
                if "clinic" in data and "complaint" in data:
                    samples.append({
                        "clinic": data["clinic"].strip(),
                        "complaint": data["complaint"].strip(),
                    })
            except json.JSONDecodeError:
                LOG.warning("Bozuk satır atlandı: %s", line[:60])
    return samples


def build_index(samples: Iterable[Dict[str, str]]) -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for sample in samples:
        clinic = sample["clinic"]
        index.setdefault(clinic, []).append(sample["complaint"])
    return index


def call_llm(clinic: str, count: int, cfg: Config) -> List[Dict[str, str]]:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_TEMPLATE.format(clinic=clinic, count=count)},
    ]

    response = completion(
        model=os.environ.get("LITELLM_MODEL", "openai/gpt-4o-mini"),
        messages=messages,
        temperature=cfg.temperature,
        max_tokens=cfg.max_tokens,
        stream=False,
    )
    raw = response["choices"][0]["message"]["content"].strip()

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        LOG.warning("LLM JSON parse hatası (%s): %s", clinic, raw[:120])
        return []

    complaints = payload.get("complaints", [])
    results: List[Dict[str, str]] = []
    for entry in complaints:
        if not isinstance(entry, dict):
            continue
        complaint_text = entry.get("complaint")
        clinic_label = entry.get("clinic", clinic)
        if not complaint_text:
            continue
        results.append({
            "clinic": clinic_label.strip(),
            "complaint": complaint_text.strip(),
        })
    return results

def generate_offline_variants(clinic: str, existing_pool: List[str], count: int) -> List[Dict[str, str]]:
    """LLM olmadan basit varyasyonlar üretir."""
    if not existing_pool:
        base_samples = [f"{clinic} değerlendirmesi istiyorum."]
    else:
        base_samples = existing_pool

    prefixes = [
        "Son günlerde",
        "Bir süredir",
        "Yaklaşık iki haftadır",
        "Bugün",
        "Dün akşamdan beri",
        "Sürekli olarak",
    ]
    suffixes = [
        "",
        "kontrol için randevu almak istiyorum",
        "gündelik hayatımı etkiliyor",
        "doktor değerlendirmesi talep ediyorum",
        "ilaç kullanıp kullanmamam gerektiğini bilmiyorum",
        "şikayetlerim giderek arttı",
    ]
    clinic_highlights = {
        "Nöroloji": ["baş dönmesi yaşıyorum", "görmede bulanıklık fark ettim"],
        "İç Hastalıkları (Dahiliye)": ["genel halsizlik hissediyorum", "kan değerlerimi kontrol ettirmek istiyorum"],
        "Kardiyoloji": ["nefes nefese kalıyorum", "göğsümde baskı hissi var"],
        "Gastroenteroloji": ["karın bölgesinde kramp hissediyorum", "midemde yanma mevcut"],
        "Dermatoloji": ["cildimde kızarıklıklar oluştu", "kaşıntı geçmedi"],
    }

    highlights = clinic_highlights.get(clinic, ["şikayetim devam ediyor"])
    results: List[Dict[str, str]] = []
    for _ in range(count):
        base = random.choice(base_samples).rstrip('.')
        pref = random.choice(prefixes)
        suf = random.choice(suffixes)
        extra = random.choice(highlights)
        sentence = f"{pref} {base}".strip()
        if extra and extra not in sentence:
            sentence = f"{sentence}, {extra}"
        if suf:
            sentence = f"{sentence}, {suf}"
        if not sentence.endswith('.'):
            sentence += '.'
        sentence = sentence.replace('  ', ' ').strip()
        if sentence:
            sentence = sentence[0].upper() + sentence[1:]
        results.append({"clinic": clinic, "complaint": sentence})
    return results



def augment_clinic(clinic: str, existing: List[str], cfg: Config, seen: Set[str]) -> List[Dict[str, str]]:
    if clinic in cfg.skip_clinics:
        LOG.info("%s atlandı", clinic)
        return []

    new_samples: List[Dict[str, str]] = []
    needed = max(cfg.target_per_clinic - len(existing), 0)
    if needed <= 0:
        LOG.info("%s için yeterli örnek var (%d)", clinic, len(existing))
        return new_samples

    if cfg.offline and not existing:
        LOG.warning("%s için mevcut veri yok, offline modda atlandı", clinic)
        return new_samples

    LOG.info("%s için %d yeni örnek üretilecek", clinic, needed)
    while needed > 0:
        batch = min(cfg.batch_size, needed)

        if cfg.offline:
            generated = generate_offline_variants(clinic, existing, batch)
        else:
            for attempt in range(cfg.retry_limit):
                try:
                    generated = call_llm(clinic, batch, cfg)
                except Exception as exc:  # noqa: BLE001
                    LOG.error("LLM çağrısı hata verdi (%s): %s", clinic, exc)
                    generated = []
                if generated:
                    break
                LOG.warning("%s için yeniden denenecek (%d/%d)", clinic, attempt + 1, cfg.retry_limit)
                time.sleep(cfg.sleep_between_calls)

        if not generated:
            LOG.error("%s için örnek üretilemedi, döngü sonlandırıldı", clinic)
            break

        added = 0
        for sample in generated:
            key = f"{clinic}::{sample['complaint'].lower()}"
            if key in seen:
                continue
            seen.add(key)
            new_samples.append(sample)
            existing.append(sample['complaint'])
            added += 1
        LOG.info("%s için %d yeni örnek eklendi", clinic, added)
        needed -= added
        time.sleep(cfg.sleep_between_calls)

    return new_samples


def write_dataset(base_samples: List[Dict[str, str]], additions: List[Dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        for sample in base_samples + additions:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
    LOG.info("Toplam %d örnek %s dosyasına yazıldı", len(base_samples) + len(additions), output)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    cfg = parse_args()

    samples = load_dataset(cfg.dataset_path)
    index = build_index(samples)
    seen = {f"{s['clinic']}::{s['complaint'].lower()}" for s in samples}

    additions: List[Dict[str, str]] = []
    for clinic, complaints in index.items():
        additions.extend(augment_clinic(clinic, complaints, cfg, seen))

    if additions:
        write_dataset(samples, additions, cfg.output_path)
    else:
        LOG.info("Yeni örnek eklenmedi; mevcut dosya değişmedi")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        LOG.warning("İşlem kullanıcı tarafından durduruldu")
        sys.exit(130)
