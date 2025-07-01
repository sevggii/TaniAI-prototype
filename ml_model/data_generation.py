import pandas as pd
import random

# Güncel yaygınlık puanlaması
levels = {
    "yaygin": 1.0,
    "az_yaygin": 0.75,
    "yaygin_olmayan": 0.5,
    "nadir": 0.25,
    "gorulmez": 0.0
}

# Tablodan alınan puanlar (güncel haliyle)
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
        levels["nadir"], levels["nadir"], levels["az_yaygin"], levels["yaygin"],
        levels["nadir"], levels["yaygin"], levels["gorulmez"], levels["yaygin"], levels["nadir"],
        levels["nadir"], levels["nadir"], levels["yaygin"], levels["az_yaygin"]
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

# Sentetik örnek oluşturucu
def generate_sample(base_vector, noise=0.1):
    return [
        max(0.0, min(1.0, round(x + random.uniform(-noise, noise), 2)))
        for x in base_vector
    ]

# Veri üret
samples = []
labels = []
N = 100  # Her hastalık için üretilecek örnek sayısı

for disease, vec in data.items():
    for _ in range(N):
        sample = generate_sample(vec)
        samples.append(sample)
        labels.append(disease)

# DataFrame ve CSV
df = pd.DataFrame(samples, columns=semptomlar)
df["Etiket"] = labels
df.to_csv("ml_model/hastalik_veriseti.csv", index=False)

print("✅ Veri seti oluşturuldu: ml_model/hastalik_veriseti.csv")
