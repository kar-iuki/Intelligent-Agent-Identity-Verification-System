import cv2
import numpy as np


BLUR_THRESHOLD = 80.0
BRIGHTNESS_MIN = 40.0
BRIGHTNESS_MAX = 220.0
CONTRAST_THRESHOLD = 30.0


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


def assess_image_quality(image):
    """
    Assess blur, brightness, and contrast against configured thresholds.

    Returns a dict with scores, passed flag, and failure messages.
    """
    blur_score = compute_blur_score(image)
    brightness_score = compute_brightness_score(image)
    contrast_score = compute_contrast_score(image)

    failures = []

    if blur_score < BLUR_THRESHOLD:
        failures.append('Image is too blurry')

    if brightness_score < BRIGHTNESS_MIN:
        failures.append('Image is too dark')
    elif brightness_score > BRIGHTNESS_MAX:
        failures.append('Image is too bright')

    if contrast_score < CONTRAST_THRESHOLD:
        failures.append('Image has low contrast')

    return {
        'blurScore': round(blur_score, 4),
        'brightnessScore': round(brightness_score, 4),
        'contrastScore': round(contrast_score, 4),
        'passed': len(failures) == 0,
        'failures': failures,
    }
