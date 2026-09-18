import logging
import re
from datetime import date, datetime

import cv2

from services.documentPreprocessService import (
    merge_preprocess_config,
    preprocess_document,
    upscale_crop,
)

logger = logging.getLogger(__name__)

CONFIDENCE_FILTER = 0.4
NAME_MATCH_THRESHOLD = 0.85
MAX_AGE_YEARS = 120

DOCUMENT_PASSPORT = 'passport'
DOCUMENT_ID_V1 = 'id_v1_full_name'
DOCUMENT_ID_V2 = 'id_v2_surname_given'

LABELS = {
    'passport_no': ('PASSPORT NO', 'PASSPORT NUMBER', 'PASSPORTNO'),
    'full_names': ('FULL NAMES', 'FULL NAME'),
    'surname': ('SURNAME',),
    'given_names': ('GIVEN NAMES', 'GIVEN NAME', 'GIVENNAMES'),
    'id_number': ('ID NUMBER', 'ID NO', 'IDENTITY NUMBER', 'IDNUMBER'),
    'dob': ('DATE OF BIRTH', 'BIRTH DATE', 'D O B', 'DOB'),
    'expiry': ('DATE OF EXPIRY', 'DATE OF EXPIRATION', 'EXPIRY DATE', 'EXPIRY'),
}

LABEL_VALUE_STOPWORDS = {
    'SURNAME', 'GIVEN', 'NAMES', 'NAME', 'FULL', 'DATE', 'BIRTH', 'EXPIRY',
    'EXPIRATION', 'PASSPORT', 'NUMBER', 'IDENTITY', 'SEX', 'MALE', 'FEMALE',
    'NATIONAL', 'REPUBLIC', 'KENYA', 'SIGNATURE', 'HOLDER',
}

DOCUMENT_DATE_PATTERN = re.compile(
    r'\b(\d{1,2})[.\-/, ](\d{1,2})[.\-/, ](\d{4})\b'
)

_reader = None


def get_reader():
    global _reader
    if _reader is None:
        import easyocr
        import torch

        gpu_available = torch.cuda.is_available()
        _reader = easyocr.Reader(['en'], gpu=gpu_available)
        logger.info('EasyOCR reader loaded gpu=%s', gpu_available)
    return _reader


def _normalise_label_text(text):
    cleaned = re.sub(r'[^A-Z0-9]+', ' ', (text or '').upper())
    cleaned = cleaned.replace('0', 'O')
    return re.sub(r'\s+', ' ', cleaned).strip()


def _text_has_label(text, variants):
    norm = _normalise_label_text(text)
    compact = norm.replace(' ', '')
    for variant in variants:
        vn = _normalise_label_text(variant)
        if vn and (vn in norm or vn.replace(' ', '') in compact):
            return True
    return False


def _strip_label(text, variants):
    original = text or ''
    remainder = original
    for variant in sorted(variants, key=len, reverse=True):
        pattern = re.compile(re.escape(variant), re.IGNORECASE)
        remainder = pattern.sub(' ', remainder, count=1)
    remainder = re.sub(r'^[\s:.\-]+', '', remainder).strip()
    return remainder


def _bbox_stats(bbox):
    xs = [float(p[0]) for p in bbox]
    ys = [float(p[1]) for p in bbox]
    return {
        'x_min': min(xs),
        'x_max': max(xs),
        'y_min': min(ys),
        'y_max': max(ys),
        'height': max(ys) - min(ys),
        'width': max(xs) - min(xs),
    }


def _ocr_items_from_easyocr(results):
    items = []
    for item in results:
        if len(item) < 3:
            continue
        text = str(item[1]).strip()
        confidence = float(item[2])
        if not text or confidence < CONFIDENCE_FILTER:
            continue
        items.append({
            'text': text,
            'confidence': confidence,
            'bbox': item[0],
        })
    return items


def extract_text_from_document(image):
    """Run EasyOCR and return [{text, confidence, bbox}, ...] filtered below 0.4."""
    if image is None:
        return []
    ocr_image = image
    if ocr_image.ndim == 2:
        ocr_image = cv2.cvtColor(ocr_image, cv2.COLOR_GRAY2BGR)
    results = get_reader().readtext(ocr_image)
    return _ocr_items_from_easyocr(results)


