"""
Module 12 — Empirical score measurement on the benchmark datasets.

Runs this project's own verification services over samples of the benchmark
datasets so the synthetic distributions in generate_dataset.py can be checked
against real measurements:

  lfw   faceMatchService  on LFW genuine / impostor pairs (DevTest split)
  nuaa  livenessService   on NUAA real-face (client) / photo-attack (imposter) test images
  midv  imageQualityService on MIDV-500 frames (blur, brightness, contrast) and
        EasyOCR field reads scored against MIDV-500 ground-truth field values

Per-sample results are written to ml/data/benchmarks/*.csv; `summary` writes
ml/reports/benchmark_measurements.json. The raw datasets are not needed after that.

Usage (from ai-service/):
    python ml/measure_benchmarks.py lfw  [--root ~/Downloads/LFW]
    python ml/measure_benchmarks.py nuaa [--root ~/Downloads/nuaa] [--per-class 600]
    python ml/measure_benchmarks.py midv [--root ~/Downloads/midv500] [--frames-per-condition 3] [--ocr-frames-per-condition 1]
    python ml/measure_benchmarks.py summary
"""

import argparse
import json
import os
import random
import re
import sys
import time

import cv2
import numpy as np
import pandas as pd

ML_DIR = os.path.dirname(os.path.abspath(__file__))
AI_ROOT = os.path.dirname(ML_DIR)
sys.path.insert(0, AI_ROOT)

OUT_DIR = os.path.join(ML_DIR, 'data', 'benchmarks')
SUMMARY_PATH = os.path.join(ML_DIR, 'reports', 'benchmark_measurements.json')
DOWNLOADS = os.path.join(os.path.expanduser('~'), 'Downloads')
SEED = 42

MIDV_CONDITIONS = {
    'TS': 'table', 'TA': 'table', 'KS': 'keyboard', 'KA': 'keyboard', 'HS': 'hand',
    'HA': 'hand', 'PS': 'partial', 'PA': 'partial', 'CS': 'clutter', 'CA': 'clutter',
}


def _progress(label, done, total, started):
    if done == total or done % 50 == 0:
        rate = done / max(time.time() - started, 1e-6)
        print(f'[{label}] {done}/{total} ({rate:.1f}/s)', flush=True)


def _read_image(path):
    # cv2.imread cannot open non-ASCII Windows paths; imdecode can
    data = np.fromfile(path, dtype=np.uint8)
    return cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None


# --------------------------------------------------------------------------- LFW
def measure_lfw(root):
    from services.faceMatchService import generate_embedding, compute_face_match_score

    image_dir = os.path.join(root, 'lfw-deepfunneled', 'lfw-deepfunneled')
    match = pd.read_csv(os.path.join(root, 'matchpairsDevTest.csv'))
    mismatch = pd.read_csv(os.path.join(root, 'mismatchpairsDevTest.csv'))

    def path(name, num):
        return os.path.join(image_dir, name, f'{name}_{int(num):04d}.jpg')

    pairs = [(path(r.name, r.imagenum1), path(r.name, r.imagenum2), 'genuine') for r in match.itertuples()]
    mismatch.columns = ['name1', 'imagenum1', 'name2', 'imagenum2']
    pairs += [(path(r.name1, r.imagenum1), path(r.name2, r.imagenum2), 'impostor') for r in mismatch.itertuples()]

    cache = {}

    def embedding(p):
        if p not in cache:
            image = _read_image(p)
            cache[p] = generate_embedding(image)[0] if image is not None else None
        return cache[p]

    rows, started = [], time.time()
    for i, (a, b, kind) in enumerate(pairs, 1):
        ea, eb = embedding(a), embedding(b)
        detected = ea is not None and eb is not None
        # Production returns 0.0 when either face is missing
        score = compute_face_match_score(ea, eb) if detected else 0.0
        rows.append({'image1': os.path.relpath(a, image_dir), 'image2': os.path.relpath(b, image_dir),
                     'pair_type': kind, 'faces_detected': detected, 'faceMatchScore': score})
        _progress('lfw', i, len(pairs), started)

    _save(rows, 'lfw_face_match.csv')


