FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Install system dependencies for OpenCV, OCR, and PDF parsing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy requirements and install
COPY requirements.txt /workspace/
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend codebase
COPY . /workspace/backend/

# Expose API port
EXPOSE 8000

# Command to run FastAPI server
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
