"""
Machine Readable Zone (MRZ) parsing for identity documents.

The new-generation national ID carries a TD1 zone (3 lines x 30 chars) on the
back; a passport data page carries a TD3 zone (2 lines x 44 chars). Both encode
document number, date of birth, sex, expiry, nationality and the holder's name
in OCR-B with check digits, so they are the most reliable source of exactly the
fields the printed face of the card makes hard to read.
"""
import logging
import re
from datetime import date

logger = logging.getLogger(__name__)

TD1_LINE_LENGTH = 30
TD3_LINE_LENGTH = 44
MRZ_LINE_PATTERN = re.compile(r'^[A-Z0-9<]{20,50}$')

# OCR confusions in the two directions the MRZ allows us to disambiguate
_TO_DIGIT = str.maketrans({'O': '0', 'Q': '0', 'D': '0', 'I': '1', 'L': '1', 'Z': '2', 'S': '5', 'B': '8', 'G': '6'})
_TO_ALPHA = str.maketrans({'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B', '6': 'G'})


def _char_value(ch):
    if ch.isdigit():
        return int(ch)
    if 'A' <= ch <= 'Z':
        return ord(ch) - ord('A') + 10
    return 0  # '<'


def check_digit(field):
    weights = (7, 3, 1)
    total = sum(_char_value(ch) * weights[i % 3] for i, ch in enumerate(field))
    return str(total % 10)


def _check_ok(field, digit):
    digit = digit.translate(_TO_DIGIT)
    return digit.isdigit() and check_digit(field) == digit


def _resolve_document_number(field, digit):
    """
    Document numbers may be alphanumeric, so try the field as read first; if
    the check digit fails, retry with letter->digit confusions fixed (I->1,
    O->0, S->5 ...), which is what a numeric national ID number needs.
    """
    raw = field
    if _check_ok(raw, digit):
        return raw.rstrip('<'), True
    fixed = _digits(field)
    if fixed != raw and _check_ok(fixed, digit):
        return fixed.rstrip('<'), True
    return raw.rstrip('<'), False


def _clean_line(text):
    text = str(text or '').upper()
    text = re.sub(r'[^A-Z0-9<]', '', text.replace(' ', ''))
    # OCR often renders the filler '<' as 'K', '(' etc.; runs of 2+ 'K' between letters are fillers
    return text


def _pad(line, length):
    return (line + '<' * length)[:length]


def _digits(field):
    return field.translate(_TO_DIGIT)


def _alpha(field):
    return field.translate(_TO_ALPHA)


def _parse_yymmdd(field, is_expiry=False):
    field = _digits(field)
    if not re.fullmatch(r'\d{6}', field):
        return None
    yy, mm, dd = int(field[:2]), int(field[2:4]), int(field[4:6])
    today = date.today()
    if is_expiry:
        year = 2000 + yy
    else:
        year = 2000 + yy
        if year > today.year:
            year -= 100
    try:
        return date(year, mm, dd)
    except ValueError:
        return None


def _parse_names(field):
    """
    Returns (surname, given_names, full_names). Standard zones separate the
    surname with '<<'; the old Kenyan ID prints the full name with single
    fillers only, in which case surname/given are None and full_names is set.
    """
    field = _alpha(field).strip('<')
    if '<<' in field:
        surname, given = field.split('<<', 1)
        surname = ' '.join(part for part in surname.split('<') if part)
        given = ' '.join(part for part in given.split('<') if part)
        full = ' '.join(part for part in (surname, given) if part)
        return surname or None, given or None, full or None
    full = ' '.join(part for part in field.split('<') if part)
    return None, None, full or None


def _candidate_lines(ocr_items):
    """OCR lines that look like MRZ text, top to bottom."""
    rows = []
    for item in ocr_items:
        cleaned = _clean_line(item.get('text', ''))
        if len(cleaned) < 20:
            continue
        # an MRZ line has fillers or is dense alphanumerics with no spaces
        if '<' not in cleaned and not re.fullmatch(r'[A-Z0-9]{28,44}', cleaned):
            continue
        if not MRZ_LINE_PATTERN.match(cleaned):
            continue
        bbox = item.get('bbox')
        y = min(float(p[1]) for p in bbox) if bbox else len(rows)
        rows.append((y, cleaned))
    rows.sort(key=lambda r: r[0])
    return [text for _, text in rows]


_TD1_L2_SHAPE = re.compile(r'^\d{7}[MF0<]\d{7}[A-Z0-9<]{3}')
_TD1_L1_SHAPE = re.compile(r'^[IAC][A-Z0-9<][A-Z0-9]{3}')


