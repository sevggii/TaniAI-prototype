#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Klinik Öneri Model Eğitimi
TF-IDF + LinearSVC ile gerçek makine öğrenmesi modeli eğitir
"""

import json
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import logging

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ClinicModelTrainer:
    """Klinik öneri model eğitimi"""
    
    def __init__(self, data_file: str = "../data/clinic_dataset.jsonl"):
        self.data_file = data_file
        self.vectorizer = TfidfVectorizer(
            max_features=100000,
            stop_words=None,  # Türkçe stop words yok
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95
        )
        self.model = LinearSVC(
            random_state=42,
            max_iter=10000,
            C=1.0
        )
        
    def load_data(self):
        """Veri setini yükle"""
        logger.info("Veri seti yükleniyor...")
        
        complaints = []
        clinics = []
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    complaints.append(data['complaint'])
                    clinics.append(data['clinic'])
        
        logger.info(f"Toplam {len(complaints)} veri yüklendi")
        logger.info(f"Klinik sayısı: {len(set(clinics))}")
        
        return complaints, clinics
    
    def train_model(self):
        """Modeli eğit"""
        logger.info("Model eğitimi başlıyor...")
        
        # Veriyi yükle
        complaints, clinics = self.load_data()
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            complaints, clinics, test_size=0.2, random_state=42, stratify=clinics
        )
        
        logger.info(f"Eğitim verisi: {len(X_train)}")
        logger.info(f"Test verisi: {len(X_test)}")
        
        # TF-IDF vektörizasyonu
        logger.info("TF-IDF vektörizasyonu yapılıyor...")
        X_train_tfidf = self.vectorizer.fit_transform(X_train)
        X_test_tfidf = self.vectorizer.transform(X_test)
        
        logger.info(f"Vektör boyutu: {X_train_tfidf.shape}")
        
        # Model eğitimi
        logger.info("LinearSVC modeli eğitiliyor...")
        self.model.fit(X_train_tfidf, y_train)
        
        # Test performansı
        y_pred = self.model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        
        # F1 skorları
        from sklearn.metrics import f1_score
        f1_macro = f1_score(y_test, y_pred, average='macro')
        f1_weighted = f1_score(y_test, y_pred, average='weighted')
        
        logger.info(f"Test doğruluğu: {accuracy:.4f}")
        logger.info(f"Weighted F1: {f1_weighted:.4f}")
        logger.info(f"Macro F1: {f1_macro:.4f}")
        logger.info("\nSınıflandırma raporu:")
        print(classification_report(y_test, y_pred))
        
        return accuracy
    
    def save_model(self, model_path: str = "../models/clinic_router_svm.joblib"):
        """Modeli kaydet"""
        logger.info("Model kaydediliyor...")
        
        # Klasör oluştur
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Model ve vectorizer'ı birlikte kaydet
        model_data = {
            'vectorizer': self.vectorizer,
            'model': self.model,
            'classes': self.model.classes_.tolist()
        }
        
        joblib.dump(model_data, model_path)
        logger.info(f"Model kaydedildi: {model_path}")
        
        return model_path
    
    def get_class_info(self):
        """Klinik sınıfları hakkında bilgi"""
        logger.info("Klinik sınıfları:")
        for i, clinic in enumerate(self.model.classes_):
            logger.info(f"{i+1:2d}. {clinic}")
        
        logger.info(f"\nToplam {len(self.model.classes_)} klinik sınıfı")

def main():
    """Ana fonksiyon"""
    logger.info("=" * 60)
    logger.info("KLİNİK MODEL EĞİTİMİ BAŞLIYOR")
    logger.info("=" * 60)
    
    trainer = ClinicModelTrainer()
    
    # Modeli eğit
    accuracy = trainer.train_model()
    
    # Modeli kaydet
    model_path = trainer.save_model()
    
    # Sınıf bilgilerini göster
    trainer.get_class_info()
    
    logger.info("=" * 60)
    logger.info("EĞİTİM TAMAMLANDI!")
    logger.info(f"Model dosyası: {model_path}")
    logger.info(f"Test doğruluğu: {accuracy:.4f}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
