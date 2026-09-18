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
):
    """
    Assess blur, brightness, and contrast against configured thresholds.

    When purpose is set ('document' | 'selfie'), purpose presets are used unless
    an explicit threshold override is passed.
    Selfie metrics use the centre crop so plain backgrounds do not fail contrast.
    """
    purpose_key = str(purpose or '').lower() if purpose else None
    presets = thresholds_for_purpose(purpose_key) if purpose_key else {
        'blur_threshold': BLUR_THRESHOLD,
        'brightness_min': BRIGHTNESS_MIN,
        'brightness_max': BRIGHTNESS_MAX,
        'contrast_threshold': CONTRAST_THRESHOLD,
    }

    blur_limit = presets['blur_threshold'] if blur_threshold is None else float(blur_threshold)
    bright_min = presets['brightness_min'] if brightness_min is None else float(brightness_min)
    bright_max = presets['brightness_max'] if brightness_max is None else float(brightness_max)
    contrast_limit = (
        presets['contrast_threshold'] if contrast_threshold is None else float(contrast_threshold)
    )

    sample = _center_region(image) if purpose_key == 'selfie' else image

    blur_score = compute_blur_score(sample)
    brightness_score = compute_brightness_score(sample)
    contrast_score = compute_contrast_score(sample)

    failures = []

    if blur_score < blur_limit:
        failures.append('Image is too blurry')

    if brightness_score < bright_min:
        failures.append('Image is too dark')
    elif brightness_score > bright_max:
        failures.append('Image is too bright')

    # Skip contrast for selfies unless extremely flat (handled by very low threshold)
    if contrast_score < contrast_limit:
        failures.append('Image has low contrast')

    return {
        'blurScore': round(blur_score, 4),
        'brightnessScore': round(brightness_score, 4),
        'contrastScore': round(contrast_score, 4),
        'passed': len(failures) == 0,
        'failures': failures,
        'purpose': purpose_key or 'default',
    }
