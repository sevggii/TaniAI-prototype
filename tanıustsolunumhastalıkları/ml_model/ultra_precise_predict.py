#!/usr/bin/env python3
"""
Ultra Hassas Tahmin Sistemi - 4 Hastalığı Mükemmel Ayırt Etmek İçin
"""

import joblib
import numpy as np
import pandas as pd
from enhanced_nlp_parser import EnhancedSymptomParser
import warnings
warnings.filterwarnings('ignore')

class UltraPreciseDiseasePredictor:
    def __init__(self, model_path="ultra_precise_disease_model.pkl"):
        self.model_path = model_path
        self.model_data = None
        self.parser = EnhancedSymptomParser()
        self.load_model()
    
    def load_model(self):
        """Ultra hassas modeli yükler"""
        try:
            self.model_data = joblib.load(self.model_path)
            print("✅ Ultra hassas model yüklendi")
            print(f"📊 Model türü: {type(self.model_data['model'])}")
            print(f"📋 Desteklenen sınıflar: {self.model_data['label_encoder'].classes_}")
        except FileNotFoundError:
            print(f"⚠️ Model dosyası bulunamadı: {self.model_path}")
            print("🔧 Önce train_ultra_precise_model.py ile model eğitimi yapın")
            self.model_data = None
    
    def preprocess_text_input(self, text_input):
        """Metin girişini ultra hassas ön işleme tabi tutar"""
        print(f"🔍 Giriş metni: '{text_input}'")
        
        # NLP parser ile semptom vektörü oluştur
        parsed_symptoms = self.parser.parse_symptoms(text_input)
        
        # Ultra hassas model için gerekli semptom sırasına göre vektör oluştur
        symptom_order = [
            "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
            "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
            "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları",
            "Göğüs Ağrısı", "Titreme", "Gece Terlemesi", "İştahsızlık", "Konsantrasyon Güçlüğü"
        ]
        
        # 18 semptom vektörü
        full_vector = []
        for symptom in symptom_order:
            full_vector.append(parsed_symptoms.get(symptom, 0.0))
        
        return np.array(full_vector), parsed_symptoms
    
    def create_ultra_precise_features(self, full_vector, parsed_symptoms):
        """Ultra hassas özellikler oluşturur"""
        # Tam vektörü DataFrame'e çevir
        symptom_names = [
            "Ateş", "Baş Ağrısı", "Bitkinlik", "Boğaz Ağrısı", "Bulantı veya Kusma",
            "Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma",
            "İshal", "Koku veya Tat Kaybı", "Nefes Darlığı", "Öksürük", "Vücut Ağrıları",
            "Göğüs Ağrısı", "Titreme", "Gece Terlemesi", "İştahsızlık", "Konsantrasyon Güçlüğü"
        ]
        
        df = pd.DataFrame([full_vector], columns=symptom_names)
        
        # Ultra hassas özellikler ekle
        enhanced_features = df.copy()
        
        # 1. COVID-19 ayırıcı kombinasyonları
        if "Ateş" in df.columns and "Koku veya Tat Kaybı" in df.columns and "Nefes Darlığı" in df.columns:
            enhanced_features["COVID_Unique_Signature"] = (
                df["Ateş"] * df["Koku veya Tat Kaybı"] * df["Nefes Darlığı"]
            )
        
        if "Koku veya Tat Kaybı" in df.columns and "Nefes Darlığı" in df.columns:
            enhanced_features["COVID_Core_Signature"] = (
                df["Koku veya Tat Kaybı"] * df["Nefes Darlığı"]
            )
        
        # 2. Grip ayırıcı kombinasyonları
        if "Ateş" in df.columns and "Vücut Ağrıları" in df.columns and "Titreme" in df.columns:
            enhanced_features["Flu_Unique_Signature"] = (
                df["Ateş"] * df["Vücut Ağrıları"] * df["Titreme"]
            )
        
        if "Vücut Ağrıları" in df.columns and "Ateş" in df.columns:
            enhanced_features["Flu_Core_Signature"] = (
                df["Vücut Ağrıları"] * df["Ateş"]
            )
        
        # 3. Soğuk algınlığı ayırıcı kombinasyonları
        if "Burun Akıntısı veya Tıkanıklığı" in df.columns and "Hapşırma" in df.columns:
            enhanced_features["Cold_Unique_Signature"] = (
                df["Burun Akıntısı veya Tıkanıklığı"] * df["Hapşırma"]
            )
        
        # Ateş olmadan soğuk algınlığı
        if "Burun Akıntısı veya Tıkanıklığı" in df.columns and "Hapşırma" in df.columns and "Ateş" in df.columns:
            enhanced_features["Cold_No_Fever"] = (
                df["Burun Akıntısı veya Tıkanıklığı"] * df["Hapşırma"] * (1 - df["Ateş"])
            )
        
        # 4. Alerji ayırıcı kombinasyonları
        if "Göz Kaşıntısı veya Sulanma" in df.columns and "Hapşırma" in df.columns:
            enhanced_features["Allergy_Unique_Signature"] = (
                df["Göz Kaşıntısı veya Sulanma"] * df["Hapşırma"]
            )
        
        # Ateş olmadan alerji
        if "Göz Kaşıntısı veya Sulanma" in df.columns and "Hapşırma" in df.columns and "Ateş" in df.columns:
            enhanced_features["Allergy_No_Fever"] = (
                df["Göz Kaşıntısı veya Sulanma"] * df["Hapşırma"] * (1 - df["Ateş"])
            )
        
        # 5. Ayırıcı tanı skorları
        # COVID-19 vs Grip
        if "Koku veya Tat Kaybı" in df.columns and "Vücut Ağrıları" in df.columns:
            enhanced_features["COVID_vs_Flu"] = (
                df["Koku veya Tat Kaybı"] - df["Vücut Ağrıları"]
            )
        
        # Alerji vs Soğuk algınlığı
        if "Göz Kaşıntısı veya Sulanma" in df.columns and "Boğaz Ağrısı" in df.columns:
            enhanced_features["Allergy_vs_Cold"] = (
                df["Göz Kaşıntısı veya Sulanma"] - df["Boğaz Ağrısı"]
            )
        
        # 6. Sistemik vs Lokal semptom ayrımı
        systemic_symptoms = ["Ateş", "Bitkinlik", "Vücut Ağrıları", "Baş Ağrısı", "Titreme"]
        available_systemic = [s for s in systemic_symptoms if s in df.columns]
        if available_systemic:
            enhanced_features["Systemic_Score"] = df[available_systemic].mean(axis=1)
        
        local_symptoms = ["Burun Akıntısı veya Tıkanıklığı", "Göz Kaşıntısı veya Sulanma", "Hapşırma", "Boğaz Ağrısı"]
        available_local = [s for s in local_symptoms if s in df.columns]
        if available_local:
            enhanced_features["Local_Score"] = df[available_local].mean(axis=1)
        
        # 7. Semptom yoğunluğu
        enhanced_features["Symptom_Intensity"] = df.sum(axis=1)
        enhanced_features["Active_Symptom_Count"] = (df > 0.1).sum(axis=1)
        
        # 8. Ayırıcı tanı indeksi
        enhanced_features["Diagnostic_Index"] = (
            enhanced_features.get("COVID_Unique_Signature", 0) * 4 +
            enhanced_features.get("Flu_Unique_Signature", 0) * 4 +
            enhanced_features.get("Cold_Unique_Signature", 0) * 3 +
            enhanced_features.get("Allergy_Unique_Signature", 0) * 3
        )
        
        return enhanced_features
    
    def predict_disease(self, text_input):
        """Ultra hassas hastalık tahmini yapar"""
        if self.model_data is None:
            return {
                "error": "Model yüklenemedi. Önce ultra hassas model eğitimi yapın.",
                "prediction": None,
                "probabilities": None,
                "confidence": None
            }
        
        try:
            # Metin girişini işle
            full_vector, parsed_symptoms = self.preprocess_text_input(text_input)
            
            # Ultra hassas özellikler oluştur
            enhanced_features = self.create_ultra_precise_features(full_vector, parsed_symptoms)
            
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
            confidence = self.calculate_ultra_confidence(max_prob, parsed_symptoms, predicted_disease)
            
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
    
    def calculate_ultra_confidence(self, max_prob, parsed_symptoms, predicted_disease):
        """Ultra hassas güven skoru hesaplar"""
        base_confidence = max_prob
        
        # Ayırıcı semptom kontrolü
        if predicted_disease == "COVID-19":
            covid_signatures = ["Koku veya Tat Kaybı", "Nefes Darlığı"]
            signature_count = sum(1 for s in covid_signatures if parsed_symptoms.get(s, 0) > 0.5)
            if signature_count >= 2:
                base_confidence += 0.15
            elif signature_count == 1:
                base_confidence += 0.05
        
        elif predicted_disease == "Grip":
            flu_signatures = ["Vücut Ağrıları", "Titreme"]
            signature_count = sum(1 for s in flu_signatures if parsed_symptoms.get(s, 0) > 0.5)
            if signature_count >= 2:
                base_confidence += 0.15
            elif signature_count == 1:
                base_confidence += 0.05
        
        elif predicted_disease == "Soğuk Algınlığı":
            cold_signatures = ["Burun Akıntısı veya Tıkanıklığı", "Hapşırma"]
            signature_count = sum(1 for s in cold_signatures if parsed_symptoms.get(s, 0) > 0.5)
            if signature_count >= 2:
                base_confidence += 0.15
            elif signature_count == 1:
                base_confidence += 0.05
        
        elif predicted_disease == "Mevsimsel Alerji":
            allergy_signatures = ["Göz Kaşıntısı veya Sulanma", "Hapşırma"]
            signature_count = sum(1 for s in allergy_signatures if parsed_symptoms.get(s, 0) > 0.5)
            if signature_count >= 2:
                base_confidence += 0.15
            elif signature_count == 1:
                base_confidence += 0.05
        
        # Semptom sayısına göre ayarlama
        symptom_count = sum(1 for v in parsed_symptoms.values() if v > 0)
        if symptom_count >= 5:
            base_confidence += 0.1
        elif symptom_count < 2:
            base_confidence -= 0.2
        
        return min(1.0, max(0.0, base_confidence))
    
    def get_ultra_detailed_analysis(self, text_input):
        """Ultra hassas detaylı analiz raporu oluşturur"""
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
            "ultra_recommendations": self.get_ultra_recommendations(result)
        }
        
        return analysis
    
    def get_ultra_recommendations(self, result):
        """Ultra hassas öneriler oluşturur"""
        recommendations = []
        predicted_disease = result["prediction"]
        confidence = result["confidence"]
        
        if confidence < 0.8:
            recommendations.append("⚠️ Orta güven skoru. Doktor konsültasyonu önerilir.")
        elif confidence < 0.9:
            recommendations.append("✅ İyi güven skoru. Takip edin.")
        else:
            recommendations.append("🎯 Yüksek güven skoru. Tanı güvenilir.")
        
        if predicted_disease == "COVID-19":
            recommendations.extend([
                "🏥 COVID-19 şüphesi. Acil doktor konsültasyonu gerekli.",
                "🔒 İzolasyon önerilir.",
                "🧪 PCR testi yaptırın.",
                "📊 Koku/tat kaybı ve nefes darlığı COVID-19'un ayırıcı semptomları."
            ])
        elif predicted_disease == "Grip":
            recommendations.extend([
                "🏥 Grip benzeri semptomlar. Doktor kontrolü önerilir.",
                "💊 Semptomatik tedavi alabilirsiniz.",
                "🛌 Dinlenme ve bol sıvı tüketimi önerilir.",
                "📊 Vücut ağrıları ve titreme grip'in ayırıcı semptomları."
            ])
        elif predicted_disease == "Soğuk Algınlığı":
            recommendations.extend([
                "🏠 Hafif soğuk algınlığı. Evde dinlenin.",
                "💧 Bol sıvı tüketin.",
                "🌡️ Ateş düşürücü kullanabilirsiniz.",
                "📊 Burun akıntısı ve hapşırma soğuk algınlığının ayırıcı semptomları."
            ])
        elif predicted_disease == "Mevsimsel Alerji":
            recommendations.extend([
                "🌸 Mevsimsel alerji belirtileri.",
                "💊 Antihistaminik kullanabilirsiniz.",
                "🏠 Allerjenlerden uzak durun.",
                "📊 Göz kaşıntısı ve hapşırma alerji'nin ayırıcı semptomları."
            ])
        
        return recommendations

