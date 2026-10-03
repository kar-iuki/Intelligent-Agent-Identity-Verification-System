import json
import logging
import os
import re
from datetime import date, datetime

import cv2
import numpy as np

from services.documentPreprocessService import (
    DEFAULT_OUTPUT_SIZE,
    draw_quad_overlay,
    merge_preprocess_config,
    preprocess_document,
    preprocess_field_crop,
    warp_quad,
)
from services.mrzService import merge_mrz, parse_mrz

logger = logging.getLogger(__name__)

CONFIDENCE_FILTER = 0.4
CROP_CONFIDENCE_MIN = 0.5
NAME_MATCH_THRESHOLD = 1.0
MAX_AGE_YEARS = 120

DOCUMENT_PASSPORT = 'passport'
DOCUMENT_ID_V1 = 'id_v1_full_name'
DOCUMENT_ID_V2 = 'id_v2_surname_given'
DOCUMENT_ID_BACK = 'id_back'
DOCUMENT_ID_BACK_V1 = 'id_back_v1'
DOCUMENT_ID_BACK_V2 = 'id_back_v2'
DOCUMENT_DRIVERS_LICENCE = 'drivers_licence'

ID_FRONT_TYPES = (DOCUMENT_ID_V1, DOCUMENT_ID_V2)
TYPES_REQUIRING_EXPIRY = (DOCUMENT_PASSPORT, DOCUMENT_ID_V2, DOCUMENT_DRIVERS_LICENCE)

TEMPLATES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'config',
    'ocr_templates.json',
)
_TEMPLATES_CACHE = None

LABELS = {
    'passport_no': ('PASSPORT NO', 'PASSPORT NUMBER', 'PASSPORTNO'),
    'full_names': ('FULL NAMES', 'FULL NAME'),
    'surname': ('SURNAME',),
    'given_names': ('GIVEN NAMES', 'GIVEN NAME', 'GIVENNAMES'),
    'other_names': ('OTHER NAMES', 'OTHER NAME'),
    'id_number': ('ID NUMBER', 'ID NO', 'IDENTITY NUMBER', 'IDNUMBER'),
    'national_id_no': ('NATIONAL ID NO', 'NATIONAL ID NUMBER', 'NAT ID NO'),
    'licence': ('DRIVING LICENCE', "DRIVER'S LICENCE", 'DRIVERS LICENCE', 'DRIVER LICENCE'),
    'dob': ('DATE OF BIRTH', 'BIRTH DATE', 'D O B', 'DOB'),
    'expiry': ('DATE OF EXPIRY', 'DATE OF EXPIRATION', 'EXPIRY DATE', 'EXPIRY'),
    # printed on the new-generation national ID, whose small bilingual field
    # labels are usually not read; the old-format ID does not carry this line
    'national_identity_card': ('NATIONAL IDENTITY CARD', 'NATIONAL IDENTITYCARD', 'NATIONALIDENTITY CARD'),
}

LABEL_VALUE_STOPWORDS = {
    'SURNAME', 'GIVEN', 'NAMES', 'NAME', 'FULL', 'DATE', 'BIRTH', 'EXPIRY',
    'EXPIRATION', 'PASSPORT', 'NUMBER', 'IDENTITY', 'SEX', 'MALE', 'FEMALE',
    'NATIONAL', 'REPUBLIC', 'KENYA', 'SIGNATURE', 'HOLDER', 'SERIAL',
    'OTHER', 'DRIVING', 'LICENCE', 'LICENSE', 'DRIVER',
}

