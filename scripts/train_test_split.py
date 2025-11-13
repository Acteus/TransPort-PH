"""
Train-Test Split
================
This script performs a time-based train-test split on the panel data.
Uses years 2000-2019 for training and 2020-2024 as holdout test set.

Time-based splitting is critical for time series and panel data to:
1. Prevent data leakage from future to past
2. Simulate realistic forecasting scenarios
3. Properly evaluate temporal generalization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("TRAIN-TEST SPLIT (TIME-BASED)")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ========================================================================
# SPLIT WORLDBANK DATA
# ========================================================================

print("\n" + "=" * 80)
print("SPLITTING WORLDBANK DATA")
print("=" * 80)

path = os.path.join(data_dir, 'worldbank_data.csv')
if os.path.exists(path):
    df = pd.read_csv(path)
    
    print(f"\nOriginal data shape: {df.shape}")
    print(f"Year range: {df['year'].min():.0f} - {df['year'].max():.0f}")
    print(f"Countries: {df['country'].nunique()}")
    
    # Define split point
    split_year = 2020
    
    # Create splits
    train = df[df['year'] < split_year].copy()
    test = df[df['year'] >= split_year].copy()
    
    print(f"\n--- Train Set (years < {split_year}) ---")
    print(f"Shape: {train.shape}")
    print(f"Year range: {train['year'].min():.0f} - {train['year'].max():.0f}")
    print(f"Countries: {train['country'].nunique()}")
    print(f"Percentage of total: {len(train) / len(df) * 100:.1f}%")
    
    print(f"\n--- Test Set (years >= {split_year}) ---")
    print(f"Shape: {test.shape}")
    print(f"Year range: {test['year'].min():.0f} - {test['year'].max():.0f}")
    print(f"Countries: {test['country'].nunique()}")
    print(f"Percentage of total: {len(test) / len(df) * 100:.1f}%")
    
    # Verify no data leakage
    assert train['year'].max() < test['year'].min(), "Data leakage detected!"
    print("\n✓ No data leakage: train years < test years")
    
    # Check country overlap
    train_countries = set(train['country'].unique())
    test_countries = set(test['country'].unique())
    common_countries = train_countries.intersection(test_countries)
    
    print(f"\n--- Country Coverage ---")
    print(f"Countries in train only: {len(train_countries - test_countries)}")
    print(f"Countries in test only: {len(test_countries - train_countries)}")
    print(f"Countries in both: {len(common_countries)}")
    
    if len(test_countries - train_countries) > 0:
        print(f"\nWARNING: {len(test_countries - train_countries)} countries in test but not train:")
        print(f"  {list(test_countries - train_countries)[:5]}")
    
    # Save splits
    train_path = os.path.join(data_dir, 'worldbank_train.csv')
    test_path = os.path.join(data_dir, 'worldbank_test.csv')
    
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)
    
    print(f"\n✓ Train set saved to: {train_path}")
    print(f"✓ Test set saved to: {test_path}")
    
    # Visualize split
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Observations per year
    train_year_counts = train['year'].value_counts().sort_index()
    test_year_counts = test['year'].value_counts().sort_index()
    
    axes[0].bar(train_year_counts.index, train_year_counts.values, 
                alpha=0.7, color='blue', label='Train', width=0.8)
    axes[0].bar(test_year_counts.index, test_year_counts.values, 
                alpha=0.7, color='red', label='Test', width=0.8)
    axes[0].axvline(x=split_year - 0.5, color='black', linestyle='--', 
                    linewidth=2, label=f'Split ({split_year})')
    axes[0].set_xlabel('Year', fontsize=12)
    axes[0].set_ylabel('Number of Observations', fontsize=12)
    axes[0].set_title('Train-Test Split by Year', fontsize=13)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3, axis='y')
    
    # Plot 2: Split proportions
    split_data = pd.DataFrame({
        'Set': ['Train', 'Test'],
        'Observations': [len(train), len(test)],
        'Percentage': [len(train) / len(df) * 100, len(test) / len(df) * 100]
    })
    
    colors = ['blue', 'red']
    axes[1].bar(split_data['Set'], split_data['Observations'], 
                alpha=0.7, color=colors)
    axes[1].set_ylabel('Number of Observations', fontsize=12)
    axes[1].set_title('Train-Test Split Distribution', fontsize=13)
    axes[1].grid(True, alpha=0.3, axis='y')
    
    # Add percentage labels on bars
    for i, row in split_data.iterrows():
        axes[1].text(i, row['Observations'], 
                    f"{row['Percentage']:.1f}%", 
                    ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'train_test_split.png'), 
                dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Visualization saved to: {output_dir}/train_test_split.png")
    
else:
    print(f"\nFile {path} not found")

# ========================================================================
# SPLIT CLEAN PANEL (if exists)
# ========================================================================

print("\n" + "=" * 80)
print("SPLITTING CLEAN PANEL DATA")
print("=" * 80)

clean_panel_path = os.path.join(data_dir, 'clean_panel.csv')
if os.path.exists(clean_panel_path):
    df_clean = pd.read_csv(clean_panel_path)
    
    print(f"\nOriginal clean panel shape: {df_clean.shape}")
    
    # Split
    train_clean = df_clean[df_clean['year'] < split_year].copy()
    test_clean = df_clean[df_clean['year'] >= split_year].copy()
    
    print(f"Train shape: {train_clean.shape}")
    print(f"Test shape: {test_clean.shape}")
    
    # Save
    train_clean.to_csv(os.path.join(data_dir, 'clean_panel_train.csv'), index=False)
    test_clean.to_csv(os.path.join(data_dir, 'clean_panel_test.csv'), index=False)
    
    print(f"✓ Clean panel splits saved")
else:
    print(f"\nClean panel not found (will be created later in pipeline)")

# ========================================================================
# GENERATE SPLIT REPORT
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING SPLIT REPORT")
print("=" * 80)

split_report = f"""
TRAIN-TEST SPLIT REPORT
{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SPLIT STRATEGY:
- Method: Time-based split
- Split year: {split_year}
- Train: years < {split_year} (2000-2019)
- Test: years >= {split_year} (2020-2024)

RATIONALE:
1. Temporal ordering preserved (no future data in training)
2. Simulates realistic forecasting scenario
3. Test period includes COVID-19 and recovery (2020+)
4. Sufficient train data (20 years) for model learning

WORLDBANK DATA:
- Original: {df.shape[0]} observations, {df['country'].nunique()} countries
- Train: {train.shape[0]} observations ({len(train) / len(df) * 100:.1f}%)
- Test: {test.shape[0]} observations ({len(test) / len(df) * 100:.1f}%)
- Countries in both sets: {len(common_countries)}

DATA QUALITY CHECKS:
✓ No data leakage: train years < test years
✓ Train set saved to: {train_path}
✓ Test set saved to: {test_path}
✓ Visualization saved to: {output_dir}/train_test_split.png

IMPORTANT NOTES:
1. All modeling should use only training data for fitting
2. Test data should be used ONLY for final evaluation
3. Validation splits (if needed) should come from training data
4. Feature engineering parameters (e.g., means, scales) should be 
   calculated from training data only and applied to test data

NEXT STEPS:
1. Verify no test data leakage in preprocessing steps
2. Use training data for EDA and feature selection
3. Save any normalization/scaling parameters from training data
4. Apply same transformations to test data using train parameters
"""

# Save report
report_path = os.path.join(data_dir, 'train_test_split_report.txt')
with open(report_path, 'w') as f:
    f.write(split_report)

print(split_report)
print(f"\n✓ Report saved to: {report_path}")

print("\n" + "=" * 80)
print("TRAIN-TEST SPLIT COMPLETE")
print("=" * 80)
print(f"Train: {len(train)} observations ({len(train) / len(df) * 100:.1f}%)")
print(f"Test: {len(test)} observations ({len(test) / len(df) * 100:.1f}%)")
print("=" * 80)