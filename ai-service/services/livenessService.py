import logging
import os
import sys
import warnings

import cv2
import numpy as np

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

SILENT_FACE_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..', 'silent_face')
)
MODEL_DIR = os.path.join(SILENT_FACE_ROOT, 'resources', 'anti_spoof_models')

if SILENT_FACE_ROOT not in sys.path:
    sys.path.insert(0, SILENT_FACE_ROOT)

LIVE_THRESHOLD = 0.75
SPOOF_THRESHOLD = 0.50

model_ready = False
model_init_error = None
_model = None
_cropper = None


def _initialise_liveness_model():
    global model_ready, model_init_error, _model, _cropper

    try:
        if not os.path.isdir(MODEL_DIR):
            raise FileNotFoundError(
                f'Silent-Face model directory not found: {MODEL_DIR}'
            )

        model_files = [
            name for name in os.listdir(MODEL_DIR)
            if name.endswith('.pth')
        ]
        if not model_files:
            raise FileNotFoundError(
                f'No .pth model weights found in {MODEL_DIR}. '
                'Download pretrained weights from the Silent-Face-Anti-Spoofing repository.'
            )

        from src.anti_spoof_predict import AntiSpoofPredict
        from src.generate_patches import CropImage

        # Always use CPU for student/local setups without a GPU
        _model = AntiSpoofPredict(device_id=0)
        _cropper = CropImage()

        # Force detector init (loads caffe face detector)
        _ = _model.detector

        model_ready = True
        model_init_error = None
        logger.info('Silent-Face-Anti-Spoofing model ready (%s weights)', len(model_files))
    except Exception as exc:
        model_ready = False
        model_init_error = str(exc)
        _model = None
        _cropper = None
        logger.error('Failed to initialise Silent-Face model: %s', exc)


_initialise_liveness_model()


def ensure_model_ready():
    if not model_ready or _model is None or _cropper is None:
        raise RuntimeError(
            model_init_error
            or 'Silent-Face model is not initialised'
        )


def _prepare_image(image):
    """Resize toward a 3:4 width:height ratio expected by Silent-Face samples."""
    height, width = image.shape[:2]
    target_ratio = 3 / 4  # width / height

    current_ratio = width / max(height, 1)
    if abs(current_ratio - target_ratio) < 0.01:
        return image

    # Pad to 3:4 without distorting the face
    if current_ratio > target_ratio:
        new_height = int(round(width / target_ratio))
        pad = new_height - height
        top = pad // 2
        bottom = pad - top
        return cv2.copyMakeBorder(image, top, bottom, 0, 0, cv2.BORDER_REPLICATE)

    new_width = int(round(height * target_ratio))
    pad = new_width - width
    left = pad // 2
    right = pad - left
    return cv2.copyMakeBorder(image, 0, 0, left, right, cv2.BORDER_REPLICATE)


def detect_liveness(image):
    """
    Run Silent-Face inference and return the real-face (class 1) probability.
    """
    ensure_model_ready()

    from src.utility import parse_model_name

    prepared = _prepare_image(image)
    image_bbox = _model.get_bbox(prepared)

    prediction = np.zeros((1, 3), dtype=np.float64)
    model_count = 0

    for model_name in os.listdir(MODEL_DIR):
        if not model_name.endswith('.pth'):
            continue

        h_input, w_input, _model_type, scale = parse_model_name(model_name)
        param = {
            'org_img': prepared,
            'bbox': image_bbox,
            'scale': scale,
            'out_w': w_input,
            'out_h': h_input,
            'crop': True,
        }
        if scale is None:
            param['crop'] = False

        cropped = _cropper.crop(**param)
        prediction += _model.predict(cropped, os.path.join(MODEL_DIR, model_name))
        model_count += 1

    if model_count == 0:
        raise RuntimeError('No Silent-Face model weights were available for inference')

    prediction = prediction / float(model_count)
    # Class 1 = real / live
    liveness_score = float(prediction[0][1])
    return max(0.0, min(1.0, liveness_score))


def assess_liveness(image):
    score = detect_liveness(image)

    if score > LIVE_THRESHOLD:
        classification = 'live'
        is_live = True
        message = 'Selfie passed liveness detection'
    elif score < SPOOF_THRESHOLD:
        classification = 'spoof'
        is_live = False
        message = 'Selfie failed liveness detection — possible spoofing attack'
    else:
        classification = 'borderline'
        is_live = False
        message = 'Selfie liveness score is borderline and needs review'

    return {
        'livenessScore': round(score, 4),
        'isLive': is_live,
        'classification': classification,
        'message': message,
    }
