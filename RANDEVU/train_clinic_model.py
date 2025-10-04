#!/usr/bin/env python3
"""
Klinik öneri modeli eğitimi
klinik_dataset.jsonl kullanarak fine-tuning
"""

import json
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    TrainingArguments, 
    Trainer,
    DataCollatorForLanguageModeling
)
from datasets import Dataset
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ClinicModelTrainer:
    def __init__(self):
        self.model_name = "microsoft/DialoGPT-small"  # Küçük model
        self.tokenizer = None
        self.model = None
        
    def prepare_dataset(self):
        """klinik_dataset.jsonl'yi eğitim formatına çevir"""
        logger.info("📊 Dataset hazırlanıyor...")
        
        training_data = []
        
        with open('/Users/sevgi/TaniAI-prototype/RANDEVU/mobile_flutter/klinik_dataset.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    complaint = data['complaint']
                    clinic = data['clinic']
                    
                    # Eğitim formatı: "Şikayet: X -> Klinik: Y"
                    formatted_text = f"Şikayet: {complaint} -> Klinik: {clinic}"
                    training_data.append({"text": formatted_text})
        
        logger.info(f"✅ {len(training_data)} eğitim örneği hazırlandı")
        return Dataset.from_list(training_data)
    
    def tokenize_dataset(self, dataset):
        """Dataset'i tokenize et"""
        logger.info("🔤 Tokenization yapılıyor...")
        
        def tokenize_function(examples):
            return self.tokenizer(
                examples["text"],
                truncation=True,
                padding=True,
                max_length=128,
                return_tensors="pt"
            )
        
        return dataset.map(tokenize_function, batched=True)
    
    def train_model(self):
        """Modeli eğit"""
        logger.info("🚀 Model eğitimi başlıyor...")
        
        # 1. Tokenizer ve model yükle
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
        
        # Pad token ekle
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 2. Dataset hazırla
        dataset = self.prepare_dataset()
        tokenized_dataset = self.tokenize_dataset(dataset)
        
        # 3. Eğitim parametreleri
        training_args = TrainingArguments(
            output_dir="./clinic_model",
            overwrite_output_dir=True,
            num_train_epochs=3,
            per_device_train_batch_size=4,
            per_device_eval_batch_size=4,
            warmup_steps=100,
            logging_steps=10,
            save_steps=500,
            save_total_limit=2,
            prediction_loss_only=True,
            remove_unused_columns=False,
        )
        
        # 4. Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False,  # Causal LM için False
        )
        
        # 5. Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=data_collator,
        )
        
        # 6. Eğitimi başlat
        logger.info("🎯 Eğitim başlıyor...")
        trainer.train()
        
        # 7. Modeli kaydet
        trainer.save_model()
        self.tokenizer.save_pretrained("./clinic_model")
        
        logger.info("✅ Model eğitimi tamamlandı!")
        
    def test_model(self, complaint: str):
        """Eğitilmiş modeli test et"""
        if self.model is None or self.tokenizer is None:
            logger.error("Model henüz eğitilmemiş!")
            return None
        
        # Test prompt'u hazırla
        prompt = f"Şikayet: {complaint} -> Klinik:"
        
        # Tokenize et
        inputs = self.tokenizer.encode(prompt, return_tensors="pt")
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + 20,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode et
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Sadece klinik kısmını çıkar
        if "-> Klinik:" in response:
            clinic = response.split("-> Klinik:")[-1].strip()
            return clinic
        
        return "Bilinmeyen"

if __name__ == "__main__":
    trainer = ClinicModelTrainer()
    
    print("🎯 Klinik Model Eğitimi")
    print("=" * 50)
    
    # Eğitimi başlat
    trainer.train_model()
    
    # Test et
    test_complaints = [
        "başım ağrıyor",
        "mide bulantım var",
        "kalp çarpıntım oluyor"
    ]
    
    print("\n🧪 Test Sonuçları:")
    print("-" * 30)
    
    for complaint in test_complaints:
        result = trainer.test_model(complaint)
        print(f"Şikayet: {complaint}")
        print(f"Önerilen Klinik: {result}")
        print()
