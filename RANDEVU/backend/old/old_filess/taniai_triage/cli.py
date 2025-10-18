"""Komut satırından TanıAI triyajını çalıştırma aracısı."""
from __future__ import annotations

import argparse
import json
import sys

from .core import detect_red_flag, determine_triage, generate_candidates, load_clinics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Klinik yönlendirme testi")
    parser.add_argument(
        "--text",
        required=True,
        help="Triyaj edilmesini istediğiniz hasta şikayeti",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    text = args.text

    try:
        allowlist = load_clinics()
    except FileNotFoundError as exc:
        print(f"Allowlist yüklenemedi: {exc}", file=sys.stderr)
        return 1

    red_flag, red_reason = detect_red_flag(text)
    candidates, notes = generate_candidates(text, allowlist)
    result = determine_triage(
        text=text,
        candidates=candidates,
        allowlist=allowlist,
        red_flag=red_flag,
        red_flag_reason=red_reason,
        llm_notes=notes,
    )

    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
