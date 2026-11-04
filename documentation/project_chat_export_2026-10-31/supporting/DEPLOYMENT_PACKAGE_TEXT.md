# Separate deployment package text

These artifacts were produced in the hosting chat outside the main repository. A local package does not prove its exact bytes are the currently deployed image.


---

## C:\Users\ikari\Documents\Codex\2026-10-22\referenced-chatgpt-conversation-this-is-an\outputs\Dockerfile

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    HOME=/home/app FLASK_ENV=production FLASK_PORT=8000 OCR_DEBUG=0 \
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libglib2.0-0 libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    python -m pip install -r requirements.txt
RUN python -m pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless opencv-contrib-python-headless &&     python -m pip install --no-cache-dir --no-deps "opencv-python-headless>=4.8,<5" &&     python -c "import cv2; print('OpenCV import OK:', cv2.__version__); assert hasattr(cv2.dnn, 'readNetFromCaffe')"
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



---

## C:\Users\ikari\Documents\Codex\2026-10-22\referenced-chatgpt-conversation-this-is-an\outputs\Verity-deployment-guide.md

# Verity AI deployment package

This is a deployment copy of the local identity-verification AI service. The original repository was not modified. It includes existing cached model weights, runtime source and the deployed SVM artifacts. It excludes .env files, identity images, debugging output, training datasets and frontend/backend code.

Status: Python syntax and SVM artifact hashes checked locally. Container build and inference have not been tested because Docker is unavailable on this computer. Azure must successfully build the image before deployment. Dependencies other than scikit-learn are not fully locked; retain the successful build's dependency list for later reproducibility.

## 1. Create the registry

In a separate Azure portal tab, search for Container registries and select Create. Select your Azure for Students subscription, your Verity resource group (create verity-rg if necessary), a supported region, a globally unique registry name containing only letters and numbers, and the Basic pricing tier. This registry and its build tasks consume student credit independently of Container Apps' free allowance. Do not select Premium.

Keep the registry private. Use RBAC registry permissions for the simplest managed-identity pull setup. ACR Tasks availability depends on subscription permissions and policy; if Azure rejects the build, retain the exact error rather than changing subscriptions or upgrading billing.

## 2. Build in Azure Cloud Shell

Open Cloud Shell, choose Bash, and select the student subscription. Use an ephemeral session without storage if offered. Upload verity-deploy.zip using Manage files > Upload. Run these commands, replacing YOUR_REGISTRY_NAME with the actual registry resource name (not its login-server address):

```bash
unzip verity-deploy.zip
cd verity-deploy
az acr build --registry YOUR_REGISTRY_NAME --image verity-ai:v1 --platform linux/amd64 .
```

The build installs CPU PyTorch and attempts to load all four model components, including running both anti-spoof networks on synthetic data. It fails if those checks fail. A passing build is not a complete endpoint or accuracy test. Model weights are included to avoid downloading them on every startup.

## 3. Fill the Container Apps form after a successful build

- Container name: verity
- Image source: Azure Container Registry
- Registry: the registry you created
- Image: verity-ai
- Tag: v1
- CPU: 2; RAM: 4 GiB as an initial profiling configuration
- Command/arguments: leave blank to use the packaged Gunicorn startup
- Registry authentication: managed identity with AcrPull on this RBAC registry; use the portal's role assignment option if available
- Environment: Consumption workload profile
- HTTP ingress: enabled, external if called by a backend hosted outside the environment
- Target port: 8000
- Minimum replicas: 0; maximum replicas: 1; single active revision

Create a random secret at least 32 characters long in Azure, then reference it as the VERITY_API_KEY environment variable. Do not put the secret in source code or the container image. The deployment wrapper requires it. Every API call other than /health must send the X-API-Key header. Update the Node backend's AI request helper to send that header from a server-side environment variable before connecting it; never send this secret from the frontend. The backend change is not included in this package.

The wrapper caps total request bodies at 20 MiB. This is not a decoded-image pixel limit. Gunicorn uses one synchronous worker to avoid duplicate model loads and concurrent access to shared inference objects. Large images and inference times still require testing. Configure startup probes with enough time for all models to load; use /health on port 8000 for HTTP probes. Startup failures should be diagnosed from logs, not bypassed by disabling model validation.

## 4. Verify before using real traffic

Confirm /health returns 200 after model initialization. Check that unauthenticated AI calls return 401, then test all four endpoints through the backend with the secret header. Measure memory, latency and first-request startup on representative test inputs. Confirm memory stays below the allocation with headroom. A 4 GiB allocation is an estimate, not a verified limit. Review registry/build/logging/compute costs in Cost Management.