# --------------------------------------------------------------------------- NUAA
def measure_nuaa(root, per_class):
    from services.livenessService import detect_liveness

    raw = os.path.join(root, 'raw')
    samples = []
    rng = random.Random(SEED)
    for kind, folder, index in [('real', 'ClientRaw', 'client_test_raw.txt'),
                                ('photo_attack', 'ImposterRaw', 'imposter_test_raw.txt')]:
        with open(os.path.join(raw, index), encoding='latin-1') as handle:
            names = [line.strip().replace('\\', os.sep) for line in handle if line.strip()]
        for name in rng.sample(names, min(per_class, len(names))):
            samples.append((os.path.join(raw, folder, name), kind))

    rows, started = [], time.time()
    for i, (p, kind) in enumerate(samples, 1):
        image = _read_image(p)
        if image is None:
            continue
        # NUAA file names: ID_glasses_pos_session_picNo — pos encodes pose / lighting
        parts = os.path.basename(p).split('_')
        rows.append({'image': os.path.relpath(p, raw), 'presentation': kind,
                     'subject': parts[0], 'session': parts[3] if len(parts) > 3 else None,
                     'livenessScore': round(detect_liveness(image), 4)})
        _progress('nuaa', i, len(samples), started)

    _save(rows, 'nuaa_liveness.csv')


# --------------------------------------------------------------------------- MIDV-500
def _normalise_text(value):
    return re.sub(r'[^A-Z0-9]', '', str(value or '').upper())


def _is_latin(value):
    return bool(value) and all(ord(ch) < 128 for ch in str(value)) and len(_normalise_text(value)) >= 2


def _frames(doc_dir, condition, count, rng):
    frames = sorted(f for f in os.listdir(os.path.join(doc_dir, 'images', condition)) if f.endswith('.tif'))
    return rng.sample(frames, min(count, len(frames)))


def _warp_to_template(frame, frame_quad, template_shape):
    h, w = template_shape[:2]
    src = np.float32(frame_quad)
    dst = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    return cv2.warpPerspective(frame, cv2.getPerspectiveTransform(src, dst), (w, h))


def _field_crop(template_view, quad, pad=4):
    xs = [p[0] for p in quad]
    ys = [p[1] for p in quad]
    h, w = template_view.shape[:2]
    x0, x1 = max(0, min(xs) - pad), min(w, max(xs) + pad)
    y0, y1 = max(0, min(ys) - pad), min(h, max(ys) + pad)
    return template_view[y0:y1, x0:x1]


def measure_midv(root, frames_per_condition, ocr_frames_per_condition):
    from services.imageQualityService import assess_image_quality
    from services.ocrService import get_reader, levenshtein_similarity

    base = os.path.join(root, 'midv500')
    docs = sorted(d for d in os.listdir(base) if os.path.isdir(os.path.join(base, d)))
    rng = random.Random(SEED)
    reader = get_reader() if ocr_frames_per_condition else None

    quality_rows, ocr_rows, started = [], [], time.time()
    for n, doc in enumerate(docs, 1):
        doc_dir = os.path.join(base, doc)
        with open(os.path.join(doc_dir, 'ground_truth', f'{doc}.json'), encoding='utf-8') as handle:
            fields = {k: v for k, v in json.load(handle).items() if k != 'photo' and _is_latin(v.get('value'))}
        template = _read_image(os.path.join(doc_dir, 'images', f'{doc}.tif'))

        for condition, label in MIDV_CONDITIONS.items():
            chosen = _frames(doc_dir, condition, max(frames_per_condition, ocr_frames_per_condition), rng)
            for k, frame_name in enumerate(chosen):
                frame = _read_image(os.path.join(doc_dir, 'images', condition, frame_name))
                if frame is None:
                    continue

                if k < frames_per_condition:
                    q = assess_image_quality(frame, purpose='document')
                    quality_rows.append({'document': doc, 'condition': condition, 'setting': label,
                                         'frame': frame_name, 'documentFound': q.get('documentFound'),
                                         'blurScore': q['blurScore'], 'brightnessScore': q['brightnessScore'],
                                         'contrastScore': q['contrastScore'], 'passed': q['passed']})

                if reader is not None and k < ocr_frames_per_condition and fields and template is not None:
                    gt_path = os.path.join(doc_dir, 'ground_truth', condition, frame_name.replace('.tif', '.json'))
                    with open(gt_path, encoding='utf-8') as handle:
                        frame_quad = json.load(handle)['quad']
                    view = _warp_to_template(frame, frame_quad, template.shape)
                    sims, confs = [], []
                    for field in fields.values():
                        crop = _field_crop(view, field['quad'])
                        if crop.size == 0:
                            sims.append(0.0)
                            continue
                        result = reader.readtext(crop, detail=1, paragraph=False)
                        text = ' '.join(r[1] for r in result)
                        confs.extend(float(r[2]) for r in result)
                        sims.append(levenshtein_similarity(_normalise_text(text), _normalise_text(field['value'])))
                    ocr_rows.append({'document': doc, 'condition': condition, 'setting': label, 'frame': frame_name,
                                     'fields': len(sims),
                                     'ocrConfidenceScore': round(float(np.mean(sims)), 4),
                                     'easyocrMeanConfidence': round(float(np.mean(confs)), 4) if confs else 0.0})
        print(f'[midv] {n}/{len(docs)} documents ({time.time() - started:.0f}s)', flush=True)

    _save(quality_rows, 'midv_image_quality.csv')
    if ocr_rows:
        _save(ocr_rows, 'midv_ocr.csv')


