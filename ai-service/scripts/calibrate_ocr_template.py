"""
Calibrate OCR field templates by drawing rectangles on a document photo.

Usage:
  python scripts/calibrate_ocr_template.py path/to/photo.jpg --type passport --warp --write
  python scripts/calibrate_ocr_template.py path/to/warped.jpg --type id_v1_full_name --write

--warp runs the same perspective correction as live OCR (outputs 1000x630 when
the card edges are found). Use a photo of the FULL card, not a cropped field.

Mouse: click-drag a box over the current field (auto-advances on release)
If --warp cannot find the card, click the 4 corners of the card first
  (top-left, top-right, bottom-right, bottom-left), then draw field boxes.
Keys (field boxes):
  u  undo last field
  r  redraw current field
  q  print JSON and quit (also writes the file if --write)
"""

import argparse
import json
import os
import sys

import cv2
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
TEMPLATES_PATH = os.path.join(ROOT, 'config', 'ocr_templates.json')

FIELDS_BY_TYPE = {
    'passport': ['surname', 'given_names', 'passport_no', 'date_of_birth', 'date_of_expiry'],
    'id_v1_full_name': ['full_names', 'id_number', 'date_of_birth'],
    'id_v2_surname_given': [
        'surname', 'given_names', 'id_number', 'date_of_birth', 'date_of_expiry',
    ],
    'id_back': ['id_number'],
    'id_back_v1': ['id_number'],
    'id_back_v2': ['id_number'],
    'drivers_licence': ['surname', 'other_names', 'id_number', 'date_of_birth', 'date_of_expiry'],
}

WINDOW = 'OCR template calibration'
CORNER_WINDOW = 'Click card corners'
CORNER_LABELS = ('top-left', 'top-right', 'bottom-right', 'bottom-left')


def _screen_size():
    try:
        import ctypes
        return int(ctypes.windll.user32.GetSystemMetrics(0)), int(ctypes.windll.user32.GetSystemMetrics(1))
    except Exception:
        return 1280, 720


def _fit_display_size(width, height):
    """Scale so the whole image fits on screen (OpenCV AUTOSIZE windows do not scroll)."""
    screen_w, screen_h = _screen_size()
    max_w = max(int(screen_w * 0.92), 400)
    max_h = max(int(screen_h * 0.78), 300)
    scale = min(1.0, max_w / float(width), max_h / float(height))
    return scale, (max(int(round(width * scale)), 1), max(int(round(height * scale)), 1))


