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

        # Documents stay stricter for OCR; selfies use laptop-webcam-friendly limits
        document_result = assess_image_quality(document_image, purpose='document')
        selfie_result = assess_image_quality(selfie_image, purpose='selfie')

        overall_passed = document_result['passed'] and selfie_result['passed']

        return jsonify({
            'document': document_result,
            'selfie': selfie_result,
            'overallPassed': overall_passed,
        }), 200

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500


@quality_bp.route('/assess-single', methods=['POST'])
def assess_single_quality():
    """Assess one image (document side or selfie) before advancing the capture wizard."""
    try:
        image_file = request.files.get('image') or request.files.get('documentImage')
        if not image_file:
            return jsonify({'error': 'image file is required'}), 400

        image = _decode_image(image_file)
        if image is None:
            return jsonify({'error': 'Invalid image file'}), 400

        purpose = (request.form.get('purpose') or 'document').strip().lower()
        if purpose not in ('document', 'selfie'):
            purpose = 'document'

        result = assess_image_quality(image, purpose=purpose)

        return jsonify({
            'passed': result['passed'],
            'failures': result['failures'],
            'blurScore': result['blurScore'],
            'brightnessScore': result['brightnessScore'],
            'contrastScore': result['contrastScore'],
            'purpose': purpose,
        }), 200

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
