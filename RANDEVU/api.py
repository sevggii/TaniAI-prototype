"""
Production-Grade API Server
Entegre triage sistemi ile yeni JSON şeması
"""

import http.server
import socketserver
import json
import logging
import socket
import time
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any

# Triage sistemini import et
from ml_clinic.integrated_triage import IntegratedTriage, TriageConfig


# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class APIRequestHandler(http.server.SimpleHTTPRequestHandler):
    """API isteklerini işleyen handler"""
    
    def __init__(self, *args, triage_system=None, **kwargs):
        self.triage_system = triage_system
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """GET isteklerini işler"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self._send_response(200, {
                "message": "TanıAI Production API Server",
                "version": "2.0.0",
                "status": "healthy",
                "endpoints": {
                    "POST /whisper/clinic-from-text": "LLM tabanlı klinik analizi",
                    "POST /whisper/clinic-from-text-llm": "LLM tabanlı klinik analizi (alias)",
                    "GET /whisper/system-status": "Sistem durumu ve ağ ipuçları",
                    "GET /health": "Sağlık kontrolü"
                }
            })
        
        elif parsed_path.path == '/health':
            self._send_response(200, {
                "status": "healthy",
                "timestamp": time.time(),
                "triage_system": "loaded" if self.triage_system else "not_loaded"
            })
        
        elif parsed_path.path == '/whisper/system-status':
            self._send_system_status()
        
        else:
            self._send_response(404, {"error": "Not Found"})
    
    def do_POST(self):
        """POST isteklerini işler"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path in ['/whisper/clinic-from-text', '/whisper/clinic-from-text-llm']:
            self._handle_clinic_analysis()
        else:
            self._send_response(404, {"error": "Not Found"})
    
    def _handle_clinic_analysis(self):
        """Klinik analizi isteğini işler"""
        try:
            # İçerik uzunluğunu kontrol et
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self._send_response(400, {"error": "Empty request body"})
                return
            
            # JSON verisini oku
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Şikayet metnini al
            complaint = data.get('complaint', '').strip()
            if not complaint:
                self._send_response(400, {"error": "Missing or empty complaint"})
                return
            
            # Triage sistemi yüklü mü kontrol et
            if not self.triage_system:
                self._send_response(500, {"error": "Triage system not loaded"})
                return
            
            # Analizi yap
            start_time = time.time()
            result = self.triage_system.analyze_complaint(complaint)
            analysis_time = int((time.time() - start_time) * 1000)
            
            # Latency bilgisini güncelle
            result['latency_ms'] = analysis_time
            
            # Başarılı yanıt
            self._send_response(200, result)
            
        except json.JSONDecodeError:
            self._send_response(400, {"error": "Invalid JSON"})
        except Exception as e:
            logging.error(f"Klinik analiz hatası: {e}")
            self._send_response(500, {"error": f"Internal Server Error: {str(e)}"})
    
    def _send_system_status(self):
        """Sistem durumu ve ağ ipuçları döndürür"""
        try:
            # Local IP adresini bul
            local_ip = self._get_local_ip()
            
            # Port bilgisini al
            port = self.server.server_address[1]
            
            status = {
                "status": "healthy",
                "timestamp": time.time(),
                "triage_system": {
                    "loaded": self.triage_system is not None,
                    "rag_enabled": self.triage_system.config.rag_enabled if self.triage_system else False,
                    "cache_enabled": self.triage_system.config.cache_enabled if self.triage_system else False,
                    "model": self.triage_system.config.model_name if self.triage_system else "unknown"
                },
                "network_hints": {
                    "emulator_android": f"http://10.0.2.2:{port}",
                    "same_wifi": f"http://{local_ip}:{port}",
                    "localhost": f"http://localhost:{port}",
                    "remote": "Use ngrok or a hosted service (Railway/VPS)"
                },
                "endpoints": {
                    "clinic_analysis": "/whisper/clinic-from-text",
                    "system_status": "/whisper/system-status",
                    "health_check": "/health"
                }
            }
            
            self._send_response(200, status)
            
        except Exception as e:
            logging.error(f"Sistem durumu hatası: {e}")
            self._send_response(500, {"error": "Failed to get system status"})
    
    def _get_local_ip(self) -> str:
        """Local IP adresini bulur"""
        try:
            # Dummy connection ile local IP'yi bul
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                local_ip = s.getsockname()[0]
                return local_ip
        except Exception:
            return "127.0.0.1"
    
    def _send_response(self, status_code: int, data: Dict[str, Any]):
        """JSON yanıtı gönderir"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_data.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Log mesajlarını özelleştirir"""
        logging.info(f"{self.address_string()} - {format % args}")


def create_handler_with_triage(triage_system):
    """Triage sistemi ile handler oluşturur"""
    def handler(*args, **kwargs):
        return APIRequestHandler(*args, triage_system=triage_system, **kwargs)
    return handler


def main():
    """Ana server fonksiyonu"""
    PORT = 8000
    
    # Triage sistemini başlat
    logging.info("🚀 TanıAI Production API Server başlatılıyor...")
    
    config = TriageConfig()
    config.dataset_path = "/Users/sevgi/TaniAI-prototype/RANDEVU/mobile_flutter/klinik_dataset.jsonl"
    config.canonical_path = "/Users/sevgi/TaniAI-prototype/RANDEVU/data/mhrs_canonical.json"
    
    try:
        triage_system = IntegratedTriage(config)
        logging.info("✅ Triage sistemi başlatıldı")
    except Exception as e:
        logging.error(f"❌ Triage sistemi başlatılamadı: {e}")
        triage_system = None
    
    # Handler'ı oluştur
    handler = create_handler_with_triage(triage_system)
    
    # Server'ı başlat
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            logging.info(f"🌐 Server başlatıldı: http://localhost:{PORT}")
            logging.info("📋 Endpoints:")
            logging.info("  GET  / - Ana sayfa")
            logging.info("  GET  /health - Sağlık kontrolü")
            logging.info("  GET  /whisper/system-status - Sistem durumu")
            logging.info("  POST /whisper/clinic-from-text - Klinik analizi")
            logging.info("  POST /whisper/clinic-from-text-llm - Klinik analizi (alias)")
            
            if triage_system:
                logging.info("🤖 Triage sistemi aktif")
                logging.info(f"📊 Dataset: {config.dataset_path}")
                logging.info(f"🦙 Model: {config.model_name}")
                logging.info(f"🔍 RAG: {'Aktif' if config.rag_enabled else 'Pasif'}")
                logging.info(f"💾 Cache: {'Aktif' if config.cache_enabled else 'Pasif'}")
            else:
                logging.warning("⚠️ Triage sistemi yüklenemedi - sadece health check çalışacak")
            
            httpd.serve_forever()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            logging.error(f"❌ Port {PORT} zaten kullanımda. Lütfen farklı bir port deneyin.")
        else:
            logging.error(f"❌ Server başlatma hatası: {e}")
    except KeyboardInterrupt:
        logging.info("🛑 Server durduruldu")
    except Exception as e:
        logging.error(f"❌ Beklenmeyen hata: {e}")


if __name__ == "__main__":
    main()
