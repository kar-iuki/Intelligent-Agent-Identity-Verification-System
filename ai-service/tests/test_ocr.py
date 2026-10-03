"""
OCR pipeline tests (matching, type detection, dates) plus an optional live smoke test.

Usage:
  python tests/test_ocr.py
  python -m pytest tests/test_ocr.py tests/test_document_preprocess.py -q
"""

import os
import sys
from datetime import date, timedelta

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from services.ocrService import (
    DOCUMENT_DRIVERS_LICENCE,
    DOCUMENT_ID_BACK,
    DOCUMENT_ID_V1,
    DOCUMENT_ID_V2,
    DOCUMENT_PASSPORT,
    _crop_template_region,
    _looks_like_date_value,
    compare_front_and_back,
    detect_document_type,
    extract_raw_fields,
    match_identity_fields,
    missing_required_fields,
    normalize_to_canonical,
    normalized_box_to_pixels,
    parse_document_date,
    parse_registered_date,
    token_overlap_ratio,
    validate_dob,
    validate_expiry,
)


def _item(text, x=10, y=10, w=120, h=20, conf=0.95):
    return {
        'text': text,
        'confidence': conf,
        'bbox': [[x, y], [x + w, y], [x + w, y + h], [x, y + h]],
    }


def test_detects_passport_by_passport_no_not_id_v2():
    items = [
        _item('Surname', y=20),
        _item('KAMAU', x=160, y=20),
        _item('Given Names', y=50),
        _item('JOHN', x=160, y=50),
        _item('Passport No', y=80),
        _item('A1234567', x=160, y=80),
        _item('Date of Birth', y=110),
        _item('01.01.1990', x=160, y=110),
    ]
    assert detect_document_type(items) == DOCUMENT_PASSPORT


def test_detects_id_version_a_by_full_names():
    items = [
        _item('Full Names', y=20),
        _item('JOHN KAMAU MWANGI', x=160, y=20, w=260),
        _item('ID Number', y=60),
        _item('12345678', x=160, y=60),
        _item('Date of Birth', y=100),
        _item('01.01.1990', x=160, y=100),
    ]
    assert detect_document_type(items) == DOCUMENT_ID_V1


def test_detects_id_version_b_by_surname_given_and_id_number():
    items = [
        _item('Surname', y=20),
        _item('KAMAU', x=160, y=20),
        _item('Given Names', y=50),
        _item('JOHN MWANGI', x=160, y=50, w=200),
        _item('ID Number', y=80),
        _item('12345678', x=160, y=80),
        _item('Date of Birth', y=110),
        _item('01.01.1990', x=160, y=110),
        _item('Date of Expiry', y=140),
        _item('01.01.2030', x=160, y=140),
    ]
    assert detect_document_type(items) == DOCUMENT_ID_V2


def test_detects_drivers_licence_by_other_names():
    items = [
        _item('Surname', y=20),
        _item('KAMAU', x=160, y=20),
        _item('Other Names', y=50),
        _item('JOHN MWANGI', x=160, y=50, w=200),
        _item('National ID No', y=80, w=140),
        _item('12345678', x=160, y=80),
        _item('Date of Birth', y=110),
        _item('01.01.1990', x=160, y=110),
        _item('Date of Expiry', y=140),
        _item('01.01.2030', x=160, y=140),
    ]
    assert detect_document_type(items) == DOCUMENT_DRIVERS_LICENCE


def test_unknown_template_is_not_guessed():
    items = [
        _item('REPUBLIC OF KENYA', y=20),
        _item('SOME RANDOM TEXT', y=60),
    ]
    assert detect_document_type(items) is None


