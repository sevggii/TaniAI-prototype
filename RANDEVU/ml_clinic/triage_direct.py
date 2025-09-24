# -*- coding: utf-8 -*-
import re, json

TXT_PATH = "D:/TaniAI-prototype/RANDEVU/ml/MHRS_Klinik_Listesi.txt"

def load_direct_clinics(path=TXT_PATH):
    direct = []
    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or "→ ❌" in line:
                continue
            # "12. ...", "24) ..." gibi numarayı at
            name = line
            if ")" in line:
                name = line.split(")", 1)[1].strip()
            elif ". " in line[:5]:
                name = line.split(". ", 1)[1].strip()
            if name:
                direct.append(name)
    return direct

DIRECT = load_direct_clinics()

# Çok basit kurallar (başlangıç listesi)
RULES = [
    (r"\bçocuk\b|\b(\d{1,2}) yaş\b|\boğlum\b|\bkızım\b", "Çocuk Sağlığı ve Hastalıkları"),
    (r"\böksürük\b|\bnefes darl[ıi]ğ[ıi]\b|\bhırılt[ıi]\b|\bbalgam\b", "Göğüs Hastalıkları"),
    (r"\bgöğüs ağr[ıi]s[ıi]\b|\bçarpınt[ıi]\b|\bbayılma\b", "Kardiyoloji"),
    (r"\bşiddetli baş ağr[ıi]s[ıi]\b|\bmigren\b|\bbaş dönmesi\b|\buyuşma\b|\bfelç\b", "Nöroloji"),
    (r"\bboğaz ağr[ıi]s[ıi]\b|\bkulak ağr[ıi]s[ıi]\b|\bgeniz akınt[ıi]s[ıi]\b|\bburun t[ıi]kan[ıi]kl[ıi]ğ[ıi]\b", "Kulak Burun Boğaz Hastalıkları"),
    (r"\bgörme bulan[ıi]kl[ıi]ğ[ıi]\b|\bgöz ağr[ıi]s[ıi]\b|\bışığa hassasiyet\b|\bçapak\b", "Göz Hastalıkları"),
    (r"\bkarın ağr[ıi]s[ıi]\b|\bmidem (bulan[ıi]yor|bulan[ıi]nca|ağr[ıi]yor)\b|\bishal\b|\bkab[ıi]zl[ıi]k\b", "İç Hastalıkları (Dahiliye)"),
    (r"\bbel ağr[ıi]s[ıi]\b|\bboyun ağr[ıi]s[ıi]\b|\beklem\b|\btravma\b|\bkırık\b|\bçıkık\b", "Ortopedi ve Travmatoloji"),
    (r"\bderi\b|\bdöküntü\b|\bkaşınt[ıi]\b|\begzama\b|\bkurdeşen\b|\bsaç dökülmesi\b", "Deri ve Zührevi Hastalıkları (Cildiye)"),
    (r"\bdiş\b|\bdiş ağr[ıi]s[ıi]\b|\bkanal tedavisi\b|\bdiş et[ıi]\b|\bapse\b", "Diş Hekimliği (Genel Diş)"),
    (r"\bidrarda yanma\b|\bs[ıi]k idrar\b|\bidrar yolu\b|\bprostat\b", "Üroloji"),
    (r"\badet\b|\bvajinal ak[ıi]nt[ıi]\b|\bgebelik\b|\bhamile\b|\bkadın do[gğ]um\b", "Kadın Hastalıkları ve Doğum"),
    (r"\bateş\b|\bhalsizlik\b|\byorgunluk\b", "İç Hastalıkları (Dahiliye)"),
    (r"\bdepresyon\b|\banksiyete\b|\bpanik atak\b|\buyku bozukluğ[uü]\b", "Ruh Sağlığı ve Hastalıkları (Psikiyatri)"),
]

RED_FLAGS = [
    ("Akut Koroner", r"(ani|aniden|ezici|sıkışma).*göğüs ağr[ıi].*(soğuk ter|terleme|bulantı|nefes darl[ıi]ğ[ıi])"),
    ("İnme", r"(ani|aniden).*(yüzde kayma|kol|bacakta güçsüzlük|konuşma bozukluğu|afazi)"),
    ("Şiddetli Travma", r"(yüksekten düşme|bilinç kayb[ıi]|kontrolsüz kanama)"),
    ("Gebelikte Acil", r"(hamile|gebeyim).*(şiddetli ağr[ıi]|kanama|bayılma)"),
]

NEG = r"(yok|değil|bulunmuyor|hiç|asla)"

def norm(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^\wçğıöşü\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip()

def suggest(text: str, top_k=3):
    t = norm(text)

    # Acil
    for name, pat in RED_FLAGS:
        if re.search(pat, t):
            return {"action":"ACIL", "red_flag":name,
                    "message":"Acil bulgu tarif ediliyor. 112’yi arayın veya en yakın acile başvurun."}

    scores = {}
    traces = {}
    # Çocuk ipucu
    is_child = bool(re.search(r"\bçocuk\b|\b(\d{1,2}) yaş\b|\boğlum\b|\bkızım\b", t))

    for pat, clinic in RULES:
        m = re.search(pat, t)
        if not m: 
            continue
        # negasyon yakınında ise sayma
        wstart, wend = max(0, m.start()-12), min(len(t), m.end()+12)
        if re.search(NEG, t[wstart:wend]): 
            continue
        if clinic not in DIRECT: 
            continue
        w = 1.0
        if is_child and clinic == "Çocuk Sağlığı ve Hastalıkları":
            w += 1.0
        scores[clinic] = scores.get(clinic, 0.0) + w
        traces.setdefault(clinic, []).append(f"+{w} {pat}")

    if not scores:
        # Fallback (sadece doğrudan randevu verilebilenlerden)
        if is_child and "Çocuk Sağlığı ve Hastalıkları" in DIRECT:
            scores["Çocuk Sağlığı ve Hastalıkları"] = 1.0
            traces["Çocuk Sağlığı ve Hastalıkları"] = ["fallback_child"]
        else:
            for c in ["İç Hastalıkları (Dahiliye)", "Aile Hekimliği"]:
                if c in DIRECT:
                    scores[c] = 1.0
                    traces[c] = [f"fallback_{c}"]

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    sugg = [c for c,_ in ranked]
    return {
        "suggestions": sugg,
        "why": {c: "; ".join(traces.get(c, [])) for c in sugg},
        "direct_only": True
    }

if __name__ == "__main__":
    tests = [
        "İki gündür ateşim ve halsizliğim var, boğazım ağrıyor.",
        "Nefes darlığı ve öksürükle geceleri uyanıyorum.",
        "Göğüste sıkışma ve sol kola vuran ağrı, soğuk terleme oldu.",
        "5 yaş oğlumda ateş ve kusma var.",
        "Diş ağrısı dayanılmaz halde, gece uyutmadı.",
    ]
    for t in tests:
        print(">", t)
        print(json.dumps(suggest(t), ensure_ascii=False, indent=2))
        print("-"*40)