def ultra_precise_demo():
    """Ultra hassas demo"""
    print("🎯 ULTRA HASSAS HASTALIK TANİ SİSTEMİ - DEMO")
    print("="*60)
    
    try:
        predictor = UltraPreciseDiseasePredictor()
        
        if predictor.model_data is None:
            print("❌ Ultra hassas model yüklenemedi.")
            return
        
        # Ultra hassas test senaryoları
        demo_tests = [
            "Ateşim var, öksürüyorum",
            "Gözlerim kaşınıyor, hapşırıyorum", 
            "Nefes alamıyorum, koku alamıyorum",
            "Vücudum ağrıyor, titreme var",
            "Burnum akıyor, hapşırıyorum"
        ]
        
        print(f"🧪 {len(demo_tests)} ultra hassas demo senaryosu test ediliyor...\n")
        
        for i, demo_input in enumerate(demo_tests, 1):
            print(f"🔍 Demo {i}: '{demo_input}'")
            
            result = predictor.predict_disease(demo_input)
            
            if not result.get('error'):
                prediction = result['prediction']
                confidence = result['confidence']
                max_prob = result['max_probability']
                
                print(f"🏥 Tahmin: {prediction}")
                print(f"📊 Güven: %{confidence*100:.1f}")
                print(f"🎲 Maksimum Olasılık: %{max_prob*100:.1f}")
                
                # En yüksek 3 olasılık
                sorted_probs = sorted(result['probabilities'].items(), key=lambda x: x[1], reverse=True)
                print("🎯 En yüksek 3 olasılık:")
                for j, (disease, prob) in enumerate(sorted_probs[:3], 1):
                    print(f"   {j}. {disease}: %{prob*100:.1f}")
                
                # Tespit edilen semptomlar
                if result['detected_symptoms']:
                    detected = [f"{s}: {v:.1f}" for s, v in result['detected_symptoms'].items() if v > 0.1]
                    if detected:
                        print(f"🔍 Tespit edilen: {', '.join(detected)}")
            else:
                print(f"❌ Hata: {result['error']}")
            
            print("-" * 60)
        
        print("\n🎉 Ultra hassas demo tamamlandı!")
        print("✅ Sistem başarıyla çalışıyor!")
    
    except Exception as e:
        print(f"❌ Demo sırasında hata: {e}")

if __name__ == "__main__":
    ultra_precise_demo()
