# -*- coding: utf-8 -*-
"""
Entegre Triage Sistemi
ML + LLM tabanlı hibrit klinik öneri sistemi
"""

import logging
import os
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass

from .triage_model import get_triage_model
from .llm_clinic_analyzer import get_llm_analyzer, LLMConfig, create_llm_config_from_env

logger = logging.getLogger(__name__)

@dataclass
class TriageConfig:
    """Triage yapılandırma sınıfı"""
    use_ml: bool = True
    use_llm: bool = True
    ml_weight: float = 0.6
    llm_weight: float = 0.4
    fallback_to_ml: bool = True
    fallback_to_rules: bool = True

class IntegratedTriageSystem:
    """Entegre triage sistemi"""
    
    def __init__(self, triage_config: TriageConfig = None, llm_config: LLMConfig = None):
        self.triage_config = triage_config or TriageConfig()
        self.llm_config = llm_config or create_llm_config_from_env()
        
        # Modelleri yükle
        self.ml_model = None
        self.llm_analyzer = None
        
        if self.triage_config.use_ml:
            try:
                self.ml_model = get_triage_model()
                logger.info("ML model başarıyla yüklendi")
            except Exception as e:
                logger.error(f"ML model yükleme hatası: {e}")
                self.triage_config.use_ml = False
        
        if self.triage_config.use_llm:
            try:
                self.llm_analyzer = get_llm_analyzer(self.llm_config)
                # LLM erişilebilirliğini kontrol et
                availability = self.llm_analyzer.check_llm_availability()
                if not availability.get("available", False):
                    logger.warning(f"LLM erişilemez: {availability.get('error', 'Bilinmeyen hata')}")
                    self.triage_config.use_llm = False
                else:
                    logger.info(f"LLM model başarıyla yüklendi: {availability.get('current_model', 'Bilinmeyen')}")
            except Exception as e:
                logger.error(f"LLM model yükleme hatası: {e}")
                self.triage_config.use_llm = False
    
    async def suggest_async(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        """Asenkron klinik önerisi"""
        results = {}
        
        # ML analizi
        if self.triage_config.use_ml and self.ml_model:
            try:
                ml_result = self.ml_model.suggest(text, top_k)
                results["ml"] = ml_result
            except Exception as e:
                logger.error(f"ML analiz hatası: {e}")
                results["ml"] = {"error": str(e)}
        
        # LLM analizi
        if self.triage_config.use_llm and self.llm_analyzer:
            try:
                llm_result = await self.llm_analyzer.analyze_with_llm_async(text)
                results["llm"] = llm_result
            except Exception as e:
                logger.error(f"LLM analiz hatası: {e}")
                results["llm"] = {"error": str(e)}
        
        return self._combine_results(results, text, top_k)
    
    def suggest(self, text: str, top_k: int = 3) -> Dict[str, Any]:
        """Senkron klinik önerisi"""
        results = {}
        
        # ML analizi
        if self.triage_config.use_ml and self.ml_model:
            try:
                ml_result = self.ml_model.suggest(text, top_k)
                results["ml"] = ml_result
            except Exception as e:
                logger.error(f"ML analiz hatası: {e}")
                results["ml"] = {"error": str(e)}
        
        # LLM analizi
        if self.triage_config.use_llm and self.llm_analyzer:
            try:
                llm_result = self.llm_analyzer.analyze_with_llm(text)
                results["llm"] = llm_result
            except Exception as e:
                logger.error(f"LLM analiz hatası: {e}")
                results["llm"] = {"error": str(e)}
        
        return self._combine_results(results, text, top_k)
    
    def _combine_results(self, results: Dict[str, Any], text: str, top_k: int) -> Dict[str, Any]:
        """Sonuçları birleştirir"""
        combined = {
            "suggestions": [],
            "confidence_scores": {},
            "reasoning": {},
            "methods_used": [],
            "raw_results": results
        }
        
        # Acil durum kontrolü (ML'den)
        if "ml" in results and "action" in results["ml"] and results["ml"]["action"] == "ACIL":
            return results["ml"]
        
        # LLM acil durum kontrolü
        if "llm" in results and results["llm"].get("urgency") == "emergency":
            return {
                "action": "ACIL",
                "red_flag": "LLM Emergency",
                "message": "LLM acil durum tespit etti. 112'yi arayın veya en yakın acile başvurun.",
                "llm_reasoning": results["llm"].get("reasoning", "")
            }
        
        # Sonuçları birleştir
        clinic_scores = {}
        clinic_reasoning = {}
        
        # ML sonuçları
        if "ml" in results and "suggestions" in results["ml"]:
            ml_suggestions = results["ml"]["suggestions"]
            combined["methods_used"].append("ml")
            
            for i, clinic in enumerate(ml_suggestions):
                # ML skorunu hesapla (sıralama bazlı)
                ml_score = (len(ml_suggestions) - i) / len(ml_suggestions) * self.triage_config.ml_weight
                clinic_scores[clinic] = clinic_scores.get(clinic, 0) + ml_score
                clinic_reasoning[clinic] = clinic_reasoning.get(clinic, [])
                clinic_reasoning[clinic].append(f"ML: {results['ml'].get('why', {}).get(clinic, 'ML skoru')}")
        
        # LLM sonuçları
        if "llm" in results and results["llm"].get("success"):
            llm_clinic = results["llm"].get("clinic")
            llm_confidence = results["llm"].get("confidence", 0.8)
            combined["methods_used"].append("llm")
            
            if llm_clinic:
                llm_score = llm_confidence * self.triage_config.llm_weight
                clinic_scores[llm_clinic] = clinic_scores.get(llm_clinic, 0) + llm_score
                clinic_reasoning[llm_clinic] = clinic_reasoning.get(llm_clinic, [])
                clinic_reasoning[llm_clinic].append(f"LLM: {results['llm'].get('reasoning', 'LLM analizi')}")
                
                # Alternatif klinikleri de ekle
                for alt_clinic in results["llm"].get("alternative_clinics", []):
                    alt_score = llm_confidence * 0.3 * self.triage_config.llm_weight
                    clinic_scores[alt_clinic] = clinic_scores.get(alt_clinic, 0) + alt_score
                    clinic_reasoning[alt_clinic] = clinic_reasoning.get(alt_clinic, [])
                    clinic_reasoning[alt_clinic].append(f"LLM Alternatif: {results['llm'].get('reasoning', '')}")
        
        # Fallback: Hiçbir model çalışmazsa
        if not clinic_scores and self.triage_config.fallback_to_rules:
            from .triage_direct import suggest as direct_suggest
            try:
                fallback_result = direct_suggest(text, top_k)
                if "suggestions" in fallback_result:
                    combined["methods_used"].append("fallback_rules")
                    for clinic in fallback_result["suggestions"]:
                        clinic_scores[clinic] = 0.5
                        clinic_reasoning[clinic] = [f"Fallback: {fallback_result.get('why', {}).get(clinic, 'Kural tabanlı')}"]
            except Exception as e:
                logger.error(f"Fallback analiz hatası: {e}")
        
        # Sonuçları sırala
        if clinic_scores:
            sorted_clinics = sorted(clinic_scores.items(), key=lambda x: x[1], reverse=True)
            combined["suggestions"] = [clinic for clinic, _ in sorted_clinics[:top_k]]
            combined["confidence_scores"] = {clinic: score for clinic, score in sorted_clinics[:top_k]}
            combined["reasoning"] = {clinic: "; ".join(reasons) for clinic, reasons in clinic_reasoning.items() if clinic in combined["suggestions"]}
        else:
            # Son çare
            combined["suggestions"] = ["Aile Hekimliği"]
            combined["confidence_scores"] = {"Aile Hekimliği": 0.3}
            combined["reasoning"] = {"Aile Hekimliği": "Son çare önerisi"}
            combined["methods_used"].append("emergency_fallback")
        
        return combined
    
    def get_system_status(self) -> Dict[str, Any]:
        """Sistem durumunu döndürür"""
        status = {
            "ml_available": self.triage_config.use_ml and self.ml_model is not None,
            "llm_available": False,
            "llm_provider": self.llm_config.provider,
            "llm_model": self.llm_config.model,
            "config": {
                "use_ml": self.triage_config.use_ml,
                "use_llm": self.triage_config.use_llm,
                "ml_weight": self.triage_config.ml_weight,
                "llm_weight": self.triage_config.llm_weight
            }
        }
        
        if self.triage_config.use_llm and self.llm_analyzer:
            llm_status = self.llm_analyzer.check_llm_availability()
            status["llm_available"] = llm_status.get("available", False)
            status["llm_details"] = llm_status
        
        return status

# Global integrated triage instance
_integrated_triage: Optional[IntegratedTriageSystem] = None

def get_integrated_triage(config: TriageConfig = None, llm_config: LLMConfig = None) -> IntegratedTriageSystem:
    """Entegre triage sistemi instance'ını döndürür"""
    global _integrated_triage
    if _integrated_triage is None:
        _integrated_triage = IntegratedTriageSystem(config, llm_config)
    return _integrated_triage

def create_triage_config_from_env() -> TriageConfig:
    """Çevre değişkenlerinden triage config oluşturur"""
    return TriageConfig(
        use_ml=os.getenv("USE_ML", "true").lower() == "true",
        use_llm=os.getenv("USE_LLM", "true").lower() == "true",
        ml_weight=float(os.getenv("ML_WEIGHT", "0.6")),
        llm_weight=float(os.getenv("LLM_WEIGHT", "0.4")),
        fallback_to_ml=os.getenv("FALLBACK_TO_ML", "true").lower() == "true",
        fallback_to_rules=os.getenv("FALLBACK_TO_RULES", "true").lower() == "true"
    )
