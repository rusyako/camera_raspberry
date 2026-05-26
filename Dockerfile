FROM python:3.11-slim-bookworm

ARG USE_PICAMERA=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopencv-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN if [ "$USE_PICAMERA" = "true" ]; then \
        apt-get update && apt-get install -y --no-install-recommends libcap-dev \
        && rm -rf /var/lib/apt/lists/*; \
    fi

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN if [ "$USE_PICAMERA" = "true" ]; then \
        pip install --no-cache-dir picamera2; \
    fi

COPY src/ src/

RUN mkdir -p /app/recordings

VOLUME ["/app/recordings"]

EXPOSE 5000

ENV CAMERA_MODE=opencv

CMD ["python", "-m", "src.main"]
