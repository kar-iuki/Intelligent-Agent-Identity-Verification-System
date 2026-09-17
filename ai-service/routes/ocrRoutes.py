from flask import Blueprint, jsonify, request
import cv2
import numpy as np

from services.ocrService import assess_document_ocr


ocr_bp = Blueprint('ocr', __name__)


def _decode_image(file_storage):
    file_bytes = file_storage.read()
    if not file_bytes:
        return None
    raw = np.frombuffer(file_bytes, dtype=np.uint8)
    return cv2.imdecode(raw, cv2.IMREAD_COLOR)


@ocr_bp.route('/verify', methods=['POST'])
def verify_document_ocr():
    try:
        document_file = request.files.get('documentImage')
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

        registered_details = {
            'name': registered_name,
            'idNumber': registered_id,
            'dateOfBirth': registered_dob,
        }

        result = assess_document_ocr(image, registered_details)
        return jsonify(result), 200

    except Exception as exc:
        return jsonify({
            'error': f'EasyOCR failed to process the image: {str(exc)}',
        }), 500
