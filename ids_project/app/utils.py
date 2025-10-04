import os
import sys
import joblib

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(current_dir))

def load_pipeline(path):
    try:
        pipeline = joblib.load(path)
        return pipeline
    except Exception as e:
        raise e
