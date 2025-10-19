"""
TanıAI Production Entry Point
Railway deployment için ana uygulama dosyası
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and start the main application
if __name__ == "__main__":
    # Railway will set PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    # Import the main FastAPI app from goruntu_isleme module
    try:
        from goruntu_isleme.api import app
        
        import uvicorn
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
    except ImportError:
        # Fallback: create a simple health check app
        from fastapi import FastAPI
        
        app = FastAPI(title="TanıAI", version="1.0.0")
        
        @app.get("/")
        async def root():
            return {"message": "TanıAI Medical Diagnosis System", "status": "running"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "service": "taniai"}
        
        import uvicorn
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port,
            log_level="info"
        )
