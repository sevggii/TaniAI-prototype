import joblib
import numpy as np
from nlp_symptom_parser import semptom_vektor_olustur  # 👈 eklendi

# Belirti sırasına göre (13 özellik)
semptomlar = [
    "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
    "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
    "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları"
]

# 👇 Yeni giriş: Doğal dil ile belirti al
metin = input("🔍 Belirtilerinizi yazın: ")  # 👈 kullanıcı girişini al
kullanici_semptomlari = semptom_vektor_olustur(metin)  # 👈 NLP parser ile vektör oluştur

# Belirti vektörünü sıraya göre oluştur
input_vector = [kullanici_semptomlari.get(s, 0.0) for s in semptomlar]
input_vector = np.array(input_vector).reshape(1, -1)

# Modeli yükle
model = joblib.load("ml_model/hastalik_modeli.pkl")

# Tahmin et
tahmin = model.predict(input_vector)[0]
olasiliklar = model.predict_proba(input_vector)[0]

# Sonuçları yazdır
print(f"\n🩺 Tahmin Edilen Hastalık: {tahmin}\n")
print("📊 Olasılıklar:")
for label, prob in zip(model.classes_, olasiliklar):
    print(f"  {label}: %{round(prob * 100, 2)}")

##sonuçlar
'''
🔍 Belirtilerinizi yazın: yüksek ateş, orta derece baş ağrısı, 
aşırı bitkinlik, biraz boğaz ağrısı, ishal yok. nefes darlığı  ve öksürük çok var bir de orta derece vücut ağrılarım var


🩺 Tahmin Edilen Hastalık: COVID-19

📊 Olasılıklar:
  COVID-19: %100.0
  Grip: %0.0
  Mevsimsel Alerji: %0.0
  Soğuk Algınlığı: %0.0

'''