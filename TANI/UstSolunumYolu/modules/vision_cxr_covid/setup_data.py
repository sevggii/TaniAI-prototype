#!/usr/bin/env python3
"""
Veri setini hazırla
"""
import kagglehub
from pathlib import Path
import random, shutil

# Veri setini indir
print("Veri seti indiriliyor...")
dl = kagglehub.dataset_download("tawsifurrahman/covid19-radiography-database")
src = Path(dl) / "COVID-19_Radiography_Dataset"

# Hedef dizinler
DATA = Path(__file__).parent / "datasets" / "cxr_covid"
SPLIT = DATA / "split"
for p in [DATA, SPLIT]: p.mkdir(parents=True, exist_ok=True)

print("Veri seti kopyalanıyor...")
random.seed(42)
for cls in ["COVID", "Normal"]:
    cls_path = src / cls / "images"
    imgs = list(cls_path.glob("*.png")) + list(cls_path.glob("*.jpg"))
    print(f"{cls}: {len(imgs)} görüntü bulundu")
    
    random.shuffle(imgs)
    n = len(imgs)
    n_tr = int(0.8 * n)
    n_va = int(0.1 * n)
    
    for sub, subset in [("train", imgs[:n_tr]), ("val", imgs[n_tr:n_tr+n_va]), ("test", imgs[n_tr+n_va:])]:
        d = SPLIT / sub / cls
        d.mkdir(parents=True, exist_ok=True)
        for pth in subset:
            shutil.copy2(pth, d / pth.name)
        print(f"  {sub}: {len(subset)} görüntü kopyalandı")

print("Veri hazırlama tamamlandı!")
