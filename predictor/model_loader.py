import joblib

bundle = joblib.load("model.pkl")

MODEL = bundle["model"]
PREPROCESS = bundle["preprocess"]
NUM_FEATURES = bundle["num_features"]
CAT_FEATURES = bundle["cat_features"]
CLASSES = bundle["classes_"]