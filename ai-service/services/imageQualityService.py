import os

import cv2
import numpy as np


# Defaults suited to identity documents (OCR needs sharper text)
BLUR_THRESHOLD = 40.0
BRIGHTNESS_MIN = 40.0
BRIGHTNESS_MAX = 220.0
CONTRAST_THRESHOLD = 25.0

# Very soft limits for webcam / laptop selfies (face match + liveness, not OCR)
SELFIE_BLUR_THRESHOLD = 2.0
SELFIE_BRIGHTNESS_MIN = 10.0
SELFIE_BRIGHTNESS_MAX = 245.0
SELFIE_CONTRAST_THRESHOLD = 2.0

DOCUMENT_BLUR_THRESHOLD = 70.0


def _env_float(name, default):
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return float(default)


# Sharpness needed per document kind, measured on the located document at its
# native size (Laplacian variance). A passport data page is matte with fine
# print and a driving licence has small text on a busy background, so both
# legitimately score lower than a national ID with large bold text.
# Override with OCR_BLUR_THRESHOLD_NATIONAL_ID / _PASSPORT / _DRIVERS_LICENCE.
# Deliberately low while the capture flow is being tested across phones: a
# located card that reads at all scores well above these. Raise per kind via
# the env vars once real photos have been collected.
DOCUMENT_BLUR_THRESHOLDS = {
    'national_id': _env_float('OCR_BLUR_THRESHOLD_NATIONAL_ID', 25.0),
    'passport': _env_float('OCR_BLUR_THRESHOLD_PASSPORT', 20.0),
    'drivers_licence': _env_float('OCR_BLUR_THRESHOLD_DRIVERS_LICENCE', 20.0),
}

# Brightness/contrast limits for a located document. They used to be judged on
# the whole frame (desk included); a white card in good light legitimately
# averages 230+, so the frame-level 'too bright' limit blocked good photos.
DOCUMENT_BRIGHTNESS_MIN = _env_float('OCR_DOC_BRIGHTNESS_MIN', 30.0)
DOCUMENT_BRIGHTNESS_MAX = _env_float('OCR_DOC_BRIGHTNESS_MAX', 248.0)
DOCUMENT_CONTRAST_THRESHOLD = _env_float('OCR_DOC_CONTRAST_THRESHOLD', 12.0)


def normalise_document_kind(kind):
    key = str(kind or '').strip().lower().replace('-', '_').replace(' ', '_')
    aliases = {
        'id': 'national_id', 'id_front': 'national_id', 'id_back': 'national_id', 'nationalid': 'national_id',
        'national_id': 'national_id', 'passport': 'passport',
        'drivers_licence': 'drivers_licence', 'drivers_license': 'drivers_licence',
        'driving_licence': 'drivers_licence', 'driving_license': 'drivers_licence', 'dl': 'drivers_licence',
    }
    return aliases.get(key)


# A located document scoring between SOFT_BLUR_FACTOR x threshold and the
# threshold is passed with a warning rather than blocked: the OCR stage has
# check-digit MRZ reading, multi-pass crops and its own retake path, so it is
# better placed to decide than a single number at capture time.
SOFT_BLUR_FACTOR = _env_float('OCR_SOFT_BLUR_FACTOR', 0.6)


def document_blur_threshold(kind=None):
    """Blur threshold for a document kind (national ID limit when unknown)."""
    return DOCUMENT_BLUR_THRESHOLDS.get(normalise_document_kind(kind) or 'national_id', DOCUMENT_BLUR_THRESHOLD)


def locate_document_region(image):
    """
    The document at its native resolution, or None when no card-like quad is
    found. Measuring quality on the whole frame lets the table or booklet
    cover decide the score; a sharp passport page on a smooth desk scores
    low and a blurry card on a busy cloth scores high.
    """
    # lazy import: documentPreprocessService imports this module
    from services.documentPreprocessService import (
        _order_corners, _quad_side_lengths, find_document_quad, warp_quad,
    )
    quad, _ = find_document_quad(image)
    if quad is None:
        return None, None
    ordered = _order_corners(quad)
    top, right, bottom, left = _quad_side_lengths(ordered)
    width = int(round(max(top, bottom)))
    height = int(round(max(left, right)))
    if height > width:
        width, height = height, width
    if width < 8 or height < 8:
        return None, None
    return warp_quad(image, quad, (width, height)), width


def thresholds_for_purpose(purpose='document'):
    """Return blur/brightness/contrast limits for document vs selfie captures."""
    if str(purpose or '').lower() == 'selfie':
        return {
            'blur_threshold': SELFIE_BLUR_THRESHOLD,
            'brightness_min': SELFIE_BRIGHTNESS_MIN,
            'brightness_max': SELFIE_BRIGHTNESS_MAX,
            'contrast_threshold': SELFIE_CONTRAST_THRESHOLD,
        }
    return {
        'blur_threshold': DOCUMENT_BLUR_THRESHOLD,
        'brightness_min': BRIGHTNESS_MIN,
        'brightness_max': BRIGHTNESS_MAX,
        'contrast_threshold': CONTRAST_THRESHOLD,
    }


