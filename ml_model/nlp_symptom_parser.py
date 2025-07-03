# ml_model/nlp_symptom_parser.py

# Semptom ve halk dili eşleşmesi
semptom_sozluk = {
    "Ateş": ["ateşim", "yanıyorum", "sıcaktan kavruluyorum"],
    "Baş Ağrısı": ["başım ağrıyor", "kafam zonkluyor", "başım çatlıyor"],
    "Bitkinlik": ["yorgunum", "halsizim", "enerjim yok"],
    "Boğaz Ağrısı": ["boğazım ağrıyor", "boğazım yanıyor", "konuşamıyorum"],
    "Bulantı veya Kusma": ["midem bulanıyor", "kusacak gibiyim", "istifra ettim"],
    "Burun Akıntısı veya Tıkanıklığı": ["burnum akıyor", "burnum tıkalı"],
    "Göz Kaşıntısı veya Sulanma": ["gözüm kaşınıyor", "gözüm sulanıyor", "gözlerim yanıyor"],
    "Hapşırma": ["hapşırıyorum", "durmadan hapşırıyorum"],
    "İshal": ["ishalim", "sürekli tuvalete gidiyorum"],
    "Koku veya Tat Kaybı": ["koku alamıyorum", "tat alamıyorum", "kokusuz"],
    "Nefes Darlığı": [
    "nefes alamıyorum", 
    "nefes almakta zorlanıyorum",  # ✅ yeni eklendi
    "zor nefes alıyorum",
    "boğuluyorum", 
    "hava yetmiyor"
],

    "Öksürük": ["öksürüyorum", "çok fena öksürüyorum", "öksürük krizim var"],
    "Vücut Ağrıları": ["her yerim ağrıyor", "vücudum sızlıyor", "kemiklerim ağrıyor"]
}

# Yoğunluk (şiddet) belirteçleri
yoğunluk_degeri = {
    "çok": 1.0,
    "aşırı": 1.0,
    "fazla": 0.75,
    "biraz": 0.5,
    "hafif": 0.5,
    "hiç": 0.0
}

def semptom_vektor_olustur(metin: str):
    metin = metin.lower()
    vektor = {}
    for semptom, ifadeler in semptom_sozluk.items():
        skor = 0.0
        for ifade in ifadeler:
            if ifade in metin:
                context_window = metin[metin.find(ifade)-10:metin.find(ifade)+len(ifade)+10]
                skor = 1.0
                for y_kelim, puan in yoğunluk_degeri.items():
                    if y_kelim in context_window:
                        skor = puan
                        break
                break
        vektor[semptom] = skor
    return vektor

