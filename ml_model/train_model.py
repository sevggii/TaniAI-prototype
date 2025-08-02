import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
import joblib

# 1. Veriyi oku
df = pd.read_csv("ml_model/hastalik_veriseti.csv")

# 2. X ve y ayır
X = df.drop("Etiket", axis=1)
y = df["Etiket"]

# 3. Train/test böl
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Model oluştur ve eğit
model = RandomForestClassifier(n_estimators=100, max_depth=5, min_samples_leaf=5, random_state=42)
model.fit(X_train, y_train)

# Cross-validation ile değerlendirme
cv_scores = cross_val_score(model, X, y, cv=5)
print(f"\n🔄 5-Fold CV Doğruluk Ortalaması: {cv_scores.mean():.2f} (Skorlar: {cv_scores})\n")

# 5. Test et
y_pred = model.predict(X_test)
print("🎯 Doğruluk:", accuracy_score(y_test, y_pred))
print("\n📊 Sınıflandırma Raporu:\n", classification_report(y_test, y_pred))

# 6. Modeli kaydet
joblib.dump(model, "ml_model/hastalik_modeli.pkl")
print("✅ Model kaydedildi: ml_model/hastalik_modeli.pkl")

'''Güncel Model

🔄 5-Fold CV Doğruluk Ortalaması: 0.76 (Skorlar: [0.71956522 0.8        0.78913043 0.78043478 0.72173913])  

🎯 Doğruluk: 0.7630434782608696

📊 Sınıflandırma Raporu:
                   precision    recall  f1-score   support

        COVID-19       1.00      0.97      0.98       156
            Grip       0.46      0.76      0.57        95
Mevsimsel Alerji       0.99      0.96      0.97        96
 Soğuk Algınlığı       0.61      0.32      0.42       113

        accuracy                           0.76       460
       macro avg       0.76      0.75      0.74       460
    weighted avg       0.79      0.76      0.76       460

✅ Model kaydedildi: ml_model/hastalik_modeli.pkl

'''


'''ÖNCEKİ EĞİTİM SONUÇLARI

🔄 5-Fold CV Doğruluk Ortalaması: 0.92 (Skorlar: [0.85   0.975  0.975  0.9875 0.8125])

🎯 Doğruluk: 0.925

📊 Sınıflandırma Raporu:
                   precision    recall  f1-score   support

        COVID-19       0.96      0.89      0.92        27
            Grip       0.83      0.94      0.88        16
Mevsimsel Alerji       0.94      0.89      0.92        19
 Soğuk Algınlığı       0.95      1.00      0.97        18

        accuracy                           0.93        80
       macro avg       0.92      0.93      0.92        80
    weighted avg       0.93      0.93      0.93        80

✅ Model kaydedildi: ml_model/hastalik_modeli.pkl

'''