def test_parses_dd_mm_yyyy_only():
    assert parse_document_date('01.01.1990') == date(1990, 1, 1)
    assert parse_document_date('1.12.2001') == date(2001, 12, 1)
    assert parse_document_date('01. 01. 1990') == date(1990, 1, 1)
    assert parse_document_date('01 . 01 . 1990') == date(1990, 1, 1)
    assert parse_document_date('01/01/1990') == date(1990, 1, 1)
    assert parse_document_date('01 / 01 / 1990') == date(1990, 1, 1)
    assert parse_document_date('1990-01-01') is None
    assert parse_document_date('not a date') is None
    assert parse_document_date('32.01.1990') is None


def test_registered_dob_dd_mm_yyyy_matches_spaced_ocr_date():
    assert parse_registered_date('01/01/1990') == date(1990, 1, 1)
    canonical = {
        'full_name': 'KAMAU JOHN',
        'id_number': '12345678',
        'date_of_birth': parse_document_date('01. 01. 1990'),
    }
    result = match_identity_fields(canonical, {
        'name': 'Kamau John',
        'idNumber': '12345678',
        'dateOfBirth': '01/01/1990',
    })
    assert canonical['date_of_birth'] == date(1990, 1, 1)
    assert result['dob_match'] is True
    assert result['matched'] is True


def test_rejects_future_and_over_120_dob():
    future = (date.today() + timedelta(days=5)).strftime('%d.%m.%Y')
    parsed_future = parse_document_date(future)
    ok, reason = validate_dob(parsed_future)
    assert ok is False
    assert 'future' in reason.lower()

    ancient = parse_document_date('01.01.1800')
    ok, reason = validate_dob(ancient)
    assert ok is False
    assert '120' in reason


def test_rejects_expired_documents():
    ok, reason = validate_expiry(date(2020, 1, 1))
    assert ok is False
    assert 'expired' in reason.lower()
    future = date.today() + timedelta(days=400)
    ok, reason = validate_expiry(future)
    assert ok is True


def test_canonical_schema_per_document_type():
    passport = normalize_to_canonical(
        {
            'surname': 'Kamau',
            'given_names': 'John Mwangi',
            'passport_no': 'A12 34567',
            'date_of_birth': '01.01.1990',
            'date_of_expiry': '01.01.2030',
        },
        DOCUMENT_PASSPORT,
    )
    assert passport['full_name'] == 'KAMAU JOHN MWANGI'
    assert passport['id_number'] == 'A1234567'
    assert passport['document_type'] == DOCUMENT_PASSPORT
    assert passport['date_of_birth'] == date(1990, 1, 1)
    assert passport['date_of_expiry'] == date(2030, 1, 1)
    assert passport['expiry_valid'] is True

    v1 = normalize_to_canonical(
        {
            'full_names': '  John   Kamau  Mwangi ',
            'id_number': '12345678',
            'date_of_birth': '01.01.1990',
        },
        DOCUMENT_ID_V1,
    )
    assert v1['full_name'] == 'JOHN KAMAU MWANGI'
    assert v1['id_number'] == '12345678'
    assert v1['document_type'] == DOCUMENT_ID_V1
    assert v1['date_of_expiry'] is None

    v2 = normalize_to_canonical(
        {
            'surname': 'KAMAU',
            'given_names': 'JOHN MWANGI',
            'id_number': '12345678',
            'date_of_birth': '01.01.1990',
            'date_of_expiry': '01.01.2030',
        },
        DOCUMENT_ID_V2,
    )
    assert v2['full_name'] == 'KAMAU JOHN MWANGI'
    assert v2['date_of_expiry'] == date(2030, 1, 1)

    licence = normalize_to_canonical(
        {
            'surname': 'KAMAU',
            'other_names': 'JOHN MWANGI',
            'id_number': '12345678',
            'date_of_birth': '01.01.1990',
            'date_of_expiry': '01.01.2030',
        },
        DOCUMENT_DRIVERS_LICENCE,
    )
    assert licence['full_name'] == 'KAMAU JOHN MWANGI'
    assert licence['id_number'] == '12345678'
    assert licence['document_type'] == DOCUMENT_DRIVERS_LICENCE
    assert licence['expiry_valid'] is True

    expired = normalize_to_canonical(
        {
            'surname': 'KAMAU',
            'given_names': 'JOHN',
            'passport_no': 'A1234567',
            'date_of_birth': '01.01.1990',
            'date_of_expiry': '01.01.2020',
        },
        DOCUMENT_PASSPORT,
    )
    assert expired['expiry_valid'] is False
    assert 'expired' in (expired['expiry_reject_reason'] or '').lower()


