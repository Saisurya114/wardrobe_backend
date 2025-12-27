# Use Python 3.9.18 as base image
FROM python:3.9.18-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for image processing and ML libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY inventory/ ./inventory/

# Create necessary directories
RUN mkdir -p images/raw images/clean images/permanent images/temp temp

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose port (default 8000, can be overridden by PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:${PORT:-8000}/')" || exit 1

# Run the application
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

