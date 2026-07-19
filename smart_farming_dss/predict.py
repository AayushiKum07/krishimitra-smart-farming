import os
import joblib
import numpy as np
import pandas as pd

# Feature order must match how the model was trained: N, P, K, temperature, humidity, ph, rainfall
FEATURE_COLUMNS = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']


class CropPredictor:
    def __init__(self, model_path=None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), 'models', 'crop_model.pkl')
        self.model_path = model_path
        self._model = None

    def _load_model(self):
        if self._model is None:
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found at {self.model_path}.")
            # joblib.load handles both joblib-saved and plain-pickle-saved sklearn models,
            # so it's a safe superset of pickle.load for this use case.
            self._model = joblib.load(self.model_path)

    def predict(self, n, p, k, temp, humidity, ph, rainfall):
        """
        Predicts crop and returns (crop_label, confidence_score)
        """
        label, _probs = self._predict_proba(n, p, k, temp, humidity, ph, rainfall)
        return label

    def _predict_proba(self, n, p, k, temp, humidity, ph, rainfall):
        self._load_model()
        features = pd.DataFrame(
            [[float(n), float(p), float(k), float(temp), float(humidity), float(ph), float(rainfall)]],
            columns=FEATURE_COLUMNS
        )
        probabilities = self._model.predict_proba(features)[0]
        classes = self._model.classes_
        prediction = self._model.predict(features)[0]
        return str(prediction), list(zip([str(c) for c in classes], [float(p) for p in probabilities]))

    def predict_top_k(self, n, p, k, temp, humidity, ph, rainfall, top_k=3):
        """
        Returns the top-k predicted crops ranked by confidence:
        [(label, confidence), (label, confidence), ...]
        """
        _label, class_probs = self._predict_proba(n, p, k, temp, humidity, ph, rainfall)
        ranked = sorted(class_probs, key=lambda pair: pair[1], reverse=True)
        return ranked[:top_k]

    def feature_importances(self):
        """
        Returns the model's global feature importances as a list of
        (feature_name, importance) sorted from most to least influential.
        This reflects what the trained Random Forest relies on overall,
        not a per-prediction explanation (which would require a library
        like SHAP and isn't part of this model).
        """
        self._load_model()
        importances = getattr(self._model, 'feature_importances_', None)
        if importances is None:
            return []
        pairs = list(zip(FEATURE_COLUMNS, [float(i) for i in importances]))
        return sorted(pairs, key=lambda pair: pair[1], reverse=True)


# Singleton instance so the model is loaded from disk only once per process
_predictor = None


def _get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = CropPredictor()
    return _predictor


def predict_crop(n, p, k, temp, humidity, ph, rainfall):
    """Returns (top_label, top_confidence)."""
    top3 = _get_predictor().predict_top_k(n, p, k, temp, humidity, ph, rainfall, top_k=1)
    return top3[0]


def predict_top_crops(n, p, k, temp, humidity, ph, rainfall, top_k=3):
    """Returns [(label, confidence), ...] ranked highest confidence first."""
    return _get_predictor().predict_top_k(n, p, k, temp, humidity, ph, rainfall, top_k=top_k)


def get_feature_importances():
    """Returns [(feature_name, importance), ...] sorted most to least influential."""
    return _get_predictor().feature_importances()