Documentation: https://learn.microsoft.com/en-us/azure/container-registry/container-registry-quickstart-task-cli

Cloud Shell uploads: https://learn.microsoft.com/en-us/azure/cloud-shell/using-the-shell-window



---

## verity-github-build-fixed.zip: verity-github-build/.dockerignore

**/__pycache__
**/*.pyc
.git
.env
.env.*
*.zip
README.md



---

## verity-github-build-fixed.zip: verity-github-build/app.py

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys

# Ensure ai-service root is on the path when running as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from routes.qualityRoutes import quality_bp
from routes.ocrRoutes import ocr_bp
from routes.faceRoutes import face_bp
from routes.livenessRoutes import liveness_bp
from routes.svmRoutes import svm_bp

load_dotenv()

app = Flask(__name__)
CORS(app)

PORT = int(os.getenv('FLASK_PORT', 5000))
ENV = os.getenv('FLASK_ENV', 'development')

app.register_blueprint(quality_bp, url_prefix='/api/quality')
app.register_blueprint(ocr_bp, url_prefix='/api/ocr')
app.register_blueprint(face_bp, url_prefix='/api/face')
app.register_blueprint(liveness_bp, url_prefix='/api/liveness')
app.register_blueprint(svm_bp, url_prefix='/api/svm')


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # use_reloader=False so concurrently/npm can manage the process cleanly
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=(ENV == 'development'),
        use_reloader=False,
    )



---

## verity-github-build-fixed.zip: verity-github-build/Dockerfile

FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    HOME=/home/app FLASK_ENV=production FLASK_PORT=8000 OCR_DEBUG=0 \
    OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libglib2.0-0 libgomp1 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    python -m pip install -r requirements.txt
RUN python -m pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless opencv-contrib-python-headless &&     python -m pip install --no-cache-dir --no-deps "opencv-python-headless>=4.8,<5" &&     python -c "import cv2; print('OpenCV import OK:', cv2.__version__); assert hasattr(cv2.dnn, 'readNetFromCaffe')"
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



---

## verity-github-build-fixed.zip: verity-github-build/requirements.txt

flask
flask-cors
opencv-python-headless>=4.8,<5
easyocr
insightface
onnxruntime
# Pinned: ml/models/*.pkl were pickled with 1.9 â€” retrain with ml/train_model.py after upgrading
scikit-learn==1.9.0
joblib
numpy
pillow
python-dotenv
torch
torchvision
timm
easydict
tqdm

gunicorn>=23,<24



---

## verity-github-build-fixed.zip: verity-github-build/validate_models.py

import numpy as np
from app import app
from services import faceMatchService as face, livenessService as live, svmService as svm
from services.ocrService import get_reader

def validate():
    face.ensure_model_ready()
    live.ensure_model_ready()
    if not svm.model_loaded:
        raise RuntimeError("SVM model failed to load")
    get_reader()
    # Validate both anti-spoof networks without using a real person's image.
    from pathlib import Path
    for path in Path(live.MODEL_DIR).glob("*.pth"):
        live._model.predict(np.zeros((80, 80, 3), dtype=np.uint8), str(path))
    print("All four model components loaded successfully", flush=True)

if __name__ == "__main__":
    validate()



---

## verity-github-build-fixed.zip: verity-github-build/wsgi.py

import os
import hmac
from flask import request, jsonify
from validate_models import app, validate

key = os.environ.get("VERITY_API_KEY", "")
if len(key) < 32:
    raise RuntimeError("Set VERITY_API_KEY to a random secret of at least 32 characters")
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
validate()

@app.before_request
def require_api_key():
    if request.path == "/health":
        return None
    if not hmac.compare_digest(request.headers.get("X-API-Key", ""), key):
        return jsonify(error="Unauthorized"), 401



---

## verity-github-build-fixed.zip: verity-github-build/.github/workflows/build.yml

name: Build Verity AI
on:
  workflow_dispatch:
permissions:
  contents: read
  packages: write
jobs:
  build:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v7
      - name: Set image name
        run: echo "IMAGE=ghcr.io/${GITHUB_REPOSITORY_OWNER,,}/verity-ai" >> "$GITHUB_ENV"
      - uses: docker/login-action@v4
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Build and publish
        run: |
          docker build --tag "$IMAGE:v1" .
          docker push "$IMAGE:v1"
          echo "Image: $IMAGE:v1" >> "$GITHUB_STEP_SUMMARY"

