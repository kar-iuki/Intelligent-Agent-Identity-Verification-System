import logging
import os
from datetime import datetime

import cv2
import numpy as np

from services.imageQualityService import DOCUMENT_BLUR_THRESHOLD, compute_blur_score

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_SIZE = (1000, 630)
# below this many pixels across the card, small print (da321w3eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeetes, ID digits) is unreliable for OCR
LOW_RESOLUTION_CARD_WIDTH = 600
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


# ID-1 cards (national ID, driving licence) are 85.6 x 54 mm; a passport data
# page is 125 x 88 mm. Both land in this band even under moderate perspective.
CARD_ASPECT = 1000.0 / 630.0
QUAD_ASPECT_RANGE = (1.1, 2.9)
QUAD_MIN_AREA_FRAC = 0.01
QUAD_MAX_AREA_FRAC = 0.97
QUAD_MIN_QUALITY = 0.35
# true aspect ratios of the documents we accept: ID-1 card, passport data page
CANONICAL_ASPECTS = (1000.0 / 630.0, 125.0 / 88.0)
QUAD_MIN_EDGE_SUPPORT = 0.45
QUAD_MIN_RECTANGULARITY = 0.6


def _quad_side_lengths(ordered):
    return [float(np.linalg.norm(ordered[(i + 1) % 4] - ordered[i])) for i in range(4)]


def _quad_angles(ordered):
    angles = []
    for i in range(4):
        prev_pt = ordered[i - 1]
        cur = ordered[i]
        nxt = ordered[(i + 1) % 4]
        v1 = prev_pt - cur
        v2 = nxt - cur
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2)) + 1e-6
        cos = float(np.clip(np.dot(v1, v2) / denom, -1.0, 1.0))
        angles.append(float(np.degrees(np.arccos(cos))))
    return angles


def _quad_is_portrait(quad):
    """True when the card's long side runs vertically in the image."""
    ordered = _order_corners(quad)
    top, right, bottom, left = _quad_side_lengths(ordered)
    width = (top + bottom) / 2.0
    height = (left + right) / 2.0
    return height > width * 1.05


EDGE_MAX_DENSITY = 0.12


