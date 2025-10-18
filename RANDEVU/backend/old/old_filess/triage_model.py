# -*- coding: utf-8 -*-
"""
ML tabanlı klinik yönlendirme

Kaynaklar:
- MHRS doğrudan randevu alınabilen klinik listesi
- `klinik_dataset.jsonl` (her klinik için ~200 örnek şikayet)

Not: Bu modül, veri seti üzerinden basit bir TF-IDF + LinearSVC modeli
eğitir ve sadece doğrudan randevu alınabilen klinikler arasından öneri yapar.
"""

from typing import List, Dict, Any
import json
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder

from .triage_direct import load_direct_clinics, RED_FLAGS, norm


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "klinik_dataset.jsonl")
TXT_PATH = os.path.join(BASE_DIR, "MHRS_Klinik_Listesi.txt")


class ClinicTriageModel:
    def __init__(self,
                 data_path: str = DATA_PATH,
                 direct_txt_path: str = TXT_PATH) -> None:
        self.data_path = data_path
        self.direct_clinics = set(load_direct_clinics(direct_txt_path))
        self.encoder = LabelEncoder()
        self.pipeline: Pipeline | None = None
        self.trained = False

    def _load_dataset(self) -> tuple[list[str], list[str]]:
        texts: list[str] = []
        labels: list[str] = []
        with open(self.data_path, "r", encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    obj = json.loads(raw)
                except Exception:
                    continue
                complaint = obj.get("complaint") or obj.get("text") or ""
                clinic = obj.get("clinic") or obj.get("label") or ""
                if not complaint or not clinic:
                    continue
                texts.append(complaint)
                labels.append(clinic)
        return texts, labels

    def fit(self) -> None:
        if self.trained:
            return
        texts, labels = self._load_dataset()
        if not texts:
            # Veri yoksa minimal güvenli fallback
            self.pipeline = Pipeline([
                ("tfidf", TfidfVectorizer(min_df=2, ngram_range=(1, 2)) ),
                ("clf", LinearSVC())
            ])
            self.encoder.fit(["Aile Hekimliği"])  # dummy
            self.trained = True
            return

        self.encoder.fit(labels)
        y = self.encoder.transform(labels)

        self.pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                analyzer="word",
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95,
                lowercase=True,
                strip_accents=None
            )),
            ("clf", LinearSVC())
        ])
        self.pipeline.fit(texts, y)
        self.trained = True

    def suggest(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        if not self.trained:
            self.fit()

        t = norm(text)
        # Acil kontrolü (triage_direct ile aynı kırmızı bayraklar)
        for name, pat in RED_FLAGS:
            import re
            if re.search(pat, t):
                return {
                    "action": "ACIL",
                    "red_flag": name,
                    "message": "Acil bulgu tarif ediliyor. 112’yi arayın veya en yakın acile başvurun."
                }

        if not self.pipeline:
            return {"suggestions": []}

        # Decision function skorları
        clf = self.pipeline.named_steps["clf"]
        tfidf = self.pipeline.named_steps["tfidf"]
        import numpy as np

        X = tfidf.transform([text])
        scores = clf.decision_function(X)
        if scores.ndim == 1:
            scores = scores.reshape(1, -1)
        scores = scores[0]

        label_ids = np.argsort(scores)[::-1]
        ranked_labels = [self.encoder.inverse_transform([i])[0] for i in label_ids]

        # Sadece doğrudan randevu alınabilenlerden seç
        filtered: list[str] = [c for c in ranked_labels if c in self.direct_clinics]
        suggestions = filtered[:top_k]

        why = {c: "ml_score" for c in suggestions}

        # Fallback: hiçbiri yoksa yönlendirici klinikler
        if not suggestions:
            for c in ["Aile Hekimliği", "İç Hastalıkları (Dahiliye)"]:
                if c in self.direct_clinics:
                    suggestions.append(c)
            suggestions = suggestions[:top_k]
            for c in suggestions:
                why[c] = "fallback"

        return {"suggestions": suggestions, "why": why, "direct_only": True}


# Global, tembel yüklenen model
_MODEL: ClinicTriageModel | None = None


def get_triage_model() -> ClinicTriageModel:
    global _MODEL
    if _MODEL is None:
        _MODEL = ClinicTriageModel()
        _MODEL.fit()
    return _MODEL


