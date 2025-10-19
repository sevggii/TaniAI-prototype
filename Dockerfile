# ===========================================
# TanıAI Multi-Service Dockerfile
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
    ffmpeg \
    libsndfile1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt* ./
COPY görüntü\ işleme/requirements.txt ./görüntü_işleme_requirements.txt
COPY Tanı-hastalıklar/requirements.txt ./tanı_requirements.txt
COPY RANDEVU/backend/requirements.txt ./randevu_requirements.txt
COPY TANI/UstSolunumYolu/services/triage_api/requirements.txt ./tani_requirements.txt
COPY ilaç\ takibi/requirements.txt ./ilaç_requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip

# Install main requirements
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install module-specific requirements
RUN pip install --no-cache-dir -r görüntü_işleme_requirements.txt || true
RUN pip install --no-cache-dir -r tanı_requirements.txt || true
RUN pip install --no-cache-dir -r randevu_requirements.txt || true
RUN pip install --no-cache-dir -r tani_requirements.txt || true
RUN pip install --no-cache-dir -r ilaç_requirements.txt || true

# Install additional ML dependencies
RUN pip install --no-cache-dir \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    tensorflow \
    scikit-learn \
    opencv-python \
    pillow \
    numpy \
    pandas \
    scipy \
    matplotlib \
    seaborn \
    jupyter \
    fastapi \
    uvicorn \
    sqlalchemy \
    psycopg2-binary \
    redis \
    celery \
    pydantic \
    python-multipart \
    python-jose[cryptography] \
    passlib[bcrypt] \
    python-dotenv \
    requests \
    aiofiles \
    httpx

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/models /app/data /app/logs /app/uploads /app/tmp

# Set permissions
RUN chmod -R 755 /app

# Expose ports
EXPOSE 8000 8001 8002 8003 8004 8005 8006 8007

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden)
CMD ["python", "-m", "uvicorn", "görüntü işleme.api:app", "--host", "0.0.0.0", "--port", "8000"]
