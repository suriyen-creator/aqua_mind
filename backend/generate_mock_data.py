import pandas as pd
import numpy as np

def generate_mock_bloom_data(n=1000, seed=42):
    np.random.seed(seed)
    
    # Features from 8.3
    ndci_mean_7d = np.random.uniform(0.3, 0.9, n)
    ndci_slope_7d = np.random.normal(0.02, 0.05, n)
    sst_anomaly = np.random.normal(1.5, 2.0, n)
    wind_speed_3d = np.random.uniform(5, 25, n)
    ndci_x_wind = ndci_mean_7d * wind_speed_3d
    
    # Sparse bloom label (imbalanced)
    # Bloom occurs when ndci is high, sst is high, and wind is moderate
    is_bloom = (
        (ndci_mean_7d > 0.7) & 
        (sst_anomaly > 1.0) & 
        (wind_speed_3d > 10) & 
        (wind_speed_3d < 20)
    ).astype(int)
    
    df = pd.DataFrame({
        'ndci_mean_7d': ndci_mean_7d,
        'ndci_slope_7d': ndci_slope_7d,
        'sst_anomaly': sst_anomaly,
        'wind_speed_3d': wind_speed_3d,
        'ndci_x_wind': ndci_x_wind,
        'is_bloom': is_bloom
    })
    
    return df

if __name__ == '__main__':
    df = generate_mock_bloom_data()
    df.to_csv('mock_data.csv', index=False)
    print(f"Generated {len(df)} records with {df['is_bloom'].sum()} bloom events.")
