import http.server
import socketserver
import json
import logging
from urllib.parse import urlparse

from llm_clinic_analyzer import get_clinic_analyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """Basit HTTP sunucusu; tüm analizler ortak analizör modülü üzerinden gider."""

    analyzer = get_clinic_analyzer()

    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path in ('/', '/health'):
            self._send_response(200, {
                "message": "Clinic LLM Server çalışıyor",
                "status": "healthy",
                "endpoints": ["POST /analyze-complaint"],
                "llm_model": self.analyzer.config.model,
                "dataset_loaded": bool(self.analyzer.clinic_examples),
            })
        else:
            self._send_response(404, {"error": "Not Found"})

    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path != '/analyze-complaint':
            self._send_response(404, {"error": "Not Found"})
            return

        try:
            content_length = int(self.headers.get('Content-Length', 0))
        except (TypeError, ValueError):
            self._send_response(400, {"error": "Invalid Content-Length"})
            return

        payload = self.rfile.read(content_length)
        try:
            data = json.loads(payload.decode('utf-8'))
        except json.JSONDecodeError:
            self._send_response(400, {"error": "Invalid JSON"})
            return

        complaint = (data.get('complaint') or '').strip()
        result = self.analyzer.analyze_complaint(complaint)
        self._send_response(200, result)

    def _send_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        response_data = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_data.encode('utf-8'))


if __name__ == "__main__":
    PORT = 8000
    Handler = RequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logging.info("🤖 Clinic LLM Server başlatıldı: http://localhost:%s", PORT)
        logging.info("Endpoints:")
        logging.info("  GET  /health")
        logging.info("  POST /analyze-complaint")
        httpd.serve_forever()