def test_extracts_fields_by_label_anchor():
    passport_items = [
        _item('Surname', x=10, y=20, w=80),
        _item('KAMAU', x=160, y=20, w=80),
        _item('Given Names', x=10, y=50, w=110),
        _item('JOHN MWANGI', x=160, y=50, w=160),
        _item('Passport No', x=10, y=80, w=110),
        _item('A1234567', x=160, y=80, w=100),
        _item('Date of Birth', x=10, y=110, w=120),
        _item('01.01.1990', x=160, y=110, w=100),
    ]
    raw = extract_raw_fields(
        passport_items,
        DOCUMENT_PASSPORT,
        image=None,
        config={'upscale': False},
    )
    assert raw['surname'] == 'KAMAU'
    assert raw['given_names'] == 'JOHN MWANGI'
    assert raw['passport_no'] == 'A1234567'
    assert raw['date_of_birth'] == '01.01.1990'


def test_extracts_dob_when_ocr_splits_date_tokens():
    items = [
        _item('Full Names', y=20),
        _item('JOHN KAMAU', x=160, y=20, w=200),
        _item('ID Number', y=60),
        _item('12345678', x=160, y=60),
        _item('Date of Birth', y=100, w=120),
        _item('09.', x=160, y=100, w=30),
        _item('03.', x=200, y=100, w=30),
        _item('1998', x=240, y=100, w=50),
    ]
    raw = extract_raw_fields(
        items,
        DOCUMENT_ID_V1,
        image=None,
        config={'upscale': False},
        template={},
    )
    assert parse_document_date(raw['date_of_birth']) == date(1998, 3, 9)


def test_does_not_scavenge_unanchored_dates():
    items = [
        _item('Full Names', y=20),
        _item('JOHN KAMAU', x=160, y=20, w=200),
        _item('ID Number', y=60),
        _item('12345678', x=160, y=60),
        _item('09. 03. 1998', x=400, y=300, w=140),
    ]
    raw = extract_raw_fields(
        items,
        DOCUMENT_ID_V1,
        image=None,
        config={'upscale': False},
        template={},
    )
    assert raw['date_of_birth'] is None


def test_label_less_new_gen_id_uses_only_plausible_birth_date():
    # new-generation national ID: no readable field labels, DOB and expiry unlabelled
    texts = ['REPUBLIC OF KENYA', 'NATIONAL IDENTITY CARD', 'IRUNGU', 'REUBEN GITHAIGA', 'MALE', 'KEN',
             '08. 07. 2006', 'NAIROBI', '115614254', '12.09. 2034', 'WAITHAKA']
    items = [_item(text, y=20 + 30 * i) for i, text in enumerate(texts)]
    assert detect_document_type(items) == DOCUMENT_ID_V2
    raw = extract_raw_fields(items, DOCUMENT_ID_V2, image=None, config={'upscale': False}, template={})
    assert raw['date_of_birth'] == '08. 07. 2006'
    # two plausible past dates -> ambiguous -> stays empty
    items.append(_item('01. 02. 1999', y=400))
    raw = extract_raw_fields(items, DOCUMENT_ID_V2, image=None, config={'upscale': False}, template={})
    assert raw['date_of_birth'] is None


def test_rejects_garbage_before_date_parse():
    assert _looks_like_date_value('01.01.1990') is True
    assert _looks_like_date_value('01. 01. 1990') is True
    assert _looks_like_date_value('not a date') is False
    assert _looks_like_date_value('32.01.1990') is False
    assert _looks_like_date_value('1990-01-01') is False


