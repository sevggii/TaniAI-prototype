#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
test_system.py
----------------
Basit ama akıllı bir triyaj demo testi.

Değişiklikler:
- BetterTriageSystem: ağırlıklı anahtar kelime tabanı, çocuk/erişkin ayrımı,
  negatif ipuçları ve genişletilmiş ACİL kuralları.
- Çıktı formatı: önceki test çıktısına çok benzer; ACİL durumları ayrı vurgular.
"""

import re
import unicodedata
from typing import List, Dict, Any


# =============== Yardımcılar ===============

def _normalize(txt: str) -> str:
    """Küçük harf + diakritik temizliği + sadeleştirme (Türkçe harfler korunur)."""
    t = txt.lower()
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    t = re.sub(r"[^a-z0-9çğıöşü\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


# =============== Triage Sistemi ===============

class BetterTriageSystem:
    """
    Ağırlıklı anahtar-kelime triage (MHRS isimleriyle hizalı çekirdek set).
    - Token bazlı eşleşme
    - Ağırlık (weight), ceza (penalty), pediatri/erişkin sinyalleri
    - Geniş ACİL kuralları
    """

    def __init__(self):
        # Sık başvuru alanları için çekirdek klinikler
        self.clinics: Dict[str, Dict[str, float]] = {
            "Aile Hekimliği": {
                "genel": 1.0, "kontrol": 0.6, "ates": 0.6, "halsizlik": 0.6
            },
            "İç Hastalıkları (Dahiliye)": {
                "mide": 1.0, "bulantı": 1.0, "kusma": 0.8, "karin": 1.0,
                "ishal": 0.8, "ates": 0.4, "halsizlik": 0.4
            },
            "Nöroloji": {
                "bas": 1.0, "migren": 1.0, "bas donmesi": 1.0,
                "bulanik": 0.8, "uyusma": 0.8, "konusma": 0.7, "agrı": 0.4
            },
            "Kardiyoloji": {
                "gogus agrisi": 1.0, "gogus": 0.9, "cok ter": 0.6, "soguk ter": 1.0,
                "nefes darligi": 0.8, "carpinti": 0.9, "tansiyon": 0.7
            },
            "Göğüs Hastalıkları": {
                "oksuruk": 0.9, "balgam": 0.7, "nefes darligi": 0.9, "hirlama": 0.7, "astim": 1.0
            },
            "Genel Cerrahi": {
                "safra": 1.0, "fitik": 1.0, "apandisit": 1.0, "karin sag alt": 1.0
            },
            "Deri ve Zührevi Hastalıkları (Cildiye)": {
                "kasinti": 1.0, "dokuntu": 0.9, "kizariklik": 0.8, "egzama": 1.0, "sivilce": 0.5
            },
            "Göz Hastalıkları": {
                "goz": 0.8, "gor me": 1.0, "goru": 1.0, "bulanik": 1.0, "kizariklik": 0.6, "yasar": 0.5
            },
            "Kulak Burun Boğaz Hastalıkları": {
                "bogaz agrisi": 1.0, "bogaz": 0.7, "burun tikaliligi": 0.9, "kulak agrisi": 0.9, "sinuzit": 0.8
            },
            "Üroloji": {
                "idrar": 1.0, "yanma": 1.0, "sik idrara cikma": 0.9, "kanli idrar": 1.0, "bobrek": 0.8
            },
            "Kadın Hastalıkları ve Doğum": {
                "adet": 1.0, "kanama": 1.0, "hamile": 1.0, "agrili adet": 0.9, "rahim": 0.7, "yumurtalik": 0.7
            },
            "Çocuk Sağlığı ve Hastalıkları": {
                "cocuk": 1.3, "bebek": 1.3, "ates": 1.0, "oksuruk": 0.9, "ishal": 0.8, "kusma": 0.7
            },
        }

        # Normalizasyonlu anahtar tabanı; "baş dönmesi" gibi ifadelerde birleşik varyantları da yakalar
        self._expand_keywords()

        # Negatif ipuçları (bazı branşların skorunu hafifçe azalt)
        self.negative_hints = {
            "Nöroloji": {"goz": -0.3, "kizariklik": -0.2},
            "İç Hastalıkları (Dahiliye)": {"goz": -0.2, "kulak": -0.2},
        }

        # Çocuk/erişkin sinyalleri
        self.child_signals = {"cocuk", "bebek", "oglum", "kizim", "yeni dogan", "ogrencim"}

        # ACİL kuralları (geniş)
        self.urgent_rules = [
            (r"\bgog(us|uz)\b.*\bagri\b.*\b(soguk|cok)\s*ter", "Kalp krizi olası"),
            (r"\ban(i|iden)\b.*\bgog(us|uz).*\bagri\b", "Ani göğüs ağrısı"),
            (r"\binme\b|\byuz(d)?e?\s*kaymasi\b|\bkonusma bozuklugu\b|\bkol(bacak)?\s*gucsuzlugu\b", "İnme olası"),
            (r"\bbilinc\b.*\b(kayb|kapal)", "Bilinç kaybı"),
            (r"\bkontrolsuz\b.*\bkanama\b", "Kontrolsüz kanama"),
            (r"\bnefes darligi\b.*\ban(i|iden)\b|\bsiddetli nefes darligi\b", "Ciddi solunum sıkıntısı"),
            (r"\bhamile\b.*\b(siddetli agri|kanama)\b", "Gebelik acili"),
        ]

    def _expand_keywords(self):
        expanded = {}
        for clinic, kws in self.clinics.items():
            bucket = {}
            for k, w in kws.items():
                nk = _normalize(k)
                bucket[nk] = w
                # boşlukları kaldırılmış varyant
                compact = nk.replace(" ", "")
                if compact != nk:
                    bucket[compact] = max(bucket.get(compact, 0.0), w * 0.9)
                # basit kök düzeltmesi (ör. görme/görü)
                if "gor" in nk and " " in nk:
                    bucket["gor"] = max(bucket.get("gor", 0.0), w * 0.8)
            expanded[clinic] = bucket
        self.clinics = expanded

    def _is_urgent(self, text_norm: str):
        for rx, reason in self.urgent_rules:
            if re.search(rx, text_norm):
                return True, reason
        return False, ""

    def suggest(self, complaint: str, top_k: int = 3) -> List[Dict[str, Any]]:
        t = _normalize(complaint)
        urgent, why = self._is_urgent(t)
        if urgent:
            return [{
                "clinic": "ACİL",
                "confidence": 1.0,
                "reason": f"ACİL DURUM: {why}",
                "rank": 1,
                "urgent": True,
                "message": "112'yi arayın veya en yakın acile başvurun!"
            }]

        tokens = set(t.split())
        is_child = any(sig in t for sig in self.child_signals)

        scores: Dict[str, float] = {}
        details: Dict[str, list] = {}

        for clinic, kws in self.clinics.items():
            s = 0.0
            hits = []
            # Pozitif sinyaller
            for k, w in kws.items():
                if k in t or all(tok in tokens for tok in k.split()):
                    s += w
                    hits.append(k)
            # Negatif sinyaller
            for k, pen in self.negative_hints.get(clinic, {}).items():
                if k in tokens or k in t:
                    s += pen

            # Pediatri boost/penalty
            if clinic == "Çocuk Sağlığı ve Hastalıkları":
                s += 0.7 if is_child else -0.6
            else:
                if is_child:
                    s -= 0.3

            scores[clinic] = s
            details[clinic] = hits

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        out = []
        rank = 1
        for clinic, s in ranked[: top_k * 2]:
            if s <= 0:
                continue
            conf = min(1.0, max(0.05, s / 3.0))  # kaba normalizasyon
            reason = ", ".join(details[clinic]) or "genel semptom profili"
            out.append({
                "clinic": clinic,
                "confidence": round(conf, 2),
                "reason": reason,
                "rank": rank,
                "urgent": False
            })
            rank += 1
            if len(out) >= top_k:
                break

        if not out:
            out = [{
                "clinic": "Aile Hekimliği",
                "confidence": 0.35,
                "reason": "Yeterli sinyal yok → güvenli başlangıç",
                "rank": 1,
                "urgent": False
            }]

        return out


# Fabrika fonksiyonu (eski isimle uyum için)
def get_simple_triage():
    return BetterTriageSystem()


# =============== Demo/Test Koşucu ===============

def run_demo():
    print("🔄 Sistem test ediliyor...")
    triage = get_simple_triage()
    print("✅ Sistem yüklendi!\n")

    examples = [
        "Başım çok ağrıyor ve mide bulantım var",
        "Aniden göğsümde ezici ağrı var, soğuk terliyorum",
        "Çocuğumda ateş ve öksürük var",
        "Gözlerim bulanık görüyor",
    ]

    print("📊 Test Sonuçları:")
    print("=" * 50, end="\n\n")

    for idx, text in enumerate(examples, 1):
        print(f"{idx}. Şikayet: {text}")
        print("-" * 30)
        res = triage.suggest(text, top_k=3)
        if res and res[0].get("urgent"):
            top = res[0]
            print(f"   🚨 ACİL ACİL - Güven: {top['confidence']:.2f}")
            print(f"   Sebep: {top['reason']}")
            message = top.get('message', '112\'yi arayın veya en yakın acile başvurun!')
            print(f"   Mesaj: {message}")
            continue

        for r in res:
            print(f"   📋 Normal {r['clinic']} - Güven: {r['confidence']:.2f}")
            print(f"   Sebep: {r['reason']}")
        print("")

    print("✅ Test tamamlandı!")

if __name__ == "__main__":
    run_demo()


'''
🔄 Sistem test ediliyor...
✅ Sistem yüklendi!

📊 Test Sonuçları:
==================================================

1. Şikayet: Başım çok ağrıyor ve mide bulantım var
------------------------------
   📋 Normal İç Hastalıkları (Dahiliye) - Güven: 0.67
   Sebep: mide, bulantı
   📋 Normal Nöroloji - Güven: 0.47
   Sebep: bas, agrı

2. Şikayet: Aniden göğsümde ezici ağrı var, soğuk terliyorum
------------------------------
   📋 Normal Kardiyoloji - Güven: 0.33
   Sebep: soguk ter
   📋 Normal Nöroloji - Güven: 0.13
   Sebep: agrı

3. Şikayet: Çocuğumda ateş ve öksürük var
------------------------------
   📋 Normal Çocuk Sağlığı ve Hastalıkları - Güven: 0.43
   Sebep: ates, oksuruk
   📋 Normal Göğüs Hastalıkları - Güven: 0.30
   Sebep: oksuruk
   📋 Normal Aile Hekimliği - Güven: 0.20
   Sebep: ates

4. Şikayet: Gözlerim bulanık görüyor
------------------------------
   📋 Normal Göz Hastalıkları - Güven: 0.87
   Sebep: goz, gor, goru

✅ Test tamamlandı!

'''