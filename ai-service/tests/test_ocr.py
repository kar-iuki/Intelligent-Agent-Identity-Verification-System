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
    DOCUMENT_ID_V1,
    DOCUMENT_ID_V2,
    DOCUMENT_PASSPORT,
    detect_document_type,
    extract_raw_fields,
    match_identity_fields,
    normalize_to_canonical,
    parse_document_date,
    token_overlap_ratio,
    validate_dob,
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


def test_unknown_template_is_not_guessed():
    items = [
        _item('REPUBLIC OF KENYA', y=20),
        _item('SOME RANDOM TEXT', y=60),
    ]
    assert detect_document_type(items) is None


def test_parses_dd_mm_yyyy_only():
    assert parse_document_date('01.01.1990') == date(1990, 1, 1)
    assert parse_document_date('1.12.2001') == date(2001, 12, 1)
    assert parse_document_date('1990-01-01') is None
    assert parse_document_date('not a date') is None
    assert parse_document_date('32.01.1990') is None


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
        test_unknown_template_is_not_guessed,
        test_parses_dd_mm_yyyy_only,
        test_rejects_future_and_over_120_dob,
        test_canonical_schema_per_document_type,
        test_extracts_fields_by_label_anchor,
        test_name_token_set_accepts_reordered_names,
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