def test_normalized_box_converts_to_pixels_and_crops():
    assert normalized_box_to_pixels([0.1, 0.2, 0.4, 0.5], 1000, 630) == (100, 126, 400, 315)
    image = np.zeros((630, 1000, 3), dtype=np.uint8)
    image[126:315, 100:400] = 255
    crop = _crop_template_region(image, [0.1, 0.2, 0.4, 0.5])
    assert crop is not None
    # the crop is padded around the calibrated box so a slightly-off box does not slice the text
    assert crop.shape[0] > 189 and crop.shape[1] > 300
    assert int((crop[:, :, 0] == 255).sum()) == 189 * 300  # whole box is inside the crop


def test_template_crop_is_preferred_over_label_anchor():
    import services.ocrService as ocr

    original = ocr._ocr_template_crop

    def fake_crop(_image, box, predicate, _variants, _config, field=None, collect=None):
        if box == [0.1, 0.1, 0.4, 0.2]:
            text = 'FROMCROP'
            return (text, None) if predicate(text) else (None, 'failed_validation')
        return None, 'empty_text'

    ocr._ocr_template_crop = fake_crop
    try:
        items = [
            _item('Surname', x=10, y=20, w=80),
            _item('KAMAU', x=160, y=20, w=80),
            _item('Given Names', x=10, y=50, w=110),
            _item('JOHN MWANGI', x=160, y=50, w=160),
            _item('Passport No', x=10, y=80, w=110),
            _item('A1234567', x=160, y=80, w=100),
            _item('Date of Birth', x=10, y=110, w=120),
            _item('01.01.1990', x=160, y=110, w=100),
        ]
        sources = {}
        raw = extract_raw_fields(
            items,
            DOCUMENT_PASSPORT,
            image=np.ones((630, 1000, 3), dtype=np.uint8),
            template={'surname': [0.1, 0.1, 0.4, 0.2]},
            sources=sources,
        )
        assert raw['surname'] == 'FROMCROP'
        assert sources['surname'] == 'template'
        assert raw['given_names'] == 'JOHN MWANGI'
        assert sources['given_names'] == 'label_fallback'
        assert raw['passport_no'] == 'A1234567'
        assert raw['date_of_birth'] == '01.01.1990'
    finally:
        ocr._ocr_template_crop = original


def test_low_confidence_or_empty_template_crop_falls_back_to_label():
    import services.ocrService as ocr

    original = ocr._ocr_template_crop

    def fake_crop(_image, _box, _predicate, _variants, _config, field=None, collect=None):
        return None, 'low_confidence:0.20'

    ocr._ocr_template_crop = fake_crop
    try:
        items = [
            _item('Surname', x=10, y=20, w=80),
            _item('KAMAU', x=160, y=20, w=80),
            _item('Given Names', x=10, y=50, w=110),
            _item('JOHN MWANGI', x=160, y=50, w=160),
            _item('Passport No', x=10, y=80, w=110),
            _item('A1234567', x=160, y=80, w=100),
            _item('Date of Birth', x=10, y=110, w=120),
            _item('01.01.1990', x=160, y=110, w=100),
        ]
        sources = {}
        raw = extract_raw_fields(
            items,
            DOCUMENT_PASSPORT,
            image=np.ones((630, 1000, 3), dtype=np.uint8),
            template={
                'surname': [0.1, 0.1, 0.4, 0.2],
                'given_names': [0.1, 0.25, 0.5, 0.35],
                'passport_no': [0.1, 0.40, 0.4, 0.50],
                'date_of_birth': [0.1, 0.55, 0.35, 0.65],
            },
            sources=sources,
        )
        assert raw['surname'] == 'KAMAU'
        assert raw['given_names'] == 'JOHN MWANGI'
        assert sources['surname'] == 'label_fallback'
        assert sources['date_of_birth'] == 'label_fallback'
    finally:
        ocr._ocr_template_crop = original


