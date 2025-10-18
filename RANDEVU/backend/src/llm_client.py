#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiteLLM Client
Ollama modelleri ile iletişim kurar
"""

import requests
import json
import logging
from typing import Optional

# Logging ayarla
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LLMClient:
    """LiteLLM ile Ollama modelleri için client"""
    
    def __init__(self, base_url: str = "http://localhost:4000"):
        self.base_url = base_url
        self.normalize_model = "ollama-llama3"
        self.embed_model = "ollama-embed"
        
    def normalize_text(self, text: str) -> str:
        """
        Metni normalize et (yazım/biçim normalizasyonu)
        
        Args:
            text: Ham hasta şikayeti
            
        Returns:
            Normalize edilmiş metin
        """
        try:
            # LiteLLM API'sine istek gönder
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer sk-local"
                },
                json={
                    "model": self.normalize_model,
                    "messages": [
                        {
                            "role": "system",
                            "content": """Sen bir metin normalizasyon asistanısın. 
                            Hasta şikayetlerini temizle ve standartlaştır.
                            
                            KURALLAR:
                            - Sadece normalize edilmiş metni döndür
                            - Yazım hatalarını düzelt
                            - Gereksiz kelimeleri çıkar
                            - Kısaltmaları aç
                            - Tutarlı terminoloji kullan
                            
                            ÖRNEK:
                            Girdi: "başım çok ağrıyor, migren ataklarım var"
                            Çıktı: "baş ağrısı, migren atakları"
                            
                            Girdi: "karnım ağrıyor, mide bulantısı"
                            Çıktı: "karın ağrısı, mide bulantısı"
                            """
                        },
                        {
                            "role": "user",
                            "content": f"Bu metni normalize et: {text}"
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 200
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                normalized_text = result['choices'][0]['message']['content'].strip()
                logger.info(f"Normalize edildi: '{text}' -> '{normalized_text}'")
                return normalized_text
            else:
                logger.error(f"LLM API hatası: {response.status_code}")
                return text  # Hata durumunda orijinal metni döndür
                
        except Exception as e:
            logger.error(f"Normalizasyon hatası: {e}")
            return text  # Hata durumunda orijinal metni döndür
    
    def get_embedding(self, text: str) -> Optional[list]:
        """
        Metin için embedding oluştur
        
        Args:
            text: Embedding oluşturulacak metin
            
        Returns:
            Embedding vektörü veya None
        """
        try:
            response = requests.post(
                f"{self.base_url}/v1/embeddings",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer sk-local"
                },
                json={
                    "model": self.embed_model,
                    "input": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result['data'][0]['embedding']
                logger.info(f"Embedding oluşturuldu: {len(embedding)} boyut")
                return embedding
            else:
                logger.error(f"Embedding API hatası: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Embedding hatası: {e}")
            return None
    
    def test_connection(self) -> bool:
        """LiteLLM bağlantısını test et"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers={"Authorization": "Bearer sk-local"},
                timeout=10
            )
            
            if response.status_code == 200:
                models = response.json()
                logger.info(f"LiteLLM bağlantısı başarılı. Mevcut modeller: {len(models.get('data', []))}")
                return True
            else:
                logger.error(f"LiteLLM bağlantı hatası: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"LiteLLM bağlantı hatası: {e}")
            return False

def main():
    """Test fonksiyonu"""
    client = LLMClient()
    
    # Bağlantıyı test et
    if client.test_connection():
        # Normalizasyon testi
        test_text = "başım çok ağrıyor, migren ataklarım var"
        normalized = client.normalize_text(test_text)
        print(f"Orijinal: {test_text}")
        print(f"Normalize: {normalized}")
    else:
        print("LiteLLM bağlantısı kurulamadı!")

if __name__ == "__main__":
    main()