# dd<sep>mm<sep>yyyy where <sep> is 1-3 non-digit characters: OCR renders the
# printed dots as '.', '_', ':', "'" or nothing recognisable at all
DOCUMENT_DATE_PATTERN = re.compile(
    r'(?<!\d)(\d{1,2})[^\d\s]{1,3}(\d{1,2})[^\d\s]{1,3}(\d{4})(?!\d)'
)
LOOSE_DATE_PATTERN = re.compile(
    r'(?<!\d)(\d{1,2})\s*[^\d\s]{1,3}\s*(\d{1,2})\s*[^\d\s]{1,3}\s*(\d{4})(?!\d)'
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


def _text_has_phrase_fuzzy(text, phrase, max_errors=None):
    """
    True when `phrase` appears in `text` allowing OCR damage (dropped or
    swapped letters): 'ONALIDENTIY CARD' still counts as 'NATIONAL IDENTITY
    CARD'. Compared without spaces; up to ~15% of the phrase may be wrong.
    """
    haystack = _normalise_label_text(text).replace(' ', '')
    needle = _normalise_label_text(phrase).replace(' ', '')
    if not haystack or not needle:
        return False
    if needle in haystack:
        return True
    if max_errors is None:
        max_errors = max(1, int(round(len(needle) * 0.15)))
    n = len(needle)
    best = None
    # the phrase inside the text (text may carry extra words)
    for length in range(max(2, n - max_errors), n + max_errors + 1):
        if length > len(haystack):
            break
        for start in range(0, len(haystack) - length + 1):
            distance = levenshtein(haystack[start:start + length], needle)
            if best is None or distance < best:
                best = distance
                if best == 0:
                    return True
    # the text as a damaged fragment of the phrase (leading letters dropped: 'ONALIDENTIYCARD')
    if len(haystack) >= 0.6 * n:
        m = len(haystack)
        for length in range(max(2, m - max_errors), min(n, m + max_errors) + 1):
            for start in range(0, n - length + 1):
                distance = levenshtein(needle[start:start + length], haystack)
                if best is None or distance < best:
                    best = distance
    return best is not None and best <= max_errors


# phrases printed only on the new-generation national ID (English and Swahili)
NEW_GEN_ID_PHRASES = ('NATIONAL IDENTITY CARD', 'KITAMBULISHO CHA TAIFA')


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


def load_ocr_templates():
    global _TEMPLATES_CACHE
    if _TEMPLATES_CACHE is not None:
        return _TEMPLATES_CACHE
    try:
        with open(TEMPLATES_PATH, encoding='utf-8') as handle:
            _TEMPLATES_CACHE = json.load(handle)
    except FileNotFoundError:
        logger.warning('OCR templates file missing path=%s', TEMPLATES_PATH)
        _TEMPLATES_CACHE = {}
    except json.JSONDecodeError:
        logger.exception('OCR templates file is invalid path=%s', TEMPLATES_PATH)
        _TEMPLATES_CACHE = {}
    return _TEMPLATES_CACHE


def _ocr_items_from_easyocr(results, min_confidence=CONFIDENCE_FILTER):
    items = []
    for item in results:
        if len(item) < 3:
            continue
        text = str(item[1]).strip()
        confidence = float(item[2])
        if not text or confidence < min_confidence:
            continue
        items.append({
            'text': text,
            'confidence': confidence,
            'bbox': item[0],
        })
    return items


def extract_text_from_document(image, min_confidence=CONFIDENCE_FILTER):
    """Run EasyOCR and return [{text, confidence, bbox}, ...] filtered below min_confidence."""
    if image is None:
        return []
    ocr_image = image
    if ocr_image.ndim == 2:
        ocr_image = cv2.cvtColor(ocr_image, cv2.COLOR_GRAY2BGR)
    results = get_reader().readtext(ocr_image)
    return _ocr_items_from_easyocr(results, min_confidence=min_confidence)


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
    has_other_names = any(_text_has_label(t, LABELS['other_names']) for t in texts)
    has_id_number = any(_text_has_label(t, LABELS['id_number']) for t in texts)
    has_national_id_no = any(_text_has_label(t, LABELS['national_id_no']) for t in texts)
    has_licence = any(_text_has_label(t, LABELS['licence']) for t in texts) or _text_has_label(
        blob, LABELS['licence']
    )
    has_national_identity_card = any(
        _text_has_label(t, LABELS['national_identity_card']) for t in texts
    ) or _text_has_label(blob, LABELS['national_identity_card']) or any(
        _text_has_phrase_fuzzy(t, phrase) for t in texts + [blob] for phrase in NEW_GEN_ID_PHRASES
    )

    if has_passport_no:
        return DOCUMENT_PASSPORT
    if has_full_names:
        return DOCUMENT_ID_V1
    if has_licence or has_other_names or (has_national_id_no and has_surname):
        return DOCUMENT_DRIVERS_LICENCE
    if has_surname and has_given and has_id_number:
        return DOCUMENT_ID_V2
    if has_national_identity_card:
        return DOCUMENT_ID_V2
    return None


def _compact_date_text(value):
    """Remove spaces so '01. 01. 1990' and '01 / 01 / 1990' become parseable."""
    return re.sub(r'\s+', '', str(value).strip())


def parse_document_date(value):
    """Parse a document date as dd.mm.yyyy (OCR may add spaces or swap '.' for '/' or '-')."""
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()

    original = str(value).strip()
    if not original:
        return None
    compacted = _compact_date_text(original)

    try:
        match = DOCUMENT_DATE_PATTERN.search(compacted)
        if not match:
            match = LOOSE_DATE_PATTERN.search(original)
        if not match:
            return None
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        return date(year, month, day)
    except (ValueError, TypeError) as exc:
        logger.debug('document date parse failed value=%r error=%s', value, exc)
        return None


def _candidate_strings(items, max_window=5):
    """Yield single OCR lines and joined neighbors (dates are often split into 2–3 boxes)."""
    texts = [str(item.get('text', '')).strip() for item in items if str(item.get('text', '')).strip()]
    for text in texts:
        yield text
    for i in range(len(texts)):
        for j in range(i + 2, min(i + max_window + 1, len(texts) + 1)):
            yield ' '.join(texts[i:j])
    if len(texts) > 1:
        yield ' '.join(texts)


def _merge_bboxes(first, second):
    sa = _bbox_stats(first)
    sb = _bbox_stats(second)
    x0, y0 = min(sa['x_min'], sb['x_min']), min(sa['y_min'], sb['y_min'])
    x1, y1 = max(sa['x_max'], sb['x_max']), max(sa['y_max'], sb['y_max'])
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def parse_registered_date(value):
    """Parse stored/user DOB: dd/mm/yyyy, spaced OCR-style dates, or ISO YYYY-MM-DD."""
    parsed = parse_document_date(value)
    if parsed:
        return parsed
    if value is None:
        return None
    text = _compact_date_text(value)
    if not text:
        return None
    try:
        if re.match(r'^\d{4}-\d{2}-\d{2}', text):
            return datetime.strptime(text[:10], '%Y-%m-%d').date()
        return datetime.strptime(text, '%d/%m/%Y').date()
    except (ValueError, TypeError) as exc:
        logger.debug('registered date parse failed value=%r error=%s', value, exc)
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


def validate_expiry(parsed):
    if parsed is None:
        return False, 'Date of expiry could not be parsed'
    if parsed < date.today():
        return False, 'Document has expired'
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


NAME_MIN_MATCHING_TOKENS = 2


def registered_name_coverage(extracted_name, registered_name):
    """
    Fraction of the shorter name's distinct tokens shared by both names.
    Either side may contain additional names, but matching uses whole tokens,
    never approximate substrings. Order and capitalization do not matter.
    """
    extracted = set(name_tokens(extracted_name))
    registered = set(name_tokens(registered_name))
    if not extracted or not registered:
        return 0.0
    return len(extracted & registered) / min(len(extracted), len(registered))


def normalize_id_number(value):
    return re.sub(r'[^A-Za-z0-9]', '', value or '').upper()


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


def _looks_like_date_value(text):
    """Require a plausible dd.mm.yyyy pattern before treating OCR text as a date."""
    if not text:
        return False
    compacted = _compact_date_text(text)
    if not DOCUMENT_DATE_PATTERN.search(compacted) and not LOOSE_DATE_PATTERN.search(str(text)):
        return False
    return parse_document_date(text) is not None


def _find_label_item(items, variants):
    for item in items:
        if _text_has_label(item.get('text', ''), variants):
            return item
    for index, item in enumerate(items[:-1]):
        neighbor = items[index + 1]
        combined_text = f"{item.get('text', '')} {neighbor.get('text', '')}"
        if _text_has_label(combined_text, variants):
            return {
                'text': combined_text,
                'confidence': min(float(item.get('confidence', 1)), float(neighbor.get('confidence', 1))),
                'bbox': _merge_bboxes(item['bbox'], neighbor['bbox']),
            }
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
        for text in _candidate_strings(group):
            if predicate is None or predicate(text):
                return text, label_item
    return None, label_item


REQUIRED_FIELDS = {
    DOCUMENT_PASSPORT: ('surname', 'given_names', 'passport_no', 'date_of_birth', 'date_of_expiry'),
    DOCUMENT_ID_V1: ('full_names', 'id_number', 'date_of_birth'),
    DOCUMENT_ID_V2: ('surname', 'given_names', 'id_number', 'date_of_birth', 'date_of_expiry'),
    DOCUMENT_ID_BACK: ('id_number',),
    DOCUMENT_ID_BACK_V1: ('id_number',),
    DOCUMENT_ID_BACK_V2: ('id_number',),
    DOCUMENT_DRIVERS_LICENCE: ('surname', 'other_names', 'id_number', 'date_of_birth', 'date_of_expiry'),
}

FIELD_SPECS = {
    DOCUMENT_PASSPORT: (
        ('surname', LABELS['surname'], _looks_like_name_value),
        ('given_names', LABELS['given_names'], _looks_like_name_value),
        ('passport_no', LABELS['passport_no'], _looks_like_id_value),
        ('date_of_birth', LABELS['dob'], _looks_like_date_value),
        ('date_of_expiry', LABELS['expiry'], _looks_like_date_value),
    ),
    DOCUMENT_ID_V1: (
        ('full_names', LABELS['full_names'], _looks_like_name_value),
        ('id_number', LABELS['id_number'], _looks_like_id_value),
        ('date_of_birth', LABELS['dob'], _looks_like_date_value),
    ),
    DOCUMENT_ID_V2: (
        ('surname', LABELS['surname'], _looks_like_name_value),
        ('given_names', LABELS['given_names'], _looks_like_name_value),
        ('id_number', LABELS['id_number'], _looks_like_id_value),
        ('date_of_birth', LABELS['dob'], _looks_like_date_value),
        ('date_of_expiry', LABELS['expiry'], _looks_like_date_value),
    ),
    DOCUMENT_ID_BACK: (
        ('id_number', LABELS['id_number'], _looks_like_id_value),
    ),
    DOCUMENT_ID_BACK_V1: (
        ('id_number', LABELS['id_number'], _looks_like_id_value),
    ),
    DOCUMENT_ID_BACK_V2: (
        ('id_number', LABELS['id_number'], _looks_like_id_value),
    ),
    DOCUMENT_DRIVERS_LICENCE: (
        ('surname', LABELS['surname'], _looks_like_name_value),
        ('other_names', LABELS['other_names'], _looks_like_name_value),
        ('id_number', LABELS['national_id_no'], _looks_like_id_value),
        ('date_of_birth', LABELS['dob'], _looks_like_date_value),
        ('date_of_expiry', LABELS['expiry'], _looks_like_date_value),
    ),
}


def back_template_key(front_type):
    if front_type == DOCUMENT_ID_V1:
        return DOCUMENT_ID_BACK_V1
    if front_type == DOCUMENT_ID_V2:
        return DOCUMENT_ID_BACK_V2
    return DOCUMENT_ID_BACK


def back_template_for(front_type):
    """Old ID uses the calibrated v1 back box. New ID has no sample yet — labels only."""
    templates = load_ocr_templates()
    if front_type == DOCUMENT_ID_V1:
        return templates.get(DOCUMENT_ID_BACK_V1) or templates.get(DOCUMENT_ID_BACK) or {}
    if front_type == DOCUMENT_ID_V2:
        return templates.get(DOCUMENT_ID_BACK_V2) or {}
    return {}


def missing_required_fields(raw, document_type):
    required = REQUIRED_FIELDS.get(document_type) or ()
    return [key for key in required if not str(raw.get(key) or '').strip()]


def normalized_box_to_pixels(box, width, height):
    x1, y1, x2, y2 = [float(v) for v in box]
    xa, xb = sorted((x1, x2))
    ya, yb = sorted((y1, y2))
    px1 = int(round(xa * width))
    py1 = int(round(ya * height))
    px2 = int(round(xb * width))
    py2 = int(round(yb * height))
    px1 = max(0, min(px1, width - 1))
    py1 = max(0, min(py1, height - 1))
    px2 = max(px1 + 1, min(px2, width))
    py2 = max(py1 + 1, min(py2, height))
    return px1, py1, px2, py2


def _valid_template_box(box):
    return isinstance(box, (list, tuple)) and len(box) == 4


TEMPLATE_BOX_PAD_X = 0.10  # fraction of box width added on each side
TEMPLATE_BOX_PAD_Y = 0.40  # fraction of box height added above and below


def _pad_template_box(box):
    x1, y1, x2, y2 = [float(v) for v in box]
    xa, xb = sorted((x1, x2))
    ya, yb = sorted((y1, y2))
    pad_x = (xb - xa) * TEMPLATE_BOX_PAD_X
    pad_y = (yb - ya) * TEMPLATE_BOX_PAD_Y
    return [max(0.0, xa - pad_x), max(0.0, ya - pad_y), min(1.0, xb + pad_x), min(1.0, yb + pad_y)]


def _crop_template_region(image, box):
    if image is None or not _valid_template_box(box):
        return None
    height, width = image.shape[:2]
    x1, y1, x2, y2 = normalized_box_to_pixels(_pad_template_box(box), width, height)
    crop = image[y1:y2, x1:x2]
    if crop is None or crop.size == 0:
        return None
    return crop


def _crop_text_candidates(items, variants):
    """
    Order the strings to try from a template crop. The field value is printed
    larger than the small labels and neighbouring lines a padded crop picks up,
    so items near the tallest text height come first (joined, then singly);
    everything else is a last resort.
    """
    def stats(item):
        return _bbox_stats(item['bbox']) if item.get('bbox') else None

    with_text = [item for item in items if str(item.get('text', '')).strip()]
    # reading order: boxes whose vertical extents overlap are one line, sorted left to right
    typical_height = max([stats(item)['height'] for item in with_text if stats(item)] or [1.0])

    def reading_key(item):
        st = stats(item) or {}
        row = int(round(st.get('y_min', 0) / max(typical_height * 0.6, 1.0)))
        return (row, st.get('x_min', 0))

    ordered = sorted(with_text, key=reading_key)
    heights = [stats(item)['height'] for item in ordered if stats(item)]
    max_height = max(heights) if heights else 0
    main = [
        item for item in ordered
        if not stats(item) or stats(item)['height'] >= max_height * 0.65
    ]
    seen = []

    def add(text):
        cleaned = (text or '').strip()
        if cleaned and cleaned not in seen:
            seen.append(cleaned)

    def add_group(group):
        joined = ' '.join(str(item.get('text', '')).strip() for item in group)
        if variants:
            add(_strip_label(joined, variants))
        add(joined)
        for item in sorted(group, key=lambda it: -len(str(it.get('text', '')))):
            text = str(item.get('text', '')).strip()
            if variants:
                add(_strip_label(text, variants))
            add(text)

    add_group(main)
    if len(main) != len(ordered):
        add_group(ordered)
        for text in _candidate_strings(ordered):
            if variants:
                add(_strip_label(text, variants))
            add(text)
    return seen


def _save_crop_debug(config, field, name, image):
    debug_dir = config.get('debug_dir') if config.get('debug') else None
    if not debug_dir or image is None:
        return
    try:
        os.makedirs(debug_dir, exist_ok=True)
        side = config.get('debug_side') or 'front'
        cv2.imwrite(os.path.join(debug_dir, f'crop_{side}_{field}_{name}.png'), image)
    except Exception:
        logger.exception('failed to save crop debug image field=%s', field)


def _ocr_crop_variant(processed, predicate, variants, collect=None):
    """OCR one prepared crop. Returns (text, fail_reason); appends every passing candidate to `collect`."""
    try:
        items = extract_text_from_document(processed, min_confidence=0.0)
    except Exception:
        logger.exception('template crop OCR failed')
        return None, 'ocr_error'
    if not items:
        return None, 'empty_text'
    best_conf = max(float(item.get('confidence') or 0) for item in items)
    if best_conf < CROP_CONFIDENCE_MIN:
        return None, f'low_confidence:{best_conf:.2f}'
    first = None
    for text in _crop_text_candidates(items, variants):
        if predicate is None or predicate(text):
            if first is None:
                first = text
            if collect is None:
                break
            collect.append(text)
    if first is not None:
        return first, None
    return None, 'failed_validation:' + '|'.join(str(item.get('text', '')) for item in items)[:80]


def _upscale_colour_crop(crop, min_height=96):
    h, w = crop.shape[:2]
    if h >= min_height:
        return crop
    scale = float(min_height) / max(h, 1)
    return cv2.resize(crop, (max(int(round(w * scale)), 1), min_height), interpolation=cv2.INTER_CUBIC)


def _ocr_template_crop(image, box, predicate, variants, config, field='field', collect=None):
    """
    OCR a template box, trying the least destructive image first: the natural
    colour crop (upscaled), then grayscale with CLAHE, and only then the
    adaptive-threshold version, which breaks thin print and turns security
    patterns into noise. With debug on, every variant is written to debug_dir.
    """
    crop = _crop_template_region(image, box)
    if crop is None:
        return None, 'empty_crop'
    _save_crop_debug(config, field, 'raw', crop)

    passes = (
        ('natural', _upscale_colour_crop(crop)),
        ('gray', preprocess_field_crop(crop, {**config, 'binarize': False, 'sharpen': False, 'crop_min_size': 96})),
        ('binarized', preprocess_field_crop(crop, config)),
    )
    first_text = None
    reasons = []
    for label, variant in passes:
        _save_crop_debug(config, field, label, variant)
        text, reason = _ocr_crop_variant(variant, predicate, variants, collect=collect)
        if text and first_text is None:
            first_text = text
            if collect is None:
                return text, None
        if not text:
            reasons.append(f'{label}:{reason}')
    if first_text:
        return first_text, None
    return None, ' / '.join(reasons)


FIELD_LABEL_KEYS = ('full_names', 'surname', 'given_names', 'other_names', 'id_number', 'dob', 'expiry')


def _document_has_field_labels(ocr_items):
    """True when at least one field label (SURNAME, DATE OF BIRTH, ...) was read."""
    texts = [str(item.get('text', '')) for item in ocr_items]
    return any(_text_has_label(t, LABELS[key]) for t in texts for key in FIELD_LABEL_KEYS)


def _unlabelled_birth_date(ocr_items, expiry_text=None):
    """
    Last resort for cards whose field labels are too small to read (new-gen
    national ID): if the page holds exactly one plausible birth date (past,
    sane age, not the expiry), return its text. Ambiguity returns None.
    """
    expiry = parse_document_date(expiry_text) if expiry_text else None
    found = {}
    for text in _candidate_strings(ocr_items):
        parsed = parse_document_date(text)
        if parsed is None or parsed == expiry or parsed in found:
            continue
        ok, _ = validate_dob(parsed)
        if ok:
            found[parsed] = text
    if len(found) != 1:
        return None
    return next(iter(found.values()))


def _line_below(ocr_items, anchor_text, predicate):
    """The OCR line printed directly under `anchor_text` (same column), if it passes predicate."""
    anchor = None
    wanted = _normalise_label_text(anchor_text)
    for item in ocr_items:
        if item.get('bbox') and _normalise_label_text(item.get('text', '')) == wanted:
            anchor = _bbox_stats(item['bbox'])
            break
    if anchor is None:
        return None
    best = None
    for item in ocr_items:
        if not item.get('bbox'):
            continue
        stats = _bbox_stats(item['bbox'])
        gap = stats['y_min'] - anchor['y_max']
        if gap < -anchor['height'] * 0.3 or gap > anchor['height'] * 2.5:
            continue
        if stats['x_min'] > anchor['x_max'] or stats['x_max'] < anchor['x_min'] - anchor['height'] * 2:
            continue
        text = str(item.get('text', '')).strip()
        if not text or (predicate and not predicate(text)):
            continue
        if best is None or gap < best[0]:
            best = (gap, text)
    return best[1] if best else None


TEMPLATE_REGISTER_MIN_FIELDS = 2
TEMPLATE_REGISTER_MAX_SPREAD = 0.05


def _item_norm_center(item):
    box = item.get('nbbox')
    if not box:
        return None
    xs = [float(p[0]) for p in box]
    ys = [float(p[1]) for p in box]
    return (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0


def register_template(template, ocr_items, document_type):
    """
    Shift the template so it lines up with where the page OCR actually found
    the values. A slightly-short document quad moves every field a few percent
    of the card; the values the page pass did read (a name-like word, a long
    number, a date) tell us by how much. Needs at least two fields agreeing.
    """
    if not isinstance(template, dict) or not template:
        return template
    offsets = []
    for key, variants, predicate in FIELD_SPECS.get(document_type) or ():
        box = template.get(key)
        if not _valid_template_box(box):
            continue
        bx = (float(box[0]) + float(box[2])) / 2.0
        by = (float(box[1]) + float(box[3])) / 2.0
        best = None
        for item in ocr_items:
            center = _item_norm_center(item)
            text = str(item.get('text', '')).strip()
            if center is None or not text or (predicate and not predicate(text)):
                continue
            if _text_has_label(text, variants or ()):
                continue
            dx, dy = center[0] - bx, center[1] - by
            if abs(dx) > 0.25 or abs(dy) > 0.12:
                continue
            distance = abs(dx) + 2 * abs(dy)
            if best is None or distance < best[0]:
                best = (distance, dx, dy)
        if best is not None:
            offsets.append((best[1], best[2], key))
    if len(offsets) < TEMPLATE_REGISTER_MIN_FIELDS:
        return template
    dys = sorted(o[1] for o in offsets)
    if dys[-1] - dys[0] > TEMPLATE_REGISTER_MAX_SPREAD:
        return template
    dy = float(dys[len(dys) // 2])
    dxs = sorted(o[0] for o in offsets)
    dx = float(dxs[len(dxs) // 2]) if dxs[-1] - dxs[0] <= TEMPLATE_REGISTER_MAX_SPREAD else 0.0
    if abs(dy) < 0.012 and abs(dx) < 0.012:
        return template
    logger.info('template registered against page OCR shift dx=%.3f dy=%.3f from %s', dx, dy, [o[2] for o in offsets])
    shifted = {}
    for key, box in template.items():
        if _valid_template_box(box):
            shifted[key] = [
                min(max(float(box[0]) + dx, 0.0), 1.0),
                min(max(float(box[1]) + dy, 0.0), 1.0),
                min(max(float(box[2]) + dx, 0.0), 1.0),
                min(max(float(box[3]) + dy, 0.0), 1.0),
            ]
        else:
            shifted[key] = box
    return shifted


def extract_raw_fields(
    ocr_items,
    document_type,
    image=None,
    config=None,
    template=None,
    sources=None,
):
    """Extract fields from template crops first, then label-anchor fallback."""
    config = merge_preprocess_config(config)
    if template is None:
        template = load_ocr_templates().get(document_type) or {}
    if sources is None:
        sources = {}
    template = register_template(template, ocr_items, document_type)

    raw = {
        'surname': None,
        'given_names': None,
        'other_names': None,
        'full_names': None,
        'id_number': None,
        'passport_no': None,
        'date_of_birth': None,
        'date_of_expiry': None,
    }

    id_readings = []  # every reading of the ID number we get, for the consensus step

    for key, variants, predicate in FIELD_SPECS.get(document_type) or ():
        value = None
        box = template.get(key) if isinstance(template, dict) else None
        attempted_template = image is not None and _valid_template_box(box)
        if attempted_template:
            collect = [] if key == 'id_number' else None
            value, fail_reason = _ocr_template_crop(
                image, box, predicate, variants, config, field=key, collect=collect
            )
            if collect:
                id_readings.extend({'value': text, 'source': 'template'} for text in collect)
            if value:
                sources[key] = 'template'
            else:
                logger.info(
                    'template crop fallback triggered field=%s document_type=%s reason=%s',
                    key,
                    document_type,
                    fail_reason,
                )
        if not value:
            value, _ = extract_value_near_label(ocr_items, variants, predicate)
            if value:
                sources[key] = 'label_fallback'
        if not value:
            sources[key] = None
        raw[key] = value

    if 'id_number' in raw and any(key == 'id_number' for key, _, _ in FIELD_SPECS.get(document_type) or ()):
        page_value, _ = extract_value_near_label(ocr_items, LABELS['id_number'], _looks_like_id_value)
        if page_value:
            id_readings.append({'value': page_value, 'source': 'page_label'})
        for item in ocr_items:
            token = normalize_id_number(str(item.get('text', '')))
            if re.fullmatch(r'\d{7,10}', token):
                id_readings.append({'value': token, 'source': 'page'})
        if raw.get('id_number'):
            id_readings.insert(0, {'value': raw['id_number'], 'source': 'chosen'})
        raw['id_readings'] = id_readings

    has_labels = _document_has_field_labels(ocr_items)
    if document_type == DOCUMENT_ID_V2 and raw.get('surname') and not raw.get('given_names') and not has_labels:
        value = _line_below(ocr_items, raw['surname'], _looks_like_name_value)
        if value:
            logger.info('given names taken from the line under the surname value=%r', value)
            raw['given_names'] = value
            sources['given_names'] = 'below_surname'

    dob_expected = any(key == 'date_of_birth' for key, _, _ in FIELD_SPECS.get(document_type) or ())
    if dob_expected and not raw.get('date_of_birth') and not has_labels:
        value = _unlabelled_birth_date(ocr_items, raw.get('date_of_expiry'))
        if value:
            logger.info('date of birth taken from the only plausible unlabelled date value=%r', value)
            raw['date_of_birth'] = value
            sources['date_of_birth'] = 'unlabelled_date'

    return raw


def normalize_to_canonical(raw, document_type):
    dob = parse_document_date(raw.get('date_of_birth'))
    dob_ok, dob_reason = validate_dob(dob)
    if not dob_ok:
        logger.info('DOB rejected: %s value=%s', dob_reason, raw.get('date_of_birth'))
        dob = None

    expiry = parse_document_date(raw.get('date_of_expiry')) if raw.get('date_of_expiry') else None
    if document_type in TYPES_REQUIRING_EXPIRY:
        expiry_ok, expiry_reason = validate_expiry(expiry)
    else:
        expiry_ok, expiry_reason = True, None

    if document_type == DOCUMENT_PASSPORT:
        full_name = normalize_full_name(f"{raw.get('surname') or ''} {raw.get('given_names') or ''}")
        id_number = normalize_id_number(raw.get('passport_no') or '')
    elif document_type == DOCUMENT_ID_V1:
        full_name = normalize_full_name(raw.get('full_names') or '')
        id_number = normalize_id_number(raw.get('id_number') or '')
    elif document_type == DOCUMENT_ID_V2:
        full_name = normalize_full_name(f"{raw.get('surname') or ''} {raw.get('given_names') or ''}")
        id_number = normalize_id_number(raw.get('id_number') or '')
    elif document_type == DOCUMENT_DRIVERS_LICENCE:
        full_name = normalize_full_name(f"{raw.get('surname') or ''} {raw.get('other_names') or ''}")
        id_number = normalize_id_number(raw.get('id_number') or '')
    else:
        full_name = ''
        id_number = normalize_id_number(raw.get('id_number') or '')

    return {
        'full_name': full_name or None,
        'id_number': id_number or None,
        'document_type': document_type,
        'date_of_birth': dob,
        'date_of_expiry': expiry,
        'dob_valid': dob_ok,
        'dob_reject_reason': None if dob_ok else dob_reason,
        'expiry_valid': expiry_ok,
        'expiry_reject_reason': None if expiry_ok else expiry_reason,
    }


def compare_front_and_back(front_raw, back_raw):
    """
    ID number on the back must match the front (both ID versions). The back's
    number is often read out of the MRZ line with the check digit attached
    (KEN1156142547), so containment of the digits counts as agreement.
    """
    front_id = normalize_id_number(front_raw.get('id_number') or '')
    back_id = normalize_id_number(back_raw.get('id_number') or '')
    id_match = bool(front_id and back_id and (front_id == back_id or _ids_agree(back_id, front_id)))
    return {
        'id_match': id_match,
        'matched': id_match,
        'front_id_number': front_id or None,
        'back_id_number': back_id or None,
    }


def match_identity_fields(canonical, registered, name_threshold=NAME_MATCH_THRESHOLD):
    registered_name = registered.get('name') or registered.get('full_name') or ''
    registered_id = registered.get('idNumber') or registered.get('id_number') or ''
    registered_dob = registered.get('dateOfBirth') or registered.get('date_of_birth')

    extracted_name = canonical.get('full_name') or ''
    overlap = token_overlap_ratio(extracted_name, registered_name)
    coverage = registered_name_coverage(extracted_name, registered_name)
    lev_score = levenshtein_similarity(
        normalize_full_name(extracted_name),
        normalize_full_name(registered_name),
    )
    shared_tokens = set(name_tokens(extracted_name)) & set(name_tokens(registered_name))
    enough_tokens = len(shared_tokens) >= NAME_MIN_MATCHING_TOKENS
    # Retain the legacy threshold argument for callers, but a fractional
    # threshold must never allow an unmatched token in the shorter name.
    name_match = bool(
        enough_tokens and coverage == 1.0
    )

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
            'score': round(coverage, 4),
            'coverage': round(coverage, 4),
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
    confidence = float((coverage + (1.0 if id_match else 0.0) + (1.0 if dob_match else 0.0)) / 3.0)

    return {
        'field_matches': field_matches,
        'name_match': name_match,
        'id_match': id_match,
        'dob_match': dob_match,
        'matched': overall,
        'confidence_score': round(confidence, 4),
        'registered_dob_parse_failed': dob_parse_failed,
    }


def _reconcile_id_number(raw_fields, back_raw=None, mrz=None, sources=None):
    """
    Pick the ID number that most sources agree on. OCR confuses 1/7, 0/8,
    5/6 in a single pass; the same number is usually read several times
    (template crop in two preprocessings, the page text, the back of the card,
    the MRZ), and a digit that only one of them saw is the one to distrust.
    """
    readings = list(raw_fields.get('id_readings') or [])
    if raw_fields.get('id_number') and not readings:
        readings.append({'value': raw_fields['id_number'], 'source': 'chosen'})
    votes = {}
    order = []
    for reading in readings:
        value = normalize_id_number(reading.get('value') or '')
        if not value or len(re.sub(r'[^0-9]', '', value)) < 5:
            continue
        if value not in votes:
            votes[value] = 0.0
            order.append(value)
        # each front source votes once per distinct reading
        votes[value] += 1.0
    if not votes:
        return None

    back_number = normalize_id_number((back_raw or {}).get('id_number') or '')
    mrz_number = normalize_id_number((mrz or {}).get('document_number') or '') if mrz else ''
    mrz_weight = 3.0 if (mrz or {}).get('id_number_verified', True) else 2.0
    for value in votes:
        if mrz_number and value == mrz_number:
            votes[value] += mrz_weight  # 3 when check-digit verified, 2 when only read
        elif back_number and _ids_agree(back_number, value):
            votes[value] += 1.5

    current = normalize_id_number(raw_fields.get('id_number') or '')
    best = max(order, key=lambda v: (votes[v], v == current))
    if best != current:
        logger.info('ID number consensus changed %r -> %r votes=%s', current, best, votes)
        raw_fields.setdefault('printed', {})
        if current and 'id_number' not in raw_fields['printed']:
            raw_fields['printed']['id_number'] = current
        raw_fields['id_number'] = best
        if sources is not None:
            sources['id_number'] = 'consensus'
    raw_fields['id_votes'] = votes
    return best


def _ids_agree(printed, mrz_number):
    """Printed number vs MRZ number, tolerating stray OCR characters around the digits."""
    a = normalize_id_number(printed or '')
    b = normalize_id_number(mrz_number or '')
    if not a or not b:
        return False
    if a == b or b in a or (len(a) >= 7 and a in b):
        return True
    digits_a = re.sub(r'[^0-9]', '', a)
    return bool(digits_a) and (digits_a == b or b in digits_a)


def _fill_from_mrz(raw, mrz, document_type, sources):
    """
    Take identity fields from a check-digit-valid MRZ. The zone is printed in
    OCR-B specifically to be machine read, so it overrides what the decorative
    face of the card yielded; the printed values are kept under raw['printed'].
    """
    filled = []
    printed = raw.setdefault('printed', {})

    def put(key, value):
        if not value:
            return
        current = raw.get(key)
        if current and current not in (None, '') and key not in printed:
            printed[key] = current
        if current != value:
            raw[key] = value
            sources[key] = 'mrz'
            filled.append(key)

    full_names = mrz.get('full_names') or ' '.join(
        part for part in (mrz.get('surname'), mrz.get('given_names')) if part
    )
    if document_type in (DOCUMENT_ID_V2, DOCUMENT_PASSPORT):
        if mrz.get('surname') or mrz.get('given_names'):
            put('surname', mrz.get('surname'))
            put('given_names', mrz.get('given_names'))
        elif full_names:
            # zone read without its '<<' separator: the whole name still beats a
            # template crop that may have caught the bilingual labels
            put('surname', full_names)
            if raw.get('given_names'):
                printed.setdefault('given_names', raw['given_names'])
                raw['given_names'] = None
                sources['given_names'] = 'mrz'
                filled.append('given_names')
    elif document_type == DOCUMENT_ID_V1:
        put('full_names', full_names or None)
    elif document_type == DOCUMENT_DRIVERS_LICENCE:
        put('surname', mrz.get('surname') or full_names)
        put('other_names', mrz.get('given_names'))
    if mrz.get('date_of_birth'):
        put('date_of_birth', mrz['date_of_birth'].strftime('%d.%m.%Y'))
    if mrz.get('date_of_expiry'):
        put('date_of_expiry', mrz['date_of_expiry'].strftime('%d.%m.%Y'))
    number = mrz.get('document_number')
    key = 'passport_no' if document_type == DOCUMENT_PASSPORT else 'id_number'
    if mrz.get('id_number_verified', True):
        put(key, number)
    elif number and not raw.get(key):
        put(key, number)  # not check-digit protected: fill a gap, never override the printed number
    return filled


def _empty_result(extra=None):
    result = {
        'extractedName': None,
        'extractedIDNumber': None,
        'extractedDOB': None,
        'extractedExpiry': None,
        'nameMatch': False,
        'idMatch': False,
        'dobMatch': False,
        'frontBackMatch': None,
        'documentExpired': False,
        'confidenceScore': 0.0,
        'matched': False,
        'rawText': [],
        'documentType': None,
        'dateOfExpiry': None,
        'needsRetake': False,
        'needsManualReview': False,
        'rejectReason': None,
        'fieldMatches': [],
        'fieldExtractionSources': {},
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


def _attach_normalized_bboxes(items, image):
    """Add item['nbbox'] in 0..1 coordinates so positions survive the OCR upscale."""
    if image is None:
        return
    h, w = image.shape[:2]
    for item in items:
        box = item.get('bbox')
        if box and w and h:
            item['nbbox'] = [[float(p[0]) / w, float(p[1]) / h] for p in box]


PAGE_OCR_MIN_ITEMS = 4

# ICAO TD3 data page: 125 x 88 mm; the 44-character MRZ (2.54 mm pitch = 111.8 mm)
# sits about 6.6 mm from the left edge, and the bottom of its second line about
# 5.5 mm above the page's bottom edge. Ratios relative to the MRZ width:
PASSPORT_PAGE_WIDTH_PER_MRZ = 125.0 / 111.8
PASSPORT_LEFT_MARGIN_PER_MRZ = 6.6 / 111.8
PASSPORT_BOTTOM_MARGIN_PER_MRZ = 5.5 / 111.8
PASSPORT_HEIGHT_PER_WIDTH = 88.0 / 125.0
MRZ_SEARCH_MAX_SIDE = 1800


def _td3_line_candidates(items):
    """OCR items that look like the two 44-character passport MRZ lines."""
    from services.mrzService import _clean_line  # same normalisation the parser uses
    found = []
    for item in items:
        if not item.get('bbox'):
            continue
        cleaned = _clean_line(item.get('text', ''))
        if len(cleaned) < 30 or cleaned.count('<') < 3:
            continue
        found.append((item, cleaned))
    return found


def locate_passport_page(image):
    """
    Find the passport data page from its machine-readable zone rather than
    from page edges. An open passport shows two pages (and the detector may
    take either, or the whole spread); a tight crop has no edges at all. The
    MRZ is always at the bottom of the data page and spans its width, so its
    two lines fix the page rectangle regardless of what else is in the frame.
    Returns (quad in image pixels, mrz dict, mrz width px) or None.
    """
    h, w = image.shape[:2]
    scale = min(1.0, MRZ_SEARCH_MAX_SIDE / float(max(h, w)))
    small = cv2.resize(image, (int(round(w * scale)), int(round(h * scale))), interpolation=cv2.INTER_AREA) if scale < 1 else image
    items = extract_text_from_document(small, min_confidence=0.2)
    lines = _td3_line_candidates(items)
    if len(lines) < 2:
        return None
    lines.sort(key=lambda pair: min(float(p[1]) for p in pair[0]['bbox']))
    # the two lowest MRZ-looking lines, closest together, are the zone
    best = None
    for i in range(len(lines) - 1):
        (a, _), (b, _) = lines[i], lines[i + 1]
        ya = np.mean([p[1] for p in a['bbox']])
        yb = np.mean([p[1] for p in b['bbox']])
        ha = max(p[1] for p in a['bbox']) - min(p[1] for p in a['bbox'])
        if 0 < yb - ya < ha * 3.5:
            best = (lines[i], lines[i + 1])
    if best is None:
        return None
    (line1, text1), (line2, text2) = best
    mrz = parse_mrz([
        {'text': text1, 'confidence': 1.0, 'bbox': line1['bbox']},
        {'text': text2, 'confidence': 1.0, 'bbox': line2['bbox']},
    ])
    if not mrz or mrz.get('format') != 'TD3':
        return None

    b1 = np.array(line1['bbox'], dtype=np.float32)
    b2 = np.array(line2['bbox'], dtype=np.float32)
    # reading direction from line 1 (top-left -> top-right); page 'up' is its left normal
    direction = b1[1] - b1[0]
    direction /= max(float(np.linalg.norm(direction)), 1e-6)
    up = np.array([direction[1], -direction[0]], dtype=np.float32)
    if up[1] > 0:  # y grows downwards; 'up' must point to smaller y
        up = -up
    pts = np.vstack([b1, b2])
    along = pts @ direction
    across = pts @ up
    mrz_left, mrz_right = float(along.min()), float(along.max())
    mrz_bottom = float(across.min())  # smallest 'up' coordinate = lowest on the page
    mrz_width = mrz_right - mrz_left
    if mrz_width < 40:
        return None
    page_width = mrz_width * PASSPORT_PAGE_WIDTH_PER_MRZ
    page_height = page_width * PASSPORT_HEIGHT_PER_WIDTH
    left = mrz_left - mrz_width * PASSPORT_LEFT_MARGIN_PER_MRZ
    bottom = mrz_bottom - mrz_width * PASSPORT_BOTTOM_MARGIN_PER_MRZ
    right = left + page_width
    top = bottom + page_height

    def to_xy(a, c):
        return direction * a + up * c

    quad = np.array([to_xy(left, top), to_xy(right, top), to_xy(right, bottom), to_xy(left, bottom)], dtype=np.float32)
    quad /= scale
    logger.info('passport page located from MRZ: width %.0fpx valid=%s', page_width / scale, mrz.get('valid'))
    return quad, mrz, page_width / scale


def _passport_side_from_mrz(image, pre, config):
    """Rebuild the aligned side around the MRZ-located page. Returns (pre, results, mrz) or None."""
    located = locate_passport_page(image)
    if located is None:
        return None
    quad, mrz, width = located
    aligned = warp_quad(image, quad, config.get('output_size') or DEFAULT_OUTPUT_SIZE)
    new_pre = {
        **pre,
        'aligned_image': aligned,
        'image': aligned,
        'perspective_applied': True,
        'perspective_fallback': False,
        'document_quad': quad.astype(float).round(1).tolist(),
        'document_width_px': int(width),
        'low_resolution': width < 600,
        'located_by': 'mrz',
    }
    if config.get('debug') and pre.get('debug_dir'):
        path = os.path.join(pre['debug_dir'], '01c_passport_page_by_mrz.png')
        if cv2.imwrite(path, aligned):
            new_pre['debug_images'] = {**(pre.get('debug_images') or {}), '01c_passport_page_by_mrz': path}
    results = _read_page(new_pre)
    return new_pre, results, mrz


def _read_page(pre):
    """
    OCR one side. EasyOCR is a neural reader and does best on the natural,
    rectified colour image; the binarised pipeline output turns a card's
    guilloche security print into black lines that swallow the text. The
    binarised image is only tried when the natural read comes back near-empty
    (very low contrast scans), and the stronger of the two is kept.
    """
    natural = pre.get('aligned_image')
    if natural is None:
        natural = pre['image']
    items = extract_text_from_document(natural)
    _attach_normalized_bboxes(items, natural)
    if len(items) >= PAGE_OCR_MIN_ITEMS or pre.get('image') is None or pre['image'] is natural:
        return items
    fallback = extract_text_from_document(pre['image'])
    _attach_normalized_bboxes(fallback, pre['image'])
    if _ocr_strength(fallback) > _ocr_strength(items):
        logger.info('page OCR: binarised fallback read better (%d vs %d items)', len(fallback), len(items))
        return fallback
    return items


def _ocr_strength(items):
    """How much readable text a pass produced: sum of confidences."""
    return sum(float(item.get('confidence') or 0) for item in items)


def _rotate_pre(pre, rotate_code):
    """Rotate the preprocessed + aligned images together (all later steps are rotation-invariant)."""
    rotated = dict(pre)
    rotated['image'] = cv2.rotate(pre['image'], rotate_code)
    if pre.get('aligned_image') is not None:
        rotated['aligned_image'] = cv2.rotate(pre['aligned_image'], rotate_code)
    return rotated


DOCUMENT_MIN_WIDTH_PX = 400
TOO_SMALL_MESSAGE = (
    'The document is too small in the photo. Move the camera closer so the card fills most of the frame.'
)
NOT_FOUND_MESSAGE = (
    'We could not find a readable document in the photo. Place it on a plain, dark surface, '
    'fill the frame with it, and avoid glare.'
)


def _retake_result(pre, message, forced_type=None):
    return {
        'ok': False,
        'needs_retake': True,
        'message': message,
        'pre': pre,
        'document_type': forced_type,
        'raw_text': [],
        'raw': {},
        'sources': {},
        'canonical': None,
    }


def _extract_fields_for(side, document_type, config, template=None, forced_type=None):
    """(Re)run field extraction on an already OCR'd side for a given document type."""
    pre = side['pre']
    text_results = side.get('text_results') or []
    sources = {}
    aligned = pre.get('aligned_image')
    if aligned is None:
        aligned = pre['image']
    raw = extract_raw_fields(
        text_results,
        document_type,
        image=aligned,
        # preprocess_document works on a copy of config, so carry its debug dir over
        config={**config, 'debug_dir': pre.get('debug_dir'), 'debug_side': 'back' if forced_type else 'front'},
        template=template,
        sources=sources,
    )
    side['document_type'] = document_type
    side['raw'] = raw
    side['sources'] = sources
    side['canonical'] = normalize_to_canonical(raw, document_type)
    return side


def _looks_like_passport(text_results):
    blob = ' '.join(str(item.get('text', '')) for item in text_results).upper()
    return 'PASSPORT' in blob or 'PASSEPORT' in blob or 'P<' in blob.replace(' ', '')


def _preprocess_passport_by_mrz(image, config):
    """
    Passport first pass: find the data page from its MRZ on the full frame and
    preprocess that page directly, bypassing edge detection entirely (an open
    booklet offers the facing page, the spine and the table as decoys).
    Returns (pre, page_mrz) or None when no MRZ was found.
    """
    located = locate_passport_page(image)
    if located is None:
        return None
    quad, page_mrz, width = located
    aligned = warp_quad(image, quad, config.get('output_size') or DEFAULT_OUTPUT_SIZE)
    pre = preprocess_document(aligned, {**config, 'perspective': False})
    pre.update({
        'perspective_applied': True,
        'perspective_fallback': False,
        'document_quad': quad.astype(float).round(1).tolist(),
        'document_width_px': int(width),
        'low_resolution': width < 600,
        'located_by': 'mrz',
    })
    if config.get('debug') and pre.get('debug_dir'):
        path = os.path.join(pre['debug_dir'], '01_01_quad_overlay.png')
        if cv2.imwrite(path, draw_quad_overlay(image, quad, colour=(255, 0, 255))):
            pre['debug_images'] = {**(pre.get('debug_images') or {}), '01_quad_overlay_mrz': path}
    return pre, page_mrz


def _extract_side(image, config, forced_type=None, template=None, document_kind=None):
    """Preprocess one image, OCR it, and extract fields for a document type."""
    pre = None
    page_mrz = None
    if forced_type is None and document_kind == 'passport':
        located = _preprocess_passport_by_mrz(image, config)
        if located is not None:
            pre, page_mrz = located
            logger.info('passport page located from MRZ before edge detection (width %spx)', pre.get('document_width_px'))

    if pre is None:
        pre = preprocess_document(image, config)

    # A wrong region (a floor tile, the facing page) must not veto a good photo:
    # if the region found by edge detection fails the blur or size checks, judge
    # the whole frame instead and carry on un-warped.
    region_rejected = (not pre.get('ok')) or (
        pre.get('document_width_px') and pre['document_width_px'] < DOCUMENT_MIN_WIDTH_PX
    )
    if region_rejected and pre.get('perspective_applied') and not pre.get('located_by'):
        plain = preprocess_document(image, {**config, 'perspective': False, 'debug': False})
        if plain.get('ok'):
            logger.info('edge-detected region rejected (%s); continuing with the full frame',
                        'blur' if not pre.get('ok') else 'too small')
            plain['perspective_fallback'] = True
            plain['quad_too_small'] = bool(pre.get('ok'))
            plain['debug_dir'] = pre.get('debug_dir')
            plain['debug_images'] = pre.get('debug_images') or {}
            pre = plain

    if not pre.get('ok'):
        return _retake_result(pre, pre.get('message') or 'Image is too blurry. Please retake.', forced_type)
    width_px = pre.get('document_width_px')
    if width_px and width_px < DOCUMENT_MIN_WIDTH_PX and not pre.get('perspective_fallback'):
        logger.info('document too small for OCR width=%dpx', width_px)
        return _retake_result(pre, TOO_SMALL_MESSAGE, forced_type)

    text_results = _read_page(pre)
    document_type = forced_type or detect_document_type(text_results)
    orientation = 0
    if page_mrz is not None and document_type is None:
        document_type = DOCUMENT_PASSPORT

    # Passports: anchor the page on its MRZ instead of trusting page edges
    # (an open booklet shows two pages; a tight crop shows no edges at all).
    if forced_type is None and pre.get('located_by') != 'mrz' and (
        document_kind == 'passport' or document_type == DOCUMENT_PASSPORT or _looks_like_passport(text_results)
    ):
        first_mrz = parse_mrz(text_results)
        if not (first_mrz and first_mrz.get('format') == 'TD3' and first_mrz.get('valid')):
            relocated = _passport_side_from_mrz(image, pre, config)
            if relocated is not None:
                new_pre, new_results, page_mrz = relocated
                if page_mrz.get('valid') or _ocr_strength(new_results) >= _ocr_strength(text_results) * 0.8:
                    pre, text_results = new_pre, new_results
                    document_type = DOCUMENT_PASSPORT
                    logger.info('passport side rebuilt around MRZ (%d items)', len(text_results))
        elif document_type is None:
            document_type = DOCUMENT_PASSPORT

    # The perspective warp puts the long side horizontal but cannot tell a card
    # from its 180-degree flip (phone held upside down, or a portrait shot that
    # landed the wrong way round). Try the flip when the first pass reads badly.
    if pre.get('perspective_applied'):
        weak = (document_type is None) if not forced_type else (
            len(text_results) < 3 or _ocr_strength(text_results) < 1.5
        )
        if weak:
            flipped_pre = _rotate_pre(pre, cv2.ROTATE_180)
            flipped_results = _read_page(flipped_pre)
            flipped_type = forced_type or detect_document_type(flipped_results)
            better = (
                (flipped_type is not None and document_type is None)
                or (bool(flipped_type) == bool(document_type)
                    and _ocr_strength(flipped_results) > _ocr_strength(text_results) * 1.2)
            )
            if better:
                logger.info('orientation retry: 180 flip reads better (%d vs %d items)',
                            len(flipped_results), len(text_results))
                pre, text_results, document_type, orientation = flipped_pre, flipped_results, flipped_type, 180
                if config.get('debug') and pre.get('debug_dir'):
                    path = os.path.join(pre['debug_dir'], '01b_orientation_180.png')
                    if cv2.imwrite(path, pre['aligned_image']):
                        pre['debug_images'] = {**(pre.get('debug_images') or {}), '01b_orientation_180': path}

    # Safety net: a confidently detected rectangle that is not the card (laptop,
    # sheet of paper) warps to garbage. If no known document is recognised on the
    # warped image, read the original frame instead.
    if pre.get('perspective_applied') and not forced_type and document_type is None:
        plain = preprocess_document(image, {**config, 'perspective': False, 'debug': False})
        if plain.get('ok'):
            plain_results = _read_page(plain)
            plain_type = detect_document_type(plain_results)
            if plain_type:
                logger.info('perspective fallback: document only recognised on un-warped image')
                plain['perspective_fallback'] = True
                plain['debug_dir'] = pre.get('debug_dir')
                plain['debug_images'] = pre.get('debug_images') or {}
                pre, text_results, document_type, orientation = plain, plain_results, plain_type, 0

    sources = {}
    raw = {}
    canonical = None
    mrz = parse_mrz(text_results)
    if page_mrz:
        # the full-frame read and the rectified-page read each miss different
        # things (a line skipped here, a digit misread there): combine them
        mrz = merge_mrz(mrz, page_mrz) if mrz else page_mrz
    if document_type:
        aligned = pre.get('aligned_image')
        if aligned is None:
            aligned = pre['image']
        raw = extract_raw_fields(
            text_results,
            document_type,
            image=aligned,
            # preprocess_document works on a copy of config, so carry its debug dir over
            config={**config, 'debug_dir': pre.get('debug_dir'), 'debug_side': 'back' if forced_type else 'front'},
            template=template,
            sources=sources,
        )
        if mrz and mrz.get('valid') and document_type == DOCUMENT_ID_BACK and mrz.get('document_number'):
            # the check-digit-verified MRZ beats a template crop of the printed number
            raw['id_number'] = mrz['document_number']
            sources['id_number'] = 'mrz'
        canonical = normalize_to_canonical(raw, document_type)

    return {
        'ok': True,
        'needs_retake': False,
        'message': None,
        'pre': pre,
        'document_type': document_type,
        'orientation': orientation,
        'mrz': mrz,
        'raw_text': [item['text'] for item in text_results],
        'raw': raw,
        'sources': sources,
        'canonical': canonical,
        'text_results': text_results,
    }


def assess_document_ocr(
    image,
    registered_details,
    debug=False,
    preprocess_config=None,
    name_threshold=None,
    back_image=None,
    document_kind=None,
):
    """
    Full OCR pipeline: preprocess → OCR → detect type → extract → match.
    Optional back_image is required for national ID front/back ID-number matching.
    """
    config = merge_preprocess_config(preprocess_config)
    config['debug'] = bool(debug or config.get('debug'))
    threshold = NAME_MATCH_THRESHOLD if name_threshold is None else float(name_threshold)

    try:
        front = _extract_side(image, config, document_kind=document_kind)
    except Exception:
        logger.exception('OCR failed assumed_document_type=unknown/not-yet-detected')
        return _empty_result({
            'needsManualReview': True,
            'rejectReason': 'OCR failed while reading the document. Flagged for manual review.',
        })

    pre = front['pre']
    extra_meta = {
        'blurScore': pre.get('blur_score'),
        'preprocessSteps': pre.get('steps_run') or [],
        'debugDir': pre.get('debug_dir') if config.get('debug') else None,
        'debugImages': pre.get('debug_images') if config.get('debug') else {},
        'rawText': front.get('raw_text') or [],
        'fieldExtractionSources': front.get('sources') or {},
        'perspectiveApplied': bool(pre.get('perspective_applied')) and not pre.get('perspective_fallback'),
        'documentQuad': pre.get('document_quad'),
        'documentWidthPx': pre.get('document_width_px'),
        'lowResolution': bool(pre.get('low_resolution')),
        'orientation': front.get('orientation') or 0,
    }

    if not front['ok']:
        return _empty_result({
            **extra_meta,
            'needsRetake': True,
            'rejectReason': front.get('message') or 'Image is too blurry. Please retake.',
            'debugDir': pre.get('debug_dir'),
            'debugImages': pre.get('debug_images') or {},
        })

    document_type = front['document_type']
    back = None
    if not document_type and back_image is not None:
        # The front's title line was unreadable; the back settles it: only the
        # new-generation national ID carries a machine-readable zone.
        try:
            back = _extract_side(back_image, config, forced_type=DOCUMENT_ID_BACK,
                                 template=back_template_for(DOCUMENT_ID_V2))
        except Exception:
            logger.exception('ID back OCR failed while resolving document type')
            back = None
        if back and back.get('ok') and back.get('mrz'):
            logger.info('document type taken from back MRZ: %s', DOCUMENT_ID_V2)
            document_type = DOCUMENT_ID_V2
            front = _extract_fields_for(front, document_type, config)
            extra_meta['fieldExtractionSources'] = front.get('sources') or {}
            extra_meta['documentTypeSource'] = 'back_mrz'
        else:
            back = None

    if not document_type:
        logger.info('document type detection failed raw_text=%s', front.get('raw_text'))
        if len(front.get('raw_text') or []) < 6:
            # almost nothing was read: the document was not really in the shot
            return _empty_result({
                **extra_meta,
                'needsRetake': True,
                'rejectReason': NOT_FOUND_MESSAGE,
            })
        return _empty_result({
            **extra_meta,
            'needsManualReview': True,
            'rejectReason': 'Could not match a known document template. Flagged for manual review.',
        })

    raw_fields = front['raw']
    sources = front.get('sources') or {}
    missing = []
    extraction_incomplete = False

    front_back = None
    back_raw = None
    if document_type in ID_FRONT_TYPES:
        if back_image is None:
            extraction_incomplete = True
            missing.append('id_back')
        else:
            try:
                if back is None:
                    back = _extract_side(
                        back_image,
                        config,
                        forced_type=DOCUMENT_ID_BACK,
                        template=back_template_for(document_type),
                    )
            except Exception:
                logger.exception('ID back OCR failed')
                back = {
                    'ok': False,
                    'needs_retake': False,
                    'message': 'OCR failed while reading the ID back.',
                    'raw': {},
                    'pre': {},
                }
            extra_meta['backRawText'] = back.get('raw_text') or []
            extra_meta['backFieldExtractionSources'] = back.get('sources') or {}
            if back.get('needs_retake'):
                return _empty_result({
                    **extra_meta,
                    'documentType': document_type,
                    'needsRetake': True,
                    'rejectReason': back.get('message') or 'The back of the ID is too blurry. Please retake.',
                })
            if not back.get('ok'):
                extraction_incomplete = True
                missing.append('id_back')
            else:
                back_missing = missing_required_fields(back.get('raw') or {}, DOCUMENT_ID_BACK)
                if back_missing:
                    extraction_incomplete = True
                    missing.extend(f'back_{key}' for key in back_missing)
                back_raw = back.get('raw') or {}
                front_back = compare_front_and_back(raw_fields, back_raw)
                extra_meta['frontBackComparison'] = front_back

    # The MRZ (back of the new-gen ID, or the passport data page itself) is
    # check-digit verified: use it for anything the printed face failed to give.
    mrz = (back or {}).get('mrz') if back else None
    if not (mrz and mrz.get('valid')):
        mrz = front.get('mrz') if front.get('mrz') and front['mrz'].get('valid') else None

    # Several independent readings of the ID number: let them vote before matching
    _reconcile_id_number(raw_fields, back_raw, mrz, sources)
    if front_back is not None:
        front_back = compare_front_and_back(raw_fields, back_raw or {})
        extra_meta['frontBackComparison'] = front_back

    if mrz:
        filled = _fill_from_mrz(raw_fields, mrz, document_type, sources)
        if filled:
            logger.info('fields filled from MRZ: %s', filled)
            extra_meta['fieldExtractionSources'] = sources
        extra_meta['mrz'] = {
            'format': mrz.get('format'),
            'documentNumber': mrz.get('document_number'),
            'dateOfBirth': mrz['date_of_birth'].isoformat() if mrz.get('date_of_birth') else None,
            'dateOfExpiry': mrz['date_of_expiry'].isoformat() if mrz.get('date_of_expiry') else None,
            'surname': mrz.get('surname'),
            'givenNames': mrz.get('given_names'),
            'checks': mrz.get('checks'),
        }
        if document_type in ID_FRONT_TYPES and back is not None and back.get('ok') and mrz.get('document_number'):
            # front/back consistency: the number printed on the front must agree
            # with the check-digit-verified number in the back's MRZ (when the
            # MRZ number line was not read, the printed-back comparison above stands)
            # any of the front's readings agreeing with the MRZ number is consistency
            # enough: a single OCR pass may misread one digit, a swapped card never agrees
            printed_front = (raw_fields.get('printed') or {}).get('id_number') or raw_fields.get('id_number')
            front_readings = [printed_front, raw_fields.get('id_number')] + [
                reading.get('value') for reading in (raw_fields.get('id_readings') or [])
            ]
            agree = any(_ids_agree(value, mrz.get('document_number')) for value in front_readings if value)
            front_back = {
                'id_match': agree,
                'matched': agree,
                'front_id_number': normalize_id_number(raw_fields.get('id_number') or '') or None,
                'back_id_number': mrz.get('document_number'),
                'source': 'mrz',
            }
            extra_meta['frontBackComparison'] = front_back

    canonical = normalize_to_canonical(raw_fields, document_type)
    try:
        comparison = match_identity_fields(canonical, registered_details or {}, name_threshold=threshold)
    except Exception:
        logger.exception('field extraction/matching failed assumed_document_type=%s', document_type)
        return _empty_result({
            **extra_meta,
            'documentType': document_type,
            'needsManualReview': True,
            'rejectReason': f'Failed to extract fields from {document_type}. Flagged for manual review.',
        })

    missing = missing_required_fields(raw_fields, document_type) + missing
    required = REQUIRED_FIELDS.get(document_type) or ()
    if 'date_of_birth' in required and not canonical.get('date_of_birth') and 'date_of_birth' not in missing:
        missing.append('date_of_birth')
    if 'date_of_expiry' in required and not canonical.get('date_of_expiry') and 'date_of_expiry' not in missing:
        missing.append('date_of_expiry')

    dob_invalid = canonical.get('dob_valid') is False
    # only a date that was actually read and lies in the past counts as expired;
    # an unreadable expiry is a missing field (review/retake), not a hard reject
    expired = (
        canonical.get('expiry_valid') is False
        and canonical.get('date_of_expiry') is not None
        and document_type in TYPES_REQUIRING_EXPIRY
    )
    parse_failed = comparison.get('registered_dob_parse_failed') or (
        canonical.get('date_of_birth') is None and bool(raw_fields.get('date_of_birth'))
    )
    extraction_incomplete = extraction_incomplete or bool(missing)

    # The card was never actually located (no quad, or the warp was rejected
    # and the full frame was read) and fields are still missing even after the
    # MRZ: the document was not properly in the shot. Ask for a better photo
    # instead of sending garbage to manual review.
    located = bool(pre.get('perspective_applied')) and not pre.get('perspective_fallback')
    field_missing = [m for m in missing if m != 'id_back']
    if field_missing and not located:
        logger.info('document not located and fields missing=%s -> retake', field_missing)
        return _empty_result({
            **extra_meta,
            'documentType': document_type,
            'needsRetake': True,
            'rejectReason': TOO_SMALL_MESSAGE if pre.get('quad_too_small') else NOT_FOUND_MESSAGE,
        })

    front_back_ok = True if front_back is None else bool(front_back.get('matched'))
    needs_review = bool(
        dob_invalid or parse_failed or extraction_incomplete or expired or not front_back_ok
    )
    matched = bool(comparison['matched']) and not extraction_incomplete and not expired and front_back_ok
    confidence = 0.0 if (expired or not front_back_ok) else comparison['confidence_score']

    reject_reason = None
    if expired:
        reject_reason = canonical.get('expiry_reject_reason') or 'Document has expired'
        logger.info('expired document rejected document_type=%s expiry=%s', document_type, raw_fields.get('date_of_expiry'))
    elif not front_back_ok:
        reject_reason = 'ID number on the back does not match the front'
        logger.info('front/back mismatch comparison=%s', front_back)
    elif extraction_incomplete:
        reject_reason = (
            'Required fields could not be extracted after template crop and label fallback: '
            + ', '.join(missing)
        )
        logger.info(
            'document flagged for manual review document_type=%s missing=%s sources=%s',
            document_type,
            missing,
            front.get('sources'),
        )
    elif dob_invalid:
        reject_reason = canonical.get('dob_reject_reason')

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
        'frontBackMatch': None if front_back is None else bool(front_back.get('matched')),
        'documentExpired': bool(expired),
        'confidenceScore': confidence,
        'matched': matched,
        'rawText': extra_meta['rawText'],
        'documentType': document_type,
        'dateOfExpiry': format_document_date(canonical.get('date_of_expiry')),
        'needsRetake': False,
        'needsManualReview': bool(needs_review),
        'rejectReason': reject_reason,
        'fieldMatches': comparison['field_matches'],
        'canonical': canonical_public,
        'rawFields': raw_fields,
        'backRawFields': back_raw,
        **extra_meta,
    }