def test_missing_required_fields_after_both_methods():
    raw = extract_raw_fields([], DOCUMENT_PASSPORT, image=None, template={})
    missing = missing_required_fields(raw, DOCUMENT_PASSPORT)
    assert missing == ['surname', 'given_names', 'passport_no', 'date_of_birth', 'date_of_expiry']
    v1_missing = missing_required_fields(
        {'full_names': 'JOHN', 'id_number': '', 'date_of_birth': '01.01.1990'},
        DOCUMENT_ID_V1,
    )
    assert v1_missing == ['id_number']


def test_front_and_back_id_number_must_match():
    matched = compare_front_and_back(
        {'id_number': '12345678'},
        {'id_number': '1234 5678'},
    )
    assert matched['matched'] is True
    assert matched['id_match'] is True

    mismatched = compare_front_and_back(
        {'id_number': '12345678'},
        {'id_number': '12345679'},
    )
    assert mismatched['matched'] is False
    assert mismatched['id_match'] is False


def test_extracts_id_back_fields_by_label():
    items = [
        _item('ID Number', y=40, w=100),
        _item('12345678', x=160, y=40, w=100),
    ]
    raw = extract_raw_fields(items, DOCUMENT_ID_BACK, image=None, template={})
    assert raw['id_number'] == '12345678'
    assert raw.get('serial_number') in (None, '')


def test_extracts_drivers_licence_fields_by_label():
    items = [
        _item('Surname', y=20, w=80),
        _item('KAMAU', x=180, y=20, w=80),
        _item('Other Names', y=50, w=120),
        _item('JOHN MWANGI', x=180, y=50, w=160),
        _item('National ID No', y=80, w=140),
        _item('12345678', x=180, y=80, w=100),
        _item('Date of Birth', y=110, w=120),
        _item('01.01.1990', x=180, y=110, w=100),
        _item('Date of Expiry', y=140, w=120),
        _item('01.01.2030', x=180, y=140, w=100),
    ]
    raw = extract_raw_fields(items, DOCUMENT_DRIVERS_LICENCE, image=None, template={})
    assert raw['surname'] == 'KAMAU'
    assert raw['other_names'] == 'JOHN MWANGI'
    assert raw['id_number'] == '12345678'
    assert raw['date_of_birth'] == '01.01.1990'
    assert raw['date_of_expiry'] == '01.01.2030'


def test_name_token_set_accepts_reordered_names():
    overlap = token_overlap_ratio('KAMAU JOHN MWANGI', 'John Mwangi Kamau')
    assert overlap == 1.0

    canonical = {
        'full_name': 'KAMAU JOHN MWANGI',
        'id_number': '12345678',
        'date_of_birth': date(1990, 1, 1),
    }
    registered = {
        'name': 'John Mwangi Kamau',
        'idNumber': '1234 5678',
        'dateOfBirth': '1990-01-01',
    }
    result = match_identity_fields(canonical, registered)
    assert result['name_match'] is True
    assert result['id_match'] is True
    assert result['dob_match'] is True
    assert result['matched'] is True
    assert result['field_matches'][0]['token_overlap'] == 1.0
    assert 'levenshtein' in result['field_matches'][0]