def _edge_map(small_bgr):
    """
    Edge map that also sees chroma boundaries (dark header on a brown desk, etc.).
    Thresholds are floored and raised while the map is saturated, so sensor
    noise on a dark desk does not turn into "edges" that support any rectangle.
    """
    blurred = cv2.GaussianBlur(small_bgr, (5, 5), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    median = float(np.median(gray))
    channels = (
        (gray, ((50, 150), (max(40.0, 0.66 * median), max(100.0, 1.33 * median)))),
        (lab[:, :, 1], ((25, 75),)),
        (lab[:, :, 2], ((25, 75),)),
        (hsv[:, :, 1], ((30, 90),)),
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    gain = 1.0
    for _ in range(4):
        edges = np.zeros(gray.shape, dtype=np.uint8)
        for channel, thresholds in channels:
            for low, high in thresholds:
                edges = cv2.bitwise_or(
                    edges,
                    cv2.Canny(channel, int(min(255, low * gain)), int(min(255, high * gain))),
                )
        if float(np.mean(edges > 0)) <= EDGE_MAX_DENSITY:
            break
        gain *= 1.6
    else:
        # still saturated at 4x thresholds: pure noise, nothing to trust
        return np.zeros(gray.shape, dtype=np.uint8)
    return cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)


def _line_intersection(p1, p2, p3, p4):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-6:
        return None
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
    return np.array([px, py], dtype=np.float32)


def _quad_from_longest_sides(poly):
    """
    For a polygon with more than 4 vertices (rounded corners, a finger over an
    edge), keep the 4 longest sides as lines and intersect neighbours.
    """
    pts = poly.reshape(-1, 2).astype(np.float32)
    n = len(pts)
    if n < 5:
        return None
    sides = []
    for i in range(n):
        a = pts[i]
        b = pts[(i + 1) % n]
        sides.append((float(np.linalg.norm(b - a)), i, a, b))
    longest = sorted(sides, key=lambda s: s[0], reverse=True)[:4]
    longest = sorted(longest, key=lambda s: s[1])  # keep polygon order
    corners = []
    for k in range(4):
        _, _, a1, b1 = longest[k]
        _, _, a2, b2 = longest[(k + 1) % 4]
        point = _line_intersection(a1, b1, a2, b2)
        if point is None:
            return None
        corners.append(point)
    return np.array(corners, dtype=np.float32)


def _contour_to_quads(contour, add):
    """
    Emit quad guesses for one contour: min-area box of its hull, polygon fits of
    the hull, and polygon fits of the raw contour (a finger sticking out over an
    edge is swallowed by the hull but still leaves the card's own sides as the
    longest segments of the raw polygon).
    """
    hull = cv2.convexHull(contour)
    add(cv2.boxPoints(cv2.minAreaRect(hull)))
    for shape in (hull, contour):
        peri = cv2.arcLength(shape, True)
        for eps in (0.01, 0.02, 0.03, 0.05, 0.08):
            approx = cv2.approxPolyDP(shape, eps * peri, True)
            if len(approx) == 4:
                add(approx.reshape(4, 2))
            elif len(approx) > 4:
                add(_quad_from_longest_sides(approx))


def _region_masks(small_bgr):
    """
    Foreground masks from Otsu thresholds on several channels. A card is usually
    a uniform, low-saturation, bright region, so at least one polarity of one
    channel isolates it even when texture lines break the edge contour.
    """
    blurred = cv2.GaussianBlur(small_bgr, (5, 5), 0)
    gray = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(blurred, cv2.COLOR_BGR2LAB)
    kernel_open = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
    for channel in (gray, hsv[:, :, 1], lab[:, :, 1], lab[:, :, 2]):
        _, mask = cv2.threshold(channel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        for polarity in (mask, cv2.bitwise_not(mask)):
            cleaned = cv2.morphologyEx(polarity, cv2.MORPH_OPEN, kernel_open)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_close)
            yield cleaned


def _quad_candidates(small_bgr, edges):
    h, w = edges.shape[:2]
    image_area = float(h * w)
    thick = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)
    candidates = []
    seen = set()
    hulls = []

    def add(quad):
        if quad is None or len(quad) != 4:
            return
        quad = np.array(quad, dtype=np.float32).reshape(4, 2)
        if not np.all(np.isfinite(quad)):
            return
        key = tuple(int(round(v / 4.0)) for v in quad.reshape(-1))
        if key in seen:
            return
        seen.add(key)
        candidates.append(quad)

    def consider(contour):
        hull = cv2.convexHull(contour)
        hull_area = float(cv2.contourArea(hull))
        if hull_area < image_area * 0.01:
            return
        hulls.append((hull_area, hull))
        if hull_area >= image_area * QUAD_MIN_AREA_FRAC:
            _contour_to_quads(contour, add)

    # 1) contours of the edge map (works for white-on-white where only a shadow line exists)
    for mode in (cv2.RETR_EXTERNAL, cv2.RETR_LIST):
        contours, _ = cv2.findContours(thick, mode, cv2.CHAIN_APPROX_SIMPLE)
        for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:20]:
            consider(contour)

    # 2) uniform regions (works on textured desks where edge contours merge with the background)
    for mask in _region_masks(small_bgr):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
            consider(contour)

    # 3) unions of touching hulls: a card with a coloured header band, or a
    #    shadow line across it, splits into parts that no single source joins
    hulls = sorted(hulls, key=lambda r: r[0], reverse=True)[:16]
    for i in range(len(hulls)):
        for j in range(i + 1, len(hulls)):
            area_i, hull_i = hulls[i]
            area_j, hull_j = hulls[j]
            union = cv2.convexHull(np.vstack([hull_i, hull_j]))
            union_area = float(cv2.contourArea(union))
            if union_area < image_area * QUAD_MIN_AREA_FRAC:
                continue
            # adjacent: clearly bigger than either part, but barely bigger than both together
            if union_area < 1.08 * max(area_i, area_j) or union_area > 1.25 * (area_i + area_j):
                continue
            _contour_to_quads(union, add)
    return candidates


def _edge_support(ordered, support_map, samples=64, trim=0.06):
    """Fraction of each side that lies on an image edge (ignoring rounded ends)."""
    h, w = support_map.shape[:2]
    per_side = []
    ts = np.linspace(trim, 1.0 - trim, samples, dtype=np.float32)
    for i in range(4):
        a = ordered[i]
        b = ordered[(i + 1) % 4]
        xs = np.clip(np.round(a[0] + (b[0] - a[0]) * ts).astype(int), 0, w - 1)
        ys = np.clip(np.round(a[1] + (b[1] - a[1]) * ts).astype(int), 0, h - 1)
        per_side.append(float(np.mean(support_map[ys, xs] > 0)))
    return per_side


