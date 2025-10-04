#!/usr/bin/env python3
"""
Ollama ile fine-tuning
Daha basit ve hızlı yöntem
"""

import json
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaFineTuner:
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.base_model = "tinyllama"
        self.finetuned_model = "clinic-tinyllama"
        
    def prepare_training_data(self):
        """klinik_dataset.jsonl'yi Ollama formatına çevir"""
        logger.info("📊 Training data hazırlanıyor...")
        
        training_data = []
        
        with open('/Users/sevgi/TaniAI-prototype/RANDEVU/mobile_flutter/klinik_dataset.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    complaint = data['complaint']
                    clinic = data['clinic']
                    
                    # Ollama fine-tuning formatı
                    training_data.append({
                        "prompt": f"Şikayet: {complaint}\nKlinik:",
                        "completion": f" {clinic}"
                    })
        
        logger.info(f"✅ {len(training_data)} training örneği hazırlandı")
        return training_data
    
    def create_modelfile(self, training_data):
        """Modelfile oluştur"""
        logger.info("📝 Modelfile oluşturuluyor...")
        
        modelfile_content = f"""FROM {self.base_model}

# Klinik öneri sistemi için fine-tuned model
# 8000 hasta verisi ile eğitildi

SYSTEM Sen bir tıbbi asistan AI'sın. Kullanıcının şikayetini analiz edip en uygun kliniği öneriyorsun.

# Eğitim örnekleri:
"""
        
        # İlk 100 örneği ekle (çok fazla olmasın)
        for i, example in enumerate(training_data[:100]):
            modelfile_content += f"# Örnek {i+1}: {example['prompt']}{example['completion']}\n"
        
        # Modelfile'ı kaydet
        with open('Modelfile', 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        logger.info("✅ Modelfile oluşturuldu")
    
    def create_finetuned_model(self):
        """Fine-tuned model oluştur"""
        logger.info("🚀 Fine-tuning başlıyor...")
        
        # 1. Training data hazırla
        training_data = self.prepare_training_data()
        
        # 2. Modelfile oluştur
        self.create_modelfile(training_data)
        
        # 3. Ollama'ya model oluştur komutu gönder
        try:
            response = requests.post(
                f"{self.ollama_url}/api/create",
                json={
                    "name": self.finetuned_model,
                    "modelfile": open('Modelfile', 'r').read()
                },
                timeout=300  # 5 dakika timeout
            )
            
            if response.status_code == 200:
                logger.info("✅ Fine-tuned model oluşturuldu!")
                return True
            else:
                logger.error(f"❌ Model oluşturma hatası: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Fine-tuning hatası: {e}")
            return False
    
    def test_finetuned_model(self, complaint: str):
        """Fine-tuned modeli test et"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.finetuned_model,
                    "prompt": f"Şikayet: {complaint}\nKlinik:",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logger.error(f"Test hatası: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Test hatası: {e}")
            return None

if __name__ == "__main__":
    tuner = OllamaFineTuner()
    
    print("🎯 Ollama Fine-tuning")
    print("=" * 50)
    
    # Fine-tuning yap
    success = tuner.create_finetuned_model()
    
    if success:
        # Test et
        test_complaints = [
            "başım ağrıyor",
            "mide bulantım var",
            "kalp çarpıntım oluyor"
        ]
        
        print("\n🧪 Test Sonuçları:")
        print("-" * 30)
        
        for complaint in test_complaints:
            result = tuner.test_finetuned_model(complaint)
            print(f"Şikayet: {complaint}")
            print(f"Önerilen Klinik: {result}")
            print()
    else:
        print("❌ Fine-tuning başarısız!")
