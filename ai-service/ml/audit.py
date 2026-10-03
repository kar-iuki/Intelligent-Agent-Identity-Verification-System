"""Dataset and split audits. Near-neighbour scale is fixed, never learned from test."""
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier
try:
    from .schema import FEATURES, CLASSES, SEED, BOUNDS
except ImportError:
    from schema import FEATURES, CLASSES, SEED, BOUNDS


def audit_and_split(df):
    assert list(df.columns) == FEATURES + ['target']
    assert set(df.target) == set(CLASSES)
    x = df[FEATURES].to_numpy()
    assert np.isfinite(x).all()
    for j, (lo, hi) in enumerate(BOUNDS):
        assert (x[:, j] >= lo).all()
        if hi is not None:
            assert (x[:, j] <= hi).all()
    duplicates = int(df.duplicated(FEATURES).sum())
    conflicts = int((df.groupby(FEATURES, dropna=False).target.nunique() > 1).sum())
    # Interpretable feature-specific tolerances; blur uses log1p since variance
    # spans orders of magnitude. L-infinity <=1 means close in ALL six channels.
    z = x.copy()
    z[:, 0] /= 0.1
    z[:, 1:3] /= 0.001
    z[:, 3] = np.log1p(z[:, 3])/0.01
    z[:, 4:] /= 0.1
    pairs = cKDTree(z).query_pairs(1, p=np.inf, output_type='ndarray')
    distances, _ = cKDTree(z).query(z, k=2, p=np.inf)
    # Fail closed before training: regenerate/group observations if these fire.
    assert duplicates == 0 and conflicts == 0, 'Exact duplicate data must be resolved before splitting'
    assert len(pairs) == 0, 'Suspicious near-duplicates must be grouped before splitting'
    train, hold = train_test_split(np.arange(len(df)), test_size=.3, stratify=df.target, random_state=SEED)
    val, test = train_test_split(hold, test_size=.5, stratify=df.target.iloc[hold], random_state=SEED)
    splits = {'train': train, 'validation': val, 'test': test}
    assert not (set(train)&set(val) or set(train)&set(test) or set(val)&set(test))
    hashes = pd.util.hash_pandas_object(df[FEATURES], index=False)
    crossings = {f'{a}_{b}': len(set(hashes.iloc[splits[a]]) & set(hashes.iloc[splits[b]]))
                 for a, b in [('train', 'test'), ('train', 'validation'), ('validation', 'test')]}
    assert not any(crossings.values())
    diagnostics = {'exact_duplicate_feature_vectors': duplicates, 'conflicting_label_vectors': conflicts,
                   'cross_split_duplicates': crossings, 'near_duplicate_pairs': len(pairs),
                   'near_duplicate_definition': 'All differences <= face .1, live .001, OCR .001, log1p(blur) .01, brightness .1, contrast .1',
                   'nearest_neighbor_tolerance_distance_percentiles': dict(zip(['min', 'p01', 'p50'], np.quantile(distances[:, 1], [0, .01, .5]).tolist()))}
    return splits, diagnostics


def training_signal_audit(df, train):
    """Detect trivial one-feature separators on TRAIN CV, never select by test."""
    cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
    scores = {}
    for feature in FEATURES:
        score = cross_val_score(DecisionTreeClassifier(max_depth=3, random_state=SEED,
                               class_weight='balanced'), df.iloc[train][[feature]], df.target.iloc[train],
                               cv=cv, scoring='f1_macro')
        scores[feature] = float(score.mean())
    return scores