def _refine_quad(quad, edges, samples=48, trim=0.08):
    """
    Snap each side of a rough quad onto the nearest edge pixels along its
    normal and re-fit the side with a robust line; return the intersections.
    Rough candidates (min-area boxes that include a shadow, hulls that include
    a finger) become pixel-accurate this way. Falls back per side when too few
    edge points are found.
    """
    h, w = edges.shape[:2]
    ordered = _order_corners(quad)
    reach = max(6, int(round(min(h, w) * 0.03)))
    ts = np.linspace(trim, 1.0 - trim, samples, dtype=np.float32)
    lines = []
    for i in range(4):
        a = ordered[i]
        b = ordered[(i + 1) % 4]
        direction = b - a
        length = float(np.linalg.norm(direction))
        if length < 1:
            return None
        direction /= length
        normal = np.array([-direction[1], direction[0]], dtype=np.float32)
        found = []
        for t in ts:
            base = a + direction * (t * length)
            best = None
            for offset in range(0, reach + 1):
                for sign in ((1,) if offset == 0 else (1, -1)):
                    px = base + normal * (sign * offset)
                    x, y = int(round(px[0])), int(round(px[1]))
                    if 0 <= x < w and 0 <= y < h and edges[y, x]:
                        best = px
                        break
                if best is not None:
                    break
            if best is not None:
                found.append(best)
        if len(found) >= max(6, int(0.4 * samples)):
            pts = np.array(found, dtype=np.float32)
            vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_HUBER, 0, 0.01, 0.01).reshape(-1)
            p0 = np.array([x0, y0], dtype=np.float32)
            p1 = p0 + np.array([vx, vy], dtype=np.float32) * 100.0
            lines.append((p0, p1))
        else:
            lines.append((a, b))

    corners = []
    for i in range(4):
        prev_line = lines[i - 1]
        line = lines[i]
        point = _line_intersection(prev_line[0], prev_line[1], line[0], line[1])
        if point is None or not np.all(np.isfinite(point)):
            return None
        corners.append(point)
    return np.array(corners, dtype=np.float32)


def _score_quad(quad, support_map, min_quality=QUAD_MIN_QUALITY):
    """
    Return (score, details) or (None, reason) when the quad is not card-like.
    `details['quality']` is size-independent (edge support, shape, aspect);
    `score` multiplies it by sqrt(area) so bigger plausible cards rank first.
    """
    h, w = support_map.shape[:2]
    image_area = float(h * w)
    ordered = _order_corners(quad)
    if len({tuple(np.round(p, 1)) for p in ordered}) < 4:
        return None, 'degenerate'

    margin_x, margin_y = w * 0.05, h * 0.05
    if (ordered[:, 0] < -margin_x).any() or (ordered[:, 0] > w + margin_x).any():
        return None, 'outside'
    if (ordered[:, 1] < -margin_y).any() or (ordered[:, 1] > h + margin_y).any():
        return None, 'outside'

    area = abs(float(cv2.contourArea(ordered)))
    area_frac = area / image_area
    if area_frac < QUAD_MIN_AREA_FRAC or area_frac > QUAD_MAX_AREA_FRAC:
        return None, 'area'
    if not cv2.isContourConvex(ordered.astype(np.int32)):
        return None, 'concave'

    angles = _quad_angles(ordered)
    if min(angles) < 50 or max(angles) > 130:
        return None, 'angles'

    top, right, bottom, left = _quad_side_lengths(ordered)
    if min(top, right, bottom, left) < 4:
        return None, 'degenerate'
    if max(top, bottom) / min(top, bottom) > 2.2 or max(left, right) / min(left, right) > 2.2:
        return None, 'skew'
    width = (top + bottom) / 2.0
    height = (left + right) / 2.0
    aspect = max(width, height) / max(min(width, height), 1.0)
    if not (QUAD_ASPECT_RANGE[0] <= aspect <= QUAD_ASPECT_RANGE[1]):
        return None, 'aspect'
    aspect_prior = float(np.exp(-((np.log(aspect) - np.log(CARD_ASPECT)) / 0.45) ** 2))

    # area / min-area-rect area: 1.0 for a true rectangle, lower for a trapezoid
    # seen at an angle, so it is only a soft term (a hard gate rejected real cards)
    rect_size = cv2.minAreaRect(ordered)[1]
    rectangularity = area / max(float(rect_size[0] * rect_size[1]), 1.0)
    if rectangularity < QUAD_MIN_RECTANGULARITY:
        return None, 'rectangularity'

    sides = _edge_support(ordered, support_map)
    support = float(np.mean(sides))
    if support < QUAD_MIN_EDGE_SUPPORT or min(sides) < 0.2:
        return None, 'edge_support'
    # weight the weakest side too, so a box that runs half through empty
    # background (card + finger, card + shadow) loses to the real outline
    support_eff = 0.6 * support + 0.4 * float(min(sides))

    quality = (support_eff ** 1.5) * np.sqrt(rectangularity) * np.sqrt(aspect_prior)
    if quality < min_quality:
        return None, 'quality'
    score = float(quality * np.sqrt(area_frac))
    return score, {
        'quality': float(quality),
        'support': support,
        'sides': sides,
        'aspect': aspect,
        'area_frac': area_frac,
        'rectangularity': rectangularity,
    }


