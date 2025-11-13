import pandas as pd
import numpy as np
import os
from datetime import datetime

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("FEATURE ENGINEERING REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

feature_report = []

# Feature engineering for worldbank_data.csv
path = os.path.join(data_dir, 'worldbank_data.csv')
if os.path.exists(path):
    print(f"\nProcessing: worldbank_data.csv")
    print("-" * 60)
    
    df = pd.read_csv(path)
    original_cols = df.columns.tolist()
    features_created = []
    
    # 1. Log transformations
    if 'gdp_per_capita' in df.columns:
        df['log_gdp_per_capita'] = np.log(df['gdp_per_capita'] + 1)  # +1 to avoid log(0)
        features_created.append('log_gdp_per_capita')
        print("✓ Created log_gdp_per_capita")
    
    if 'population' in df.columns:
        df['log_population'] = np.log(df['population'] + 1)
        features_created.append('log_population')
        print("✓ Created log_population")
    
    # 2. Urbanization rate
    if 'urban_population' in df.columns and 'population' in df.columns:
        df['urbanization_rate'] = (df['urban_population'] / df['population']) * 100
        features_created.append('urbanization_rate')
        print("✓ Created urbanization_rate (urban_pop / total_pop * 100)")
    elif 'urban_population_pct' in df.columns:
        df['urbanization_rate'] = df['urban_population_pct']
        features_created.append('urbanization_rate')
        print("✓ Created urbanization_rate (from urban_population_pct)")
    
    # 3. Road per capita
    if 'road_length_km' in df.columns and 'population' in df.columns:
        df['road_per_capita'] = df['road_length_km'] / (df['population'] / 1000)  # per 1000 people
        features_created.append('road_per_capita')
        print("✓ Created road_per_capita (km per 1000 people)")
    
    # 4. GDP-based dummies
    if 'gdp_per_capita' in df.columns:
        median_gdp = df['gdp_per_capita'].median()
        df['high_gdp_dummy'] = (df['gdp_per_capita'] > median_gdp).astype(int)
        features_created.append('high_gdp_dummy')
        print(f"✓ Created high_gdp_dummy (threshold: ${median_gdp:,.2f})")
    
    # 5. Transit investment dummy
    # First, create a proxy for transit_investment_gdp if not exists
    if 'transit_investment_gdp' not in df.columns:
        if 'road_length_km' in df.columns and 'gdp_current_usd' in df.columns:
            # Proxy: infrastructure investment as % of GDP
            df['transit_investment_gdp'] = (df['road_length_km'] * 1e6) / df['gdp_current_usd'] * 100
            features_created.append('transit_investment_gdp')
            print("✓ Created transit_investment_gdp (proxy from road data)")
    
    if 'transit_investment_gdp' in df.columns:
        # High investment dummy: top 25% of investment levels
        threshold_75 = df['transit_investment_gdp'].quantile(0.75)
        df['high_invest_dummy'] = (df['transit_investment_gdp'] > threshold_75).astype(int)
        features_created.append('high_invest_dummy')
        print(f"✓ Created high_invest_dummy (top 25%, threshold: {threshold_75:.4f}%)")
        
        # Transit investment dummy: any non-zero investment
        df['transit_invest_dummy'] = (df['transit_investment_gdp'] > 0).astype(int)
        features_created.append('transit_invest_dummy')
        print("✓ Created transit_invest_dummy (non-zero investment)")
    
    # 6. Create lagged variables for transit investment
    if 'country' in df.columns and 'year' in df.columns and 'transit_investment_gdp' in df.columns:
        df = df.sort_values(['country', 'year'])
        df['transit_invest_lag1'] = df.groupby('country')['transit_investment_gdp'].shift(1)
        df['transit_invest_lag2'] = df.groupby('country')['transit_investment_gdp'].shift(2)
        features_created.extend(['transit_invest_lag1', 'transit_invest_lag2'])
        print("✓ Created transit_invest_lag1 and lag2")
    
    # 7. GDP growth rate (if not exists)
    if 'gdp_per_capita' in df.columns and 'country' in df.columns and 'year' in df.columns:
        df = df.sort_values(['country', 'year'])
        df['gdp_growth_rate'] = df.groupby('country')['gdp_per_capita'].pct_change() * 100
        features_created.append('gdp_growth_rate')
        print("✓ Created gdp_growth_rate (year-over-year % change)")
    
    # Save updated file
    df.to_csv(path, index=False)
    print(f"\n✓ Saved updated worldbank_data.csv")
    print(f"  Original columns: {len(original_cols)}")
    print(f"  New columns: {len(df.columns)}")
    print(f"  Features created: {len(features_created)}")
    
    feature_report.append({
        'file': 'worldbank_data.csv',
        'original_columns': len(original_cols),
        'new_columns': len(df.columns),
        'features_created': ', '.join(features_created)
    })

# Process PSA data for urbanization rate
psa_path = os.path.join(data_dir, 'psa_data.csv')
if os.path.exists(psa_path):
    print(f"\nProcessing: psa_data.csv")
    print("-" * 60)
    
    df_psa = pd.read_csv(psa_path)
    psa_features = []
    
    if 'urban_population_pct' in df_psa.columns and 'urbanization_rate' not in df_psa.columns:
        df_psa['urbanization_rate'] = df_psa['urban_population_pct']
        psa_features.append('urbanization_rate')
        print("✓ Created urbanization_rate")
    
    df_psa.to_csv(psa_path, index=False)
    print(f"✓ Saved updated psa_data.csv")
    
    if psa_features:
        feature_report.append({
            'file': 'psa_data.csv',
            'original_columns': len(df_psa.columns) - len(psa_features),
            'new_columns': len(df_psa.columns),
            'features_created': ', '.join(psa_features)
        })

# Save feature engineering report
print("\n" + "=" * 80)
print("GENERATING REPORT...")
print("=" * 80)

if feature_report:
    report_df = pd.DataFrame(feature_report)
    report_path = os.path.join(data_dir, 'feature_engineering_report.csv')
    report_df.to_csv(report_path, index=False)
    print(f"Report saved to: {report_path}")
    
    # Create detailed text report
    txt_report_path = os.path.join(data_dir, 'feature_engineering_report.txt')
    with open(txt_report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("FEATURE ENGINEERING REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write("FEATURES CREATED:\n")
        f.write("-" * 80 + "\n")
        f.write("1. log_gdp_per_capita: Log transformation of GDP per capita\n")
        f.write("2. log_population: Log transformation of population\n")
        f.write("3. urbanization_rate: Urban population as % of total\n")
        f.write("4. road_per_capita: Road length per 1000 people\n")
        f.write("5. high_gdp_dummy: Binary indicator for above-median GDP\n")
        f.write("6. transit_investment_gdp: Proxy for transit investment (if needed)\n")
        f.write("7. high_invest_dummy: Binary indicator for top 25% investment\n")
        f.write("8. transit_invest_dummy: Binary indicator for any investment\n")
        f.write("9. transit_invest_lag1: 1-year lagged investment\n")
        f.write("10. transit_invest_lag2: 2-year lagged investment\n")
        f.write("11. gdp_growth_rate: Year-over-year GDP growth %\n\n")
        f.write("=" * 80 + "\n")
        f.write("SUMMARY:\n")
        f.write("=" * 80 + "\n\n")
        f.write(report_df.to_string(index=False))
    
    print(f"Detailed report saved to: {txt_report_path}")

print("\nFeature engineering complete.")