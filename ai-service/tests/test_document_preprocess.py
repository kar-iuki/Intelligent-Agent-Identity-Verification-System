"""Preprocessing pipeline tests.

Usage:
  python tests/test_document_preprocess.py
  python -m pytest tests/test_document_preprocess.py -q
"""

import os
import sys
import tempfile

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.documentPreprocessService import (
    _order_corners,
    correct_perspective,
    find_document_quad,
    preprocess_document,
    preprocess_field_crop,
    warp_quad,
)


def make_sharp_text_image(size=500):
    image = np.ones((size, size, 3), dtype=np.uint8) * 240
    cv2.rectangle(image, (30, 30), (size - 30, size - 30), (20, 20, 20), 3)
    for i, text in enumerate(('FULL NAMES', 'JOHN KAMAU', 'ID NUMBER', '12345678')):
        cv2.putText(
            image,
            text,
            (50, 90 + i * 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.1,
            (10, 10, 10),
            2,
            cv2.LINE_AA,
        )
    return image


def make_blurry_image():
    sharp = make_sharp_text_image()
    return cv2.GaussianBlur(sharp, (51, 51), 0)


def test_blurry_image_is_rejected_for_retake():
    result = preprocess_document(make_blurry_image(), {
        'perspective': False,
        'denoise': False,
        'clahe': False,
        'sharpen': False,
        'binarize': False,
        'morph': False,
        'upscale': False,
        'blur_check': True,
        'blur_threshold': 70.0,
    })
    assert result['ok'] is False
    assert result['reason'] == 'too_blurry'
    assert 'retake' in result['message'].lower()


def test_sharp_image_runs_requested_steps_and_debug_images(tmp_path=None):
    if tmp_path is not None:
        debug_dir = str(tmp_path / 'preprocess')
    else:
        debug_dir = tempfile.mkdtemp(prefix='ocr_debug_')
    result = preprocess_document(make_sharp_text_image(), {
        'perspective': True,
        'blur_check': True,
        'denoise': True,
        'clahe': True,
        'sharpen': True,
        'binarize': True,
        'morph': True,
        'upscale': True,
        'min_resolution': 400,
        'debug': True,
        'debug_dir': debug_dir,
    })
    assert result['ok'] is True
    assert result['image'] is not None
    assert result['aligned_image'] is not None
    assert result['aligned_image'].ndim == 3
    assert 'clahe' in result['steps_run']
    assert 'sharpen' in result['steps_run']
    assert 'binarize' in result['steps_run']
    assert os.path.isdir(debug_dir)
    assert result['debug_images']
    for path in result['debug_images'].values():
        assert os.path.isfile(path)


def test_steps_can_be_toggled_off():
    result = preprocess_document(make_sharp_text_image(), {
        'perspective': False,
        'blur_check': False,
        'denoise': False,
        'clahe': False,
        'sharpen': False,
        'binarize': False,
        'morph': False,
        'upscale': False,
        'debug': False,
    })
    assert result['ok'] is True
    assert result['steps_run'] == []
    assert result['aligned_image'] is not None


def test_handheld_card_on_large_background_is_warped():
    canvas = np.ones((1200, 900, 3), dtype=np.uint8) * 40
    cv2.rectangle(canvas, (80, 350), (820, 820), (230, 230, 230), -1)
    cv2.rectangle(canvas, (80, 350), (820, 820), (20, 20, 20), 6)
    warped, applied = correct_perspective(canvas)
    assert applied is True
    assert warped.shape[1] == 1000
    assert warped.shape[0] == 630


def make_card_photo(quad, background='wood', header=True, finger_edge=None, size=(1280, 960), seed=3):
    """
    Render a card (rounded corners, optional dark header band, photo box, text)
    onto a background at the given corner positions, with a soft shadow and a
    lighting gradient. Returns (image, quad) so tests know the true corners.
    """
    rng = np.random.default_rng(seed)
    cw, ch = 860, 540
    card = np.full((ch, cw, 3), (235, 238, 240), dtype=np.uint8)
    if header:
        cv2.rectangle(card, (0, 0), (cw, 70), (120, 90, 40), -1)
        cv2.putText(card, 'REPUBLIC OF KENYA', (30, 48), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.rectangle(card, (40, 110), (250, 400), (90, 110, 130), -1)
    for text, y in (('FULL NAMES', 130), ('JOHN KAMAU MWANGI', 165), ('ID NUMBER', 225), ('12345678', 260),
                    ('DATE OF BIRTH', 320), ('01.01.1990', 355)):
        cv2.putText(card, text, (290, y), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (25, 25, 25), 2, cv2.LINE_AA)
    mask = np.zeros((ch, cw), dtype=np.uint8)
    r = 30
    cv2.rectangle(mask, (r, 0), (cw - r, ch), 255, -1)
    cv2.rectangle(mask, (0, r), (cw, ch - r), 255, -1)
    for cx, cy in ((r, r), (cw - r, r), (r, ch - r), (cw - r, ch - r)):
        cv2.circle(mask, (cx, cy), r, 255, -1)

    w, h = size
    bg = np.zeros((h, w, 3), dtype=np.uint8)
    if background == 'wood':
        bg[:] = (60, 90, 140)
        for _ in range(60):
            y = int(rng.integers(0, h))
            cv2.line(bg, (0, y), (w, y + int(rng.integers(-30, 30))), (40, 70, 115), int(rng.integers(1, 4)))
    elif background == 'white':
        bg[:] = (225, 228, 232)
    elif background == 'dark':
        bg[:] = (35, 35, 38)
    elif background == 'grid':
        bg[:] = (180, 185, 190)
        for x in range(0, w, 120):
            cv2.line(bg, (x, 0), (x, h), (120, 125, 130), 3)
        for y in range(0, h, 120):
            cv2.line(bg, (0, y), (w, y), (120, 125, 130), 3)
    bg = np.clip(bg.astype(np.float32) + rng.normal(0, 3, bg.shape), 0, 255).astype(np.uint8)

    quad = np.array(quad, dtype=np.float32)
    src = np.array([[0, 0], [cw - 1, 0], [cw - 1, ch - 1], [0, ch - 1]], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(src, quad)
    warped = cv2.warpPerspective(card, matrix, (w, h))
    wmask = cv2.warpPerspective(mask, matrix, (w, h))
    shadow = np.roll(cv2.GaussianBlur(wmask, (0, 0), 12), (14, 10), axis=(0, 1))
    out = bg.astype(np.float32) * (1 - 0.45 * shadow[..., None] / 255.0)
    alpha = (wmask.astype(np.float32) / 255.0)[..., None]
    out = out * (1 - alpha) + warped.astype(np.float32) * alpha
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out *= (1 - 0.35 * (xx / w) * 0.6 - 0.35 * (yy / h) * 0.4)[..., None]
    out = np.clip(out + rng.normal(0, 2.5, out.shape), 0, 255).astype(np.uint8)
    if finger_edge is not None:
        p1, p2 = quad[finger_edge], quad[(finger_edge + 1) % 4]
        centre = (int((p1[0] + p2[0]) / 2), int((p1[1] + p2[1]) / 2))
        cv2.ellipse(out, centre, (70, 110), 0, 0, 360, (120, 150, 200), -1)
    return out, quad


def _corner_error(found, truth):
    return float(np.mean(np.linalg.norm(_order_corners(found) - _order_corners(truth), axis=1)))


CARD_SCENARIOS = {
    'wood_two_tone': dict(quad=[[250, 220], [1030, 250], [1010, 720], [230, 700]], background='wood'),
    'white_on_white': dict(quad=[[260, 230], [1020, 240], [1015, 715], [255, 705]], background='white'),
    'finger_over_bottom_edge': dict(quad=[[250, 220], [1030, 250], [1010, 720], [230, 700]], background='wood', finger_edge=2),
    'finger_over_left_edge_dark': dict(quad=[[280, 220], [1040, 250], [1030, 720], [260, 700]], background='dark', finger_edge=3),
    'grid_table': dict(quad=[[250, 220], [1030, 250], [1010, 720], [230, 700]], background='grid'),
    'strong_perspective': dict(quad=[[200, 300], [1050, 180], [1150, 700], [150, 640]], background='wood'),
    'small_far': dict(quad=[[480, 380], [800, 390], [795, 590], [475, 580]], background='wood'),
}


def test_finds_card_corners_in_hard_photos():
    failures = []
    for name, spec in CARD_SCENARIOS.items():
        image, truth = make_card_photo(**spec)
        quad, score = find_document_quad(image)
        if quad is None:
            failures.append(f'{name}: not found')
            continue
        err = _corner_error(quad, truth)
        if err > 12:
            failures.append(f'{name}: corner error {err:.1f}px')
    assert not failures, failures


def test_no_card_returns_none():
    rng = np.random.default_rng(1)
    plain = np.full((960, 1280, 3), (60, 90, 140), dtype=np.uint8)
    plain = np.clip(plain.astype(np.float32) + rng.normal(0, 3, plain.shape), 0, 255).astype(np.uint8)
    assert find_document_quad(plain)[0] is None
    noise = np.clip(rng.normal(90, 40, (960, 1280, 3)), 0, 255).astype(np.uint8)
    assert find_document_quad(noise)[0] is None


def test_portrait_photo_is_warped_to_landscape():
    # upright card in a landscape frame, then the whole frame turned 90 degrees
    # (phone held in portrait): the warp must still come out landscape
    image, _ = make_card_photo(quad=[[250, 220], [1030, 250], [1010, 720], [230, 700]], background='wood')
    for rotation in (cv2.ROTATE_90_CLOCKWISE, cv2.ROTATE_90_COUNTERCLOCKWISE):
        portrait = cv2.rotate(image, rotation)
        quad, _ = find_document_quad(portrait)
        assert quad is not None
        warped = warp_quad(portrait, quad)
        assert warped.shape[:2] == (630, 1000)
        # header band (dark) must end up along a long edge (top or bottom), not a short edge
        gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        top, bottom = gray[:60].mean(), gray[-60:].mean()
        left, right = gray[:, :60].mean(), gray[:, -60:].mean()
        assert min(top, bottom) < min(left, right)


def test_field_crop_preprocesses_small_region():
    crop = make_sharp_text_image()[80:140, 40:280]
    processed = preprocess_field_crop(crop, {
        'clahe': True,
        'sharpen': True,
        'binarize': True,
        'upscale': True,
        'crop_min_size': 64,
    })
    assert processed is not None
    assert processed.size > 0
    assert min(processed.shape[:2]) >= 64


if __name__ == '__main__':
    test_blurry_image_is_rejected_for_retake()
    test_sharp_image_runs_requested_steps_and_debug_images()
    test_steps_can_be_toggled_off()
    test_handheld_card_on_large_background_is_warped()
    test_finds_card_corners_in_hard_photos()
    test_no_card_returns_none()
    test_portrait_photo_is_warped_to_landscape()
    test_field_crop_preprocesses_small_region()
    print('document preprocess tests passed')
