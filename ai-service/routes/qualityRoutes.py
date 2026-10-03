import json
import logging
import os
from datetime import datetime

from flask import Blueprint, jsonify, request
import cv2
import numpy as np

from services.imageQualityService import assess_image_quality

logger = logging.getLogger(__name__)
QUALITY_DEBUG_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'debug', 'quality')


def _debug_enabled():
    flag = request.args.get('debug', request.form.get('debug', ''))
    return str(flag).strip().lower() in ('1', 'true', 'yes', 'on') or str(
        os.environ.get('OCR_DEBUG', '')
    ).strip().lower() in ('1', 'true', 'yes', 'on')


def _save_quality_debug(image, result, purpose):
    """Keep the checked image and its scores so a rejected capture can be inspected."""
    try:
        os.makedirs(QUALITY_DEBUG_ROOT, exist_ok=True)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        verdict = 'pass' if result.get('passed') else 'fail'
        base = os.path.join(QUALITY_DEBUG_ROOT, f'{stamp}_{purpose}_{verdict}')
        cv2.imwrite(base + '.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 90])
        with open(base + '.json', 'w', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2, default=str)
    except Exception:
        logger.exception('failed to save quality debug capture')


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
        document_kind = request.form.get('documentKind')
        document_result = assess_image_quality(document_image, purpose='document', document_kind=document_kind)
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

        document_kind = request.form.get('documentKind')
        result = assess_image_quality(image, purpose=purpose, document_kind=document_kind)
        logger.info(
            'quality check purpose=%s kind=%s passed=%s blur=%.1f/%.0f found=%s width=%s frame=%dx%d failures=%s',
            purpose, result.get('documentKind'), result['passed'], result['blurScore'],
            result.get('blurThreshold') or 0, result.get('documentFound'), result.get('documentWidthPx'),
            image.shape[1], image.shape[0], result['failures'],
        )
        if _debug_enabled():
            _save_quality_debug(image, {**result, 'frame': [image.shape[1], image.shape[0]]}, purpose)

        return jsonify({
            'passed': result['passed'],
            'failures': result['failures'],
            'warnings': result.get('warnings', []),
            'blurScore': result['blurScore'],
            'brightnessScore': result['brightnessScore'],
            'contrastScore': result['contrastScore'],
            'blurThreshold': result.get('blurThreshold'),
            'documentKind': result.get('documentKind'),
            'documentFound': result.get('documentFound'),
            'documentWidthPx': result.get('documentWidthPx'),
            'purpose': purpose,
        }), 200

    except Exception as exc:
        return jsonify({'error': str(exc)}), 500
