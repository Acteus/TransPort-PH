"""
Data Standardization
====================
This script standardizes country names and year ranges across all datasets.

Key operations:
1. Country name normalization (handle aliases, misspellings)
2. Year filtering (2000-2024 only)
3. Data type corrections
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

data_dir = '../data'

print("=" * 80)
print("DATA STANDARDIZATION")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ========================================================================
# COUNTRY NAME MAPPING
# ========================================================================

# Comprehensive country name mapping to handle various formats
country_map = {
    # Philippines variants
    'Philippines': 'Philippines',
    'PH': 'Philippines',
    'Republic of the Philippines': 'Philippines',
    'Philippine': 'Philippines',
    'philippines': 'Philippines',
    
    # Common country name standardizations
    'United States': 'United States',
    'USA': 'United States',
    'U.S.': 'United States',
    'US': 'United States',
    
    'United Kingdom': 'United Kingdom',
    'UK': 'United Kingdom',
    'U.K.': 'United Kingdom',
    'Great Britain': 'United Kingdom',
    
    'Korea, Rep.': 'South Korea',
    'Republic of Korea': 'South Korea',
    'Korea': 'South Korea',
    
    'China': 'China',
    'People\'s Republic of China': 'China',
    'PRC': 'China',
    
    'Russian Federation': 'Russia',
    'Russia': 'Russia',
    
    'Viet Nam': 'Vietnam',
    'Vietnam': 'Vietnam',
    
    # Add more as needed based on data
}

print(f"\nCountry mapping dictionary contains {len(country_map)} entries")

# ========================================================================
# STANDARDIZE FILES
# ========================================================================

files_to_standardize = [
    'worldbank_data.csv',
    'tomtom_traffic_data.csv',
    'uitp_modal_share.csv',
    'psa_data.csv',
    'overpass_data.csv',
    'openaq_pm25.csv',
    'ltfrb_data.csv',
    'jica_mrt_lrt.csv',
    'adb_projects.csv',
    'dpwh_data.csv',
    'sws_satisfaction.csv'
]

standardization_report = []

for file in files_to_standardize:
    path = os.path.join(data_dir, file)
    if not os.path.exists(path):
        print(f"\nFile {file} not found, skipping...")
        continue
    
    print(f"\n{'='*60}")
    print(f"Processing: {file}")
    print(f"{'='*60}")
    
    df = pd.read_csv(path)
    original_rows = len(df)
    
    file_report = {
        'file': file,
        'original_rows': original_rows,
        'rows_after': 0,
        'countries_standardized': 0,
        'years_filtered': 0,
        'invalid_years_removed': 0
    }
    
    # Standardize country names
    if 'country' in df.columns:
        unique_countries_before = df['country'].nunique()
        print(f"  Unique countries before: {unique_countries_before}")
        
        # Apply mapping
        df['country'] = df['country'].str.strip()  # Remove whitespace
        df['country'] = df['country'].replace(country_map)
        
        unique_countries_after = df['country'].nunique()
        print(f"  Unique countries after: {unique_countries_after}")
        
        if unique_countries_before != unique_countries_after:
            file_report['countries_standardized'] = unique_countries_before - unique_countries_after
            print(f"  ✓ Standardized {file_report['countries_standardized']} country name variants")
    
    # Standardize and filter years
    if 'year' in df.columns:
        # Convert to numeric
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
        # Check for invalid years
        invalid_years = df['year'].isnull().sum()
        if invalid_years > 0:
            print(f"  WARNING: {invalid_years} invalid year values (set to NaN)")
            file_report['invalid_years_removed'] = invalid_years
        
        # Filter to 2000-2024 range
        year_min = 2000
        year_max = 2024
        
        before_filter = len(df)
        df = df[(df['year'] >= year_min) & (df['year'] <= year_max)].copy()
        after_filter = len(df)
        
        rows_filtered = before_filter - after_filter
        if rows_filtered > 0:
            print(f"  Filtered {rows_filtered} rows outside {year_min}-{year_max} range")
            file_report['years_filtered'] = rows_filtered
        
        # Ensure year is integer
        df['year'] = df['year'].astype('Int64')  # Use nullable integer
        
        print(f"  Year range: {df['year'].min()} - {df['year'].max()}")
    
    # Final row count
    file_report['rows_after'] = len(df)
    
    # Save standardized data
    df.to_csv(path, index=False)
    print(f"  ✓ Saved standardized data ({len(df)} rows)")
    
    standardization_report.append(file_report)

# ========================================================================
# GENERATE REPORT
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING REPORT...")
print("=" * 80)

report_df = pd.DataFrame(standardization_report)
report_path = os.path.join(data_dir, 'standardization_report.csv')
report_df.to_csv(report_path, index=False)

# Create detailed text report
txt_report_path = os.path.join(data_dir, 'standardization_report.txt')
with open(txt_report_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("DATA STANDARDIZATION REPORT\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    f.write("STANDARDIZATION OPERATIONS:\n")
    f.write("-" * 80 + "\n")
    f.write("1. Country name normalization\n")
    f.write("   - Strip whitespace from country names\n")
    f.write("   - Apply country name mapping dictionary\n")
    f.write("   - Consolidate variants and aliases\n\n")
    f.write("2. Year filtering and validation\n")
    f.write("   - Convert year to numeric type\n")
    f.write("   - Filter to 2000-2024 range\n")
    f.write("   - Remove invalid/missing years\n")
    f.write("   - Ensure integer data type\n\n")
    f.write("=" * 80 + "\n")
    f.write("RESULTS:\n")
    f.write("=" * 80 + "\n\n")
    f.write(report_df.to_string(index=False))
    f.write("\n\n")
    f.write(f"Total files processed: {len(report_df)}\n")
    f.write(f"Total rows after standardization: {report_df['rows_after'].sum()}\n")
    f.write(f"Total rows filtered: {report_df['original_rows'].sum() - report_df['rows_after'].sum()}\n")
    f.write(f"Total country name variants standardized: {report_df['countries_standardized'].sum()}\n")

print(f"Report saved to: {report_path}")
print(f"Detailed report saved to: {txt_report_path}")

print("\n" + "=" * 80)
print("DATA STANDARDIZATION COMPLETE")
print("=" * 80)
print(f"Files processed: {len(report_df)}")
print(f"Total rows standardized: {report_df['rows_after'].sum()}")
print("=" * 80)