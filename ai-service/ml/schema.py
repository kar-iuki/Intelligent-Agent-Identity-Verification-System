"""Shared training/inference contract. Quality scores retain production units."""
FEATURES = ['face_match_score', 'liveness_score', 'ocr_confidence_score',
            'blur_score', 'brightness_score', 'contrast_score']
LEGACY_FEATURES = ['faceMatchScore', 'livenessScore', 'ocrConfidenceScore',
                   'blurScore', 'brightnessScore', 'contrastScore']
CLASSES = ['Verified', 'Manual Review', 'Rejected']
CLASS_KEYS = ['verified', 'review', 'rejected']
# Laplacian variance has no application-specific upper limit.
# Grayscale standard deviation on 8-bit images cannot exceed 127.5.
BOUNDS = [(0, 100), (0, 1), (0, 1), (0, None), (0, 255), (0, 127.5)]
SEED = 42


def validate_scores(body):
    """Accept canonical snake_case or legacy camelCase; never coerce strings."""
    import math
    if not isinstance(body, dict):
        return {}, ['Request body must be a JSON object']
    errors, scores = [], {}
    unknown = set(body) - set(FEATURES) - set(LEGACY_FEATURES)
    if unknown:
        errors.append('Unknown score fields: ' + ', '.join(sorted(unknown)))
    for name, alias, (lo, hi) in zip(FEATURES, LEGACY_FEATURES, BOUNDS):
        if name in body and alias in body:
            errors.append(f'Provide only one of {name} and {alias}')
            continue
        value = body.get(name, body.get(alias))
        if value is None:
            errors.append(f'{name} is required')
        elif isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f'{name} must be a number')
        elif (isinstance(value, int) and value.bit_length() > 1023) or not math.isfinite(value):
            errors.append(f'{name} must be finite')
        elif value < lo or (hi is not None and value > hi):
            errors.append(f'{name} must be in [{lo}, {hi if hi is not None else "infinity"}]')
        else:
            scores[name] = float(value)
    return scores, errors
