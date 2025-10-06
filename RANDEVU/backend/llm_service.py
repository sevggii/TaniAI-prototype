#!/usr/bin/env python3
"""
LLM Servisi
Ollama ve diğer LLM sağlayıcıları ile entegrasyon
"""

import os
import json
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

class LLMService:
    """LLM servisi - Ollama ve diğer sağlayıcılar"""
    
    def __init__(self):
        self.ollama_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model_name = os.getenv("LITELLM_MODEL", "llama3.2:3b")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "30"))
        
        # Model sağlayıcısını belirle
        if self.model_name.startswith("ollama/"):
            self.provider = "ollama"
            self.model_name = self.model_name.replace("ollama/", "")
        elif self.model_name.startswith("gpt-"):
            self.provider = "openai"
        elif self.model_name.startswith("gemini/"):
            self.provider = "google"
        else:
            self.provider = "ollama"  # Varsayılan
        
        logging.info(f"LLM Service initialized: {self.provider}/{self.model_name}")
    
    def get_chat_response(self, message: str, context: str = "medical_assistant") -> str:
        """Chat yanıtı al"""
        try:
            if self.provider == "ollama":
                return self._call_ollama(message, context)
            elif self.provider == "openai":
                return self._call_openai(message, context)
            elif self.provider == "google":
                return self._call_google(message, context)
            else:
                return self._get_fallback_response(message)
        except Exception as e:
            logging.error(f"LLM call error: {e}")
            return self._get_fallback_response(message)
    
    def _call_ollama(self, message: str, context: str) -> str:
        """Ollama API'sini çağır"""
        try:
            # Sistem prompt'u oluştur
            system_prompt = self._get_system_prompt(context)
            
            # Prompt'u hazırla
            full_prompt = f"{system_prompt}\n\nKullanıcı: {message}\nAsistan:"
            
            payload = {
                "model": self.model_name,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "max_tokens": 512,
                    "top_p": 0.9,
                    "repeat_penalty": 1.1
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                logging.error(f"Ollama API error: {response.status_code}")
                return self._get_fallback_response(message)
                
        except requests.exceptions.Timeout:
            logging.error("Ollama timeout")
            return self._get_fallback_response(message)
        except Exception as e:
            logging.error(f"Ollama call error: {e}")
            return self._get_fallback_response(message)
    
    def _call_openai(self, message: str, context: str) -> str:
        """OpenAI API'sini çağır"""
        try:
            import openai
            
            client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            
            system_prompt = self._get_system_prompt(context)
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                max_tokens=512
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logging.error(f"OpenAI call error: {e}")
            return self._get_fallback_response(message)
    
    def _call_google(self, message: str, context: str) -> str:
        """Google Gemini API'sini çağır"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
            
            model = genai.GenerativeModel(self.model_name.replace("gemini/", ""))
            
            system_prompt = self._get_system_prompt(context)
            full_prompt = f"{system_prompt}\n\nKullanıcı: {message}"
            
            response = model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=512
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            logging.error(f"Google Gemini call error: {e}")
            return self._get_fallback_response(message)
    
    def _get_system_prompt(self, context: str) -> str:
        """Sistem prompt'unu al"""
        if context == "medical_assistant":
            return """Sen TanıAI Asistanısın, Türkiye'de sağlık hizmetleri konusunda uzman bir yapay zeka asistanısın. 

Görevlerin:
1. Kullanıcıların sağlık sorularını yanıtlamak
2. Randevu alma konusunda rehberlik etmek
3. Semptom analizi yapmak (sadece genel bilgi amaçlı)
4. Uygun klinik önerileri sunmak
5. Eczane ve ilaç bilgileri vermek

Önemli kurallar:
- Tıbbi teşhis koyma, sadece genel bilgi ver
- Acil durumlarda 112'yi aramalarını söyle
- Doktor muayenesi öner
- Türkçe yanıt ver
- Kısa ve net yanıtlar ver
- Empatik ve anlayışlı ol"""
        
        return "Sen yardımcı bir AI asistanısın. Kullanıcılara yardımcı olmaya çalış."
    
    def _get_fallback_response(self, message: str) -> str:
        """Fallback yanıtlar"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['randevu', 'appointment', 'doktor']):
            return "Randevu almak için size yardımcı olabilirim! Hangi bölüm için randevu almak istiyorsunuz?"
        
        elif any(word in message_lower for word in ['semptom', 'ağrı', 'hasta']):
            return "Semptomlarınız hakkında konuşabiliriz, ancak kesin teşhis için mutlaka bir doktora başvurmanızı öneririm."
        
        elif any(word in message_lower for word in ['eczane', 'ilaç']):
            return "Eczane ve ilaç konularında size yardımcı olabilirim. Yakınızdaki eczaneleri bulmak için eczane bulma özelliğini kullanabilirsiniz."
        
        elif any(word in message_lower for word in ['merhaba', 'selam', 'hello']):
            return "Merhaba! Ben TanıAI Asistanıyım. Size nasıl yardımcı olabilirim?"
        
        else:
            return "Anlıyorum. Size daha iyi yardımcı olabilmem için daha spesifik bir soru sorabilir misiniz?"
