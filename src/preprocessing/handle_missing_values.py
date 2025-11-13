import pandas as pd
import os
from datetime import datetime

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

files = ['worldbank_data.csv', 'tomtom_traffic_data.csv', 'uitp_modal_share.csv', 'psa_data.csv']

# Define variable types for different imputation strategies
# Time-invariant: should be constant for each country (use forward fill within country)
# Smooth trends: GDP, Population (use interpolation)
# Sparse: modal share, transit data (use forward fill + backward fill)

time_invariant_vars = ['country']
smooth_trend_vars = ['gdp_per_capita', 'gdp_current_usd', 'population', 'gdp_growth']
sparse_vars = ['modal_share_public', 'transit_investment_gdp', 'rail_km_built', 'fleet_size']

missing_report = []

print("=" * 80)
print("MISSING VALUE HANDLING REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

for file in files:
    path = os.path.join(data_dir, file)
    if os.path.exists(path):
        df = pd.read_csv(path)
        
        print(f"\n{'='*60}")
        print(f"Processing: {file}")
        print(f"{'='*60}")
        
        # Record before state
        missing_before = df.isnull().sum().sum()
        missing_pct_before = (missing_before / (df.shape[0] * df.shape[1])) * 100
        
        print(f"Missing values before: {missing_before} ({missing_pct_before:.2f}%)")
        
        # Sort by country and year if applicable
        if 'country' in df.columns and 'year' in df.columns:
            df = df.sort_values(['country', 'year'])
            print("Data sorted by country and year")
            
            # Handle different variable types
            for col in df.columns:
                if col in time_invariant_vars:
                    continue  # Don't impute country names
                    
                elif col in smooth_trend_vars or any(term in col.lower() for term in ['gdp', 'population', 'growth']):
                    # Use interpolation for smooth economic indicators
                    # Group by country and interpolate within each country
                    df[col] = df.groupby('country')[col].transform(
                        lambda x: x.interpolate(method='linear', limit_direction='both')
                    )
                    
                elif col in sparse_vars or any(term in col.lower() for term in ['modal', 'transit', 'rail', 'fleet']):
                    # For sparse data, use forward fill then backward fill within country
                    df[col] = df.groupby('country')[col].transform(
                        lambda x: x.fillna(method='ffill').fillna(method='bfill')
                    )
                    
                else:
                    # For other numeric columns, use interpolation
                    if df[col].dtype in ['float64', 'int64']:
                        df[col] = df.groupby('country')[col].transform(
                            lambda x: x.interpolate(method='linear', limit_direction='both')
                        )
        else:
            # If no country/year structure, use simpler approach
            # Forward fill
            df = df.fillna(method='ffill')
            # Interpolate numeric columns
            df = df.interpolate(method='linear')
        
        # Fill any remaining missing values with column mean (only numeric)
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numeric_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].mean())
        
        # Record after state
        missing_after = df.isnull().sum().sum()
        missing_pct_after = (missing_after / (df.shape[0] * df.shape[1])) * 100
        
        print(f"Missing values after: {missing_after} ({missing_pct_after:.2f}%)")
        print(f"Reduction: {missing_before - missing_after} values")
        
        # Save processed file
        df.to_csv(path, index=False)
        print(f"✓ Saved processed file")
        
        # Store report
        missing_report.append({
            'file': file,
            'missing_before': missing_before,
            'missing_pct_before': missing_pct_before,
            'missing_after': missing_after,
            'missing_pct_after': missing_pct_after,
            'reduction': missing_before - missing_after
        })
    else:
        print(f"\nFile {file} not found")

# Save missing value report
print("\n" + "=" * 80)
print("GENERATING REPORT...")
print("=" * 80)

report_df = pd.DataFrame(missing_report)
report_path = os.path.join(data_dir, 'missing_values_report.csv')
report_df.to_csv(report_path, index=False)
print(f"Report saved to: {report_path}")

# Create detailed text report
txt_report_path = os.path.join(data_dir, 'missing_values_report.txt')
with open(txt_report_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("MISSING VALUE HANDLING REPORT\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    f.write("IMPUTATION STRATEGY:\n")
    f.write("-" * 80 + "\n")
    f.write("1. Time-invariant variables (country): No imputation\n")
    f.write("2. Smooth trends (GDP, Population): Linear interpolation within country\n")
    f.write("3. Sparse variables (modal share, transit data): Forward/backward fill within country\n")
    f.write("4. Other numeric: Interpolation + mean for remaining\n\n")
    f.write("=" * 80 + "\n")
    f.write("RESULTS:\n")
    f.write("=" * 80 + "\n\n")
    f.write(report_df.to_string(index=False))
    f.write("\n\n")
    f.write(f"Total reduction: {report_df['reduction'].sum()} missing values handled\n")

print(f"Detailed report saved to: {txt_report_path}")
print("\nMissing value handling complete.")