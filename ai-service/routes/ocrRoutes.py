import os

from flask import Blueprint, jsonify, request
import cv2
import numpy as np

from services.imageQualityService import SOFT_BLUR_FACTOR, document_blur_threshold
from services.ocrService import assess_document_ocr


ocr_bp = Blueprint('ocr', __name__)


def _decode_image(file_storage):
    file_bytes = file_storage.read()
    if not file_bytes:
        return None
    raw = np.frombuffer(file_bytes, dtype=np.uint8)
    return cv2.imdecode(raw, cv2.IMREAD_COLOR)


def _truthy(value):
    return str(value).strip().lower() in ('1', 'true', 'yes', 'on')


def _debug_requested():
    # per-request ?debug=1, or OCR_DEBUG=1 in the environment to capture every upload
    flag = request.args.get('debug', request.form.get('debug', ''))
    return _truthy(flag) or _truthy(os.environ.get('OCR_DEBUG', ''))


@ocr_bp.route('/verify', methods=['POST'])
def verify_document_ocr():
    try:
        document_file = request.files.get('documentImage')
        back_file = request.files.get('documentBackImage')
        registered_name = request.form.get('registeredName')
        registered_id = request.form.get('registeredIDNumber')
        registered_dob = request.form.get('registeredDOB')

        missing = []
        if not document_file:
            missing.append('documentImage')
        if registered_name is None:
            missing.append('registeredName')
        if registered_id is None:
            missing.append('registeredIDNumber')
        if registered_dob is None:
            missing.append('registeredDOB')

        if missing:
            return jsonify({
                'error': f"Missing required fields: {', '.join(missing)}",
            }), 400

        image = _decode_image(document_file)
        if image is None:
            return jsonify({'error': 'Invalid image file'}), 400

        back_image = None
        if back_file:
            back_image = _decode_image(back_file)
            if back_image is None:
                return jsonify({'error': 'Invalid back image file'}), 400

        registered_details = {
            'name': registered_name,
            'idNumber': registered_id,
            'dateOfBirth': registered_dob,
        }

        document_kind = request.form.get('documentKind')
        result = assess_document_ocr(
            image,
            registered_details,
            debug=_debug_requested(),
            back_image=back_image,
            # the capture check already let a soft-but-found document through; do not re-block it here
            preprocess_config={'blur_threshold': document_blur_threshold(document_kind) * SOFT_BLUR_FACTOR},
            document_kind=(document_kind or '').strip().lower() or None,
        )
        return jsonify(result), 200

    except Exception as exc:
        return jsonify({
            'error': f'EasyOCR failed to process the image: {str(exc)}',
        }), 500
