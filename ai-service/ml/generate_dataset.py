"""Benchmark-informed scenario simulation; no score thresholds or label flips.

Labels represent assumed adjudication outcomes of latent scenarios. The same
observed evidence may occur for different outcomes: six scores cannot encode
all facts an adjudicator knows. These are assumed outcomes, not human labels.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import truncnorm
try:
    from .schema import FEATURES, BOUNDS
except ImportError:
    from schema import FEATURES, BOUNDS
ROOT = Path(__file__).resolve().parent


def bounded_normal(rng, mean, sd, low, high, n):
    return truncnorm.rvs((low-mean)/sd, (high-mean)/sd,
                         loc=mean, scale=sd, size=n, random_state=rng)


def generate_dataset(config_path=None, *, seed=None, record_counts=None):
    cfg = json.loads(Path(config_path or ROOT/'generation_config.json').read_text())
    # Explicit independent evaluation draws; default training generation is unchanged.
    if seed is not None:
        cfg['seed'] = int(seed)
    if record_counts is not None:
        cfg['class_counts'] = dict(record_counts)
    rng = np.random.default_rng(cfg['seed'])
    base = ROOT/'data'/'benchmarks'
    frames = {name: pd.read_csv(base/f'{name}.csv') for name in
              ['lfw_face_match', 'nuaa_liveness', 'midv_image_quality', 'midv_ocr']}
    provenance = {name: {'rows': len(df), 'sha256': hashlib.sha256((base/f'{name}.csv').read_bytes()).hexdigest()}
                  for name, df in frames.items()}
    def moments(series):
        return [float(series.mean()), float(series.std())]
    face = {k: moments(g.faceMatchScore) for k, g in frames['lfw_face_match'].groupby('pair_type')}
    live = {k: moments(g.livenessScore) for k, g in frames['nuaa_liveness'].groupby('presentation')}
    ocr = frames['midv_ocr'].ocrConfidenceScore
    # Upper-half conditioning is an assumption about readable cases.
    clear = moments(ocr[ocr >= ocr.quantile(cfg['clear_ocr_quantile'])])
    q = frames['midv_image_quality'][['blurScore', 'brightnessScore', 'contrastScore']].to_numpy()
    q[:, 0] = np.log1p(q[:, 0])
    qmean, qcov = q.mean(axis=0), np.cov(q.T)
    sources = {'face': dict(face), 'liveness': dict(live), 'ocr_clear_conditional': clear,
               'ocr_all': moments(ocr), 'quality_transformed_mean': qmean.tolist(),
               'quality_transformed_covariance': qcov.tolist()}
    face.update(borderline=cfg['face_borderline'], difficult_impostor=cfg['face_difficult_impostor'])
    live.update(attack=live['photo_attack'], borderline=cfg['live_borderline'],
                difficult_attack=cfg['live_difficult_attack'])
    ocr_params = {'clear': clear, 'borderline': cfg['ocr_borderline'], 'mismatch': cfg['ocr_mismatch']}
    records, scenario_counts = [], {}
    for label, n in cfg['class_counts'].items():
        scenarios = cfg['scenarios'][label]
        assert np.isclose(sum(s[1] for s in scenarios), 1)
        counts = rng.multinomial(n, [s[1] for s in scenarios])
        for scenario, count in zip(scenarios, counts):
            name, _, f, l, o, poor = scenario
            scenario_counts[name] = int(count)
            # Continuous draws, not resampled benchmark rows. Shared covariance
            # and noise have no class-specific seeds or encoded identifiers.
            latent_q = rng.multivariate_normal(qmean, qcov, count)
            if poor:
                latent_q += cfg['poor_quality_shift']
            difficulty = (np.maximum(0, cfg['quality_logblur_reference']-latent_q[:, 0]) +
                          np.maximum(0, (cfg['quality_contrast_reference']-latent_q[:, 2])/cfg['quality_contrast_reference']))
            obs_q = latent_q + rng.normal(0, cfg['quality_observation_noise'], (count, 3))
            obs_q[:, 0] = np.expm1(obs_q[:, 0])
            values = np.column_stack([
                bounded_normal(rng, *face[f], 0, 100, count) + rng.normal(0, cfg['face_measurement_sd'], count),
                bounded_normal(rng, *live[l], 0, 1, count) + rng.normal(0, cfg['live_measurement_sd'], count),
                bounded_normal(rng, *ocr_params[o], 0, 1, count) - cfg['ocr_quality_penalty']*difficulty +
                rng.normal(0, cfg['ocr_measurement_sd'], count), obs_q])
            for i, (lo, hi) in enumerate(BOUNDS):
                values[:, i] = np.clip(values[:, i], lo, hi)
            frame = pd.DataFrame(values, columns=FEATURES)
            frame['target'] = label
            records.append(frame)
    df = pd.concat(records, ignore_index=True).sample(frac=1, random_state=cfg['seed']).reset_index(drop=True)
    assert len(df) == (10000 if record_counts is None else sum(record_counts.values()))
    return df, {'configuration': cfg, 'measured_sources': provenance,
                'measured_parameters': sources, 'scenario_counts': scenario_counts,
                'caveat': 'Truncated normals approximate benchmark moments; resulting moments differ after truncation. Joint KYC labels and cross-modality dependencies are assumptions. No benchmark is a joint KYC ground-truth dataset.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config')
    args = parser.parse_args()
    df, metadata = generate_dataset(args.config)
    path = ROOT/'data'/'kyc_synthetic_dataset_10000.csv'
    df.to_csv(path, index=False)
    path.with_suffix('.metadata.json').write_text(json.dumps(metadata, indent=2))
    print(path, df.target.value_counts().to_dict())
