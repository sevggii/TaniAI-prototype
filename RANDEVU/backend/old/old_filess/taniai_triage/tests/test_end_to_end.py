"""Triyaj servisinin temel uçtan uca davranış testleri."""
from __future__ import annotations

from typing import List

import pytest
from fastapi.testclient import TestClient

from taniai_triage.core.allowlist import has_acil, load_clinics
from taniai_triage.core.canonical import canonicalize

try:
    ALLOWLIST = load_clinics()
except FileNotFoundError as exc:  # pragma: no cover - test ortamı eksik
    pytest.skip(str(exc), allow_module_level=True)


def _fake_generate(return_candidates: List[dict]):
    def _inner(text: str, allowlist, retries: int = 1):  # noqa: ARG001
        return return_candidates, []

    return _inner


@pytest.fixture
def client() -> TestClient:
    from taniai_triage.app import app

    return TestClient(app)


@pytest.mark.parametrize(
    "complaint,raw_clinic",
    [
        ("Uzun süredir öksürüyorum, balgam geliyor", "Göğüs Hastalıkları"),
        ("Eforla ortaya çıkan göğüs baskısı yaşıyorum", "Kardiyoloji"),
    ],
)
def test_llm_candidates_are_canonicalised(monkeypatch: pytest.MonkeyPatch, client: TestClient, complaint: str, raw_clinic: str) -> None:
    expected, success = canonicalize(raw_clinic, ALLOWLIST)
    if not success:
        pytest.skip(f"Allowlist içinde {raw_clinic} bulunamadı")

    monkeypatch.setattr(
        "taniai_triage.app.generate_candidates",
        _fake_generate([
            {"clinic": raw_clinic.lower(), "confidence": 0.7, "reason": "LLM tahmini"}
        ]),
    )

    response = client.post("/triage", json={"text": complaint})
    assert response.status_code == 200
    payload = response.json()
    assert payload["clinic"] == expected
    assert payload["canonicalized"] is True
    assert payload["red_flag"] is False


@pytest.mark.skipif(not has_acil(ALLOWLIST), reason="Allowlist'te ACİL bulunmuyor")
def test_red_flag_routes_to_acil(monkeypatch: pytest.MonkeyPatch, client: TestClient) -> None:
    monkeypatch.setattr(
        "taniai_triage.app.generate_candidates",
        _fake_generate([
            {"clinic": "Kardiyoloji", "confidence": 0.9, "reason": "Kalp değerlendirmesi önerisi"}
        ]),
    )

    response = client.post(
        "/triage",
        json={"text": "Göğsümde ezici ağrı var, soğuk terliyorum"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["red_flag"] is True
    assert payload["clinic"].lower().startswith("ac")
    assert any(entry["clinic"].lower().startswith("ac") for entry in payload["candidates"])