# --------------------------------------------------------------------------- summary
def _describe(series):
    s = pd.Series(series).dropna()
    return {'n': int(s.size), 'mean': round(float(s.mean()), 4), 'std': round(float(s.std()), 4),
            'p05': round(float(s.quantile(0.05)), 4), 'p25': round(float(s.quantile(0.25)), 4),
            'median': round(float(s.median()), 4), 'p75': round(float(s.quantile(0.75)), 4),
            'p95': round(float(s.quantile(0.95)), 4)}


def summarise():
    summary = {'generated_by': 'ml/measure_benchmarks.py', 'seed': SEED}

    def load(name):
        p = os.path.join(OUT_DIR, name)
        return pd.read_csv(p) if os.path.exists(p) else None

    lfw = load('lfw_face_match.csv')
    if lfw is not None:
        summary['lfw_faceMatchScore'] = {k: _describe(g['faceMatchScore']) for k, g in lfw.groupby('pair_type')}
        summary['lfw_faces_detected_rate'] = round(float(lfw['faces_detected'].mean()), 4)

    nuaa = load('nuaa_liveness.csv')
    if nuaa is not None:
        summary['nuaa_livenessScore'] = {k: _describe(g['livenessScore']) for k, g in nuaa.groupby('presentation')}

    quality = load('midv_image_quality.csv')
    if quality is not None:
        summary['midv_image_quality'] = {
            feat: {k: _describe(g[feat]) for k, g in quality.groupby('setting')}
            for feat in ('blurScore', 'brightnessScore', 'contrastScore')
        }
        summary['midv_document_found_rate'] = round(float(quality['documentFound'].mean()), 4)

    ocr = load('midv_ocr.csv')
    if ocr is not None:
        summary['midv_ocrConfidenceScore'] = {k: _describe(g['ocrConfidenceScore']) for k, g in ocr.groupby('setting')}

    os.makedirs(os.path.dirname(SUMMARY_PATH), exist_ok=True)
    with open(SUMMARY_PATH, 'w', encoding='utf-8') as handle:
        json.dump(summary, handle, indent=2)
    print(json.dumps(summary, indent=2))


def _save(rows, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, name)
    pd.DataFrame(rows).to_csv(path, index=False)
    print(f'Saved {len(rows)} rows -> {path}', flush=True)


def main():
    parser = argparse.ArgumentParser(description='Measure verification scores on benchmark datasets')
    parser.add_argument('dataset', choices=['lfw', 'nuaa', 'midv', 'summary'])
    parser.add_argument('--root', help='dataset folder (defaults to ~/Downloads/<LFW|nuaa|midv500>)')
    parser.add_argument('--per-class', type=int, default=600, help='NUAA images per class')
    parser.add_argument('--frames-per-condition', type=int, default=3, help='MIDV frames per document/condition for quality')
    parser.add_argument('--ocr-frames-per-condition', type=int, default=1, help='MIDV frames per document/condition for OCR (0 = skip)')
    args = parser.parse_args()

    defaults = {'lfw': 'LFW', 'nuaa': 'nuaa', 'midv': 'midv500'}
    root = args.root or (os.path.join(DOWNLOADS, defaults[args.dataset]) if args.dataset in defaults else None)

    if args.dataset == 'lfw':
        measure_lfw(root)
    elif args.dataset == 'nuaa':
        measure_nuaa(root, args.per_class)
    elif args.dataset == 'midv':
        measure_midv(root, args.frames_per_condition, args.ocr_frames_per_condition)
    else:
        summarise()


if __name__ == '__main__':
    main()
