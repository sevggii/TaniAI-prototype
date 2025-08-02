import joblib
import numpy as np
from nlp_symptom_parser import semptom_vektor_olustur  # 👈 eklendi
import random
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

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


print("\n🧠 Vektör Detayı:")
for semptom, skor in zip(semptomlar, input_vector[0]):
    print(f"{semptom}: {skor}")

def generate_sample(base_vector, noise=0.2, missing_prob=0.2):
    sample = []
    for val in base_vector:
        # Bazı semptomları eksik bırak
        if random.random() < missing_prob:
            sample.append(0.0)
        elif val == 0.0:
            sample.append(0.0)
        else:
            # Gürültüyü artır
            sample.append(
                max(0.0, min(1.0, round(val + random.uniform(-noise, noise), 2)))
            )
    return sample

scores = cross_val_score(model, X, y, cv=5)
print("5-Fold CV Doğruluk Ortalaması:", scores.mean())

print("Modelin tipi:", type(model))
print("Model kaydediliyor:", model)
joblib.dump(model, "ml_model/hastalik_modeli.pkl")

''' GRİP TESPİTİ

Belirtilerinizi yazın: ateşim var, başım ağrıyor, çok bitkinim, vücudum ağrıyor


🩺 Tahmin Edilen Hastalık: Grip

📊 Olasılıklar:
  COVID-19: %18.42
  Grip: %46.33
  Mevsimsel Alerji: %25.12
  Soğuk Algınlığı: %10.13

🧠 Vektör Detayı:
Ateş: 1.0
Baş Ağrısı: 1.0
Bitkinlik: 0.0
Boğaz Ağrısı: 0.0
Bulantı veya Kusma: 0.0
Burun Akıntısı veya Tıkanıklığı: 0.0
Göz Kaşıntısı veya Sulanma: 0.0
Hapşırma: 0.0
İshal: 0.0
Koku veya Tat Kaybı: 0.0
Nefes Darlığı: 0.0
Öksürük: 0.0
Vücut Ağrıları: 0.0

'''

print("\n🧠 Vektör Detayı:")
for semptom, skor in zip(semptomlar, input_vector[0]):
    if skor > 0.0:
        print(f"{semptom}: {skor}")