def _center_region(image, fraction=0.55):
    """Crop the centre of the frame where a selfie face usually sits."""
    h, w = image.shape[:2]
    fw = max(int(w * fraction), 1)
    fh = max(int(h * fraction), 1)
    x0 = (w - fw) // 2
    y0 = max((h - fh) // 2 - int(h * 0.05), 0)
    return image[y0:y0 + fh, x0:x0 + fw]


def compute_blur_score(image):
    """Return Laplacian variance — higher means sharper."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return float(laplacian.var())


def compute_brightness_score(image):
    """Return mean of HSV V channel."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    _h, _s, v = cv2.split(hsv)
    return float(np.mean(v))


def compute_contrast_score(image):
    """Return grayscale standard deviation — higher means more contrast."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(np.std(gray))


def assess_image_quality(
    image,
    blur_threshold=None,
    brightness_min=None,
    brightness_max=None,
    contrast_threshold=None,
    purpose=None,
    document_kind=None,
):
    """
    Assess blur, brightness, and contrast against configured thresholds.

    When purpose is set ('document' | 'selfie'), purpose presets are used unless
    an explicit threshold override is passed. Documents are measured on the
    located document itself (native size) with a per-kind blur limit; selfies
    use the centre crop so plain backgrounds do not fail contrast.
    """
    purpose_key = str(purpose or '').lower() if purpose else None
    presets = thresholds_for_purpose(purpose_key) if purpose_key else {
        'blur_threshold': BLUR_THRESHOLD,
        'brightness_min': BRIGHTNESS_MIN,
        'brightness_max': BRIGHTNESS_MAX,
        'contrast_threshold': CONTRAST_THRESHOLD,
    }

    if purpose_key == 'document':
        presets = {
            **presets,
            'blur_threshold': document_blur_threshold(document_kind),
            'brightness_min': DOCUMENT_BRIGHTNESS_MIN,
            'brightness_max': DOCUMENT_BRIGHTNESS_MAX,
            'contrast_threshold': DOCUMENT_CONTRAST_THRESHOLD,
        }
    blur_limit = presets['blur_threshold'] if blur_threshold is None else float(blur_threshold)
    bright_min = presets['brightness_min'] if brightness_min is None else float(brightness_min)
    bright_max = presets['brightness_max'] if brightness_max is None else float(brightness_max)
    contrast_limit = (
        presets['contrast_threshold'] if contrast_threshold is None else float(contrast_threshold)
    )

    document_found = None
    document_width = None
    if purpose_key == 'selfie':
        sample = _center_region(image)
    elif purpose_key == 'document':
        region, document_width = locate_document_region(image)
        document_found = region is not None
        sample = region if region is not None else image
    else:
        sample = image

    blur_score = compute_blur_score(sample)
    brightness_score = compute_brightness_score(sample)
    contrast_score = compute_contrast_score(sample)

    failures = []
    warnings = []

    if blur_score < blur_limit:
        soft_limit = blur_limit * SOFT_BLUR_FACTOR
        if purpose_key == 'document' and document_found and blur_score >= soft_limit:
            warnings.append(
                f'Image is a little soft (sharpness {blur_score:.0f}, ideal {blur_limit:.0f}). '
                'It will be tried, but a steadier, better-focused shot reads more reliably.'
            )
        else:
            failures.append(f'Image is too blurry (sharpness {blur_score:.0f}, needs {blur_limit:.0f})')

    if brightness_score < bright_min:
        failures.append(f'Image is too dark (brightness {brightness_score:.0f}, needs at least {bright_min:.0f})')
    elif brightness_score > bright_max:
        failures.append(f'Image is too bright (brightness {brightness_score:.0f}, limit {bright_max:.0f})')

    # Skip contrast for selfies unless extremely flat (handled by very low threshold)
    if contrast_score < contrast_limit:
        failures.append(f'Image has low contrast (contrast {contrast_score:.0f}, needs {contrast_limit:.0f})')

    return {
        'blurScore': round(blur_score, 4),
        'brightnessScore': round(brightness_score, 4),
        'contrastScore': round(contrast_score, 4),
        'passed': len(failures) == 0,
        'failures': failures,
        'warnings': warnings,
        'purpose': purpose_key or 'default',
        'blurThreshold': blur_limit,
        'documentKind': normalise_document_kind(document_kind) if purpose_key == 'document' else None,
        'documentFound': document_found,
        'documentWidthPx': document_width,
    }
