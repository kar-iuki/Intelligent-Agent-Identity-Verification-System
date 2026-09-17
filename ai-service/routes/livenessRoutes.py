from flask import Blueprint, jsonify, request
import cv2
import numpy as np

from services.livenessService import (
    assess_liveness,
    model_init_error,
    model_ready,
)


liveness_bp = Blueprint('liveness', __name__)


def _decode_image(file_storage):
    file_bytes = file_storage.read()
    if not file_bytes:
        return None
    raw = np.frombuffer(file_bytes, dtype=np.uint8)
    return cv2.imdecode(raw, cv2.IMREAD_COLOR)


@liveness_bp.route('/detect', methods=['POST'])
def detect_liveness_route():
    try:
        if not model_ready:
            return jsonify({
                'error': (
                    'Silent-Face model unavailable. '
                    f'{model_init_error or "Model weights missing or failed to load."}'
                ),
            }), 503

        selfie_file = request.files.get('selfieImage')
        if not selfie_file:
            return jsonify({'error': 'selfieImage is required'}), 400

        image = _decode_image(selfie_file)
        if image is None:
            return jsonify({'error': 'Invalid image file'}), 400

        result = assess_liveness(image)
        return jsonify(result), 200

    except Exception as exc:
        return jsonify({
            'error': f'Liveness detection failed: {str(exc)}',
        }), 500
