#!/usr/bin/env python3
"""
LLM Konfigürasyon Yöneticisi
Farklı model sağlayıcıları için LiteLLM entegrasyonu
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ModelProvider(Enum):
    """Desteklenen model sağlayıcıları"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COLAB = "colab"

@dataclass
class ModelConfig:
    """Model konfigürasyonu"""
    name: str
    provider: ModelProvider
    api_base: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 256
    description: str = ""

class LLMConfigManager:
    """LLM konfigürasyon yöneticisi"""
    
    def __init__(self):
        self.configs = self._load_configs()
        self.current_config = self._get_current_config()
    
    def _load_configs(self) -> Dict[str, ModelConfig]:
        """Tüm model konfigürasyonlarını yükle"""
        return {
            # Ollama modelleri (lokal)
            "ollama_tinyllama": ModelConfig(
                name="ollama/tinyllama",
                provider=ModelProvider.OLLAMA,
                api_base="http://localhost:11434",
                temperature=0.1,
                max_tokens=256,
                description="TinyLLaMA - Hızlı, küçük model (1B parametre)"
            ),
            "ollama_llama3.2_3b": ModelConfig(
                name="ollama/llama3.2:3b",
                provider=ModelProvider.OLLAMA,
                api_base="http://localhost:11434",
                temperature=0.1,
                max_tokens=512,
                description="Llama 3.2 3B - Dengeli performans (3.2B parametre)"
            ),
            "ollama_llama3.2_1b": ModelConfig(
                name="ollama/llama3.2:1b",
                provider=ModelProvider.OLLAMA,
                api_base="http://localhost:11434",
                temperature=0.1,
                max_tokens=256,
                description="Llama 3.2 1B - Çok hızlı, küçük model (1B parametre)"
            ),
            
            # OpenAI modelleri
            "openai_gpt4o_mini": ModelConfig(
                name="gpt-4o-mini",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.1,
                max_tokens=512,
                description="GPT-4o Mini - OpenAI'nin en hızlı modeli"
            ),
            "openai_gpt3.5_turbo": ModelConfig(
                name="gpt-3.5-turbo",
                provider=ModelProvider.OPENAI,
                api_key=os.getenv("OPENAI_API_KEY"),
                temperature=0.1,
                max_tokens=256,
                description="GPT-3.5 Turbo - Hızlı ve ekonomik"
            ),
            
            # Google modelleri
            "google_gemini_flash": ModelConfig(
                name="gemini/gemini-1.5-flash",
                provider=ModelProvider.GOOGLE,
                api_key=os.getenv("GOOGLE_API_KEY"),
                temperature=0.1,
                max_tokens=512,
                description="Gemini 1.5 Flash - Google'ın hızlı modeli"
            ),
            
            # Colab/Kaggle için özel konfigürasyonlar
            "colab_llama3.2_3b": ModelConfig(
                name="ollama/llama3.2:3b",
                provider=ModelProvider.COLAB,
                api_base="http://localhost:11434",  # Colab'da ngrok ile expose edilecek
                temperature=0.1,
                max_tokens=512,
                description="Colab'da çalışan Llama 3.2 3B"
            ),
        }
    
    def _get_current_config(self) -> ModelConfig:
        """Mevcut konfigürasyonu al"""
        # Önce environment variable'dan kontrol et
        model_name = os.getenv("LITELLM_MODEL", "ollama_llama3.2_3b")
        
        if model_name in self.configs:
            return self.configs[model_name]
        
        # Varsayılan olarak Ollama Llama 3.2 3B
        return self.configs["ollama_llama3.2_3b"]
    
    def get_config(self, config_name: Optional[str] = None) -> ModelConfig:
        """Belirtilen konfigürasyonu al"""
        if config_name and config_name in self.configs:
            return self.configs[config_name]
        return self.current_config
    
    def list_available_configs(self) -> Dict[str, str]:
        """Mevcut konfigürasyonları listele"""
        return {
            name: config.description 
            for name, config in self.configs.items()
        }
    
    def set_config(self, config_name: str) -> bool:
        """Konfigürasyonu değiştir"""
        if config_name in self.configs:
            self.current_config = self.configs[config_name]
            return True
        return False
    
    def get_litellm_params(self, config_name: Optional[str] = None) -> Dict[str, Any]:
        """LiteLLM için parametreleri hazırla"""
        config = self.get_config(config_name)
        
        params = {
            "model": config.name,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        
        if config.api_base:
            params["api_base"] = config.api_base
        
        if config.api_key:
            params["api_key"] = config.api_key
        
        return params

# Global instance
config_manager = LLMConfigManager()

def get_llm_config(config_name: Optional[str] = None) -> ModelConfig:
    """LLM konfigürasyonunu al"""
    return config_manager.get_config(config_name)

def get_litellm_params(config_name: Optional[str] = None) -> Dict[str, Any]:
    """LiteLLM parametrelerini al"""
    return config_manager.get_litellm_params(config_name)

def list_available_models() -> Dict[str, str]:
    """Mevcut modelleri listele"""
    return config_manager.list_available_configs()

def set_llm_model(model_name: str) -> bool:
    """LLM modelini değiştir"""
    return config_manager.set_config(model_name)

if __name__ == "__main__":
    print("🤖 Mevcut LLM Modelleri:")
    print("=" * 50)
    
    for name, description in list_available_models().items():
        print(f"📌 {name}")
        print(f"   {description}")
        print()
    
    print("🔧 Mevcut Konfigürasyon:")
    current = get_llm_config()
    print(f"Model: {current.name}")
    print(f"Provider: {current.provider.value}")
    print(f"Description: {current.description}")