def _is_frontal(ordered, max_angle_deg=6.0, max_length_ratio=1.08):
    """Opposite sides parallel and equal: the apparent aspect is then the true aspect."""
    def angle(a, b):
        v = b - a
        return np.degrees(np.arctan2(v[1], v[0]))
    top = angle(ordered[0], ordered[1])
    bottom = angle(ordered[3], ordered[2])
    left = angle(ordered[0], ordered[3])
    right = angle(ordered[1], ordered[2])
    if abs(top - bottom) > max_angle_deg or abs(left - right) > max_angle_deg:
        return False
    t, r, b, l = _quad_side_lengths(ordered)
    return max(t, b) / max(min(t, b), 1) <= max_length_ratio and max(l, r) / max(min(l, r), 1) <= max_length_ratio


def _shift_side(ordered, side, offset):
    """Move one side (0 top, 1 right, 2 bottom, 3 left) along its outward normal by `offset` px."""
    moved = ordered.copy()
    a, b = ordered[side], ordered[(side + 1) % 4]
    direction = b - a
    direction /= max(float(np.linalg.norm(direction)), 1e-6)
    # corners are clockwise (TL, TR, BR, BL), so the outward normal is to the left of the direction
    outward = np.array([direction[1], -direction[0]], dtype=np.float32)
    moved[side] = a + outward * offset
    moved[(side + 1) % 4] = b + outward * offset
    return moved


def _aspect_side_search(ordered, edges, support_map):
    """
    A side of a white card on a light background is easy to lose: the strong
    edge just inside it (a header band, the first text line) wins the
    refinement and the quad ends up slightly short, which shifts every
    template box. For a near-frontal quad, slide each side in and out and keep
    the position that best combines edge support with a *card-shaped* aspect.
    """
    if not _is_frontal(ordered):
        return ordered

    def quality(quad):
        t, r, b, l = _quad_side_lengths(quad)
        width, height = (t + b) / 2.0, (l + r) / 2.0
        aspect = max(width, height) / max(min(width, height), 1.0)  # orientation-agnostic
        target = min(CANONICAL_ASPECTS, key=lambda a: abs(np.log(aspect) - np.log(a)))
        aspect_prior = float(np.exp(-((np.log(aspect) - np.log(target)) / 0.06) ** 2))
        sides = _edge_support(quad, support_map)
        support = 0.6 * float(np.mean(sides)) + 0.4 * float(min(sides))
        return (support ** 1.5) * np.sqrt(aspect_prior)

    best = ordered.copy()
    best_q = quality(best)
    for _ in range(2):  # greedy passes: fixing one side changes the aspect for the others
        improved = False
        for side in range(4):
            t, r, b, l = _quad_side_lengths(best)
            extent = (l + r) / 2.0 if side in (0, 2) else (t + b) / 2.0
            reach = max(4, int(round(extent * 0.08)))
            for offset in range(-reach, reach + 1, 2):
                if offset == 0:
                    continue
                candidate = _shift_side(best, side, float(offset))
                # mild preference for staying put, so a parallel background line far out does not win
                q = quality(candidate) * float(np.exp(-0.2 * (offset / float(reach)) ** 2))
                if q > best_q * 1.02:
                    best, best_q, improved = candidate, q, True
        if not improved:
            break

    if not np.allclose(best, ordered):
        # snap the moved sides precisely onto the edge they now sit near
        refined = _refine_quad(best, edges)
        if refined is not None and quality(refined) >= best_q * 0.98:
            best = _order_corners(refined)
        logger.info('aspect side search adjusted quad quality %.3f', best_q)
    return best


