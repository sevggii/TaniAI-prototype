"""
VISION (CXR) Eğitim – EfficientNetV2B0, transfer learning
Veri: Kaggle 'tawsifurrahman/covid19-radiography-database' (COVID-19, Normal)
Çıktılar bu modül altına kaydedilir: models/ (best.keras, labelmap.json)
Eğitim tamamlanınca model registry'e kayıt atılır (modality='vision', task='cxr_covid').
"""
from pathlib import Path
from datetime import datetime
import json, random, shutil
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import kagglehub
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[4] / "diagnosis_core" / "src" / "common"))
from registry import register_model

MOD_ROOT=Path(__file__).resolve().parents[1]
DATA=MOD_ROOT/"datasets"/"cxr_covid"
SPLIT=DATA/"split"
MODELS=MOD_ROOT/"models"
for p in [DATA, MODELS]: p.mkdir(parents=True, exist_ok=True)

# 1) indir
dl=kagglehub.dataset_download("tawsifurrahman/covid19-radiography-database")
src=Path(dl) / "COVID-19_Radiography_Dataset"

# 2) split
if not SPLIT.exists():
    random.seed(42)
    for cls in ["COVID","Normal"]:
        # Veri seti yapısı: COVID-19_Radiography_Dataset/COVID/images/ ve Normal/images/
        cls_path = src / cls / "images"
        imgs=list(cls_path.glob("*.png"))+list(cls_path.glob("*.jpg"))
        random.shuffle(imgs); n=len(imgs); n_tr=int(0.8*n); n_va=int(0.1*n)
        for sub, subset in [("train",imgs[:n_tr]),("val",imgs[n_tr:n_tr+n_va]),("test",imgs[n_tr+n_va:])]:
            d=(SPLIT/sub/cls); d.mkdir(parents=True, exist_ok=True)
            for pth in subset: shutil.copy2(pth, d/pth.name)

IMG=(224,224); BATCH=32; AUT=tf.data.AUTOTUNE
def ds(sub, sh=False):
    return tf.keras.utils.image_dataset_from_directory(SPLIT/sub, image_size=IMG, batch_size=BATCH, label_mode="categorical", shuffle=sh)
tr=ds("train",True); va=ds("val"); te=ds("test"); NCLS=tr.element_spec[1].shape[-1]

def prep(d, aug=False):
    d=d.map(lambda x,y:(tf.cast(x,tf.float32)/255.0,y), num_parallel_calls=AUT)
    if aug:
        augm=keras.Sequential([layers.RandomFlip("horizontal"),layers.RandomRotation(0.05),layers.RandomZoom(0.1),layers.RandomContrast(0.1)])
        d=d.map(lambda x,y:(augm(x,training=True),y), num_parallel_calls=AUT)
    return d.prefetch(AUT)
tr=prep(tr,True); va=prep(va); te=prep(te)

base=tf.keras.applications.EfficientNetV2B0(include_top=False,weights="imagenet",input_shape=IMG+(3,))
base.trainable=False
inp=keras.Input(shape=IMG+(3,))
x=tf.keras.applications.efficientnet_v2.preprocess_input(inp)
x=base(x,training=False)
x=layers.GlobalAveragePooling2D()(x)
x=layers.Dropout(0.25)(x)
x=layers.Dense(256,activation="relu")(x)
x=layers.Dropout(0.25)(x)
out=layers.Dense(NCLS,activation="softmax")(x)
model=keras.Model(inp,out)
model.compile(optimizer=keras.optimizers.Adam(1e-3),loss="categorical_crossentropy",metrics=[keras.metrics.AUC(name="auc",multi_label=True),"accuracy"])

run=MODELS/f"v1_{datetime.now().strftime('%Y%m%d_%H%M')}"
run.mkdir(parents=True, exist_ok=True)
ckpt=run/"best.keras"
cbs=[keras.callbacks.ModelCheckpoint(ckpt,monitor="val_accuracy",mode="max",save_best_only=True,verbose=1),
     keras.callbacks.EarlyStopping(monitor="val_accuracy",mode="max",patience=3,restore_best_weights=True)]

model.fit(tr,validation_data=va,epochs=15,callbacks=cbs)

base.trainable=True
for l in base.layers[:-40]: l.trainable=False
model.compile(optimizer=keras.optimizers.Adam(1e-4),loss="categorical_crossentropy",metrics=[keras.metrics.AUC(name="auc",multi_label=True),"accuracy"])
model.fit(tr,validation_data=va,epochs=8,callbacks=cbs)

loss,auc,acc=model.evaluate(te,verbose=0)
labels=sorted([p.name for p in (SPLIT/"train").iterdir()])
(run/"labelmap.json").write_text(json.dumps({i:n for i,n in enumerate(labels)}))

# registry'ye kaydet
register_model({
  "id": run.name,
  "modality": "vision",
  "task": "cxr_covid",
  "dataset": "tawsifurrahman/covid19-radiography-database",
  "path": str(run.resolve())
})
print({"test_loss": float(loss), "test_auc": float(auc), "test_acc": float(acc), "saved": str(run)})