def test_registered_names_may_be_subset_of_document_names():
    # card: IRUNGU REUBEN GITHAIGA, agent registered as "Reuben Githaiga"
    canonical = {'full_name': 'IRUNGU REUBEN GITHAIGA', 'id_number': '115614254', 'date_of_birth': date(2006, 7, 8)}
    result = match_identity_fields(canonical, {'name': 'Reuben Githaiga', 'idNumber': '115614254', 'dateOfBirth': '2006-07-08'})
    assert result['name_match'] is True
    assert result['matched'] is True
    # Approximate spellings no longer count as a matching name.
    canonical['full_name'] = 'TRUNGU REUBEN GITHAIGA'
    result = match_identity_fields(canonical, {'name': 'Irungu Reuben Githaiga', 'idNumber': '115614254', 'dateOfBirth': '2006-07-08'})
    assert result['name_match'] is False
    # a registered name that is not on the card fails
    result = match_identity_fields(canonical, {'name': 'Peter Githaiga', 'idNumber': '115614254', 'dateOfBirth': '2006-07-08'})
    assert result['name_match'] is False
    # OCR fused the given names into one token with two wrong letters
    canonical['full_name'] = 'IRUNGU REUBEMGTTAIGA'
    result = match_identity_fields(canonical, {'name': 'Reuben Githaiga', 'idNumber': '115614254', 'dateOfBirth': '2006-07-08'})
    assert result['name_match'] is False
    # the same stretch of text cannot satisfy two different registered names
    canonical['full_name'] = 'IRUNGU REUBEN'
    result = match_identity_fields(canonical, {'name': 'Reuben Reuben', 'idNumber': '115614254', 'dateOfBirth': '2006-07-08'})
    assert result['name_match'] is False
    # a single registered token is never enough
    result = match_identity_fields(canonical, {'name': 'Reuben', 'idNumber': '115614254', 'dateOfBirth': '2006-07-08'})
    assert result['name_match'] is False


def test_name_subset_rules_use_complete_distinct_tokens():
    cases = [
        ('JOHN KAMAU', 'John Kamau Mwangi', True),
        ('KAMAU JOHN', '  john   kamau  ', True),
        ('JOHN KAMAU MWANGI', 'John Kamau', True),
        ('JOHN KAMAU', 'John Peter', False),
        ('JOHN KAMAU MWANGI', 'John Kamau Peter', False),
        ('JOHN KAMAU MWANGI', 'John Kamau Peter James', False),
        ('JOHN KAMAU', 'John Peter James', False),
        ('JOHN KAMAU', 'John John', False),
        ('JOHN', 'John Kamau', False),
        ('JOHN KAMAU', 'John', False),
        ('JOHN KAMAU', 'Jo Kamau', False),
        ('JOHNKAMAU', 'John Kamau', False),
        ('JOHN KAMAU', 'Johnkamau', False),
        ('JOHN KAMAU', '', False),
        ('', 'John Kamau', False),
        ('', '', False),
        ('ANNE-MARIE KAMAU', 'Anne Marie Kamau', True),
    ]
    for extracted, provided, expected in cases:
        result = match_identity_fields(
            {'full_name': extracted, 'id_number': '12345678', 'date_of_birth': date(1990, 1, 1)},
            {'name': provided, 'idNumber': '12345678', 'dateOfBirth': '1990-01-01'},
            name_threshold=0.5,
        )
        assert result['name_match'] is expected, (extracted, provided)
        assert result['matched'] is expected, (extracted, provided)
        if expected:
            assert result['field_matches'][0]['score'] == 1.0
            assert result['confidence_score'] == 1.0


def test_name_mismatch_and_id_exact_only():
    canonical = {
        'full_name': 'KAMAU JOHN',
        'id_number': '12345678',
        'date_of_birth': date(1990, 1, 1),
    }
    registered = {
        'name': 'Jane Doe',
        'idNumber': '12345679',
        'dateOfBirth': '02.01.1990',
    }
    result = match_identity_fields(canonical, registered)
    assert result['name_match'] is False
    assert result['id_match'] is False
    assert result['dob_match'] is False
    assert result['matched'] is False


def test_overall_pass_requires_all_three_fields():
    canonical = {
        'full_name': 'KAMAU JOHN',
        'id_number': '12345678',
        'date_of_birth': date(1990, 1, 1),
    }
    registered = {
        'name': 'Kamau John',
        'idNumber': '12345678',
        'dateOfBirth': '01.01.1991',
    }
    result = match_identity_fields(canonical, registered)
    assert result['name_match'] is True
    assert result['id_match'] is True
    assert result['dob_match'] is False
    assert result['matched'] is False


