FROM balenalib/raspberrypi4-64-python:3.11-bookworm AS pi

RUN install_packages \
    libopencv-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-pip \
    build-essential \
    libcap-dev

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir --no-build-isolation picamera2

COPY src/ src/

RUN mkdir -p /app/recordings

VOLUME ["/app/recordings"]

EXPOSE 5000

ENV CAMERA_MODE=picamera2

CMD ["python", "-m", "src.main"]


FROM python:3.11-slim-bookworm AS dev

ARG USE_PICAMERA=false

RUN apt-get update && apt-get install -y --no-install-recommends \
    libopencv-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN if [ "$USE_PICAMERA" = "true" ]; then \
        apt-get update && apt-get install -y --no-install-recommends \
            build-essential \
            libcap-dev \
            python3-dev \
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

ENV CAMERA_MODE=${USE_PICAMERA:+picamera2}
ENV CAMERA_MODE=${CAMERA_MODE:-opencv}

CMD ["python", "-m", "src.main"]