def _classify_td1_line(line):
    """
    Which TD1 row a line is, judged by its shape rather than its position:
    row 2 is dates and sex, row 1 starts with a document code and carries the
    number (digits), row 3 is names only (no digits, '<<' between the parts).
    """
    if _TD1_L2_SHAPE.match(_digits(line[:15]) + _alpha(line[15:18])):
        return 'L2'
    digits_in_number = sum(ch.isdigit() for ch in _digits(line[5:15]))
    if _TD1_L1_SHAPE.match(line) and digits_in_number >= 4:
        return 'L1'
    if '<<' in line and sum(ch.isdigit() for ch in line) <= 2:
        return 'L3'
    return None


def _assemble_td1(lines):
    """Pick line 1/2/3 out of whatever MRZ-looking lines the OCR returned (line 2 is mandatory)."""
    rows = {'L1': None, 'L2': None, 'L3': None}
    for line in lines:
        kind = _classify_td1_line(line)
        if kind and rows[kind] is None:
            rows[kind] = line
    if rows['L2'] is None:
        return None
    return [rows['L1'], rows['L2'], rows['L3']]


def _parse_td1(lines):
    # lines may be missing: [l1 or None, l2, l3 or None]
    l1 = _pad(lines[0], TD1_LINE_LENGTH) if lines[0] else None
    l2 = _pad(lines[1], TD1_LINE_LENGTH)
    l3 = _pad(lines[2], TD1_LINE_LENGTH) if lines[2] else '<' * TD1_LINE_LENGTH
    doc_number = l1[5:14] if l1 else ''
    doc_check = l1[14] if l1 else ''
    dob_field, dob_check = l2[0:6], l2[6]
    sex = _alpha(l2[7])
    exp_field, exp_check = l2[8:14], l2[14]
    nationality = _alpha(l2[15:18])
    surname, given, full_names = _parse_names(l3)

    if l1:
        doc_number_clean, doc_ok = _resolve_document_number(doc_number, doc_check)
    else:
        doc_number_clean, doc_ok = None, None  # line 1 not read: number unknown, not wrong
    checks = {
        'document_number': doc_ok,
        'date_of_birth': _check_ok(_digits(dob_field), dob_check),
        'date_of_expiry': _check_ok(_digits(exp_field), exp_check),
    }
    result = {
        'format': 'TD1',
        'variant': 'standard',
        'document_code': _alpha(l1[0:2]) if l1 else None,
        'issuing_country': _alpha(l1[2:5]) if l1 else None,
        'document_number': doc_number_clean or None,
        'id_number_verified': bool(doc_ok),
        'serial_number': None,
        'date_of_birth': _parse_yymmdd(dob_field),
        'sex': sex if sex in ('M', 'F') else None,
        'date_of_expiry': _parse_yymmdd(exp_field, is_expiry=True),
        'date_of_issue': None,
        'nationality': nationality,
        'surname': surname,
        'given_names': given,
        'full_names': full_names,
        'checks': checks,
        'lines': [l1 or '', l2, l3],
    }

    # Old-format Kenyan ID (issuer 'KYA', nationality slot not a country code):
    # line 1 holds the card SERIAL, the expiry slot holds the date of ISSUE, and
    # the ID number is the digit run in line 2's optional field. Its check
    # digits cover the serial and the dates, not the ID number itself.
    old_kenyan = (result['issuing_country'] == 'KYA') or not re.fullmatch(r'[A-Z]{3}', nationality or '')
    optional = _digits(l2[18:29])
    id_match = re.match(r'\d{6,10}', optional)
    if old_kenyan and id_match:
        result['variant'] = 'kenya_old'
        result['serial_number'] = doc_number_clean
        result['document_number'] = id_match.group(0)
        result['id_number_verified'] = False
        result['date_of_issue'] = result['date_of_expiry']
        result['date_of_expiry'] = None
    return result


_TD3_L2_SHAPE = re.compile(r'^[A-Z0-9<]{9}\d[A-Z<]{3}\d{7}[MF<]\d{7}')


def _is_td3_line2(line):
    padded = _pad(line, TD3_LINE_LENGTH)
    shaped = padded[:9] + _digits(padded[9]) + _alpha(padded[10:13]) + _digits(padded[13:20]) + _alpha(padded[20]) + _digits(padded[21:28])
    return bool(_TD3_L2_SHAPE.match(shaped))


def _is_td3_line1(line):
    """Names line: starts with a document code, has fillers, carries no digits."""
    if sum(ch.isdigit() for ch in line) > 2:
        return False
    return line.count('<') >= 3 and bool(re.match(r'^[A-Z][A-Z<]', line))