def make_sample_id_image():
    image = np.ones((420, 700, 3), dtype=np.uint8) * 245
    cv2.rectangle(image, (20, 20), (680, 400), (30, 30, 30), 2)

    lines = [
        (40, 70, 'FULL NAMES'),
        (40, 110, 'JOHN KAMAU MWANGI'),
        (40, 170, 'ID NUMBER'),
        (40, 210, '12345678'),
        (40, 270, 'DATE OF BIRTH'),
        (40, 310, '01.01.1990'),
    ]

    for x, y, text in lines:
        cv2.putText(
            image,
            text,
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (10, 10, 10),
            2,
            cv2.LINE_AA,
        )

    return image


if __name__ == '__main__':
    unit_tests = [
        test_detects_passport_by_passport_no_not_id_v2,
        test_detects_id_version_a_by_full_names,
        test_detects_id_version_b_by_surname_given_and_id_number,
        test_detects_drivers_licence_by_other_names,
        test_unknown_template_is_not_guessed,
        test_parses_dd_mm_yyyy_only,
        test_registered_dob_dd_mm_yyyy_matches_spaced_ocr_date,
        test_rejects_future_and_over_120_dob,
        test_rejects_expired_documents,
        test_canonical_schema_per_document_type,
        test_extracts_fields_by_label_anchor,
        test_extracts_dob_when_ocr_splits_date_tokens,
        test_does_not_scavenge_unanchored_dates,
        test_label_less_new_gen_id_uses_only_plausible_birth_date,
        test_rejects_garbage_before_date_parse,
        test_normalized_box_converts_to_pixels_and_crops,
        test_template_crop_is_preferred_over_label_anchor,
        test_low_confidence_or_empty_template_crop_falls_back_to_label,
        test_missing_required_fields_after_both_methods,
        test_front_and_back_id_number_must_match,
        test_extracts_id_back_fields_by_label,
        test_extracts_drivers_licence_fields_by_label,
        test_name_token_set_accepts_reordered_names,
        test_registered_names_may_be_subset_of_document_names,
        test_name_subset_rules_use_complete_distinct_tokens,
        test_name_mismatch_and_id_exact_only,
        test_overall_pass_requires_all_three_fields,
    ]
    for test_fn in unit_tests:
        test_fn()
        print(f'ok {test_fn.__name__}')
    print('OCR unit tests passed\n')

    from services.ocrService import assess_document_ocr

    samples_dir = os.path.join(os.path.dirname(__file__), 'samples')
    sample_path = os.path.join(samples_dir, 'id_document.jpg')

    if os.path.exists(sample_path):
        image = cv2.imread(sample_path)
        print(f'Loaded sample identity document from {sample_path}')
    else:
        image = make_sample_id_image()
        print('Using generated sample identity document image')

    registered = {
        'name': 'John Kamau Mwangi',
        'idNumber': '12345678',
        'dateOfBirth': '01.01.1990',
    }

    result = assess_document_ocr(image, registered, debug=True)

    print('\n=== OCR Result ===')
    print(f"documentType:       {result.get('documentType')}")
    print(f"extractedName:      {result.get('extractedName')}")
    print(f"extractedIDNumber:  {result.get('extractedIDNumber')}")
    print(f"extractedDOB:       {result.get('extractedDOB')}")
    print(f"nameMatch:          {result.get('nameMatch')}")
    print(f"idMatch:            {result.get('idMatch')}")
    print(f"dobMatch:           {result.get('dobMatch')}")
    print(f"confidenceScore:    {result.get('confidenceScore')}")
    print(f"matched:            {result.get('matched')}")
    print(f"needsRetake:        {result.get('needsRetake')}")
    print(f"needsManualReview:  {result.get('needsManualReview')}")
    print(f"fieldMatches:       {result.get('fieldMatches')}")
    print(f"rawText:            {result.get('rawText')}")
    print(f"debugDir:           {result.get('debugDir')}")
