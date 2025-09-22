# ml_model/nlp_symptom_parser.py

# Semptom ve halk dili eşleşmesi
semptom_sozluk = {
    "Ateş": ["ateşim", "yanıyorum", "sıcaktan kavruluyorum"],
    "Baş Ağrısı": ["başım ağrıyor", "kafam zonkluyor", "başım çatlıyor"],
    "Bitkinlik": [
    "yorgunum", "halsizim", "enerjim yok",
    "bitkinim", "çok bitkinim", "kendimi çok yorgun hissediyorum"
],

    "Boğaz Ağrısı": [
    "boğazım ağrıyor", 
    "boğazımda batma var",  
    "boğazım şişti",         
    "boğazım gıcık yapıyor"
],
    "Bulantı veya Kusma": ["midem bulanıyor", "kusacak gibiyim", "istifra ettim"],
    "Burun Akıntısı veya Tıkanıklığı": [
    "burnum akıyor",   
    "burnum tıkanık",  
    "nefesim burnumdan zor geliyor", 
    "burun dolu"  
],
    "Göz Kaşıntısı veya Sulanma": ["gözüm kaşınıyor", "gözüm sulanıyor", "gözlerim yanıyor"],
    "Hapşırma": ["hapşırıyorum", "durmadan hapşırıyorum"],
    "İshal": ["ishalim", "sürekli tuvalete gidiyorum"],
    "Koku veya Tat Kaybı": ["koku alamıyorum", "tat alamıyorum", "kokusuz"],
    "Nefes Darlığı": [
    "nefes alamıyorum", 
    "nefes almakta zorlanıyorum",
    "zor nefes alıyorum",
    "boğuluyorum", 
    "hava yetmiyor"
],

   "Vücut Ağrıları": [
    "her yerim ağrıyor", "vücudum sızlıyor", "kemiklerim ağrıyor",
    "vücudum ağrıyor", "vücudum çok ağrıyor"  # 👈 ekle!
],

"Öksürük": [
    "öksürüyorum", "çok fena öksürüyorum", "öksürük krizim var",
    "hafif öksürüğüm var", "biraz öksürüyorum"  # 👈 ekle!
]

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

