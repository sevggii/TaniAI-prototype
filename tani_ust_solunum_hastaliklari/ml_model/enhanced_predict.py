import joblib
import numpy as np
import pandas as pd
from enhanced_nlp_parser import EnhancedSymptomParser
import warnings
warnings.filterwarnings('ignore')

class EnhancedDiseasePredictor:
    def __init__(self, model_path="advanced_disease_model.pkl"):
        self.model_path = model_path
        self.model_data = None
        self.parser = EnhancedSymptomParser()
        self.load_model()
    
    def load_model(self):
        """Eğitilmiş modeli yükler"""
        try:
            self.model_data = joblib.load(self.model_path)
            print("✅ Gelişmiş model yüklendi")
            print(f"📊 Model türü: {type(self.model_data['model'])}")
            print(f"📋 Desteklenen sınıflar: {self.model_data['label_encoder'].classes_}")
        except FileNotFoundError:
            print(f"⚠️ Model dosyası bulunamadı: {self.model_path}")
            print("🔧 Önce advanced_models.py ile model eğitimi yapın")
            self.model_data = None
    
    def preprocess_text_input(self, text_input):
        """Metin girişini ön işleme tabi tutar"""
        print(f"🔍 Giriş metni: '{text_input}'")
        
        # NLP parser ile semptom vektörü oluştur
        parsed_symptoms = self.parser.parse_symptoms(text_input)
        
        # Model için gerekli semptom sırasına göre vektör oluştur (TÜM 18 SEMPTOM)
        symptom_order = [
            "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
            "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
            "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları",
            "Göğüs Ağrısı", "Titreme", "Gece Terlemesi", "İştahsızlık", "Konsantrasyon Güçlüğü"
        ]
        
        # TÜM semptom vektörü (18 semptom)
        full_vector = []
        for symptom in symptom_order:
            full_vector.append(parsed_symptoms.get(symptom, 0.0))
        
        return np.array(full_vector), parsed_symptoms
    
    def create_enhanced_features(self, full_vector, parsed_symptoms):
        """Gelişmiş özellikler oluşturur"""
        # Tam vektörü DataFrame'e çevir
        symptom_names = [
            "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
            "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
            "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları",
            "Göğüs Ağrısı", "Titreme", "Gece Terlemesi", "İştahsızlık", "Konsantrasyon Güçlüğü"
        ]
        
        df = pd.DataFrame([full_vector], columns=symptom_names)
        
        # Gelişmiş özellikler ekle
        enhanced_features = df.copy()
        
        # 1. COVID-19 göstergesi
        if "Ateş" in df.columns and "Koku veya Tat Kaybı" in df.columns and "Nefes Darlığı" in df.columns:
            enhanced_features["COVID_Indicator"] = (
                df["Ateş"] * df["Koku veya Tat Kaybı"] * df["Nefes Darlığı"]
            )
        
        # 2. Grip göstergesi
        if "Ateş" in df.columns and "Vücut Ağrıları" in df.columns and "Bitkinlik" in df.columns:
            enhanced_features["Grip_Indicator"] = (
                df["Ateş"] * df["Vücut Ağrıları"] * df["Bitkinlik"]
            )
        
        # 3. Soğuk algınlığı göstergesi
        if "Burun Akıntısı veya Tıkanıklığı" in df.columns and "Hapşırma" in df.columns:
            enhanced_features["Cold_Indicator"] = (
                df["Burun Akıntısı veya Tıkanıklığı"] * df["Hapşırma"] * (1 - df["Ateş"])
            )
        
        # 4. Alerji göstergesi
        if "Göz Kaşıntısı veya Sulanma" in df.columns and "Hapşırma" in df.columns:
            enhanced_features["Allergy_Indicator"] = (
                df["Göz Kaşıntısı veya Sulanma"] * df["Hapşırma"] * (1 - df["Ateş"])
            )
        
        # 5. Toplam semptom şiddeti
        enhanced_features["Total_Symptom_Severity"] = df.sum(axis=1)
        
        # 6. Semptom sayısı
        enhanced_features["Symptom_Count"] = (df > 0.1).sum(axis=1)
        
        # 7. Solunum sistemi skoru
        respiratory_symptoms = ["Nefes Darlığı", "Öksürük", "Burun Akıntısı veya Tıkanıklığı"]
        available_resp = [s for s in respiratory_symptoms if s in df.columns]
        if available_resp:
            enhanced_features["Respiratory_Score"] = df[available_resp].mean(axis=1)
        
        # 8. Sistemik semptom skoru
        systemic_symptoms = ["Ateş", "Bitkinlik", "Vücut Ağrıları", "Baş Ağrısı"]
        available_syst = [s for s in systemic_symptoms if s in df.columns]
        if available_syst:
            enhanced_features["Systemic_Score"] = df[available_syst].mean(axis=1)
        
        # 9. Gastrointestinal semptom skoru
        gi_symptoms = ["Bulantı veya Kusma", "İshal"]
        available_gi = [s for s in gi_symptoms if s in df.columns]
        if available_gi:
            enhanced_features["GI_Score"] = df[available_gi].mean(axis=1)
        
        return enhanced_features
    
    def predict_disease(self, text_input):
        """Hastalık tahmini yapar"""
        if self.model_data is None:
            return {
                "error": "Model yüklenemedi. Önce model eğitimi yapın.",
                "prediction": None,
                "probabilities": None,
                "confidence": None
            }
        
        try:
            # Metin girişini işle
            full_vector, parsed_symptoms = self.preprocess_text_input(text_input)
            
            # Gelişmiş özellikler oluştur
            enhanced_features = self.create_enhanced_features(full_vector, parsed_symptoms)
            
            # Ölçeklendirme
            scaled_features = self.model_data['scaler'].transform(enhanced_features)
            
            # Özellik seçimi
            selected_features = self.model_data['feature_selector'].transform(scaled_features)
            
            # Tahmin yap
            prediction = self.model_data['model'].predict(selected_features)[0]
            probabilities = self.model_data['model'].predict_proba(selected_features)[0]
            
            # Etiketleri decode et
            predicted_disease = self.model_data['label_encoder'].inverse_transform([prediction])[0]
            
            # Olasılık skorları
            class_names = self.model_data['label_encoder'].classes_
            prob_dict = {name: prob for name, prob in zip(class_names, probabilities)}
            
            # Güven skoru hesapla
            max_prob = max(probabilities)
            confidence = self.calculate_confidence(max_prob, parsed_symptoms, predicted_disease)
            
            # Tanısal güven skorları
            diagnostic_confidence = self.parser.get_diagnostic_confidence(full_vector)
            
            return {
                "prediction": predicted_disease,
                "probabilities": prob_dict,
                "confidence": confidence,
                "diagnostic_confidence": diagnostic_confidence,
                "detected_symptoms": {k: v for k, v in parsed_symptoms.items() if v > 0},
                "max_probability": max_prob
            }
            
        except Exception as e:
            return {
                "error": f"Tahmin sırasında hata: {str(e)}",
                "prediction": None,
                "probabilities": None,
                "confidence": None
            }
    
    def calculate_confidence(self, max_prob, parsed_symptoms, predicted_disease):
        """Güven skoru hesaplar"""
        base_confidence = max_prob
        
        # Semptom sayısına göre ayarlama
        symptom_count = sum(1 for v in parsed_symptoms.values() if v > 0)
        if symptom_count >= 5:
            base_confidence += 0.1
        elif symptom_count < 2:
            base_confidence -= 0.2
        
        # Hastalığa özel güven ayarlaması
        if predicted_disease == "COVID-19":
            covid_key_symptoms = ["Koku veya Tat Kaybı", "Nefes Darlığı", "Ateş"]
            covid_symptom_count = sum(1 for s in covid_key_symptoms if parsed_symptoms.get(s, 0) > 0.5)
            if covid_symptom_count >= 2:
                base_confidence += 0.15
        
        elif predicted_disease == "Grip":
            flu_key_symptoms = ["Ateş", "Vücut Ağrıları", "Bitkinlik"]
            flu_symptom_count = sum(1 for s in flu_key_symptoms if parsed_symptoms.get(s, 0) > 0.5)
            if flu_symptom_count >= 2:
                base_confidence += 0.1
        
        return min(1.0, max(0.0, base_confidence))
    
    def get_detailed_analysis(self, text_input):
        """Detaylı analiz raporu oluşturur"""
        result = self.predict_disease(text_input)
        
        if result.get("error"):
            return result
        
        analysis = {
            "input_text": text_input,
            "predicted_disease": result["prediction"],
            "confidence": result["confidence"],
            "max_probability": result["max_probability"],
            "detected_symptoms": result["detected_symptoms"],
            "all_probabilities": result["probabilities"],
            "diagnostic_confidence": result["diagnostic_confidence"],
            "recommendations": self.get_recommendations(result)
        }
        
        return analysis
    
    def get_recommendations(self, result):
        """Öneriler oluşturur"""
        recommendations = []
        predicted_disease = result["prediction"]
        confidence = result["confidence"]
        
        if confidence < 0.7:
            recommendations.append("⚠️ Düşük güven skoru. Doktor konsültasyonu önerilir.")
        
        if predicted_disease == "COVID-19":
            recommendations.extend([
                "🏥 COVID-19 şüphesi. Acil doktor konsültasyonu gerekli.",
                "🔒 İzolasyon önerilir.",
                "🧪 PCR testi yaptırın."
            ])
        elif predicted_disease == "Grip":
            recommendations.extend([
                "🏥 Grip benzeri semptomlar. Doktor kontrolü önerilir.",
                "💊 Semptomatik tedavi alabilirsiniz.",
                "🛌 Dinlenme ve bol sıvı tüketimi önerilir."
            ])
        elif predicted_disease == "Soğuk Algınlığı":
            recommendations.extend([
                "🏠 Hafif soğuk algınlığı. Evde dinlenin.",
                "💧 Bol sıvı tüketin.",
                "🌡️ Ateş düşürücü kullanabilirsiniz."
            ])
        elif predicted_disease == "Mevsimsel Alerji":
            recommendations.extend([
                "🌸 Mevsimsel alerji belirtileri.",
                "💊 Antihistaminik kullanabilirsiniz.",
                "🏠 Allerjenlerden uzak durun."
            ])
        
        return recommendations