def _parse_td3(lines):
    l1 = _pad(lines[0], TD3_LINE_LENGTH) if lines[0] else None
    l2 = _pad(lines[1], TD3_LINE_LENGTH)
    surname, given, full_names = _parse_names(l1[5:44]) if l1 else (None, None, None)
    doc_number = l2[0:9]
    doc_check = l2[9]
    nationality = _alpha(l2[10:13])
    dob_field, dob_check = l2[13:19], l2[19]
    sex = _alpha(l2[20])
    exp_field, exp_check = l2[21:27], l2[27]
    doc_number_clean, doc_ok = _resolve_document_number(doc_number, doc_check)
    checks = {
        'document_number': doc_ok,
        'date_of_birth': _check_ok(_digits(dob_field), dob_check),
        'date_of_expiry': _check_ok(_digits(exp_field), exp_check),
    }
    return {
        'format': 'TD3',
        'variant': 'standard',
        'document_code': _alpha(l1[0:2]) if l1 else None,
        'issuing_country': _alpha(l1[2:5]) if l1 else None,
        'document_number': doc_number_clean or None,
        'id_number_verified': bool(doc_ok),
        'serial_number': None,
        'date_of_birth': _parse_yymmdd(dob_field),
        'sex': sex if sex in ('M', 'F') else None,
        'date_of_expiry': _parse_yymmdd(exp_field, is_expiry=True),
        'date_of_issue': None,
        'nationality': nationality,
        'surname': surname,
        'given_names': given,
        'full_names': full_names,
        'checks': checks,
        'lines': [l1 or '', l2],
    }


def merge_mrz(primary, secondary):
    """
    Combine two reads of the same zone (e.g. full frame and rectified page):
    each field comes from the read whose check digit verified it, or from
    whichever read has it. Names have no check digit, so they come from the
    read that has them at all, primary first.
    """
    if not primary:
        return secondary
    if not secondary:
        return primary
    merged = dict(primary)
    merged['checks'] = dict(primary.get('checks') or {})
    for field, key in (('document_number', 'document_number'), ('date_of_birth', 'date_of_birth'), ('date_of_expiry', 'date_of_expiry')):
        p_ok = (primary.get('checks') or {}).get(key)
        s_ok = (secondary.get('checks') or {}).get(key)
        if not p_ok and s_ok:
            merged[field] = secondary.get(field)
            merged['checks'][key] = True
            if key == 'document_number':
                merged['id_number_verified'] = secondary.get('id_number_verified', True)
    for field in ('surname', 'given_names', 'full_names', 'serial_number', 'date_of_issue', 'sex', 'nationality'):
        if not merged.get(field) and secondary.get(field):
            merged[field] = secondary[field]
    checks = merged['checks']
    merged['valid'] = bool(
        checks.get('document_number') is not False and checks.get('date_of_birth') and checks.get('date_of_expiry')
    )
    merged['checks_passed'] = sum(1 for ok in checks.values() if ok)
    return merged


def parse_mrz(ocr_items):
    """
    Find and parse an MRZ among OCR lines. Returns None when no zone is present.
    The result carries per-field check-digit outcomes; `valid` is True when the
    document number, birth date and expiry all verify.
    """
    lines = _candidate_lines(ocr_items)
    if not lines:
        return None

    parsed = None
    # TD1: up to three ~30-char lines; any of them may have been missed by the
    # OCR, so rows are recognised by shape. Line 2 (dates) is required.
    td1_lines = [line for line in lines if 22 <= len(line) <= 34]
    assembled = _assemble_td1(td1_lines)
    if assembled is not None:
        candidate = _parse_td1(assembled)
        if candidate['checks']['date_of_birth'] or candidate['checks']['date_of_expiry']:
            parsed = candidate
    # TD3: line 2 is recognised by shape (number, check, country, dates, sex);
    # line 1 is the names line just above it and must look like one (fillers,
    # no digits) - a long bilingual label must never be taken for it.
    if parsed is None:
        td3_lines = [line for line in lines if 36 <= len(line) <= 48]
        for i, line in enumerate(td3_lines):
            if not _is_td3_line2(line):
                continue
            line1 = td3_lines[i - 1] if i > 0 and _is_td3_line1(td3_lines[i - 1]) else None
            candidate = _parse_td3([line1, line])
            if candidate['date_of_birth'] or candidate['checks']['document_number']:
                parsed = candidate
                break
    if parsed is None:
        return None

    checks = parsed['checks']
    # valid = every field we did read verifies; an unread number line is not a failure
    parsed['valid'] = bool(
        checks['document_number'] is not False and checks['date_of_birth'] and checks['date_of_expiry']
    )
    parsed['checks_passed'] = sum(1 for ok in checks.values() if ok)
    logger.info(
        'MRZ parsed format=%s doc=%s dob=%s expiry=%s checks=%s',
        parsed['format'], parsed['document_number'], parsed['date_of_birth'],
        parsed['date_of_expiry'], checks,
    )
    return parsed
