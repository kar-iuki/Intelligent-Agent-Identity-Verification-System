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
