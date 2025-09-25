# -*- coding: utf-8 -*-
"""
LLM Tabanlı Klinik Analiz Modülü
Whisper transkripsiyonundan LLM ile klinik önerisi yapan sistem
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
import asyncio
import aiohttp
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class LLMConfig:
    """LLM yapılandırma sınıfı"""
    provider: str = "ollama"  # ollama, openai, anthropic
    model: str = "llama2:7b"  # Model adı
    base_url: str = "http://localhost:11434"  # Ollama varsayılan URL
    api_key: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.1
    timeout: int = 30

class LLMClinicAnalyzer:
    """LLM tabanlı klinik analiz sınıfı"""
    
    def __init__(self, config: LLMConfig = None):
        self.config = config or LLMConfig()
        self.clinic_list = self._load_clinic_list()
        self.system_prompt = self._create_system_prompt()
        
    def _load_clinic_list(self) -> List[str]:
        """MHRS klinik listesini yükler"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            txt_path = os.path.join(base_dir, "MHRS_Klinik_Listesi.txt")
            
            clinics = []
            with open(txt_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or "→ ❌" in line or "MHRS" in line or "Doğrudan" in line or "Toplam" in line:
                        continue
                    # Numarayı temizle
                    if ")" in line:
                        name = line.split(")", 1)[1].strip()
                    elif ". " in line[:5]:
                        name = line.split(". ", 1)[1].strip()
                    else:
                        name = line
                    if name:
                        clinics.append(name)
            return clinics
        except Exception as e:
            logger.error(f"Klinik listesi yükleme hatası: {e}")
            return ["Aile Hekimliği", "İç Hastalıkları (Dahiliye)", "Çocuk Sağlığı ve Hastalıkları"]
    
    def _create_system_prompt(self) -> str:
        """Sistem prompt'unu oluşturur"""
        clinic_list_str = "\n".join([f"- {clinic}" for clinic in self.clinic_list])
        
        return f"""Sen Türkiye'deki MHRS (Merkezi Hekim Randevu Sistemi) için çalışan bir tıbbi triage asistanısın. 

Görevin: Hastanın sesli şikayetlerini analiz ederek hangi kliniğe yönlendirilmesi gerektiğini belirlemek.

Mevcut Klinikler:
{clinic_list_str}

Kurallar:
1. Sadece yukarıdaki kliniklerden birini öner
2. Acil durumları tespit et (kalp krizi, inme, şiddetli travma vb.)
3. Çocuk hastalar için "Çocuk Sağlığı ve Hastalıkları" öncelikli
4. Belirsiz durumlar için "Aile Hekimliği" veya "İç Hastalıkları (Dahiliye)" öner
5. Sadece JSON formatında yanıt ver

Yanıt Formatı:
{{
    "clinic": "Klinik Adı",
    "confidence": 0.85,
    "reasoning": "Neden bu kliniği önerdiğin",
    "urgency": "normal|high|emergency",
    "alternative_clinics": ["Alternatif 1", "Alternatif 2"]
}}"""

    async def analyze_with_llm_async(self, transcript: str) -> Dict[str, Any]:
        """LLM ile asenkron analiz"""
        try:
            if self.config.provider == "ollama":
                return await self._analyze_with_ollama_async(transcript)
            elif self.config.provider == "openai":
                return await self._analyze_with_openai_async(transcript)
            else:
                raise ValueError(f"Desteklenmeyen provider: {self.config.provider}")
        except Exception as e:
            logger.error(f"LLM analiz hatası: {e}")
            return self._fallback_analysis(transcript)
    
    def analyze_with_llm(self, transcript: str) -> Dict[str, Any]:
        """LLM ile senkron analiz"""
        try:
            if self.config.provider == "ollama":
                return self._analyze_with_ollama(transcript)
            elif self.config.provider == "openai":
                return self._analyze_with_openai(transcript)
            else:
                raise ValueError(f"Desteklenmeyen provider: {self.config.provider}")
        except Exception as e:
            logger.error(f"LLM analiz hatası: {e}")
            return self._fallback_analysis(transcript)
    
    async def _analyze_with_ollama_async(self, transcript: str) -> Dict[str, Any]:
        """Ollama ile asenkron analiz"""
        url = f"{self.config.base_url}/api/generate"
        
        payload = {
            "model": self.config.model,
            "prompt": f"{self.system_prompt}\n\nHasta Şikayeti: {transcript}",
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.timeout)) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    response_text = result.get("response", "")
                    return self._parse_llm_response(response_text)
                else:
                    raise Exception(f"Ollama API hatası: {response.status}")
    
    def _analyze_with_ollama(self, transcript: str) -> Dict[str, Any]:
        """Ollama ile senkron analiz"""
        url = f"{self.config.base_url}/api/generate"
        
        payload = {
            "model": self.config.model,
            "prompt": f"{self.system_prompt}\n\nHasta Şikayeti: {transcript}",
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.config.timeout)
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                return self._parse_llm_response(response_text)
            else:
                raise Exception(f"Ollama API hatası: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama bağlantı hatası: {e}")
    
    async def _analyze_with_openai_async(self, transcript: str) -> Dict[str, Any]:
        """OpenAI ile asenkron analiz"""
        import openai
        
        client = openai.AsyncOpenAI(api_key=self.config.api_key)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Hasta Şikayeti: {transcript}"}
        ]
        
        response = await client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        response_text = response.choices[0].message.content
        return self._parse_llm_response(response_text)
    
    def _analyze_with_openai(self, transcript: str) -> Dict[str, Any]:
        """OpenAI ile senkron analiz"""
        import openai
        
        client = openai.OpenAI(api_key=self.config.api_key)
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Hasta Şikayeti: {transcript}"}
        ]
        
        response = client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
        
        response_text = response.choices[0].message.content
        return self._parse_llm_response(response_text)
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """LLM yanıtını parse eder"""
        try:
            # JSON kısmını bul
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                result = json.loads(json_str)
                
                # Validasyon
                if "clinic" not in result:
                    raise ValueError("clinic alanı bulunamadı")
                
                # Klinik adını doğrula
                if result["clinic"] not in self.clinic_list:
                    # En yakın kliniği bul
                    result["clinic"] = self._find_closest_clinic(result["clinic"])
                
                return {
                    "success": True,
                    "clinic": result["clinic"],
                    "confidence": result.get("confidence", 0.8),
                    "reasoning": result.get("reasoning", "LLM analizi"),
                    "urgency": result.get("urgency", "normal"),
                    "alternative_clinics": result.get("alternative_clinics", []),
                    "method": "llm"
                }
            else:
                raise ValueError("JSON formatı bulunamadı")
                
        except Exception as e:
            logger.error(f"LLM yanıt parse hatası: {e}")
            return self._fallback_analysis(response_text)
    
    def _find_closest_clinic(self, clinic_name: str) -> str:
        """En yakın kliniği bulur"""
        clinic_name_lower = clinic_name.lower()
        
        # Tam eşleşme
        for clinic in self.clinic_list:
            if clinic.lower() == clinic_name_lower:
                return clinic
        
        # Kısmi eşleşme
        for clinic in self.clinic_list:
            if clinic_name_lower in clinic.lower() or clinic.lower() in clinic_name_lower:
                return clinic
        
        # Varsayılan
        return "Aile Hekimliği"
    
    def _fallback_analysis(self, transcript: str) -> Dict[str, Any]:
        """Fallback analiz (LLM çalışmazsa)"""
        transcript_lower = transcript.lower()
        
        # Basit kural tabanlı analiz
        if any(word in transcript_lower for word in ["çocuk", "oğlum", "kızım", "bebek"]):
            clinic = "Çocuk Sağlığı ve Hastalıkları"
        elif any(word in transcript_lower for word in ["kalp", "çarpıntı", "göğüs ağrısı"]):
            clinic = "Kardiyoloji"
        elif any(word in transcript_lower for word in ["baş ağrısı", "migren", "nöroloji"]):
            clinic = "Nöroloji"
        elif any(word in transcript_lower for word in ["diş", "diş ağrısı"]):
            clinic = "Diş Hekimliği (Genel Diş)"
        else:
            clinic = "Aile Hekimliği"
        
        return {
            "success": True,
            "clinic": clinic,
            "confidence": 0.6,
            "reasoning": "Fallback kural tabanlı analiz",
            "urgency": "normal",
            "alternative_clinics": ["İç Hastalıkları (Dahiliye)"],
            "method": "fallback"
        }
    
    def check_llm_availability(self) -> Dict[str, Any]:
        """LLM servisinin erişilebilirliğini kontrol eder"""
        try:
            if self.config.provider == "ollama":
                response = requests.get(f"{self.config.base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [model["name"] for model in models]
                    return {
                        "available": True,
                        "provider": "ollama",
                        "models": model_names,
                        "current_model": self.config.model
                    }
                else:
                    return {"available": False, "error": f"HTTP {response.status_code}"}
            else:
                return {"available": True, "provider": self.config.provider}
        except Exception as e:
            return {"available": False, "error": str(e)}

# Global analyzer instance
_llm_analyzer: Optional[LLMClinicAnalyzer] = None

def get_llm_analyzer(config: LLMConfig = None) -> LLMClinicAnalyzer:
    """LLM analyzer instance'ını döndürür"""
    global _llm_analyzer
    if _llm_analyzer is None:
        _llm_analyzer = LLMClinicAnalyzer(config)
    return _llm_analyzer

def create_llm_config_from_env() -> LLMConfig:
    """Çevre değişkenlerinden LLM config oluşturur"""
    return LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "ollama"),
        model=os.getenv("LLM_MODEL", "llama2:7b"),
        base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434"),
        api_key=os.getenv("LLM_API_KEY"),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
        timeout=int(os.getenv("LLM_TIMEOUT", "30"))
    )
