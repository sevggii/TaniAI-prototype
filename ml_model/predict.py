import joblib
import numpy as np

# Belirti sırasına göre (13 özellik)
semptomlar = [
    "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
    "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
    "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları"
]

# Kullanıcının girişine göre (1 = var, 0 = yok)
# Bu kısmı kendin test edebilirsin
kullanici_semptomlari = {
    "Ateş": 1,
    "Baş Ağrısı": 0,
    "Bitkinlik": 1,
    "Boğaz Ağrısı": 1,
    "Bulantı veya Kusma": 0,
    "Burun Akıntısı veya Tıkanıklığı": 0,
    "Göz Kaşıntısı veya Sulanma": 0,
    "Hapşırma": 0,
    "İshal": 0,
    "Koku veya Tat Kaybı": 1,
    "Nefes Darlığı": 1,
    "Öksürük": 1,
    "Vücut Ağrıları": 1
}

# Belirti vektörünü sıraya göre oluştur
input_vector = [kullanici_semptomlari.get(s, 0) for s in semptomlar]
input_vector = np.array(input_vector).reshape(1, -1)

# Modeli yükle
model = joblib.load("ml_model/hastalik_modeli.pkl")

# Tahmin et
tahmin = model.predict(input_vector)[0]
olasiliklar = model.predict_proba(input_vector)[0]

# Sonuçları yazdır
print(f"🩺 Tahmin Edilen Hastalık: {tahmin}\n")
print("📊 Olasılıklar:")
for label, prob in zip(model.classes_, olasiliklar):
    print(f"  {label}: %{round(prob * 100, 2)}")
