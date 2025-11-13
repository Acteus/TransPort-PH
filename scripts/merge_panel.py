import pandas as pd
import os
from datetime import datetime

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("PANEL DATA MERGING REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Load base data (use full worldbank_data.csv to get all years including 2020-2024)
# This ensures we can merge TomTom data from 2015-2023 and future data
base_file = 'worldbank_data.csv'
print(f"\nLoading base data: {base_file} (using FULL dataset for maximum year coverage)")
df = pd.read_csv(os.path.join(data_dir, base_file))
print(f"  Shape: {df.shape}")
print(f"  Columns: {list(df.columns)}")

merge_report = []
initial_rows = len(df)

# Merge Congestion data - USE COMPREHENSIVE DATASET for maximum coverage
# Try comprehensive first, fallback to basic TomTom if not available
congestion_comp_path = os.path.join(data_dir, 'congestion_comprehensive.csv')
tomtom_path = os.path.join(data_dir, 'tomtom_traffic_data.csv')

if os.path.exists(congestion_comp_path):
    print("\n✓ Merging COMPREHENSIVE congestion data (includes ML estimates)...")
    congestion = pd.read_csv(congestion_comp_path)
    print(f"  Source: congestion_comprehensive.csv")
    print(f"  Coverage: {len(congestion)} country-year pairs, {congestion['country'].nunique()} countries")
    
    # Check data source distribution
    if 'data_source' in congestion.columns:
        actual_count = len(congestion[congestion['data_source'] == 'actual_tomtom'])
        estimated_count = len(congestion) - actual_count
        print(f"  Actual measurements: {actual_count} ({actual_count/len(congestion)*100:.1f}%)")
        print(f"  ML estimates: {estimated_count} ({estimated_count/len(congestion)*100:.1f}%)")
    
    before_merge = len(df)
    df = df.merge(congestion, on=['country', 'year'], how='left', suffixes=('', '_congestion'))
    print(f"  Rows after merge: {len(df)}")
    merge_report.append({
        'source': 'congestion_comprehensive.csv', 
        'rows_added': len(df) - before_merge,
        'coverage': f"{len(congestion)} obs, {congestion['country'].nunique()} countries"
    })
    
elif os.path.exists(tomtom_path):
    print("\nMerging TomTom traffic data (basic dataset)...")
    tomtom = pd.read_csv(tomtom_path)
    before_merge = len(df)
    df = df.merge(tomtom, on=['country', 'year'], how='left', suffixes=('', '_tomtom'))
    print(f"  Rows after merge: {len(df)} (added {len(df) - before_merge} from TomTom)")
    merge_report.append({'source': 'tomtom_traffic_data.csv', 'rows_added': len(df) - before_merge})
else:
    print("\n⚠️  WARNING: No congestion data found!")

# Merge UITP modal share data (city-level, aggregate to country-level)
uitp_path = os.path.join(data_dir, 'uitp_modal_share.csv')
if os.path.exists(uitp_path):
    print("\nMerging UITP modal share data...")
    uitp = pd.read_csv(uitp_path)
    print(f"  Raw UITP data: {len(uitp)} city-year observations")
    
    # Aggregate city-level data to country-level (take mean of cities in each country-year)
    if 'city' in uitp.columns:
        uitp_country = uitp.groupby(['country', 'year']).agg({
            'modal_share_public': 'mean',
            'modal_share_private': 'mean',
            'modal_share_walk': 'mean',
            'modal_share_bike': 'mean'
        }).reset_index()
        print(f"  Aggregated to country-level: {len(uitp_country)} country-year observations")
    else:
        uitp_country = uitp
    
    before_merge = len(df)
    df = df.merge(uitp_country, on=['country', 'year'], how='left', suffixes=('', '_uitp'))
    print(f"  Rows after merge: {len(df)}")
    merge_report.append({'source': 'uitp_modal_share.csv', 'rows_added': len(df) - before_merge})

# Merge PSA data
psa_path = os.path.join(data_dir, 'psa_data.csv')
if os.path.exists(psa_path):
    print("\nMerging PSA data...")
    psa = pd.read_csv(psa_path)
    before_merge = len(df)
    df = df.merge(psa, on=['country', 'year'], how='left', suffixes=('', '_psa'))
    print(f"  Rows after merge: {len(df)}")
    merge_report.append({'source': 'psa_data.csv', 'rows_added': len(df) - before_merge})

# Merge OpenAQ air quality data
openaq_path = os.path.join(data_dir, 'openaq_pm25.csv')
if os.path.exists(openaq_path):
    print("\nMerging OpenAQ air quality data...")
    openaq = pd.read_csv(openaq_path)
    before_merge = len(df)
    df = df.merge(openaq, on=['country', 'year'], how='left', suffixes=('', '_openaq'))
    print(f"  Rows after merge: {len(df)}")
    merge_report.append({'source': 'openaq_pm25.csv', 'rows_added': len(df) - before_merge})

# Merge Overpass (OSM) infrastructure data
overpass_path = os.path.join(data_dir, 'overpass_data.csv')
if os.path.exists(overpass_path):
    print("\nMerging Overpass infrastructure data...")
    overpass = pd.read_csv(overpass_path)
    # OSM data is static/current, so apply to all years for matching country
    if 'year' not in overpass.columns:
        # Merge on country only, OSM data applies to all years
        before_merge = len(df)
        df = df.merge(overpass.drop(columns=['note'], errors='ignore'), on='country', how='left', suffixes=('', '_overpass'))
        print(f"  Rows after merge: {len(df)} (OSM data applied to all years)")
    else:
        before_merge = len(df)
        df = df.merge(overpass, on=['country', 'year'], how='left', suffixes=('', '_overpass'))
        print(f"  Rows after merge: {len(df)}")
    merge_report.append({'source': 'overpass_data.csv', 'rows_added': len(df) - before_merge})

# Merge LTFRB data
ltfrb_path = os.path.join(data_dir, 'ltfrb_data.csv')
if os.path.exists(ltfrb_path):
    print("\nMerging LTFRB data...")
    ltfrb = pd.read_csv(ltfrb_path)
    before_merge = len(df)
    df = df.merge(ltfrb, on=['country', 'year'], how='left', suffixes=('', '_ltfrb'))
    print(f"  Rows after merge: {len(df)}")
    merge_report.append({'source': 'ltfrb_data.csv', 'rows_added': len(df) - before_merge})

# Merge JICA data
jica_path = os.path.join(data_dir, 'jica_mrt_lrt.csv')
if os.path.exists(jica_path):
    print("\nMerging JICA MRT/LRT data...")
    jica = pd.read_csv(jica_path)
    before_merge = len(df)
    df = df.merge(jica, on=['country', 'year'], how='left', suffixes=('', '_jica'))
    print(f"  Rows after merge: {len(df)}")
    merge_report.append({'source': 'jica_mrt_lrt.csv', 'rows_added': len(df) - before_merge})

# Merge ADB projects data
adb_path = os.path.join(data_dir, 'adb_projects.csv')
if os.path.exists(adb_path):
    print("\nMerging ADB projects data...")
    adb = pd.read_csv(adb_path)
    before_merge = len(df)
    df = df.merge(adb, on=['country', 'year'], how='left', suffixes=('', '_adb'))
    print(f"  Rows after merge: {len(df)}")
    merge_report.append({'source': 'adb_projects.csv', 'rows_added': len(df) - before_merge})

# Create/improve transit_investment_gdp if not already present or if needed
print("\nCalculating transit_investment_gdp...")
if 'transit_investment_gdp' not in df.columns or df['transit_investment_gdp'].isnull().all():
    # Multiple proxies to create transit investment estimate
    if 'adb_loan_amount' in df.columns and 'gdp_current_usd' in df.columns:
        df['transit_investment_gdp'] = (df['adb_loan_amount'] / df['gdp_current_usd']) * 100
        print("  Using ADB loan data as proxy")
    elif 'road_length_km' in df.columns and 'gdp_current_usd' in df.columns:
        # Fallback: infrastructure proxy
        df['transit_investment_gdp'] = (df['road_length_km'] * 1e6) / df['gdp_current_usd'] * 100
        print("  Using road infrastructure as proxy")
    else:
        df['transit_investment_gdp'] = 0
        print("  WARNING: Could not calculate transit_investment_gdp, set to 0")

# Ensure lagged variables exist
print("\nCreating lagged variables...")
df = df.sort_values(['country', 'year'])
if 'transit_invest_lag1' not in df.columns:
    df['transit_invest_lag1'] = df.groupby('country')['transit_investment_gdp'].shift(1)
    print("  Created transit_invest_lag1")

# Standardize column names
print("\nStandardizing column names...")
rename_map = {
    'congestion_level_pct': 'congestion_index',
    'congestion_level': 'congestion_index',
    'pm25_annual_mean': 'pm25',
    'pm25_value': 'pm25',
    'urban_population_pct': 'population_density',  # Approximate
    'modal_share': 'modal_share_public',
}

for old_name, new_name in rename_map.items():
    if old_name in df.columns and new_name not in df.columns:
        df = df.rename(columns={old_name: new_name})
        print(f"  Renamed: {old_name} -> {new_name}")

# Define final columns for clean panel (as per plan.txt)
# UPDATED: Added data_source and estimation_method for sensitivity analysis
final_columns = [
    'country', 'year', 'transit_investment_gdp', 'modal_share_public', 
    'congestion_index', 'gdp_per_capita', 'pm25', 'population_density', 
    'log_gdp_per_capita', 'transit_invest_lag1', 'high_invest_dummy',
    'data_source', 'estimation_method'  # NEW: Track data quality
]

# Check which columns are missing and add them with NaN
print("\nEnsuring all required columns exist...")
for col in final_columns:
    if col not in df.columns:
        df[col] = None
        print(f"  Added missing column: {col}")

# Select only final columns
df_clean = df[final_columns].copy()

print(f"\nFinal clean panel shape: {df_clean.shape}")
print(f"Columns: {list(df_clean.columns)}")

# Data Quality Summary
print("\n" + "=" * 80)
print("DATA QUALITY SUMMARY")
print("=" * 80)
if 'data_source' in df_clean.columns:
    print("\nCongestion data sources:")
    source_counts = df_clean['data_source'].value_counts()
    for source, count in source_counts.items():
        if pd.notna(source):
            print(f"  {source}: {count} ({count/len(df_clean)*100:.1f}%)")
    
    actual_with_data = len(df_clean[df_clean['data_source'] == 'actual_tomtom'])
    if actual_with_data > 0:
        print(f"\n✓ High-quality actual measurements: {actual_with_data} observations")
    
    estimated_with_data = len(df_clean[(df_clean['data_source'] != 'actual_tomtom') & df_clean['data_source'].notna()])
    if estimated_with_data > 0:
        print(f"✓ ML-estimated data: {estimated_with_data} observations")

print(f"\nCongestion coverage: {df_clean['congestion_index'].notna().sum()}/{len(df_clean)} ({df_clean['congestion_index'].notna().sum()/len(df_clean)*100:.1f}%)")
print(f"Modal share coverage: {df_clean['modal_share_public'].notna().sum()}/{len(df_clean)} ({df_clean['modal_share_public'].notna().sum()/len(df_clean)*100:.1f}%)")
print(f"PM2.5 coverage: {df_clean['pm25'].notna().sum()}/{len(df_clean)} ({df_clean['pm25'].notna().sum()/len(df_clean)*100:.1f}%)")

# Save clean panel
output_path = os.path.join(data_dir, 'clean_panel.csv')
df_clean.to_csv(output_path, index=False)
print(f"\n✓ Clean panel saved to: {output_path}")

# Generate report
print("\n" + "=" * 80)
print("GENERATING MERGE REPORT...")
print("=" * 80)

report_df = pd.DataFrame(merge_report)
report_path = os.path.join(data_dir, 'panel_merge_report.csv')
report_df.to_csv(report_path, index=False)

# Create detailed text report
txt_report_path = os.path.join(data_dir, 'panel_merge_report.txt')
with open(txt_report_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("PANEL DATA MERGING REPORT\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Base data: {base_file}\n")
    f.write(f"Initial rows: {initial_rows}\n")
    f.write(f"Final rows: {len(df_clean)}\n\n")
    f.write("=" * 80 + "\n")
    f.write("DATA SOURCES MERGED:\n")
    f.write("=" * 80 + "\n\n")
    if len(report_df) > 0:
        f.write(report_df.to_string(index=False))
    else:
        f.write("No additional sources merged\n")
    f.write("\n\n")
    f.write("=" * 80 + "\n")
    f.write("FINAL PANEL STRUCTURE:\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Columns: {', '.join(final_columns)}\n")
    f.write(f"Shape: {df_clean.shape[0]} rows × {df_clean.shape[1]} columns\n\n")
    f.write("Missing value summary:\n")
    f.write(df_clean.isnull().sum().to_string())

print(f"Report saved to: {report_path}")
print(f"Detailed report saved to: {txt_report_path}")
print("\nPanel merging complete.")