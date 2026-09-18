import logging
import os
from datetime import datetime

import cv2
import numpy as np

from services.imageQualityService import DOCUMENT_BLUR_THRESHOLD, compute_blur_score

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_SIZE = (1000, 630)
DEFAULT_DEBUG_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug', 'preprocess')

DEFAULT_CONFIG = {
    'perspective': True,
    'output_size': DEFAULT_OUTPUT_SIZE,
    'blur_check': True,
    'blur_threshold': DOCUMENT_BLUR_THRESHOLD,
    'denoise': True,
    'denoise_method': 'median',  # median | gaussian
    'denoise_noise_threshold': 4.5,
    'clahe': True,
    'clahe_clip_limit': 2.0,
    'clahe_tile_size': 8,
    'sharpen': True,
    'sharpen_amount': 1.0,
    'sharpen_sigma': 1.5,
    'binarize': True,
    'adaptive_block_size': 31,
    'adaptive_c': 10,
    'morph': True,
    'morph_mode': 'auto',  # auto | open | close | erode | dilate
    'upscale': True,
    'min_resolution': 800,
    'crop_min_size': 64,
    'debug': False,
    'debug_dir': None,
}


def merge_preprocess_config(overrides=None):
    config = dict(DEFAULT_CONFIG)
    if overrides:
        config.update(overrides)
    return config


def _as_bgr(image):
    if image is None:
        return None
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if image.shape[2] == 4:
        return cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image


def _as_gray(image):
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def _save_debug(config, step_name, image, debug_images):
    if not config.get('debug'):
        return
    debug_dir = config.get('debug_dir')
    if not debug_dir:
        return
    os.makedirs(debug_dir, exist_ok=True)
    path = os.path.join(debug_dir, f'{len(debug_images):02d}_{step_name}.png')
    ok = cv2.imwrite(path, image)
    if ok:
        debug_images[step_name] = path
        logger.info('preprocess debug saved step=%s path=%s', step_name, path)
    else:
        logger.warning('preprocess debug failed to write step=%s path=%s', step_name, path)


def _order_corners(pts):
    pts = np.array(pts, dtype=np.float32)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1).reshape(-1)
    return np.array([
        pts[np.argmin(s)],
        pts[np.argmin(diff)],
        pts[np.argmax(s)],
        pts[np.argmax(diff)],
    ], dtype=np.float32)


def _find_document_quad(image):
    gray = _as_gray(image)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    h, w = gray.shape[:2]
    img_area = float(h * w)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:8]

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        area = cv2.contourArea(approx)
        if len(approx) == 4 and area > img_area * 0.25:
            return approx.reshape(4, 2)

    return None


def correct_perspective(image, output_size=DEFAULT_OUTPUT_SIZE):
    """Warp the largest 4-corner document contour to a rectangle. Skip if none found."""
    quad = _find_document_quad(image)
    if quad is None:
        return image, False

    h, w = image.shape[:2]
    img_area = float(h * w)
    area = cv2.contourArea(quad)
    if area > img_area * 0.92:
        return image, False

    ordered = _order_corners(quad)
    width, height = int(output_size[0]), int(output_size[1])
    dest = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
    ], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(ordered, dest)
    warped = cv2.warpPerspective(image, matrix, (width, height))
    return warped, True


def _noise_score(gray):
    median = cv2.medianBlur(gray, 3)
    return float(np.mean(cv2.absdiff(gray, median)))


def maybe_denoise(gray, config):
    score = _noise_score(gray)
    threshold = float(config.get('denoise_noise_threshold', 4.5))
    if score < threshold:
        return gray, False, score

    method = str(config.get('denoise_method') or 'median').lower()
    if method == 'gaussian':
        cleaned = cv2.GaussianBlur(gray, (3, 3), 0)
    else:
        cleaned = cv2.medianBlur(gray, 3)
    return cleaned, True, score


def apply_clahe(gray, config):
    clip = float(config.get('clahe_clip_limit', 2.0))
    tile = int(config.get('clahe_tile_size', 8))
    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(tile, tile))
    return clahe.apply(gray)


def unsharp_mask(gray, amount=1.0, sigma=1.5):
    amount = float(amount)
    sigma = float(sigma)
    blurred = cv2.GaussianBlur(gray, (0, 0), sigma)
    sharpened = cv2.addWeighted(gray, 1.0 + amount, blurred, -amount, 0)
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def adaptive_binarize(gray, config):
    block = int(config.get('adaptive_block_size', 31))
    if block % 2 == 0:
        block += 1
    block = max(block, 3)
    c_value = int(config.get('adaptive_c', 10))
    binary = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        block,
        c_value,
    )
    if np.mean(binary) < 127:
        binary = cv2.bitwise_not(binary)
    return binary


def morph_cleanup(binary, mode='auto'):
    text = cv2.bitwise_not(binary)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    op = str(mode or 'auto').lower()

    if op == 'auto':
        n_labels, _, stats, _ = cv2.connectedComponentsWithStats(text, connectivity=8)
        areas = stats[1:, cv2.CC_STAT_AREA] if n_labels > 1 else np.array([])
        small_ratio = float(np.mean(areas < 20)) if len(areas) else 0.0
        op = 'close' if small_ratio > 0.35 else 'open'

    if op == 'open':
        text = cv2.morphologyEx(text, cv2.MORPH_OPEN, kernel, iterations=1)
    elif op == 'close':
        text = cv2.morphologyEx(text, cv2.MORPH_CLOSE, kernel, iterations=1)
    elif op == 'erode':
        text = cv2.erode(text, kernel, iterations=1)
    elif op == 'dilate':
        text = cv2.dilate(text, kernel, iterations=1)

    return cv2.bitwise_not(text)


