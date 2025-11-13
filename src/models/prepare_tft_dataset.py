import pandas as pd
from pytorch_forecasting import TimeSeriesDataSet
import os

data_dir = '../data'

df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))

# Assume time_idx is year, group_ids is country
df['time_idx'] = (df['year'] - df['year'].min()).astype(int)
df['group_ids'] = df['country']
df = df.dropna(subset=['time_idx', 'congestion_index'])  # Drop rows with NaN in key columns

print(f"\n{'='*80}")
print("CRITICAL WARNING: INSUFFICIENT DATA FOR TFT MODEL")
print(f"{'='*80}")
print(f"Total observations with congestion_index: {len(df)}")
print(f"Number of countries: {df['country'].nunique()}")
print(f"Countries: {df['country'].unique().tolist()}")
print(f"\nTFT models typically require:")
print(f"  - At least 1000+ observations for meaningful training")
print(f"  - Multiple time series (10+ countries/groups)")
print(f"  - Longer time periods (10+ years per group)")
print(f"\nRECOMMENDATIONS:")
print(f"  1. Use simpler models (ARIMA, Prophet, Panel Regression)")
print(f"  2. Gather more congestion_index data for more countries/years")
print(f"  3. Consider imputing missing congestion values")
print(f"  4. Use a different target variable with better coverage")
print(f"{'='*80}\n")

# Define dataset with minimal requirements (will likely fail or produce poor results)
dataset = TimeSeriesDataSet(
    df,
    time_idx='time_idx',
    target='congestion_index',
    group_ids=['group_ids'],
    min_encoder_length=1,
    max_encoder_length=2,  # Reduced from 5
    min_prediction_length=1,
    max_prediction_length=1,  # Reduced from 5
    static_categoricals=['group_ids'],
    time_varying_known_reals=['transit_investment_gdp'],
    time_varying_unknown_reals=['congestion_index', 'gdp_per_capita'],
    allow_missing_timesteps=True
)

# Save or something
print("TFT dataset prepared")