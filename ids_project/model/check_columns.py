import pandas as pd
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "20 Percent Training Set.csv")


df = pd.read_csv(DATA_PATH)
print("📋 Columns in dataset:")
print(df.columns.tolist())
