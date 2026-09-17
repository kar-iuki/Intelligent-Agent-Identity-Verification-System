from flask import Blueprint, jsonify, request
import cv2
import numpy as np

from services.faceMatchService import (
    face_app,
    model_init_error,
    verify_face_match,
)


face_bp = Blueprint('face', __name__)


def _decode_image(file_storage):
    file_bytes = file_storage.read()
    if not file_bytes:
        return None
    raw = np.frombuffer(file_bytes, dtype=np.uint8)
    return cv2.imdecode(raw, cv2.IMREAD_COLOR)


@face_bp.route('/verify', methods=['POST'])
def verify_faces():
    try:
        if face_app is None:
            return jsonify({
                'error': (
                    'InsightFace model unavailable. '
                    f'{model_init_error or "Model failed to initialise."}'
                ),
            }), 503

        document_file = request.files.get('documentImage')
        selfie_file = request.files.get('selfieImage')

        if not document_file or not selfie_file:
            return jsonify({
                'error': 'Both documentImage and selfieImage are required',
            }), 400

        document_image = _decode_image(document_file)
        selfie_image = _decode_image(selfie_file)

        if document_image is None or selfie_image is None:
            return jsonify({'error': 'Invalid image file'}), 400

        result = verify_face_match(document_image, selfie_image)
        return jsonify(result), 200

    except Exception as exc:
        return jsonify({
            'error': f'InsightFace face matching failed: {str(exc)}',
        }), 500