def detect_document_type(ocr_items):
    """Label-anchor document type. Returns type string or None if unknown."""
    texts = [item.get('text', '') for item in ocr_items]
    blob = ' '.join(texts)

    has_passport_no = any(_text_has_label(t, LABELS['passport_no']) for t in texts) or _text_has_label(
        blob, LABELS['passport_no']
    )
    has_full_names = any(_text_has_label(t, LABELS['full_names']) for t in texts)
    has_surname = any(_text_has_label(t, LABELS['surname']) for t in texts)
    has_given = any(_text_has_label(t, LABELS['given_names']) for t in texts)
    has_id_number = any(_text_has_label(t, LABELS['id_number']) for t in texts)

    if has_passport_no:
        return DOCUMENT_PASSPORT
    if has_full_names:
        return DOCUMENT_ID_V1
    if has_surname and has_given and has_id_number:
        return DOCUMENT_ID_V2
    return None


def parse_document_date(value):
    """Parse a document date as dd.mm.yyyy (OCR may replace '.' with similar separators)."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()

    text = str(value).strip()
    if not text:
        return None

    try:
        match = DOCUMENT_DATE_PATTERN.search(text)
        if not match:
            return None
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        return date(year, month, day)
    except (ValueError, TypeError) as exc:
        logger.debug('document date parse failed value=%r error=%s', value, exc)
        return None


def parse_registered_date(value):
    """Parse user-input / stored DOB. Documents use dd.mm.yyyy; DB stores ISO."""
    parsed = parse_document_date(value)
    if parsed:
        return parsed
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}', text):
            return datetime.strptime(text[:10], '%Y-%m-%d').date()
    except (ValueError, TypeError) as exc:
        logger.warning('registered date parse failed value=%r error=%s', value, exc)
    return None


def validate_dob(parsed):
    if parsed is None:
        return False, 'Date of birth could not be parsed'
    today = date.today()
    if parsed > today:
        return False, 'Date of birth is in the future'
    age_days = (today - parsed).days
    if age_days > MAX_AGE_YEARS * 365.25:
        return False, 'Date of birth implies age over 120'
    return True, None


def format_document_date(parsed):
    if parsed is None:
        return None
    return parsed.strftime('%d.%m.%Y')


def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            insert = prev[j] + 1
            delete = curr[-1] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            curr.append(min(insert, delete, sub))
        prev = curr
    return prev[-1]


def levenshtein_similarity(a, b):
    left = a or ''
    right = b or ''
    if not left and not right:
        return 1.0
    return 1.0 - levenshtein(left, right) / max(len(left), len(right))


def name_tokens(value):
    return [tok for tok in re.sub(r'[^A-Z]+', ' ', (value or '').upper()).split() if tok]


def normalize_full_name(value):
    tokens = name_tokens(value)
    return ' '.join(tokens)


def token_overlap_ratio(extracted_name, registered_name):
    extracted = set(name_tokens(extracted_name))
    registered = set(name_tokens(registered_name))
    if not extracted or not registered:
        return 0.0
    return len(extracted & registered) / max(len(extracted), len(registered))


def normalize_id_number(value):
    return re.sub(r'\s+', '', value or '').upper()


def _looks_like_name_value(text):
    tokens = name_tokens(text)
    if not tokens:
        return False
    if any(tok in LABEL_VALUE_STOPWORDS for tok in tokens):
        return False
    if any(ch.isdigit() for ch in text):
        return False
    return True


def _looks_like_id_value(text):
    compact = normalize_id_number(text)
    if len(re.sub(r'[^A-Za-z0-9]', '', compact)) < 5:
        return False
    return any(ch.isdigit() for ch in compact)


def _find_label_item(items, variants):
    for item in items:
        if _text_has_label(item.get('text', ''), variants):
            return item
    return None


def _same_row(label_stats, item_stats):
    overlap = min(label_stats['y_max'], item_stats['y_max']) - max(label_stats['y_min'], item_stats['y_min'])
    min_h = min(label_stats['height'], item_stats['height']) or 1.0
    return overlap / min_h >= 0.45


def _value_candidates(items, label_item):
    label_stats = _bbox_stats(label_item['bbox'])
    right = []
    below = []
    for item in items:
        if item is label_item:
            continue
        stats = _bbox_stats(item['bbox'])
        if stats['x_min'] >= label_stats['x_max'] - 4 and _same_row(label_stats, stats):
            right.append((stats['x_min'], item))
        elif stats['y_min'] >= label_stats['y_max'] - (label_stats['height'] * 0.35):
            x_overlap = min(label_stats['x_max'] + label_stats['width'] * 3, stats['x_max']) - max(
                label_stats['x_min'], stats['x_min']
            )
            if x_overlap > 0:
                below.append((stats['y_min'], item))
    right.sort(key=lambda pair: pair[0])
    below.sort(key=lambda pair: pair[0])
    return [item for _, item in right], [item for _, item in below]


def extract_value_near_label(items, variants, predicate=None):
    label_item = _find_label_item(items, variants)
    if not label_item:
        return None, None

    remainder = _strip_label(label_item.get('text', ''), variants)
    if remainder and (predicate is None or predicate(remainder)):
        return remainder, label_item

    right, below = _value_candidates(items, label_item)
    for group in (right, below):
        for item in group:
            text = item.get('text', '').strip()
            if predicate is None or predicate(text):
                return text, label_item
    return None, label_item


def _crop_near_label(image, label_item):
    if image is None or not label_item:
        return None
    stats = _bbox_stats(label_item['bbox'])
    h, w = image.shape[:2]
    pad_x = max(stats['width'] * 4, 180)
    pad_y = max(stats['height'] * 3, 70)
    x0 = int(max(stats['x_min'] - 4, 0))
    y0 = int(max(stats['y_min'] - 4, 0))
    x1 = int(min(w, stats['x_max'] + pad_x))
    y1 = int(min(h, stats['y_max'] + pad_y))
    if x1 <= x0 or y1 <= y0:
        return None
    return image[y0:y1, x0:x1]


def _ocr_missing_field(image, items, variants, predicate, config):
    value, label_item = extract_value_near_label(items, variants, predicate)
    if value or not config.get('upscale'):
        return value, label_item
    crop = _crop_near_label(image, label_item or _find_label_item(items, variants))
    if crop is None:
        return None, label_item
    crop = upscale_crop(crop, min_size=int(config.get('crop_min_size', 64)))
    try:
        crop_items = extract_text_from_document(crop)
    except Exception as exc:
        logger.exception('field-crop OCR failed label=%s error=%s', variants[0], exc)
        return None, label_item
    for item in crop_items:
        text = item.get('text', '').strip()
        if _text_has_label(text, variants):
            stripped = _strip_label(text, variants)
            if stripped and (predicate is None or predicate(stripped)):
                return stripped, label_item
            continue
        if predicate is None or predicate(text):
            return text, label_item
    return None, label_item


def extract_raw_fields(ocr_items, document_type, image=None, config=None):
    config = merge_preprocess_config(config)
    raw = {
        'surname': None,
        'given_names': None,
        'full_names': None,
        'id_number': None,
        'passport_no': None,
        'date_of_birth': None,
        'date_of_expiry': None,
    }

    def read_field(key, variants, predicate):
        value, _ = _ocr_missing_field(image, ocr_items, variants, predicate, config)
        raw[key] = value

    if document_type == DOCUMENT_PASSPORT:
        read_field('surname', LABELS['surname'], _looks_like_name_value)
        read_field('given_names', LABELS['given_names'], _looks_like_name_value)
        read_field('passport_no', LABELS['passport_no'], _looks_like_id_value)
        read_field('date_of_birth', LABELS['dob'], lambda t: parse_document_date(t) is not None)
        read_field('date_of_expiry', LABELS['expiry'], lambda t: parse_document_date(t) is not None)
    elif document_type == DOCUMENT_ID_V1:
        read_field('full_names', LABELS['full_names'], _looks_like_name_value)
        read_field('id_number', LABELS['id_number'], _looks_like_id_value)
        read_field('date_of_birth', LABELS['dob'], lambda t: parse_document_date(t) is not None)
    elif document_type == DOCUMENT_ID_V2:
        read_field('surname', LABELS['surname'], _looks_like_name_value)
        read_field('given_names', LABELS['given_names'], _looks_like_name_value)
        read_field('id_number', LABELS['id_number'], _looks_like_id_value)
        read_field('date_of_birth', LABELS['dob'], lambda t: parse_document_date(t) is not None)
        read_field('date_of_expiry', LABELS['expiry'], lambda t: parse_document_date(t) is not None)

    return raw


def normalize_to_canonical(raw, document_type):
    dob = parse_document_date(raw.get('date_of_birth'))
    dob_ok, dob_reason = validate_dob(dob)
    if not dob_ok:
        logger.info('DOB rejected: %s value=%s', dob_reason, raw.get('date_of_birth'))
        dob = None

    expiry = parse_document_date(raw.get('date_of_expiry')) if raw.get('date_of_expiry') else None

    if document_type == DOCUMENT_PASSPORT:
        full_name = normalize_full_name(f"{raw.get('surname') or ''} {raw.get('given_names') or ''}")
        id_number = normalize_id_number(raw.get('passport_no') or '')
    elif document_type == DOCUMENT_ID_V1:
        full_name = normalize_full_name(raw.get('full_names') or '')
        id_number = normalize_id_number(raw.get('id_number') or '')
    elif document_type == DOCUMENT_ID_V2:
        full_name = normalize_full_name(f"{raw.get('surname') or ''} {raw.get('given_names') or ''}")
        id_number = normalize_id_number(raw.get('id_number') or '')
    else:
        full_name = ''
        id_number = ''

    return {
        'full_name': full_name or None,
        'id_number': id_number or None,
        'document_type': document_type,
        'date_of_birth': dob,
        'date_of_expiry': expiry,
        'dob_valid': dob_ok,
        'dob_reject_reason': None if dob_ok else dob_reason,
    }


def match_identity_fields(canonical, registered, name_threshold=NAME_MATCH_THRESHOLD):
    registered_name = registered.get('name') or registered.get('full_name') or ''
    registered_id = registered.get('idNumber') or registered.get('id_number') or ''
    registered_dob = registered.get('dateOfBirth') or registered.get('date_of_birth')

    extracted_name = canonical.get('full_name') or ''
    overlap = token_overlap_ratio(extracted_name, registered_name)
    lev_score = levenshtein_similarity(
        normalize_full_name(extracted_name),
        normalize_full_name(registered_name),
    )
    name_match = bool(extracted_name and registered_name and overlap >= float(name_threshold))

    extracted_id = normalize_id_number(canonical.get('id_number') or '')
    expected_id = normalize_id_number(registered_id)
    id_match = bool(extracted_id and expected_id and extracted_id == expected_id)

    extracted_dob = canonical.get('date_of_birth')
    expected_dob = parse_registered_date(registered_dob)
    dob_parse_failed = expected_dob is None and bool(str(registered_dob or '').strip())
    if dob_parse_failed:
        logger.warning('registered DOB parse failed value=%r', registered_dob)
    dob_match = (
        extracted_dob is not None
        and expected_dob is not None
        and extracted_dob == expected_dob
    )

    field_matches = [
        {
            'field': 'full_name',
            'matched': name_match,
            'score': round(overlap, 4),
            'token_overlap': round(overlap, 4),
            'levenshtein': round(lev_score, 4),
        },
        {
            'field': 'id_number',
            'matched': id_match,
            'score': 1.0 if id_match else 0.0,
        },
        {
            'field': 'date_of_birth',
            'matched': dob_match,
            'score': 1.0 if dob_match else 0.0,
        },
    ]

    overall = name_match and id_match and dob_match
    confidence = float((overlap + (1.0 if id_match else 0.0) + (1.0 if dob_match else 0.0)) / 3.0)

    return {
        'field_matches': field_matches,
        'name_match': name_match,
        'id_match': id_match,
        'dob_match': dob_match,
        'matched': overall,
        'confidence_score': round(confidence, 4),
        'registered_dob_parse_failed': dob_parse_failed,
    }


def _empty_result(extra=None):
    result = {
        'extractedName': None,
        'extractedIDNumber': None,
        'extractedDOB': None,
        'extractedExpiry': None,
        'nameMatch': False,
        'idMatch': False,
        'dobMatch': False,
        'confidenceScore': 0.0,
        'matched': False,
        'rawText': [],
        'documentType': None,
        'dateOfExpiry': None,
        'needsRetake': False,
        'needsManualReview': False,
        'rejectReason': None,
        'fieldMatches': [],
        'canonical': {
            'full_name': None,
            'id_number': None,
            'document_type': None,
            'date_of_birth': None,
            'date_of_expiry': None,
        },
    }
    if extra:
        result.update(extra)
    return result


def assess_document_ocr(image, registered_details, debug=False, preprocess_config=None, name_threshold=None):
    """
    Full OCR pipeline: preprocess → OCR → detect type → extract → match.
    """
    config = merge_preprocess_config(preprocess_config)
    config['debug'] = bool(debug or config.get('debug'))
    threshold = NAME_MATCH_THRESHOLD if name_threshold is None else float(name_threshold)

    pre = preprocess_document(image, config)
    if not pre.get('ok'):
        return _empty_result({
            'needsRetake': True,
            'rejectReason': pre.get('message') or 'Image is too blurry. Please retake.',
            'blurScore': pre.get('blur_score'),
            'preprocessSteps': pre.get('steps_run') or [],
            'debugDir': pre.get('debug_dir'),
            'debugImages': pre.get('debug_images') or {},
        })

    processed = pre['image']
    document_type = None

    try:
        text_results = extract_text_from_document(processed)
        document_type = detect_document_type(text_results)
        raw_text = [item['text'] for item in text_results]
    except Exception:
        logger.exception(
            'OCR failed assumed_document_type=%s',
            document_type or 'unknown/not-yet-detected',
        )
        return _empty_result({
            'needsManualReview': True,
            'rejectReason': 'OCR failed while reading the document. Flagged for manual review.',
            'documentType': document_type,
            'blurScore': pre.get('blur_score'),
            'preprocessSteps': pre.get('steps_run') or [],
            'debugDir': pre.get('debug_dir'),
            'debugImages': pre.get('debug_images') or {},
        })

    extra_meta = {
        'blurScore': pre.get('blur_score'),
        'preprocessSteps': pre.get('steps_run') or [],
        'debugDir': pre.get('debug_dir') if config.get('debug') else None,
        'debugImages': pre.get('debug_images') if config.get('debug') else {},
        'rawText': raw_text,
    }

    if not document_type:
        logger.info('document type detection failed raw_text=%s', raw_text)
        return _empty_result({
            **extra_meta,
            'needsManualReview': True,
            'rejectReason': 'Could not match a known document template. Flagged for manual review.',
        })

    try:
        raw_fields = extract_raw_fields(text_results, document_type, image=processed, config=config)
        canonical = normalize_to_canonical(raw_fields, document_type)
        comparison = match_identity_fields(canonical, registered_details or {}, name_threshold=threshold)
    except Exception:
        logger.exception('field extraction/matching failed assumed_document_type=%s', document_type)
        return _empty_result({
            **extra_meta,
            'documentType': document_type,
            'needsManualReview': True,
            'rejectReason': f'Failed to extract fields from {document_type}. Flagged for manual review.',
        })

    dob_invalid = canonical.get('dob_valid') is False
    parse_failed = comparison.get('registered_dob_parse_failed') or (
        canonical.get('date_of_birth') is None and bool(raw_fields.get('date_of_birth'))
    )
    extraction_incomplete = not (
        canonical.get('full_name') and canonical.get('id_number') and canonical.get('date_of_birth')
    )
    needs_review = bool(dob_invalid or parse_failed or extraction_incomplete)

    canonical_public = {
        'full_name': canonical.get('full_name'),
        'id_number': canonical.get('id_number'),
        'document_type': canonical.get('document_type'),
        'date_of_birth': canonical['date_of_birth'].isoformat() if canonical.get('date_of_birth') else None,
        'date_of_expiry': canonical['date_of_expiry'].isoformat() if canonical.get('date_of_expiry') else None,
    }

    return {
        'extractedName': canonical.get('full_name'),
        'extractedIDNumber': canonical.get('id_number'),
        'extractedDOB': format_document_date(canonical.get('date_of_birth')),
        'extractedExpiry': format_document_date(canonical.get('date_of_expiry')),
        'nameMatch': comparison['name_match'],
        'idMatch': comparison['id_match'],
        'dobMatch': comparison['dob_match'],
        'confidenceScore': comparison['confidence_score'],
        'matched': comparison['matched'],
        'rawText': raw_text,
        'documentType': document_type,
        'dateOfExpiry': format_document_date(canonical.get('date_of_expiry')),
        'needsRetake': False,
        'needsManualReview': bool(needs_review),
        'rejectReason': canonical.get('dob_reject_reason') if dob_invalid else None,
        'fieldMatches': comparison['field_matches'],
        'canonical': canonical_public,
        'rawFields': raw_fields,
        **extra_meta,
    }