def maybe_upscale(image, min_resolution=800):
    h, w = image.shape[:2]
    min_dim = min(h, w)
    if min_dim >= int(min_resolution):
        return image, False
    scale = float(min_resolution) / float(min_dim)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    unique_vals = np.unique(image)
    interpolation = cv2.INTER_NEAREST if image.ndim == 2 and unique_vals.size <= 2 else cv2.INTER_CUBIC
    return cv2.resize(image, (new_w, new_h), interpolation=interpolation), True


def upscale_crop(crop, min_size=64):
    """Upscale a small field crop before a second OCR pass."""
    if crop is None or crop.size == 0:
        return crop
    h, w = crop.shape[:2]
    min_dim = min(h, w)
    if min_dim >= int(min_size):
        return crop
    scale = float(min_size) / float(max(min_dim, 1))
    unique_vals = np.unique(crop)
    interpolation = cv2.INTER_NEAREST if crop.ndim == 2 and unique_vals.size <= 2 else cv2.INTER_CUBIC
    return cv2.resize(
        crop,
        (max(int(round(w * scale)), 1), max(int(round(h * scale)), 1)),
        interpolation=interpolation,
    )


def _prepare_debug_dir(config):
    if not config.get('debug'):
        return None
    if config.get('debug_dir'):
        os.makedirs(config['debug_dir'], exist_ok=True)
        return config['debug_dir']
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    debug_dir = os.path.join(DEFAULT_DEBUG_ROOT, stamp)
    os.makedirs(debug_dir, exist_ok=True)
    config['debug_dir'] = debug_dir
    return debug_dir


def preprocess_document(image, config=None):
    """
    Run the OCR preprocessing pipeline. Returns a dict:
      ok, image, reason, message, blur_score, steps_run, debug_dir, debug_images
    """
    config = merge_preprocess_config(config)
    debug_images = {}
    steps_run = []
    bgr = _as_bgr(image)
    current = bgr.copy()
    _prepare_debug_dir(config)
    _save_debug(config, '00_original', current, debug_images)

    if config.get('perspective'):
        current, warped = correct_perspective(current, config.get('output_size') or DEFAULT_OUTPUT_SIZE)
        steps_run.append('perspective')
        logger.info('preprocess perspective applied=%s', warped)
        _save_debug(config, '01_perspective', current, debug_images)

    blur_score = compute_blur_score(current)
    if config.get('blur_check'):
        steps_run.append('blur_check')
        threshold = float(config.get('blur_threshold', DOCUMENT_BLUR_THRESHOLD))
        logger.info('preprocess blur_score=%.4f threshold=%.4f', blur_score, threshold)
        if blur_score < threshold:
            _save_debug(config, '02_blur_rejected', current, debug_images)
            return {
                'ok': False,
                'image': current,
                'reason': 'too_blurry',
                'message': 'Image is too blurry. Please retake.',
                'blur_score': round(blur_score, 4),
                'steps_run': steps_run,
                'debug_dir': config.get('debug_dir'),
                'debug_images': debug_images,
            }

    gray = _as_gray(current)

    if config.get('denoise'):
        gray, applied, noise_score = maybe_denoise(gray, config)
        steps_run.append('denoise')
        logger.info('preprocess denoise applied=%s noise_score=%.4f', applied, noise_score)
        _save_debug(config, '03_denoise', gray, debug_images)

    if config.get('clahe'):
        gray = apply_clahe(gray, config)
        steps_run.append('clahe')
        _save_debug(config, '04_clahe', gray, debug_images)

    if config.get('sharpen'):
        gray = unsharp_mask(
            gray,
            amount=config.get('sharpen_amount', 1.0),
            sigma=config.get('sharpen_sigma', 1.5),
        )
        steps_run.append('sharpen')
        _save_debug(config, '05_sharpen', gray, debug_images)

    processed = gray

    if config.get('binarize'):
        processed = adaptive_binarize(gray, config)
        steps_run.append('binarize')
        _save_debug(config, '06_binarize', processed, debug_images)

        if config.get('morph'):
            processed = morph_cleanup(processed, config.get('morph_mode', 'auto'))
            steps_run.append('morph')
            _save_debug(config, '07_morph', processed, debug_images)

    if config.get('upscale'):
        processed, scaled = maybe_upscale(processed, config.get('min_resolution', 800))
        steps_run.append('upscale')
        logger.info('preprocess upscale applied=%s shape=%s', scaled, processed.shape[:2])
        _save_debug(config, '08_upscale', processed, debug_images)

    return {
        'ok': True,
        'image': processed,
        'reason': None,
        'message': None,
        'blur_score': round(blur_score, 4),
        'steps_run': steps_run,
        'debug_dir': config.get('debug_dir'),
        'debug_images': debug_images,
    }
