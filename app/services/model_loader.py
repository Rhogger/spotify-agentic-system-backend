import os
import pickle
import joblib


class ModelLoader:
    _instance = None
    _model = None
    _scaler = None
    _features = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load(self):
        if self._model is not None:
            return self._model, self._scaler, self._features

        base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../assets")
        )

        path_model = os.path.join(base_path, "models/music_recommender_model.joblib")
        path_scaler = os.path.join(base_path, "models/scaler.joblib")
        path_features = os.path.join(base_path, "models/music_model_features.pkl")

        self._model = joblib.load(path_model)
        self._scaler = joblib.load(path_scaler)
        with open(path_features, "rb") as f:
            self._features = pickle.load(f)

        return self._model, self._scaler, self._features

    def get_model(self):
        if self._model is None:
            self.load()
        return self._model

    def get_preprocessor(self):
        if self._scaler is None:
            self.load()
        return self._scaler

    def get_features(self):
        if self._features is None:
            self.load()
        return self._features


_loader = ModelLoader()


def get_model():
    return _loader.get_model()


def get_preprocessor():
    return _loader.get_preprocessor()


def get_features():
    return _loader.get_features()
