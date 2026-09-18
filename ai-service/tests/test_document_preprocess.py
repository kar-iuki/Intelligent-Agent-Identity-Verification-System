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

from services.documentPreprocessService import preprocess_document


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


if __name__ == '__main__':
    test_blurry_image_is_rejected_for_retake()
    test_sharp_image_runs_requested_steps_and_debug_images()
    test_steps_can_be_toggled_off()
    print('document preprocess tests passed')
