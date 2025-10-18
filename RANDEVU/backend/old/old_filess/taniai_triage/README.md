# TanıAI Klinik Triyaj

LiteLLM ve FastAPI kullanarak Türkçe hasta şikayetlerinden klinik önerisi üreten triayj servisi.

## Kurulum
1. Python 3.11+ ortamı oluşturun.
2. Bağımlılıkları yükleyin:
   ```bash
   pip install -r requirements.txt
   ```
3. Ortam değişkenlerini ayarlayın (örnek `.env.example` dosyasına bakın). Örn:
   ```bash
   export LITELLM_MODEL=ollama/llama3:8b
   export OLLAMA_HOST=http://localhost:11434
   export CLINIC_DATA_PATH=RANDEVU/tum_klinikler_jsonl
   ```

## Ollama ile model hazırlığı
```bash
brew install ollama
ollama pull llama3:8b
```

## OpenAI / Claude kullanımına geçiş
```bash
export LITELLM_MODEL=gpt-4o-mini
export OPENAI_API_KEY=sk-...
```

## Servisi çalıştırma
```bash
uvicorn taniai_triage.app:app --reload
```

## İstek örneği
```bash
curl -X POST http://localhost:8000/triage \
  -H "Content-Type: application/json" \
  -d '{"text":"göğsüm sıkışıyor, soğuk terleme var"}'
```

## CLI testi
```bash
python -m taniai_triage.cli --text "göğsüm sıkışıyor, soğuk terliyorum"
```

## Testler
```bash
pytest -q
```

> **Not:** Allowlist verisi `/mnt/data/klinik_dataset.jsonl` yolundan okunur. Dosya yoksa servis başlatılamaz.