class CornerPicker:
    def __init__(self, image):
        self.original = image
        self.points = []
        h, w = image.shape[:2]
        self.scale, self.display_size = _fit_display_size(w, h)

    def on_mouse(self, event, x, y, flags, _param):
        if event != cv2.EVENT_LBUTTONDOWN or len(self.points) >= 4:
            return
        self.points.append((x / self.scale, y / self.scale))
        print(f'{CORNER_LABELS[len(self.points) - 1]}: {self.points[-1]}')

    def _display_image(self):
        frame = cv2.resize(self.original, self.display_size, interpolation=cv2.INTER_AREA)
        for index, (x, y) in enumerate(self.points):
            px, py = int(round(x * self.scale)), int(round(y * self.scale))
            cv2.circle(frame, (px, py), 6, (0, 255, 255), -1)
            cv2.putText(
                frame,
                CORNER_LABELS[index],
                (px + 8, py - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                1,
            )
        if len(self.points) >= 2:
            pts = [(int(round(x * self.scale)), int(round(y * self.scale))) for x, y in self.points]
            for start, end in zip(pts, pts[1:]):
                cv2.line(frame, start, end, (0, 200, 0), 2)
            if len(pts) == 4:
                cv2.line(frame, pts[-1], pts[0], (0, 200, 0), 2)
        next_label = CORNER_LABELS[len(self.points)] if len(self.points) < 4 else 'press Enter'
        cv2.putText(
            frame,
            f'Click {next_label}  (u=undo)',
            (10, 24),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )
        return frame

    def run(self):
        cv2.namedWindow(CORNER_WINDOW, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(CORNER_WINDOW, self.on_mouse)
        print('Click the 4 corners of the CARD (not the photo): top-left, top-right, bottom-right, bottom-left')
        while True:
            cv2.imshow(CORNER_WINDOW, self._display_image())
            key = cv2.waitKey(20) & 0xFF
            if key == ord('u') and self.points:
                self.points.pop()
            if key in (13, 10) and len(self.points) == 4:
                break
            if key == ord('q') and len(self.points) == 4:
                break
        cv2.destroyWindow(CORNER_WINDOW)
        if len(self.points) != 4:
            return None
        return np.array(self.points, dtype=np.float32)


class Calibrator:
    def __init__(self, image, fields):
        self.original = image
        self.fields = list(fields)
        self.boxes = {}
        self.index = 0
        self.dragging = False
        self.start = None
        self.current_rect = None
        h, w = image.shape[:2]
        self.scale, self.display_size = _fit_display_size(w, h)

    def current_field(self):
        if self.index >= len(self.fields):
            return None
        return self.fields[self.index]

    def _display_image(self):
        frame = cv2.resize(self.original, self.display_size, interpolation=cv2.INTER_AREA)
        h, w = self.original.shape[:2]
        for name, box in self.boxes.items():
            x1, y1, x2, y2 = _norm_to_display(box, w, h, self.scale)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), 2)
            cv2.putText(frame, name, (x1, max(y1 - 6, 14)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 0), 1)
        if self.current_rect is not None:
            (x1, y1), (x2, y2) = self.current_rect
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)
        field = self.current_field()
        status = f'{field}  ({self.index + 1}/{len(self.fields)})' if field else 'done — press q'
        cv2.putText(frame, status, (10, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        return frame

    def on_mouse(self, event, x, y, flags, _param):
        if self.current_field() is None:
            return
        if event == cv2.EVENT_LBUTTONDOWN:
            self.dragging = True
            self.start = (x, y)
            self.current_rect = ((x, y), (x, y))
        elif event == cv2.EVENT_MOUSEMOVE and self.dragging:
            self.current_rect = (self.start, (x, y))
        elif event == cv2.EVENT_LBUTTONUP and self.dragging:
            self.dragging = False
            self.current_rect = (self.start, (x, y))
            self._commit_current()

    def _commit_current(self):
        field = self.current_field()
        if not field or self.current_rect is None:
            return
        (x1, y1), (x2, y2) = self.current_rect
        if abs(x2 - x1) < 4 or abs(y2 - y1) < 4:
            print('box too small, drag again')
            self.current_rect = None
            return
        h, w = self.original.shape[:2]
        box = _display_to_norm(x1, y1, x2, y2, w, h, self.scale)
        self.boxes[field] = box
        print(f'{field}: {box}')
        self.current_rect = None
        self.index += 1

    def undo(self):
        if self.dragging:
            return
        if self.current_rect is not None:
            self.current_rect = None
            return
        if self.index <= 0:
            return
        self.index -= 1
        field = self.fields[self.index]
        self.boxes.pop(field, None)
        print(f'undid {field}')

    def run(self):
        cv2.namedWindow(WINDOW, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(WINDOW, self.on_mouse)
        print('Draw a box for each field. u=undo  r=redraw  q=finish')
        while True:
            cv2.imshow(WINDOW, self._display_image())
            key = cv2.waitKey(20) & 0xFF
            if key == ord('q'):
                break
            if key == ord('u'):
                self.undo()
            if key == ord('r'):
                field = self.current_field()
                if field:
                    self.current_rect = None
        cv2.destroyAllWindows()
        return {name: self.boxes[name] for name in self.fields if name in self.boxes}


def _display_to_norm(x1, y1, x2, y2, orig_w, orig_h, scale):
    xa, xb = sorted((x1 / scale, x2 / scale))
    ya, yb = sorted((y1 / scale, y2 / scale))
    return [
        round(max(xa, 0.0) / orig_w, 4),
        round(max(ya, 0.0) / orig_h, 4),
        round(min(xb, orig_w) / orig_w, 4),
        round(min(yb, orig_h) / orig_h, 4),
    ]


def _norm_to_display(box, orig_w, orig_h, scale):
    x1 = int(round(box[0] * orig_w * scale))
    y1 = int(round(box[1] * orig_h * scale))
    x2 = int(round(box[2] * orig_w * scale))
    y2 = int(round(box[3] * orig_h * scale))
    return x1, y1, x2, y2


def _merge_and_write(document_type, boxes):
    templates = {}
    if os.path.isfile(TEMPLATES_PATH):
        with open(TEMPLATES_PATH, encoding='utf-8') as handle:
            templates = json.load(handle)
    current = dict(templates.get(document_type) or {})
    current.update(boxes)
    templates[document_type] = current
    os.makedirs(os.path.dirname(TEMPLATES_PATH), exist_ok=True)
    with open(TEMPLATES_PATH, 'w', encoding='utf-8') as handle:
        json.dump(templates, handle, indent=2)
        handle.write('\n')
    print(f'wrote {TEMPLATES_PATH}')


def _prepare_image(image, warp, save_warped):
    from services.documentPreprocessService import DEFAULT_OUTPUT_SIZE, correct_perspective, warp_quad

    if not warp:
        h, w = image.shape[:2]
        print(f'using image as-is {w}x{h} (pass --warp to flatten to {DEFAULT_OUTPUT_SIZE[0]}x{DEFAULT_OUTPUT_SIZE[1]})')
        return image

    warped, applied = correct_perspective(image, DEFAULT_OUTPUT_SIZE)
    if applied:
        h, w = warped.shape[:2]
        print(f'perspective correction applied → {w}x{h}')
    else:
        print('could not find card edges automatically. Click the 4 corners of the card.')
        corners = CornerPicker(image).run()
        if corners is None:
            h, w = image.shape[:2]
            print(f'no corners selected; using original {w}x{h}')
            warped = image
        else:
            warped = warp_quad(image, corners, DEFAULT_OUTPUT_SIZE)
            h, w = warped.shape[:2]
            print(f'perspective correction from clicked corners → {w}x{h}')
    if save_warped:
        ok = cv2.imwrite(save_warped, warped)
        if ok:
            print(f'saved warped image to {save_warped}')
        else:
            print(f'failed to write {save_warped}', file=sys.stderr)
    return warped


def main():
    parser = argparse.ArgumentParser(description='Draw OCR template boxes on a document photo')
    parser.add_argument('image', help='Path to a full-card photo or already-warped image')
    parser.add_argument('--type', required=True, choices=sorted(FIELDS_BY_TYPE), help='Document type key')
    parser.add_argument('--write', action='store_true', help=f'Merge boxes into {TEMPLATES_PATH}')
    parser.add_argument(
        '--warp',
        action='store_true',
        help='Flatten the card the same way live OCR does (1000x630 when edges are found)',
    )
    parser.add_argument('--save-warped', metavar='PATH', help='Write the warped image to this path')
    args = parser.parse_args()

    image = cv2.imread(args.image)
    if image is None:
        print(f'could not read image: {args.image}', file=sys.stderr)
        return 1

    image = _prepare_image(image, args.warp, args.save_warped)
    boxes = Calibrator(image, FIELDS_BY_TYPE[args.type]).run()
    payload = {args.type: boxes}
    print('\nPaste into config/ocr_templates.json:\n')
    print(json.dumps(payload, indent=2))
    if args.write:
        _merge_and_write(args.type, boxes)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
