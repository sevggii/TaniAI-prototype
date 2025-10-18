#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dataset Builder
clinics/*.jsonl dosyalarını birleştirerek clinic_dataset.jsonl oluşturur
"""

import json
import os
import logging
from pathlib import Path
from typing import Set, List, Dict, Any

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DatasetBuilder:
    """Dataset oluşturucu"""
    
    def __init__(self, clinics_dir: str = "../clinics", output_dir: str = "../data"):
        self.clinics_dir = clinics_dir
        self.output_dir = output_dir
        self.clinic_labels: Set[str] = set()
        self.dataset: List[Dict[str, Any]] = []
        
    def load_clinics_data(self):
        """Clinics klasöründeki tüm JSONL dosyalarını yükle"""
        logger.info("Clinics verileri yükleniyor...")
        
        if not os.path.exists(self.clinics_dir):
            raise FileNotFoundError(f"Clinics klasörü bulunamadı: {self.clinics_dir}")
        
        clinic_files = [f for f in os.listdir(self.clinics_dir) if f.endswith('.jsonl')]
        logger.info(f"Bulunan klinik dosyaları: {len(clinic_files)}")
        
        total_loaded = 0
        total_skipped = 0
        
        for clinic_file in clinic_files:
            clinic_name = clinic_file.replace('.jsonl', '').replace('_', ' ')
            file_path = os.path.join(self.clinics_dir, clinic_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_loaded = 0
                    file_skipped = 0
                    
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if not line:
                            continue
                            
                        try:
                            data = json.loads(line)
                            
                            # Şema kontrolü
                            if not isinstance(data, dict):
                                logger.warning(f"{clinic_file}:{line_num} - Geçersiz JSON formatı")
                                file_skipped += 1
                                continue
                            
                            # Gerekli alanları kontrol et
                            complaint = data.get('complaint', '').strip()
                            clinic = data.get('clinic', '').strip()
                            
                            # Clinic alanı yoksa dosya adından üret
                            if not clinic:
                                clinic = clinic_name
                            
                            # Boş complaint kontrolü
                            if not complaint:
                                logger.warning(f"{clinic_file}:{line_num} - Boş complaint")
                                file_skipped += 1
                                continue
                            
                            # Veri kaydet
                            record = {
                                'id': f"{clinic_name}_{line_num}",
                                'complaint': complaint,
                                'clinic': clinic
                            }
                            
                            self.dataset.append(record)
                            self.clinic_labels.add(clinic)
                            file_loaded += 1
                            
                        except json.JSONDecodeError as e:
                            logger.warning(f"{clinic_file}:{line_num} - JSON parse hatası: {e}")
                            file_skipped += 1
                            continue
                
                total_loaded += file_loaded
                total_skipped += file_skipped
                logger.info(f"✓ {clinic_name}: {file_loaded} yüklendi, {file_skipped} atlandı")
                
            except Exception as e:
                logger.error(f"✗ {clinic_file} okuma hatası: {e}")
                continue
        
        logger.info(f"Toplam yüklenen: {total_loaded}")
        logger.info(f"Toplam atlanan: {total_skipped}")
        logger.info(f"Benzersiz klinik sayısı: {len(self.clinic_labels)}")
    
    def remove_duplicates(self):
        """Tekrarları kaldır (complaint + clinic çiftine göre)"""
        logger.info("Tekrarlar kaldırılıyor...")
        
        seen = set()
        unique_dataset = []
        
        for record in self.dataset:
            key = (record['complaint'], record['clinic'])
            if key not in seen:
                seen.add(key)
                unique_dataset.append(record)
        
        removed_count = len(self.dataset) - len(unique_dataset)
        self.dataset = unique_dataset
        
        logger.info(f"Tekrar kaldırıldı: {removed_count}")
        logger.info(f"Benzersiz kayıt sayısı: {len(self.dataset)}")
    
    def save_dataset(self):
        """Dataset'i kaydet"""
        logger.info("Dataset kaydediliyor...")
        
        # Çıktı klasörünü oluştur
        os.makedirs(self.output_dir, exist_ok=True)
        
        # clinic_dataset.jsonl kaydet
        dataset_path = os.path.join(self.output_dir, "clinic_dataset.jsonl")
        with open(dataset_path, 'w', encoding='utf-8') as f:
            for record in self.dataset:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        logger.info(f"Dataset kaydedildi: {dataset_path}")
        
        # clinic_labels.txt kaydet
        labels_path = os.path.join(self.output_dir, "clinic_labels.txt")
        sorted_labels = sorted(self.clinic_labels)
        with open(labels_path, 'w', encoding='utf-8') as f:
            for label in sorted_labels:
                f.write(label + '\n')
        
        logger.info(f"Klinik etiketleri kaydedildi: {labels_path}")
        logger.info(f"Toplam {len(sorted_labels)} benzersiz klinik")
        
        return dataset_path, labels_path
    
    def build(self):
        """Tam dataset oluşturma süreci"""
        logger.info("=" * 60)
        logger.info("DATASET OLUŞTURMA BAŞLIYOR")
        logger.info("=" * 60)
        
        # Veriyi yükle
        self.load_clinics_data()
        
        # Tekrarları kaldır
        self.remove_duplicates()
        
        # Kaydet
        dataset_path, labels_path = self.save_dataset()
        
        logger.info("=" * 60)
        logger.info("DATASET OLUŞTURMA TAMAMLANDI!")
        logger.info(f"Dataset: {dataset_path}")
        logger.info(f"Etiketler: {labels_path}")
        logger.info(f"Toplam kayıt: {len(self.dataset)}")
        logger.info(f"Klinik sayısı: {len(self.clinic_labels)}")
        logger.info("=" * 60)
        
        return dataset_path, labels_path

def main():
    """Ana fonksiyon"""
    builder = DatasetBuilder()
    builder.build()

if __name__ == "__main__":
    main()