def find_document_quad(image, return_debug=False):
    """
    Locate the 4 corners of an ID card / passport page in a photo.

    Returns (quad, score) in full-image pixel coordinates (TL, TR, BR, BL), or
    (None, 0.0) when nothing card-like is found. Candidates come from edge
    contours, uniform colour regions and unions of touching regions; each is
    snapped onto nearby edges and ranked by how much of its perimeter sits on
    real edges, how rectangular it is, how close its aspect is to a card, and
    its size - instead of "largest 4-gon wins".
    """
    bgr = _as_bgr(image)
    h, w = bgr.shape[:2]
    max_side = 1000.0
    scale = min(1.0, max_side / float(max(h, w)))
    if scale < 1.0:
        small = cv2.resize(
            bgr,
            (max(int(round(w * scale)), 1), max(int(round(h * scale)), 1)),
            interpolation=cv2.INTER_AREA,
        )
    else:
        small = bgr

    edges = _edge_map(small)
    rect = cv2.MORPH_RECT
    loose_support = cv2.dilate(edges, cv2.getStructuringElement(rect, (15, 15)), iterations=1)
    tight_support = cv2.dilate(edges, cv2.getStructuringElement(rect, (7, 7)), iterations=1)

    best = None
    for candidate in _quad_candidates(small, edges):
        # cheap pre-filter with generous tolerance, then snap to edges and re-score strictly
        loose_score, _ = _score_quad(candidate, loose_support, min_quality=QUAD_MIN_QUALITY * 0.4)
        if loose_score is None:
            continue
        options = [candidate]
        refined = _refine_quad(candidate, edges)
        if refined is not None:
            options.insert(0, refined)
        for option in options:
            score, details = _score_quad(option, tight_support)
            if score is None:
                continue
            if best is None or score > best[0]:
                best = (score, _order_corners(option), details)
            break

    if best is None:
        return (None, 0.0, {'edges': edges}) if return_debug else (None, 0.0)
    score, quad, details = best
    adjusted = _aspect_side_search(quad, edges, tight_support)
    if not np.allclose(adjusted, quad):
        new_score, new_details = _score_quad(adjusted, tight_support)
        if new_score is not None:
            quad, score, details = _order_corners(adjusted), new_score, new_details
    quad = quad / scale if scale else quad
    logger.info(
        'document quad found score=%.3f support=%.2f aspect=%.2f area=%.2f',
        score, details['support'], details['aspect'], details['area_frac'],
    )
    if return_debug:
        return quad, score, {'edges': edges, **details}
    return quad, score


def warp_quad(image, quad, output_size=DEFAULT_OUTPUT_SIZE):
    """
    Warp a 4-point document quad to the standard landscape rectangle.
    A portrait quad (phone held upright) is rotated so the long side is
    horizontal; whether it needs a further 180 turn is decided by OCR later.
    """
    ordered = _order_corners(quad)
    if _quad_is_portrait(ordered):
        # shift corner order so the image's BL becomes the output's TL
        ordered = np.roll(ordered, -1, axis=0)
    width, height = int(output_size[0]), int(output_size[1])
    dest = np.array([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
    ], dtype=np.float32)
    matrix = cv2.getPerspectiveTransform(ordered, dest)
    return cv2.warpPerspective(image, matrix, (width, height))


