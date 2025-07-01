import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# 1. Veriyi oku
df = pd.read_csv("ml_model/hastalik_veriseti.csv")

# 2. X ve y ayır
X = df.drop("Etiket", axis=1)
y = df["Etiket"]

# 3. Train/test böl
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Model oluştur ve eğit
model = DecisionTreeClassifier(random_state=42)
model.fit(X_train, y_train)

# 5. Test et
y_pred = model.predict(X_test)
print("🎯 Doğruluk:", accuracy_score(y_test, y_pred))
print("\n📊 Sınıflandırma Raporu:\n", classification_report(y_test, y_pred))

# 6. Modeli kaydet
joblib.dump(model, "ml_model/hastalik_modeli.pkl")
print("✅ Model kaydedildi: ml_model/hastalik_modeli.pkl")
