#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Turkish Medical Anamnesis Classification - Inference Script
Predicts the appropriate clinic for a given Turkish anamnesis text
"""

import joblib
import json
import re
import sys
from typing import List, Tuple

# Turkish stopwords (same as in training)
TURKISH_STOPWORDS = {
    'acaba', 'ama', 'ancak', 'artık', 'aslında', 'az', 'bana', 'bazı', 'belki',
    'ben', 'beni', 'benim', 'beri', 'beş', 'bile', 'bin', 'bir', 'birçok',
    'birkaç', 'birşey', 'biz', 'bizim', 'bu', 'buna', 'bunda', 'bundan',
    'bunlar', 'bunları', 'bunların', 'bunu', 'bunun', 'burada', 'çok',
    'çünkü', 'da', 'daha', 'dahi', 'de', 'defa', 'diye', 'dokuz', 'dört',
    'eğer', 'en', 'gibi', 'hem', 'hep', 'hepsi', 'her', 'hiç', 'hiçbir',
    'için', 'iki', 'ile', 'ilgili', 'ise', 'işte', 'kadar', 'karşın',
    'kendi', 'kendine', 'kendini', 'kendisi', 'kendisine', 'kendisini',
    'ki', 'kim', 'kimden', 'kime', 'kimi', 'kimse', 'mı', 'mi', 'mu',
    'mü', 'nasıl', 'ne', 'neden', 'nerede', 'nereden', 'nereye', 'niçin',
    'niye', 'o', 'olan', 'olarak', 'olduğu', 'olduğunu', 'olsa', 'olur',
    'on', 'ona', 'ondan', 'onlar', 'onlara', 'onlardan', 'onları', 'onların',
    'onu', 'onun', 'otuz', 'şey', 'şu', 'şuna', 'şunda', 'şundan', 'şunlar',
    'şunları', 'şunların', 'şunu', 'şunun', 'tüm', 'var', 've', 'veya',
    'ya', 'yani', 'yedi', 'yirmi', 'yok', 'zaten', 'zira'
}

class ClinicPredictor:
    """Turkish medical anamnesis clinic predictor"""
    
    def __init__(self, model_path: str = 'models/clinic_classifier.pkl',
                 vectorizer_path: str = 'models/tfidf_vectorizer.pkl',
                 clinic_names_path: str = 'models/clinic_names.json'):
        """
        Initialize the predictor with trained model and vectorizer
        """
        try:
            # Load model
            self.model = joblib.load(model_path)
            print(f"✓ Model loaded from {model_path}")
            
            # Load vectorizer
            self.vectorizer = joblib.load(vectorizer_path)
            print(f"✓ Vectorizer loaded from {vectorizer_path}")
            
            # Load clinic names
            with open(clinic_names_path, 'r', encoding='utf-8') as f:
                self.clinic_names = json.load(f)
            print(f"✓ Clinic names loaded from {clinic_names_path}")
            print(f"✓ Total clinics: {len(self.clinic_names)}")
            
        except FileNotFoundError as e:
            print(f"Error: Could not find required files. Please run train_model.py first.")
            print(f"Missing file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading model files: {e}")
            sys.exit(1)
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess Turkish text (same as training)
        """
        if not text or text.strip() == "":
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove Turkish-specific characters normalization
        text = text.replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u')
        text = text.replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
        
        # Remove punctuation and special characters
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Remove Turkish stopwords
        words = text.split()
        words = [word for word in words if word not in TURKISH_STOPWORDS and len(word) > 2]
        
        return ' '.join(words)
    
    def predict_clinic(self, anamnesis_text: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Predict the most likely clinic(s) for given anamnesis text
        
        Args:
            anamnesis_text: Turkish anamnesis text
            top_k: Number of top predictions to return
            
        Returns:
            List of tuples (clinic_name, probability)
        """
        # Preprocess text
        processed_text = self.preprocess_text(anamnesis_text)
        
        if not processed_text:
            return [("Geçersiz metin", 0.0)]
        
        # Transform text to vector
        text_vector = self.vectorizer.transform([processed_text])
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(text_vector)[0]
        
        # Get top-k predictions
        top_indices = probabilities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            clinic_name = self.clinic_names[idx]
            probability = probabilities[idx]
            results.append((clinic_name, probability))
        
        return results
    
    def predict_single(self, anamnesis_text: str) -> str:
        """
        Predict the most likely clinic for given anamnesis text
        
        Args:
            anamnesis_text: Turkish anamnesis text
            
        Returns:
            Most likely clinic name
        """
        predictions = self.predict_clinic(anamnesis_text, top_k=1)
        return predictions[0][0]

def interactive_mode():
    """Interactive mode for testing predictions"""
    
    print("\n" + "="*60)
    print("TÜRKÇE TIBBİ ANAMNEZ KLİNİK TAHMİN SİSTEMİ")
    print("Turkish Medical Anamnesis Clinic Prediction System")
    print("="*60)
    print("\nBu sistem Türkçe anamnez metinlerini analiz ederek")
    print("hangi kliniğe yönlendirilmesi gerektiğini tahmin eder.")
    print("\nÇıkış için 'quit' veya 'exit' yazın.")
    print("-"*60)
    
    # Initialize predictor
    try:
        predictor = ClinicPredictor()
    except SystemExit:
        return
    
    while True:
        print("\n" + "-"*40)
        anamnesis = input("Anamnez metnini girin: ").strip()
        
        if anamnesis.lower() in ['quit', 'exit', 'çıkış']:
            print("Görüşürüz!")
            break
        
        if not anamnesis:
            print("Lütfen geçerli bir anamnez metni girin.")
            continue
        
        try:
            # Get predictions
            predictions = predictor.predict_clinic(anamnesis, top_k=3)
            
            print(f"\n📋 Anamnez: {anamnesis}")
            print(f"\n🎯 Tahmin Edilen Klinikler:")
            
            for i, (clinic, prob) in enumerate(predictions, 1):
                confidence = prob * 100
                print(f"{i}. {clinic} ({confidence:.1f}% güven)")
            
            # Show top prediction
            top_clinic = predictions[0][0]
            top_confidence = predictions[0][1] * 100
            
            print(f"\n✅ En Olası Klinik: {top_clinic}")
            print(f"   Güven Seviyesi: {top_confidence:.1f}%")
            
        except Exception as e:
            print(f"Hata oluştu: {e}")

def batch_mode(input_file: str, output_file: str = None):
    """Batch mode for processing multiple texts"""
    
    try:
        predictor = ClinicPredictor()
    except SystemExit:
        return
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            texts = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Dosya bulunamadı: {input_file}")
        return
    
    results = []
    for i, text in enumerate(texts, 1):
        try:
            prediction = predictor.predict_single(text)
            results.append(f"{i}. Metin: {text}")
            results.append(f"   Tahmin: {prediction}")
            results.append("")
        except Exception as e:
            results.append(f"{i}. Hata: {e}")
            results.append("")
    
    # Save or print results
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))
        print(f"Sonuçlar {output_file} dosyasına kaydedildi.")
    else:
        print('\n'.join(results))

def main():
    """Main function"""
    
    if len(sys.argv) == 1:
        # Interactive mode
        interactive_mode()
    elif len(sys.argv) == 2:
        # Single text prediction
        text = sys.argv[1]
        try:
            predictor = ClinicPredictor()
            prediction = predictor.predict_single(text)
            print(f"Anamnez: {text}")
            print(f"Tahmin Edilen Klinik: {prediction}")
        except SystemExit:
            pass
    elif len(sys.argv) == 3:
        # Batch mode
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        batch_mode(input_file, output_file)
    else:
        print("Kullanım:")
        print("  python inference.py                    # Etkileşimli mod")
        print("  python inference.py 'anamnez metni'    # Tek metin tahmini")
        print("  python inference.py input.txt output.txt # Toplu işlem")

if __name__ == "__main__":
    main()


'''
PS D:\TaniAI-prototype> & C:/Users/Grundig/AppData/Local/Programs/Python/Python310/python.exe d:/TaniAI-prototype/RANDEVU/inference.py

============================================================
Turkish Medical Anamnesis Clinic Prediction System

Bu sistem Türkçe anamnez metinlerini analiz ederek
hangi kliniğe yönlendirilmesi gerektiğini tahmin eder.

Çıkış için 'quit' veya 'exit' yazın.
------------------------------------------------------------
Error: Could not find required files. Please run train_model.py first.
Missing file: [Errno 2] No such file or directory: 'models/clinic_classifier.pkl'  
PS D:\TaniAI-prototype> cd d:\TaniAI-prototype\RANDEVU
PS D:\TaniAI-prototype\RANDEVU> & C:/Users/Grundig/AppData/Local/Programs/Python/Python310/python.exe d:/TaniAI-prototype/RANDEVU/inference.py

============================================================
TÜRKÇE TIBBİ ANAMNEZ KLİNİK TAHMİN SİSTEMİ
Turkish Medical Anamnesis Clinic Prediction System
============================================================

Bu sistem Türkçe anamnez metinlerini analiz ederek
hangi kliniğe yönlendirilmesi gerektiğini tahmin eder.

Çıkış için 'quit' veya 'exit' yazın.
------------------------------------------------------------
✓ Model loaded from models/clinic_classifier.pkl
✓ Vectorizer loaded from models/tfidf_vectorizer.pkl
✓ Clinic names loaded from models/clinic_names.json
✓ Total clinics: 66

----------------------------------------
Anamnez metnini girin: dişim çok ağrıyor

📋 Anamnez: dişim çok ağrıyor

🎯 Tahmin Edilen Klinikler:
1. Nefroloji (2.7% güven)
2. Genel Cerrahi (2.4% güven)
3. Aile Hekimliği (2.3% güven)

✅ En Olası Klinik: Nefroloji
   Güven Seviyesi: 2.7%

----------------------------------------
Anamnez metnini girin: burnum akıyor boğazım ağrıyor hapşuruyorum

📋 Anamnez: burnum akıyor boğazım ağrıyor hapşuruyorum

🎯 Tahmin Edilen Klinikler:
1. Aile Hekimliği (1.9% güven)
2. Beyin ve Sinir Cerrahisi (1.8% güven)
3. Radyoloji (1.8% güven)

✅ En Olası Klinik: Aile Hekimliği
   Güven Seviyesi: 1.9%

----------------------------------------



'''