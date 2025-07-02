import joblib
import numpy as np

# Belirti sırasına göre (13 özellik)
semptomlar = [
    "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
    "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
    "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları"
]

'''
  "yaygin": 1.0,
    "az_yaygin": 0.75,
    "yaygin_olmayan": 0.5,
    "nadir": 0.25,
    "gorulmez": 0.0
'''

# Kullanıcının girişine göre (1 = var, 0 = yok)
# Bu kısmı kendin test edebilirsin
kullanici_semptomlari = {
    "Ateş": 1,
    "Baş Ağrısı": 0.75,
    "Bitkinlik": 1,
    "Boğaz Ağrısı": 0.75,
    "Bulantı veya Kusma": 0.5,
    "Burun Akıntısı veya Tıkanıklığı": 0.25,
    "Göz Kaşıntısı veya Sulanma": 0.25,
    "Hapşırma": 0.25,
    "İshal": 0.5,
    "Koku veya Tat Kaybı": 0.75,
    "Nefes Darlığı": 1,
    "Öksürük": 1,
    "Vücut Ağrıları": 0.75
}
'''
🩺 Tahmin Edilen Hastalık: COVID-19

📊 Olasılıklar:
  COVID-19: %100.0
  Grip: %0.0
  Mevsimsel Alerji: %0.0
  Soğuk Algınlığı: %0.0
'''



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
