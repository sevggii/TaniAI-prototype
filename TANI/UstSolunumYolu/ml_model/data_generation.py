import pandas as pd
import random
import numpy as np

# Yaygınlık seviyeleri
levels = {
    "yaygin": 1.0,
    "az_yaygin": 0.75,
    "yaygin_olmayan": 0.5,
    "nadir": 0.25,
    "gorulmez": 0.0
}

# Hastalık başına semptom yaygınlık puanları
# Semptomlar sırası:
# Ateş, Baş Ağrısı, Bitkinlik, Boğaz Ağrısı, Bulantı veya Kusma,
# Burun Akıntısı veya Tıkanıklığı, Göz Kaşıntısı/Sulanma, Hapşırma,
# İshal, Koku/Tat Kaybı, Nefes Darlığı, Öksürük, Vücut Ağrıları

data = {
    "COVID-19": [
        levels["yaygin"], levels["az_yaygin"], levels["yaygin"], levels["az_yaygin"], levels["yaygin_olmayan"],
        levels["nadir"], levels["nadir"], levels["nadir"], levels["yaygin_olmayan"], levels["yaygin"],
        levels["yaygin"], levels["yaygin"], levels["az_yaygin"]
    ],
    "Grip": [
        levels["yaygin"], levels["yaygin"], levels["yaygin"], levels["az_yaygin"], levels["az_yaygin"],
        levels["az_yaygin"], levels["gorulmez"], levels["yaygin_olmayan"], levels["az_yaygin"], levels["nadir"],
        levels["nadir"], levels["yaygin"], levels["yaygin"]
    ],
    "Soğuk Algınlığı": [
        levels["nadir"], levels["nadir"], levels["az_yaygin"], levels["yaygin"], levels["nadir"],
        levels["yaygin"], levels["gorulmez"], levels["yaygin"], levels["nadir"], levels["nadir"],
        levels["nadir"], levels["yaygin"], levels["az_yaygin"]
    ],
    "Mevsimsel Alerji": [
        levels["nadir"], levels["az_yaygin"], levels["az_yaygin"], levels["az_yaygin"], levels["gorulmez"],
        levels["yaygin"], levels["yaygin"], levels["yaygin"], levels["gorulmez"], levels["nadir"],
        levels["az_yaygin"], levels["az_yaygin"], levels["nadir"]
    ]
}

semptomlar = [
    "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
    "Burun Akıntısı veya Tıkanıklığı", "Gözlerde Kaşıntı veya Sulanma", "Hapşırma",
    "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları"
]

def generate_sample(base_vector, noise=0.1, disease_name=""):
    sample = []
    for val in base_vector:
        if val == 0.0:
            sample.append(0.0)
        else:
            sample.append(random.choice([0.25, 0.5, 0.75, 1.0]))

    if disease_name != "COVID-19":
        sample[semptomlar.index("Koku veya Tat Kaybı")] = 0.0
        sample[semptomlar.index("Nefes Darlığı")] = 0.0
        sample[semptomlar.index("Öksürük")] = random.choice([0.0, 0.25])

    if disease_name == "COVID-19":
        sample[semptomlar.index("Koku veya Tat Kaybı")] = 1.0
        sample[semptomlar.index("Nefes Darlığı")] = 1.0
        sample[semptomlar.index("Öksürük")] = 1.0

    return sample

# Veri üretimi
samples = []
labels = []

for disease, vec in data.items():
    n = 800 if disease == "COVID-19" else 500
    for _ in range(n):
        sample = generate_sample(vec, disease_name=disease)
        samples.append(sample)
        labels.append(disease)

# %5 oranında etiket karışması ekle
num_wrong = int(0.05 * len(samples))
for _ in range(num_wrong):
    idx = random.randint(0, len(samples) - 1)
    wrong_label = random.choice([d for d in data.keys() if d != labels[idx]])
    labels[idx] = wrong_label

# DataFrame ve CSV
df = pd.DataFrame(samples, columns=semptomlar)
df["Etiket"] = labels

df.loc[(df["Etiket"] != "COVID-19"), "Koku veya Tat Kaybı"] = 0.0
df.loc[(df["Etiket"] != "COVID-19"), "Nefes Darlığı"] = 0.0

# Kaydet
output_path = "ml_model/hastalik_veriseti.csv"
df.to_csv(output_path, index=False)
print(f"✅ Veri seti oluşturuldu: {output_path}")
