# ===========================================
# TanıAI Randevu Sistemi API Dockerfile
# ===========================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install additional dependencies
RUN pip install --no-cache-dir \
    scikit-learn \
    numpy \
    pandas \
    scipy \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    redis \
    pydantic \
    python-multipart \
    python-jose[cryptography] \
    passlib[bcrypt] \
    python-dotenv \
    requests \
    aiofiles \
    httpx \
    joblib

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/tmp

# Set permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "simple_api:app", "--host", "0.0.0.0", "--port", "8000"]
