FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    HOME=/home/app FLASK_ENV=production FLASK_PORT=8000 OCR_DEBUG=0 \
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libglib2.0-0 libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    python -m pip install -r requirements.txt && \
    python -m pip install "gunicorn>=23,<24"
RUN python -m pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless opencv-contrib-python-headless && \
    python -m pip install --no-cache-dir --no-deps "opencv-python-headless>=4.8,<5" && \
    python -c "import cv2; print('OpenCV import OK:', cv2.__version__); assert hasattr(cv2.dnn, 'readNetFromCaffe')"
RUN useradd --create-home --uid 10001 app
COPY --chown=app:app app.py wsgi.py validate_models.py /app/
COPY --chown=app:app routes/ /app/routes/
COPY --chown=app:app services/ /app/services/
COPY --chown=app:app ml/ /app/ml/
COPY --chown=app:app config/ /app/config/
COPY --chown=app:app silent_face/ /app/silent_face/
USER app
RUN python validate_models.py
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "1", "--timeout", "240", "--access-logfile", "-", "--error-logfile", "-", "wsgi:app"]
