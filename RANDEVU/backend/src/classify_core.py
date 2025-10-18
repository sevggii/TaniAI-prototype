#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Klinik Sınıflandırma Core
Eğitilmiş SVM modelini yükler ve tahmin yapar
"""

import joblib
import os
import logging
from typing import Optional, List

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ClinicClassifier:
    """Klinik sınıflandırıcı"""
    
    def __init__(self, model_path: str = "models/clinic_router_svm.joblib"):
        self.model_path = model_path
        self.model_data = None
        self.vectorizer = None
        self.model = None
        self.classes = None
        
    def load_model(self) -> bool:
        """
        Eğitilmiş modeli yükle
        
        Returns:
            Yükleme başarılı mı
        """
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Model dosyası bulunamadı: {self.model_path}")
                return False
            
            logger.info(f"Model yükleniyor: {self.model_path}")
            self.model_data = joblib.load(self.model_path)
            
            self.vectorizer = self.model_data['vectorizer']
            self.model = self.model_data['model']
            self.classes = self.model_data['classes']
            
            logger.info(f"Model başarıyla yüklendi")
            logger.info(f"Klinik sınıfları: {len(self.classes)}")
            logger.info(f"Vektör boyutu: {self.vectorizer.vocabulary_.__len__()}")
            
            return True
            
        except Exception as e:
            logger.error(f"Model yükleme hatası: {e}")
            return False
    
    def predict_clinic(self, text: str) -> str:
        """
        Metni sınıflandır ve klinik öner
        
        Args:
            text: Sınıflandırılacak metin
            
        Returns:
            Önerilen klinik adı
            
        Raises:
            AssertionError: Model yüklenmemiş veya tahmin allowed list dışında
        """
        if not self.model or not self.vectorizer:
            raise AssertionError("Model yüklenmemiş! Önce load_model() çağırın.")
        
        try:
            # Metni vektörize et
            text_vector = self.vectorizer.transform([text])
            
            # Tahmin yap
            prediction = self.model.predict(text_vector)[0]
            
            # Allowed list kontrolü
            assert prediction in self.classes, f"Tahmin allowed list dışında: {prediction}"
            
            logger.info(f"Tahmin: {prediction}")
            
            return prediction
            
        except Exception as e:
            logger.error(f"Tahmin hatası: {e}")
            raise
    
    def predict_with_confidence(self, text: str) -> Optional[dict]:
        """
        Metni sınıflandır ve güven skoru ile birlikte döndür
        
        Args:
            text: Sınıflandırılacak metin
            
        Returns:
            {'clinic': str, 'confidence': float} veya None
        """
        if not self.model or not self.vectorizer:
            logger.error("Model yüklenmemiş! Önce load_model() çağırın.")
            return None
        
        try:
            # Metni vektörize et
            text_vector = self.vectorizer.transform([text])
            
            # Tahmin yap
            prediction = self.model.predict(text_vector)[0]
            
            # Güven skorları al
            confidence_scores = self.model.decision_function(text_vector)[0]
            max_confidence = max(confidence_scores)
            
            # Güven skorunu 0-1 aralığına normalize et
            normalized_confidence = min(1.0, max(0.0, (max_confidence + 1) / 2))
            
            result = {
                'clinic': prediction,
                'confidence': round(normalized_confidence, 3)
            }
            
            logger.info(f"Tahmin: {result['clinic']} (güven: {result['confidence']})")
            
            return result
            
        except Exception as e:
            logger.error(f"Tahmin hatası: {e}")
            return None
    
    def get_available_clinics(self) -> List[str]:
        """
        Mevcut klinik sınıflarını döndür
        
        Returns:
            Klinik sınıfları listesi
        """
        if not self.classes:
            logger.error("Model yüklenmemiş!")
            return []
        
        return self.classes.copy()
    
    def get_model_info(self) -> dict:
        """
        Model hakkında bilgi döndür
        
        Returns:
            Model bilgileri
        """
        if not self.model_data:
            return {"error": "Model yüklenmemiş"}
        
        return {
            "model_path": self.model_path,
            "num_classes": len(self.classes) if self.classes else 0,
            "vocabulary_size": len(self.vectorizer.vocabulary_) if self.vectorizer else 0,
            "classes": self.classes
        }

# Global classifier instance
classifier = ClinicClassifier()

def predict_clinic(text: str) -> str:
    """
    Convenience function for clinic prediction
    
    Args:
        text: Sınıflandırılacak metin
        
    Returns:
        Önerilen klinik adı
        
    Raises:
        AssertionError: Model yüklenmemiş veya tahmin allowed list dışında
    """
    if not classifier.model:
        classifier.load_model()
    
    return classifier.predict_clinic(text)

def predict_clinic_with_confidence(text: str) -> Optional[dict]:
    """
    Convenience function for clinic prediction with confidence
    
    Args:
        text: Sınıflandırılacak metin
        
    Returns:
        {'clinic': str, 'confidence': float} veya None
    """
    if not classifier.model:
        classifier.load_model()
    
    return classifier.predict_with_confidence(text)

def main():
    """Test fonksiyonu"""
    # Modeli yükle
    if classifier.load_model():
        # Test tahminleri
        test_cases = [
            "başım çok ağrıyor",
            "göğsümde sıkışma var",
            "gözlerim bulanık görüyor",
            "karnım ağrıyor",
            "minicik el kesiği"
        ]
        
        print("Test tahminleri:")
        print("-" * 50)
        
        for text in test_cases:
            result = classifier.predict_with_confidence(text)
            if result:
                print(f"'{text}' -> {result['clinic']} (güven: {result['confidence']})")
            else:
                print(f"'{text}' -> HATA")
    else:
        print("Model yüklenemedi!")

if __name__ == "__main__":
    main()
