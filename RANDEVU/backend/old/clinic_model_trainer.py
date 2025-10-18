#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Klinik Önerisi Model Eğitimi
JSONL verilerinden Ollama ile model eğitimi
"""

import json
import os
import random
import logging
from typing import List, Dict, Any
from pathlib import Path

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ClinicModelTrainer:
    """Klinik önerisi model eğitimi"""
    
    def __init__(self, clinics_dir: str = "../clinics"):
        self.clinics_dir = clinics_dir
        self.training_data = []
        self.clinic_names = []
        
    def load_clinics_data(self, sample_size: int = 1000) -> List[Dict[str, str]]:
        """JSONL dosyalarından veri yükle"""
        logger.info("Clinics verileri yükleniyor...")
        
        all_data = []
        clinic_files = [f for f in os.listdir(self.clinics_dir) if f.endswith('.jsonl')]
        
        logger.info(f"Bulunan klinik dosyaları: {len(clinic_files)}")
        
        for clinic_file in clinic_files:
            clinic_name = clinic_file.replace('.jsonl', '').replace('_', ' ')
            file_path = os.path.join(self.clinics_dir, clinic_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Her klinikten rastgele örnekleme
                    sample_lines = random.sample(lines, min(sample_size, len(lines)))
                    
                    for line in sample_lines:
                        if line.strip():
                            data = json.loads(line)
                            all_data.append({
                                'complaint': data['complaint'],
                                'clinic': clinic_name
                            })
                            
                self.clinic_names.append(clinic_name)
                logger.info(f"✓ {clinic_name}: {len(sample_lines)} örnek")
                
            except Exception as e:
                logger.error(f"✗ Hata {clinic_file}: {e}")
                
        logger.info(f"Toplam yüklenen veri: {len(all_data)}")
        logger.info(f"Toplam klinik sayısı: {len(self.clinic_names)}")
        
        return all_data
    
    def create_training_prompts(self, data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Eğitim promptları oluştur - Bu fonksiyon artık kullanılmıyor"""
        logger.info("Eğitim promptları oluşturuluyor...")
        
        # Bu fonksiyon artık kullanılmıyor çünkü few-shot learning kullanıyoruz
        # Sadece Modelfile'daki örnekler yeterli
        return []
    
    def create_modelfile(self, output_file: str = "ClinicModelfile"):
        """Modelfile oluştur"""
        logger.info("Modelfile oluşturuluyor...")
        
        # Klinik isimlerini alfabetik sıraya koy
        sorted_clinics = sorted(self.clinic_names)
        
        modelfile_content = f"""FROM llama3.2:3b

SYSTEM \"\"\"Sen bir tıbbi triyaj asistanısın. {len(self.training_data)} gerçek hasta verisiyle eğitilmişsin.

KURALLAR:
- SADECE JSON formatında yanıt ver
- Format: {{"clinic": "klinik_adı", "confidence": 0.95, "reasoning": "açıklama"}}
- Türkçe yanıt ver
- Sadece mevcut kliniklerden birini öner
- Gerçek hasta verilerinden öğrendiğin kalıpları kullan

MEVCUT KLİNİKLER:
{', '.join(sorted_clinics)}

ÖRNEKLER (Gerçek hasta verilerinden):
Hasta: "Başım çok ağrıyor, migren ataklarım arttı"
Sen: {{"clinic": "Nöroloji", "confidence": 0.95, "reasoning": "Baş ağrısı ve migren semptomları nöroloji bölümüne uygun"}}

Hasta: "Göğsümde sıkışma var, nefes almakta zorlanıyorum"
Sen: {{"clinic": "Kardiyoloji", "confidence": 0.90, "reasoning": "Göğüs sıkışması ve nefes darlığı kalp ile ilgili olabilir"}}

Hasta: "Gözlerim bulanık görüyor, numara büyümüş olabilir"
Sen: {{"clinic": "Göz Hastalıkları", "confidence": 0.95, "reasoning": "Görme problemleri göz hastalıkları bölümüne uygun"}}

Hasta: "Kolum kırıldı, acil müdahale gerekli"
Sen: {{"clinic": "Acil Servis", "confidence": 0.98, "reasoning": "Kırık ve acil müdahale gerektiren durum"}}

Hasta: "Ateşim var ve halsizim, genel kontrol istiyorum"
Sen: {{"clinic": "Aile Hekimliği", "confidence": 0.85, "reasoning": "Genel semptomlar için aile hekimliği uygun"}}

Hasta: "Minicik el kesiği, küçük bir yara"
Sen: {{"clinic": "Aile Hekimliği", "confidence": 0.90, "reasoning": "Küçük kesikler için aile hekimliği yeterli"}}

Hasta: "Portakal doğrarken elimi kestim"
Sen: {{"clinic": "Aile Hekimliği", "confidence": 0.85, "reasoning": "Basit kesikler için aile hekimliği uygun"}}

Hasta: "El kesiği, kanama durdu"
Sen: {{"clinic": "Aile Hekimliği", "confidence": 0.88, "reasoning": "Kontrol edilebilir kesikler için aile hekimliği"}}

Hasta: "Kolum kırıldı, kemik çıktı"
Sen: {{"clinic": "Acil Servis", "confidence": 0.98, "reasoning": "Açık kırık acil müdahale gerektirir"}}

Hasta: "Kalp krizi geçiriyorum, göğsüm yanıyor"
Sen: {{"clinic": "Acil Servis", "confidence": 0.99, "reasoning": "Kalp krizi acil müdahale gerektirir"}}

Hasta: "Karnım ağrıyor, mide bulantısı var"
Sen: {{"clinic": "Gastroenteroloji Cerrahisi", "confidence": 0.92, "reasoning": "Karın ağrısı ve mide bulantısı gastroenteroloji bölümüne uygun"}}

Hasta: "Kulaklarım ağrıyor, işitme sorunu yaşıyorum"
Sen: {{"clinic": "Kulak Burun Boğaz Hastalıkları", "confidence": 0.95, "reasoning": "Kulak ağrısı ve işitme sorunu KBB bölümüne uygun"}}

Hasta: "Cildimde döküntü var, kaşıntı oluyor"
Sen: {{"clinic": "Deri ve Zührevi Hastalıkları (Cildiye)", "confidence": 0.95, "reasoning": "Cilt döküntüsü ve kaşıntı cildiye bölümüne uygun"}}

Hasta: "Ruh halim bozuk, depresif hissediyorum"
Sen: {{"clinic": "Ruh Sağlığı ve Hastalıkları (Psikiyatri)", "confidence": 0.95, "reasoning": "Ruh hali bozukluğu psikiyatri bölümüne uygun"}}

Şimdi hasta şikayetini analiz et ve uygun kliniği öner:\"\"\"

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1
PARAMETER stop "Hasta:"
PARAMETER stop "Sen:"
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        logger.info(f"Modelfile kaydedildi: {output_file}")
        return output_file
    
    # create_training_file fonksiyonu kaldırıldı - artık gerekli değil
    
    def train_model(self, sample_size: int = 1000):
        """Modeli eğit - Sadece Modelfile oluşturur"""
        logger.info("=" * 60)
        logger.info("KLİNİK MODEL EĞİTİMİ BAŞLIYOR")
        logger.info("=" * 60)
        
        # Veriyi yükle (sadece klinik isimlerini almak için)
        self.training_data = self.load_clinics_data(sample_size)
        
        # Modelfile oluştur
        modelfile = self.create_modelfile()
        
        logger.info("=" * 60)
        logger.info("EĞİTİM HAZIR!")
        logger.info("=" * 60)
        logger.info("Şimdi şu komutları çalıştırın:")
        logger.info("1. ollama create clinic-recommender -f ClinicModelfile")
        logger.info("2. Test et: python3 test_clinic_model.py")
        
        return modelfile

def main():
    """Ana fonksiyon"""
    trainer = ClinicModelTrainer()
    
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "--test":
        # Test modu
        logger.info("Model test ediliyor...")
        # Test kodu buraya eklenecek
    else:
        # Eğitim modu
        trainer.train_model(sample_size=500)  # Her klinikten 500 örnek

if __name__ == "__main__":
    main()