def interactive_prediction():
    """Etkileşimli tahmin sistemi"""
    predictor = EnhancedDiseasePredictor()
    
    if predictor.model_data is None:
        print("❌ Model yüklenemedi. Önce model eğitimi yapın:")
        print("1. enhanced_data_generation.py çalıştırın")
        print("2. advanced_models.py çalıştırın")
        return
    
    print("🏥 Gelişmiş Hastalık Tanı Sistemi")
    print("=" * 50)
    print("Semptomlarınızı doğal dilde yazın...")
    print("Örnek: 'Yüksek ateşim var, nefes alamıyorum, koku alamıyorum'")
    print("Çıkmak için 'quit' yazın\n")
    
    while True:
        try:
            user_input = input("🔍 Belirtilerinizi yazın: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'çık']:
                print("👋 Görüşmek üzere!")
                break
            
            if not user_input:
                print("⚠️ Lütfen belirtilerinizi yazın.")
                continue
            
            print("\n🔄 Analiz yapılıyor...")
            
            # Detaylı analiz
            analysis = predictor.get_detailed_analysis(user_input)
            
            if analysis.get("error"):
                print(f"❌ Hata: {analysis['error']}")
                continue
            
            # Sonuçları göster
            print("\n" + "="*50)
            print("🎯 TANİ SONUCU")
            print("="*50)
            
            print(f"🏥 Tahmin Edilen Hastalık: {analysis['predicted_disease']}")
            print(f"📊 Güven Skoru: %{analysis['confidence']*100:.1f}")
            print(f"🎲 Maksimum Olasılık: %{analysis['max_probability']*100:.1f}")
            
            print("\n📋 Tespit Edilen Semptomlar:")
            for symptom, severity in analysis['detected_symptoms'].items():
                print(f"  • {symptom}: {severity:.2f}")
            
            print("\n📊 Tüm Olasılıklar:")
            for disease, prob in analysis['all_probabilities'].items():
                bar = "█" * int(prob * 20)
                print(f"  {disease}: {prob*100:5.1f}% {bar}")
            
            print("\n🎯 Tanısal Güven Skorları:")
            for disease, score in analysis['diagnostic_confidence'].items():
                print(f"  {disease}: {score:.2f}")
            
            print("\n💡 Öneriler:")
            for rec in analysis['recommendations']:
                print(f"  {rec}")
            
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n👋 Görüşmek üzere!")
            break
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")

if __name__ == "__main__":
    interactive_prediction()
