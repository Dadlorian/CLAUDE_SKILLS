"""
Business Analytics Python Script
"""
import pandas as pd
import numpy as np

def analyze_data(df):
    """Perform analytical calculations"""
    results = df.groupby('segment').agg({
        'metric': ['count', 'sum', 'mean', 'std']
    })
    return results

if __name__ == "__main__":
    df = pd.read_csv('data.csv')
    results = analyze_data(df)
    print(results)
