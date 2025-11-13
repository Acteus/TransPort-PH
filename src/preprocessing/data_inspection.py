import pandas as pd
import os
import numpy as np
from datetime import datetime

data_dir = '../data'
output_dir = '../output'

# Create directories if they don't exist
os.makedirs(data_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# List of CSV files
files = [
    'worldbank_data.csv',
    'tomtom_traffic_data.csv',
    'uitp_modal_share.csv',
    'psa_data.csv',
    'dpwh_data.csv',
    'ltfrb_data.csv',
    'openaq_pm25.csv',
    'overpass_data.csv',
    'adb_projects.csv',
    'jica_mrt_lrt.csv',
    'sws_satisfaction.csv'
]

# Store all inspection results
inspection_results = []
detailed_report = []

print("=" * 80)
print("DATA INSPECTION REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

for file in files:
    path = os.path.join(data_dir, file)
    if os.path.exists(path):
        df = pd.read_csv(path)
        
        print(f"\n{'='*60}")
        print(f"Inspecting: {file}")
        print(f"{'='*60}")
        print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Duplicates: {df.duplicated().sum()}")
        
        # Store basic info
        file_info = {
            'file': file,
            'rows': df.shape[0],
            'columns': df.shape[1],
            'duplicates': df.duplicated().sum(),
            'total_missing': df.isnull().sum().sum(),
            'missing_pct': (df.isnull().sum().sum() / (df.shape[0] * df.shape[1]) * 100)
        }
        
        # Check dtypes
        print(f"\nData Types:")
        for col, dtype in df.dtypes.items():
            print(f"  {col}: {dtype}")
            # Check if year column is not numeric
            if 'year' in col.lower() and dtype not in ['int64', 'float64']:
                print(f"    WARNING: Year column should be numeric!")
        
        # Missing values
        print(f"\nMissing Values:")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            for col, count in missing[missing > 0].items():
                pct = (count / len(df)) * 100
                print(f"  {col}: {count} ({pct:.1f}%)")
        else:
            print("  No missing values")
        
        # Outliers in numeric columns
        print(f"\nOutlier Detection (>3 std):")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_count = 0
        for col in numeric_cols:
            if df[col].std() > 0:
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outliers = df[z_scores > 3]
                if len(outliers) > 0:
                    print(f"  {col}: {len(outliers)} outliers")
                    outlier_count += len(outliers)
        
        if outlier_count == 0:
            print("  No outliers detected")
        
        file_info['outliers'] = outlier_count
        
        # Country name checks
        if 'country' in df.columns:
            unique_countries = df['country'].unique()
            print(f"\nUnique Countries ({len(unique_countries)}):")
            print(f"  {', '.join(map(str, unique_countries[:10]))}")
            if len(unique_countries) > 10:
                print(f"  ... and {len(unique_countries) - 10} more")
            file_info['countries'] = len(unique_countries)
        
        # Year range check
        if 'year' in df.columns:
            try:
                year_col = pd.to_numeric(df['year'], errors='coerce')
                min_year = year_col.min()
                max_year = year_col.max()
                print(f"\nYear Range: {min_year} to {max_year}")
                file_info['year_range'] = f"{min_year}-{max_year}"
            except:
                print("\nYear Range: Could not parse years")
                file_info['year_range'] = "N/A"
        
        inspection_results.append(file_info)
        
    else:
        print(f"\nFile {file} not found")
        inspection_results.append({
            'file': file,
            'status': 'NOT FOUND'
        })

# Save summary report
print("\n" + "=" * 80)
print("GENERATING REPORTS...")
print("=" * 80)

summary_df = pd.DataFrame(inspection_results)
summary_df.to_csv(os.path.join(data_dir, 'data_inspection_summary.csv'), index=False)
print(f"Summary report saved to: {data_dir}/data_inspection_summary.csv")

# Create a detailed text report
report_path = os.path.join(data_dir, 'data_inspection_report.txt')
with open(report_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DATA INSPECTION REPORT\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    f.write(summary_df.to_string())
    f.write("\n\n" + "=" * 80 + "\n")
    f.write("RECOMMENDATIONS:\n")
    f.write("=" * 80 + "\n")
    f.write("1. Check files with high missing value percentages\n")
    f.write("2. Verify outliers are genuine or data errors\n")
    f.write("3. Standardize country names across datasets\n")
    f.write("4. Ensure year columns are numeric (int64)\n")
    f.write("5. Remove duplicate rows before merging\n")

print(f"Detailed report saved to: {report_path}")
print("\nData inspection complete.")