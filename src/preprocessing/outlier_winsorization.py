"""
Outlier Detection and Winsorization
====================================
This script detects outliers in numeric variables and applies winsorization
at the 99th percentile to reduce the impact of extreme values while preserving
the overall distribution shape.

Winsorization is preferred over removal because:
1. Preserves sample size
2. Reduces but doesn't eliminate extreme values
3. Maintains relationships between variables
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("OUTLIER DETECTION AND WINSORIZATION")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

files = ['worldbank_data.csv', 'tomtom_traffic_data.csv', 'uitp_modal_share.csv', 
         'psa_data.csv', 'openaq_pm25.csv']

winsorization_report = []

for file in files:
    path = os.path.join(data_dir, file)
    if not os.path.exists(path):
        print(f"\nFile {file} not found, skipping...")
        continue
    
    print(f"\n{'='*60}")
    print(f"Processing: {file}")
    print(f"{'='*60}")
    
    df = pd.read_csv(path)
    print(f"Shape: {df.shape}")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Exclude year and index columns from winsorization
    exclude_cols = ['year', 'time_idx', 'index', 'id']
    numeric_cols = [col for col in numeric_cols if col not in exclude_cols]
    
    print(f"Numeric columns to winsorize: {len(numeric_cols)}")
    
    winsorization_summary = {
        'file': file,
        'total_columns': len(numeric_cols),
        'columns_winsorized': 0,
        'total_values_winsorized': 0
    }
    
    for col in numeric_cols:
        if df[col].std() > 0:  # Only process non-constant columns
            # Count outliers before winsorization (values > 99th percentile)
            percentile_99 = df[col].quantile(0.99)
            percentile_01 = df[col].quantile(0.01)
            
            outliers_upper = (df[col] > percentile_99).sum()
            outliers_lower = (df[col] < percentile_01).sum()
            
            if outliers_upper > 0 or outliers_lower > 0:
                # Winsorize both tails at 1st and 99th percentiles
                df[col] = np.where(df[col] > percentile_99, percentile_99, df[col])
                df[col] = np.where(df[col] < percentile_01, percentile_01, df[col])
                
                total_winsorized = outliers_upper + outliers_lower
                winsorization_summary['columns_winsorized'] += 1
                winsorization_summary['total_values_winsorized'] += total_winsorized
                
                if total_winsorized > 0:
                    print(f"  {col}:")
                    print(f"    Upper outliers (>{percentile_99:.2f}): {outliers_upper}")
                    print(f"    Lower outliers (<{percentile_01:.2f}): {outliers_lower}")
                    print(f"    Total winsorized: {total_winsorized}")
    
    # Save winsorized data
    df.to_csv(path, index=False)
    print(f"\n✓ Saved winsorized data to {file}")
    
    # Add to report
    winsorization_report.append(winsorization_summary)
    
    print(f"\nSummary for {file}:")
    print(f"  Columns processed: {winsorization_summary['total_columns']}")
    print(f"  Columns winsorized: {winsorization_summary['columns_winsorized']}")
    print(f"  Total values winsorized: {winsorization_summary['total_values_winsorized']}")

# ========================================================================
# SAVE WINSORIZATION REPORT
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING REPORT...")
print("=" * 80)

report_df = pd.DataFrame(winsorization_report)
report_path = os.path.join(data_dir, 'winsorization_report.csv')
report_df.to_csv(report_path, index=False)

# Create detailed text report
txt_report_path = os.path.join(data_dir, 'winsorization_report.txt')
with open(txt_report_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("OUTLIER DETECTION AND WINSORIZATION REPORT\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    f.write("WINSORIZATION STRATEGY:\n")
    f.write("-" * 80 + "\n")
    f.write("Method: Two-tailed winsorization at 1st and 99th percentiles\n")
    f.write("- Values above 99th percentile are capped at 99th percentile\n")
    f.write("- Values below 1st percentile are floored at 1st percentile\n")
    f.write("- Year and index columns are excluded from winsorization\n\n")
    f.write("RATIONALE:\n")
    f.write("-" * 80 + "\n")
    f.write("1. Reduces impact of extreme outliers on statistical models\n")
    f.write("2. Preserves sample size (no data deletion)\n")
    f.write("3. Maintains relative ordering of observations\n")
    f.write("4. More robust than trimming for panel data\n\n")
    f.write("=" * 80 + "\n")
    f.write("RESULTS:\n")
    f.write("=" * 80 + "\n\n")
    f.write(report_df.to_string(index=False))
    f.write("\n\n")
    f.write(f"Total files processed: {len(report_df)}\n")
    f.write(f"Total columns winsorized: {report_df['columns_winsorized'].sum()}\n")
    f.write(f"Total values winsorized: {report_df['total_values_winsorized'].sum()}\n")

print(f"Report saved to: {report_path}")
print(f"Detailed report saved to: {txt_report_path}")

print("\n" + "=" * 80)
print("OUTLIER WINSORIZATION COMPLETE")
print("=" * 80)
print(f"Files processed: {len(report_df)}")
print(f"Total values winsorized: {report_df['total_values_winsorized'].sum()}")
print("=" * 80)