def draw_quad_overlay(image, quad, colour=(0, 0, 255)):
    """Debug helper: draw the detected quad and corner labels on a copy of the image."""
    canvas = _as_bgr(image).copy()
    if quad is None:
        cv2.putText(canvas, 'no document quad found', (12, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.9, colour, 2)
        return canvas
    ordered = _order_corners(quad).astype(np.int32)
    cv2.polylines(canvas, [ordered], True, colour, max(2, canvas.shape[1] // 400))
    for label, (x, y) in zip(('TL', 'TR', 'BR', 'BL'), ordered):
        cv2.circle(canvas, (int(x), int(y)), 8, colour, -1)
        cv2.putText(canvas, label, (int(x) + 10, int(y) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, colour, 2)
    return canvas


def correct_perspective(image, output_size=DEFAULT_OUTPUT_SIZE, return_quad=False):
    """Warp the best card-like quad to a rectangle. Skip if none found."""
    quad, score = find_document_quad(image)
    if quad is None:
        return (image, False, None) if return_quad else (image, False)

    warped = warp_quad(image, quad, output_size)
    return (warped, True, quad) if return_quad else (warped, True)


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


def _odd_block_size(value, min_dim):
    block = int(value)
    max_block = min_dim if min_dim % 2 == 1 else min_dim - 1
    block = min(block, max_block)
    if block % 2 == 0:
        block -= 1
    return max(3, block)


def preprocess_field_crop(crop, config=None):
    """CLAHE, sharpen, and adaptive-threshold a template crop. Tune block size to crop size."""
    if crop is None or crop.size == 0:
        return crop
    config = merge_preprocess_config(config)
    gray = _as_gray(crop)
    h, w = gray.shape[:2]
    min_dim = min(h, w)

    if config.get('clahe') and min_dim >= 8:
        tile = min(int(config.get('clahe_tile_size', 8)), max(2, min_dim // 4))
        gray = apply_clahe(gray, {**config, 'clahe_tile_size': tile})

    if config.get('sharpen'):
        gray = unsharp_mask(
            gray,
            amount=config.get('sharpen_amount', 1.0),
            sigma=min(1.0, float(config.get('sharpen_sigma', 1.5))),
        )

    processed = gray
    if config.get('binarize'):
        if min_dim < 12:
            _, processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            if np.mean(processed) < 127:
                processed = cv2.bitwise_not(processed)
        else:
            block = _odd_block_size(config.get('adaptive_block_size', 31), min_dim)
            processed = adaptive_binarize(gray, {**config, 'adaptive_block_size': block})

    if config.get('upscale'):
        processed = upscale_crop(processed, min_size=int(config.get('crop_min_size', 64)))
    return processed


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

    quad = None
    warped = False
    if config.get('perspective'):
        current, warped, quad = correct_perspective(
            current, config.get('output_size') or DEFAULT_OUTPUT_SIZE, return_quad=True
        )
        steps_run.append('perspective')
        logger.info('preprocess perspective applied=%s', warped)
        if config.get('debug'):
            _save_debug(config, '01_quad_overlay', draw_quad_overlay(bgr, quad), debug_images)
        _save_debug(config, '01_perspective', current, debug_images)

    aligned = current.copy()

    # Blur must be judged at the card's native resolution: warping a small card
    # up to 1000x630 smooths every pixel and the Laplacian score collapses even
    # for a perfectly sharp photo (a 300px-wide card drops from ~800 to ~30).
    native_size = None
    if quad is not None:
        ordered = _order_corners(quad)
        top, right, bottom, left = _quad_side_lengths(ordered)
        native_w = int(round(max(top, bottom)))
        native_h = int(round(max(left, right)))
        if native_h > native_w:
            native_w, native_h = native_h, native_w
        native_size = (max(native_w, 8), max(native_h, 8))
    out_w, out_h = config.get('output_size') or DEFAULT_OUTPUT_SIZE
    if native_size is not None and (native_size[0] < out_w or native_size[1] < out_h):
        blur_source = warp_quad(bgr, quad, native_size)
        logger.info('blur measured on native-size warp %dx%d', native_size[0], native_size[1])
    else:
        blur_source = current
    blur_score = compute_blur_score(blur_source)
    if native_size is not None and native_size[0] < LOW_RESOLUTION_CARD_WIDTH:
        logger.warning(
            'document is only %dpx wide in the photo; OCR accuracy will suffer (capture at higher resolution)',
            native_size[0],
        )

    perspective_meta = {
        'perspective_applied': bool(warped),
        'document_quad': quad.astype(float).round(1).tolist() if quad is not None else None,
        'document_width_px': native_size[0] if native_size is not None else None,
        'low_resolution': bool(native_size is not None and native_size[0] < LOW_RESOLUTION_CARD_WIDTH),
    }

    if config.get('blur_check'):
        steps_run.append('blur_check')
        threshold = float(config.get('blur_threshold', DOCUMENT_BLUR_THRESHOLD))
        logger.info('preprocess blur_score=%.4f threshold=%.4f', blur_score, threshold)
        if blur_score < threshold:
            _save_debug(config, '02_blur_rejected', current, debug_images)
            return {
                'ok': False,
                'image': current,
                'aligned_image': aligned,
                'reason': 'too_blurry',
                'message': 'Image is too blurry. Please retake.',
                'blur_score': round(blur_score, 4),
                'steps_run': steps_run,
                'debug_dir': config.get('debug_dir'),
                'debug_images': debug_images,
                **perspective_meta,
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
        'aligned_image': aligned,
        'reason': None,
        'message': None,
        'blur_score': round(blur_score, 4),
        'steps_run': steps_run,
        'debug_dir': config.get('debug_dir'),
        'debug_images': debug_images,
        **perspective_meta,
    }
