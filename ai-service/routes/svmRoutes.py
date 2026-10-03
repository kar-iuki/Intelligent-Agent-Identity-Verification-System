import logging

from flask import Blueprint, jsonify, request
from ml.schema import LEGACY_FEATURES, CLASSES, CLASS_KEYS, validate_scores

from services.svmService import (
    ModelNotLoadedError,
    get_model_status,
    predict_kyc_decision,
)

logger = logging.getLogger(__name__)

svm_bp = Blueprint('svm', __name__)


_validate_scores = validate_scores


@svm_bp.route('/predict', methods=['POST'])
def predict():
    body = request.get_json(silent=True)
    scores, errors = _validate_scores(body)
    if errors:
        return jsonify({'error': 'Invalid scores', 'details': errors}), 400

    try:
        result = predict_kyc_decision(scores)
    except ModelNotLoadedError as exc:
        return jsonify({'error': str(exc), **get_model_status()}), 503
    except Exception as exc:
        logger.exception('SVM prediction failed')
        return jsonify({'error': f'SVM prediction failed: {exc}'}), 500

    # Preserve the existing Node/Supabase enums for legacy camelCase callers.
    if all(name in body for name in LEGACY_FEATURES):
        result['finalDecision'] = dict(zip(CLASSES, CLASS_KEYS))[result['finalDecision']]

    logger.info('svm decision=%s p=(%.3f, %.3f, %.3f)', result['finalDecision'],
                result['verifiedProbability'], result['reviewProbability'], result['rejectedProbability'])
    return jsonify(result), 200


@svm_bp.route('/status', methods=['GET'])
def status():
    model_status = get_model_status()
    model_status['status'] = 'ready' if model_status['model_loaded'] else 'unavailable'
    return jsonify(model_status), (200 if model_status['model_loaded'] else 503)
