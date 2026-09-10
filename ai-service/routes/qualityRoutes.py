from flask import Blueprint, jsonify, request
import cv2
import numpy as np

from services.imageQualityService import assess_image_quality


quality_bp = Blueprint('quality', __name__)


def _decode_image(file_storage):
    file_bytes = file_storage.read()
    if not file_bytes:
        return None
    raw = np.frombuffer(file_bytes, dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    return image


@quality_bp.route('/assess', methods=['POST'])
def assess_quality():
    try:
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

        document_result = assess_image_quality(document_image)
        selfie_result = assess_image_quality(selfie_image)

        overall_passed = document_result['passed'] and selfie_result['passed']

        return jsonify({
            'document': document_result,
            'selfie': selfie_result,
            'overallPassed': overall_passed,
        }), 200

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
