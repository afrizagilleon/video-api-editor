FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt /app/requirements.txt

# install fontconfig agar fc-cache bisa jalan
RUN apt-get update && \
    apt-get install -y fontconfig && \
    rm -rf /var/lib/apt/lists/*

# buat folder untuk font custom
RUN mkdir -p /usr/share/fonts/truetype/oswald

# copy semua ttf dari folder Oswald/static di host
COPY Oswald/static/*.ttf /usr/share/fonts/truetype/oswald/

# set permission + rebuild cache
RUN chmod 644 /usr/share/fonts/truetype/oswald/* && \
    fc-cache -fv


# Install Python deps (MoviePy, faster-whisper, dll.)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir "moviepy>=2.0.0"


# Install auto-editor terpisah
RUN pip install --no-cache-dir auto-editor
RUN pip install requests

# Copy aplikasi
COPY app/ /app/

RUN mkdir -p /app/uploads /app/outputs

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

CMD ["python", "video_editing_api.py"]
