"""FastAPI tabanlı TanıAI triyaj servisi."""
from __future__ import annotations

import os
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .core import (
    detect_red_flag,
    determine_triage,
    generate_candidates,
    load_clinics,
)

app = FastAPI(title="TanıAI Klinik Triyaj", version="1.0.0")


class TriageRequest(BaseModel):
    text: str = Field(..., min_length=3, description="Hasta tarafından tariflenen şikayet")


class HealthResponse(BaseModel):
    status: str
    allowlist_size: int
    model: str


@app.on_event("startup")
def _load_allowlist_on_startup() -> None:
    """Servis ayağa kalkarken allowlist'i cache'e al."""
    try:
        load_clinics()
    except FileNotFoundError as exc:  # pragma: no cover - konfigürasyon hatası
        raise RuntimeError(str(exc)) from exc


@app.get("/healthz", response_model=HealthResponse)
def healthcheck() -> Dict[str, Any]:
    """Basit sağlık kontrol uç noktası."""
    clinics = load_clinics()
    model_name = os.getenv("LITELLM_MODEL", "ollama/llama3:8b")
    return {"status": "ok", "allowlist_size": len(clinics), "model": model_name}


@app.post("/triage")
def triage(request: TriageRequest) -> JSONResponse:
    """Şikayet metnini klinik önerisine dönüştürür."""
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Metin boş olamaz.")

    try:
        allowlist = load_clinics()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

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

    if not result.get("clinic"):
        raise HTTPException(status_code=422, detail="Klinik belirlenemedi.")

    return JSONResponse(content=result)


__all__ = ["app"]
