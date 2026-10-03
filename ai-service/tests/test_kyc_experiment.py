"""Reproducibility, split isolation and serialized preprocessing checks."""
import sys
import unittest
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ml.generate_dataset import generate_dataset
from ml.schema import FEATURES
from ml.audit import audit_and_split


class ExperimentTests(unittest.TestCase):
    def test_saved_dataset_is_reproducible_and_has_no_hidden_predictors(self):
        generated, _ = generate_dataset()
        saved = pd.read_csv(ROOT/'ml/data/kyc_synthetic_dataset_10000.csv')
        pd.testing.assert_frame_equal(generated, saved, check_exact=False, rtol=1e-14, atol=1e-14)
        self.assertEqual(list(saved.columns), FEATURES+['target'])
        self.assertEqual(saved.target.value_counts().to_dict(), {'Verified': 6000, 'Manual Review': 2000, 'Rejected': 2000})

    def test_split_manifest_and_scaler_only_fit_training(self):
        df = pd.read_csv(ROOT/'ml/data/kyc_synthetic_dataset_10000.csv')
        splits, diagnostics = audit_and_split(df)
        manifest = pd.read_csv(ROOT/'ml/reports/split_manifest.csv')
        self.assertEqual({k: len(v) for k,v in splits.items()}, {'train':7000,'validation':1500,'test':1500})
        for name, idx in splits.items():
            self.assertEqual(set(manifest.loc[manifest.split == name, 'row_index']), set(idx))
        scaler = joblib.load(ROOT/'ml/models/scaler.pkl')
        self.assertEqual(scaler.n_samples_seen_, 7000)
        np.testing.assert_allclose(scaler.data_min_, df.iloc[splits['train']][FEATURES].min().to_numpy())
        np.testing.assert_allclose(scaler.data_max_, df.iloc[splits['train']][FEATURES].max().to_numpy())
        self.assertEqual(diagnostics['near_duplicate_pairs'], 0)
        self.assertFalse(any(diagnostics['cross_split_duplicates'].values()))


if __name__ == '__main__':
    unittest.main(verbosity=2)
