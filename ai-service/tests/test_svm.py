"""API contract tests using the actual saved artifacts; no image models loaded."""
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from flask import Flask
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from services import svmService
from routes.svmRoutes import svm_bp
from ml.schema import FEATURES, LEGACY_FEATURES, CLASSES, CLASS_KEYS


class SVMContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app = Flask(__name__)
        app.register_blueprint(svm_bp, url_prefix='/api/svm')
        cls.client = app.test_client()
        cls.scores = dict(zip(FEATURES, [84.5, .93, .88, .72, .81, .76]))

    def test_saved_artifact_prediction_parity_and_legacy_contract(self):
        self.assertTrue(svmService.model_loaded)
        for values in [[84.5, .93, .88, .72, .81, .76], [66, .6, .52, 62, 50, 21], [3, .1, .2, 25, 150, 45]]:
            scores = dict(zip(FEATURES, values))
            res = self.client.post('/api/svm/predict', json=scores)
            self.assertEqual(res.status_code, 200)
            result = res.get_json()
            scaled = svmService.scaler.transform(np.array([values]))
            probs = dict(zip(svmService.svm_model.classes_, svmService.svm_model.predict_proba(scaled)[0]))
            self.assertEqual(result['finalDecision'], svmService.svm_model.predict(scaled)[0])
            self.assertEqual(result['decisionBasis'], 'svm_model')
            self.assertEqual(set(result['probabilities']), set(CLASSES))
            self.assertAlmostEqual(sum(result['probabilities'].values()), 1)
            for name in CLASSES: self.assertAlmostEqual(result['probabilities'][name], probs[name])
            legacy = self.client.post('/api/svm/predict', json=dict(zip(LEGACY_FEATURES, values))).get_json()
            self.assertEqual(legacy['finalDecision'], dict(zip(CLASSES, CLASS_KEYS))[result['finalDecision']])
            for name, key in zip(CLASSES, ['verifiedProbability', 'reviewProbability', 'rejectedProbability']):
                self.assertAlmostEqual(legacy[key], probs[name])

    def test_rejects_missing_malformed_nonfinite_out_of_range(self):
        for name in FEATURES:
            missing = self.scores.copy(); missing.pop(name)
            self.assertEqual(self.client.post('/api/svm/predict', json=missing).status_code, 400)
            for bad in [None, True, '0.9', [], {}, float('nan'), float('inf'), -float('inf'), -1, 10**400]:
                with self.subTest(name=name, bad=str(bad)[:20]):
                    self.assertEqual(self.client.post('/api/svm/predict', json={**self.scores, name: bad}).status_code, 400)
        for name, value in [('face_match_score', 101), ('liveness_score', 1.01), ('ocr_confidence_score', 1.01),
                            ('brightness_score', 256), ('contrast_score', 128)]:
            self.assertEqual(self.client.post('/api/svm/predict', json={**self.scores, name: value}).status_code, 400)
        for body in [None, [], 'text', 5]:
            self.assertEqual(self.client.post('/api/svm/predict', json=body).status_code, 400)
        self.assertEqual(self.client.post('/api/svm/predict', data='{invalid', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/svm/predict', json={**self.scores, 'faceMatchScore': 84.5}).status_code, 400)
        self.assertEqual(self.client.post('/api/svm/predict', json={**self.scores, 'target': 'Verified'}).status_code, 400)

    def test_unavailable_has_no_silent_prediction(self):
        with patch.object(svmService, 'model_loaded', False):
            self.assertEqual(self.client.post('/api/svm/predict', json=self.scores).status_code, 503)
            self.assertEqual(self.client.get('/api/svm/status').status_code, 503)

    def test_class_probability_order_is_not_assumed(self):
        class ReorderedModel:
            classes_ = np.array(['Rejected', 'Verified', 'Manual Review'])
            def predict_proba(self, x): return np.array([[.1, .7, .2]])
            def predict(self, x): return np.array(['Verified'])
        with patch.object(svmService, 'svm_model', ReorderedModel()):
            result = svmService.predict_kyc_decision(self.scores)
        self.assertEqual(result['finalDecision'], 'Verified')
        self.assertEqual(result['probabilities'], {'Verified': .7, 'Manual Review': .2, 'Rejected': .1})

    def test_sharp_image_valid_without_assumed_decision(self):
        self.assertEqual(self.client.post('/api/svm/predict', json={**self.scores, 'blur_score': 1800}).status_code, 200)

    def test_saved_review_policy_is_honored_without_rewriting_probabilities(self):
        class ReviewPolicyModel:
            classes_ = np.array(['Rejected', 'Verified', 'Manual Review'])
            decision_policy = {'name': 'probability', 'verified_threshold': .6}
            def predict_proba(self, x): return np.array([[.1, .55, .35]])
            def predict(self, x): return np.array(['Manual Review'])
        with patch.object(svmService, 'svm_model', ReviewPolicyModel()):
            result = self.client.post('/api/svm/predict', json=self.scores).get_json()
        self.assertEqual(result['finalDecision'], 'Manual Review')
        self.assertEqual(result['probabilities']['Verified'], .55)
        self.assertEqual(result['probabilities']['Manual Review'], .35)
        self.assertEqual(result['decisionPolicy']['verified_threshold'], .6)


if __name__ == '__main__':
    unittest.main(verbosity=2)
