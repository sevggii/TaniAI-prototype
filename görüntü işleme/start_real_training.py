#!/usr/bin/env python3
"""
Gerçek Tıbbi Verilerle Model Eğitimi
====================================
"""

import subprocess
import sys
import logging
import os
from pathlib import Path
from datetime import datetime

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_command(command: str, description: str) -> bool:
    """Komut çalıştır ve sonucu logla"""
    logger.info(f"BASLIYOR: {description}")
    logger.info(f"Komut: {command}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=300  # 5 dakika timeout
        )
        
        if result.returncode == 0:
            logger.info(f"BASARILI: {description}")
            if result.stdout:
                logger.info(f"Çıktı: {result.stdout[:500]}")
            return True
        else:
            logger.error(f"HATA: {description}")
            logger.error(f"Stderr: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"TIMEOUT: {description}")
        return False
    except Exception as e:
        logger.error(f"Beklenmeyen hata: {str(e)}")
        return False


def main():
    """Ana eğitim süreci"""
    logger.info("GERCEK TIBBI VERILERLE MODEL EGITIMI BASLIYOR")
    
    # ADIM 1: TCIA Veri İndirme
    logger.info("ADIM 1: TCIA VERI INDIRME")
    success1 = run_command("python tcia_data_downloader.py", "TCIA veri indirme")
    
    if not success1:
        logger.error("TCIA veri indirme basarisiz, devam ediliyor...")
    
    # ADIM 2: DICOM İşleme
    logger.info("ADIM 2: DICOM ISLEME")
    success2 = run_command("python dicom_processor.py", "DICOM görüntü işleme")
    
    if not success2:
        logger.error("DICOM işleme basarisiz, devam ediliyor...")
    
    # ADIM 3: Model Eğitimi
    logger.info("ADIM 3: MODEL EGITIMI")
    success3 = run_command("python train_tcia_models.py", "TCIA verilerle model eğitimi")
    
    if success3:
        logger.info("GERCEK VERILERLE EGITIM TAMAMLANDI!")
    else:
        logger.error("Model eğitimi basarisiz")
    
    # ADIM 4: Test
    logger.info("ADIM 4: MODEL TEST")
    success4 = run_command("python quick_test.py", "Model test")
    
    if success4:
        logger.info("TEST TAMAMLANDI!")
    else:
        logger.error("Test basarisiz")
    
    logger.info("EGITIM SUREÇI TAMAMLANDI")


if __name__ == "__main__":
    main()
