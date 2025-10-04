from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import LabelEncoder
import numpy as np

class CustomEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.encoders = {}

    def fit(self, X, y=None):
        
        for col in X.columns:
            if X[col].dtype == "object" or X[col].dtype == "str":
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                self.encoders[col] = le
        return self

    def transform(self, X):
        
        X = X.copy()
        for col, le in self.encoders.items():
            if col in X.columns:
                X[col] = X[col].astype(str)
                unknown_mask = ~X[col].isin(le.classes_)
                if unknown_mask.any():
                    
                    extended_classes = np.append(le.classes_, "<UNK>")
                    le.classes_ = extended_classes
                    X.loc[unknown_mask, col] = "<UNK>"
                X[col] = le.transform(X[col])
        return X
