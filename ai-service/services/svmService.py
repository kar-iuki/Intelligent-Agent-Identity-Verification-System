"""
SVM KYC decision service (Module 12).

Loads the trained SVM classifier and its fitted MinMaxScaler once at import time
and exposes predict_kyc_decision() for the /api/svm routes.
"""

import hashlib
import json
import logging
import os
import warnings

import joblib
import numpy as np
from ml.schema import FEATURES, CLASSES, validate_scores

logger = logging.getLogger(__name__)

AI_SERVICE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(AI_SERVICE_ROOT, 'ml', 'models')
MODEL_PATH = os.path.join(MODEL_DIR, 'svm_kyc_model.pkl')
SCALER_PATH = os.path.join(MODEL_DIR, 'scaler.pkl')
VERSION_PATH = os.path.join(MODEL_DIR, 'model_version.txt')

FEATURE_ORDER = FEATURES


class ModelNotLoadedError(RuntimeError):
    """Raised when a prediction is requested but the model files failed to load."""


svm_model = None
scaler = None
model_loaded = False


def _load_artifacts():
    global svm_model, scaler, model_loaded
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            svm_model = joblib.load(MODEL_PATH)
            scaler = joblib.load(SCALER_PATH)
        for warning in caught:
            logger.warning('SVM artifact load warning: %s', warning.message)
        with open(os.path.join(MODEL_DIR, 'artifact_manifest.json'), encoding='utf-8') as handle:
            manifest = json.load(handle)
        if manifest['features'] != FEATURES or set(svm_model.classes_) != set(CLASSES):
            raise ValueError('Model feature/class contract mismatch')
        if svm_model.n_features_in_ != len(FEATURES) or scaler.n_features_in_ != len(FEATURES):
            raise ValueError('Model/scaler feature count mismatch')
        for path in (MODEL_PATH, SCALER_PATH):
            with open(path, 'rb') as handle:
                digest = hashlib.sha256(handle.read()).hexdigest()
            if digest != manifest['artifacts'][os.path.basename(path)]:
                raise ValueError('Model/scaler artifact integrity mismatch')
        if manifest['version'] != get_model_version():
            raise ValueError('Model version mismatch')
        model_loaded = True
        logger.info('SVM KYC model loaded (version %s)', get_model_version())
    except FileNotFoundError as exc:
        logger.error(
            'SVM model not loaded — missing file %s. Run `python ml/train_model.py` from ai-service/.',
            exc.filename,
        )
        svm_model, scaler, model_loaded = None, None, False
    except Exception:
        logger.exception('SVM model not loaded — failed to deserialise %s / %s', MODEL_PATH, SCALER_PATH)
        svm_model, scaler, model_loaded = None, None, False


def _read_version_file():
    try:
        with open(VERSION_PATH, encoding='utf-8') as handle:
            lines = [line.strip() for line in handle if line.strip()]
    except FileNotFoundError:
        return None, None
    version = lines[0] if lines else None
    trained_at = None
    for line in lines[1:]:
        if line.startswith('trained_at='):
            trained_at = line.split('=', 1)[1]
    return version, trained_at


def get_model_version():
    version, _ = _read_version_file()
    return version or 'unknown'


def get_model_status():
    version, trained_at = _read_version_file()
    return {
        'model_loaded': model_loaded,
        'model_version': version or 'unknown',
        'trained_at': trained_at,
    }


def predict_kyc_decision(scores):
    """
    Classify one applicant from their six verification scores.

    :param scores: all six numeric fields in ml.schema; camelCase aliases accepted.
    :raises ModelNotLoadedError: if the model or scaler is unavailable (HTTP 503)
    """
    if not model_loaded:
        raise ModelNotLoadedError('SVM model is not loaded')

    scores, errors = validate_scores(scores)
    if errors:
        raise ValueError('; '.join(errors))
    features = np.array([[scores[name] for name in FEATURE_ORDER]], dtype=float)
    scaled = scaler.transform(features)
    probabilities = svm_model.predict_proba(scaled)[0]
    by_label = {str(label): float(p) for label, p in zip(svm_model.classes_, probabilities)}
    # A validation-selected review policy may intentionally differ from argmax.
    # Keep probabilities unchanged and expose the policy separately.
    prediction = str(svm_model.predict(scaled)[0])
    return {
        'finalDecision': prediction,
        'probabilities': {name: by_label[name] for name in CLASSES},
        'verifiedProbability': by_label['Verified'],
        'reviewProbability': by_label['Manual Review'],
        'rejectedProbability': by_label['Rejected'],
        'decisionBasis': 'svm_model',
        'modelVersion': get_model_version(),
        'decisionPolicy': getattr(svm_model, 'decision_policy', {'name': 'probability_argmax'}),
    }



_load_artifacts()
