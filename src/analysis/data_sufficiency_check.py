#!/usr/bin/env python3
"""
Data Sufficiency Analysis Report
=================================
This script generates a comprehensive report on data coverage and model viability,
implementing the analysis from DATA_COVERAGE_ANALYSIS.md

It answers the critical question: "What can we do with the data we have?"
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)

# Set up directories
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
data_dir = os.path.join(project_dir, 'data')
output_dir = os.path.join(project_dir, 'output')
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("DATA SUFFICIENCY ANALYSIS")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print("\nBased on: DATA_COVERAGE_ANALYSIS.md")

# Load data
df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))
print(f"\nLoaded panel data: {df.shape}")

# ============================================================================
# OVERALL DATA COVERAGE
# ============================================================================

print("\n" + "=" * 80)
print("1. OVERALL DATA COVERAGE")
print("=" * 80)

total_rows = len(df)
n_countries = df['country'].nunique()
year_min = df['year'].min()
year_max = df['year'].max()
year_range = int(year_max - year_min) + 1

print(f"\nPanel Structure:")
print(f"  • Total country-year observations: {total_rows:,}")
print(f"  • Number of countries: {n_countries}")
print(f"  • Year range: {year_min:.0f} - {year_max:.0f} ({year_range} years)")
print(f"  • Average observations per country: {total_rows/n_countries:.1f}")

# ============================================================================
# KEY OUTCOME VARIABLES COVERAGE
# ============================================================================

print("\n" + "=" * 80)
print("2. KEY OUTCOME VARIABLES COVERAGE")
print("=" * 80)

outcome_vars = {
    'congestion_index': 'Traffic Congestion Index',
    'modal_share_public': 'Public Transport Modal Share',
    'pm25': 'Air Quality (PM2.5)',
}

coverage_summary = []

for var, label in outcome_vars.items():
    if var in df.columns:
        n_obs = df[var].notna().sum()
        pct_coverage = (n_obs / total_rows) * 100
        n_countries_var = df[df[var].notna()]['country'].nunique()
        
        coverage_summary.append({
            'Variable': label,
            'Observations': n_obs,
            'Coverage %': pct_coverage,
            'Countries': n_countries_var
        })
        
        status = "✓" if pct_coverage > 50 else "⚠" if pct_coverage > 10 else "✗"
        print(f"\n{status} {label} ({var}):")
        print(f"  • Observations: {n_obs:,} / {total_rows:,} ({pct_coverage:.1f}%)")
        print(f"  • Countries: {n_countries_var}")
        
        if n_obs > 0:
            df_var = df[df[var].notna()]
            year_range_var = int(df_var['year'].max() - df_var['year'].min()) + 1
            print(f"  • Year range: {df_var['year'].min():.0f} - {df_var['year'].max():.0f} ({year_range_var} years)")

coverage_df = pd.DataFrame(coverage_summary)

# ============================================================================
# CONGESTION DATA DEEP DIVE
# ============================================================================

print("\n" + "=" * 80)
print("3. CONGESTION DATA DEEP DIVE (PRIMARY OUTCOME)")
print("=" * 80)

if 'congestion_index' in df.columns:
    df_cong = df[df['congestion_index'].notna()].copy()
    
    print(f"\nTotal observations with congestion data: {len(df_cong)}")
    
    # By country
    country_counts = df_cong.groupby('country').agg({
        'congestion_index': 'count',
        'year': ['min', 'max']
    }).reset_index()
    country_counts.columns = ['Country', 'Observations', 'Year Min', 'Year Max']
    country_counts['Year Range'] = (country_counts['Year Max'] - country_counts['Year Min']).astype(int) + 1
    country_counts = country_counts.sort_values('Observations', ascending=False)
    
    print("\nObservations by Country:")
    print(country_counts.to_string(index=False))
    
    # By year
    year_counts = df_cong.groupby('year').size().reset_index(name='Observations')
    print("\nObservations by Year:")
    print(year_counts.to_string(index=False))

# ============================================================================
# MODEL VIABILITY ASSESSMENT
# ============================================================================

print("\n" + "=" * 80)
print("4. MODEL VIABILITY ASSESSMENT")
print("=" * 80)
print("\nBased on DATA_COVERAGE_ANALYSIS.md requirements:\n")

# Model requirements from DATA_COVERAGE_ANALYSIS.md
model_requirements = {
    'Panel Fixed Effects': {
        'min_data': 20,
        'min_countries': 2,
        'min_years': 3,
        'complexity': 'Low',
        'interpretability': '⭐⭐⭐⭐⭐'
    },
    'ARIMA/SARIMAX': {
        'min_data': 10,
        'min_countries': 1,
        'min_years': 5,
        'complexity': 'Low',
        'interpretability': '⭐⭐⭐⭐'
    },
    'Facebook Prophet': {
        'min_data': 20,
        'min_countries': 1,
        'min_years': 3,
        'complexity': 'Low',
        'interpretability': '⭐⭐⭐⭐'
    },
    'Simple LSTM': {
        'min_data': 50,
        'min_countries': 3,
        'min_years': 5,
        'complexity': 'Medium',
        'interpretability': '⭐⭐⭐'
    },
    'TFT (Deep Learning)': {
        'min_data': 1000,
        'min_countries': 10,
        'min_years': 10,
        'complexity': 'High',
        'interpretability': '⭐⭐⭐'
    },
}

# Check viability for congestion_index
if 'congestion_index' in df.columns and df['congestion_index'].notna().sum() > 0:
    df_cong = df[df['congestion_index'].notna()]
    current_obs = len(df_cong)
    current_countries = df_cong['country'].nunique()
    
    # Calculate average years per country
    years_per_country = df_cong.groupby('country')['year'].apply(lambda x: x.max() - x.min() + 1)
    avg_years = years_per_country.mean()
    
    print(f"Current Data Status for Congestion Index:")
    print(f"  • Observations: {current_obs}")
    print(f"  • Countries: {current_countries}")
    print(f"  • Average years per country: {avg_years:.1f}")
    
    print("\n" + "-" * 80)
    print(f"{'Model':<25} {'Required':<15} {'Status':<10} {'Complexity':<12} {'Interpretability'}")
    print("-" * 80)
    
    viable_models = []
    
    for model, req in model_requirements.items():
        # Check if requirements met
        meets_data = current_obs >= req['min_data']
        meets_countries = current_countries >= req['min_countries']
        meets_years = avg_years >= req['min_years']
        
        viable = meets_data and meets_countries and meets_years
        status = "✓ VIABLE" if viable else "✗ NO"
        
        required_str = f"{req['min_data']}+ obs"
        
        print(f"{model:<25} {required_str:<15} {status:<10} {req['complexity']:<12} {req['interpretability']}")
        
        if viable:
            viable_models.append(model)
    
    print("-" * 80)
    
    if viable_models:
        print(f"\n✓ VIABLE MODELS: {', '.join(viable_models)}")
    else:
        print(f"\n✗ NO MODELS VIABLE - Need more data")

# ============================================================================
# DATA EXPANSION NEEDS
# ============================================================================

print("\n" + "=" * 80)
print("5. DATA EXPANSION NEEDS FOR TFT")
print("=" * 80)

if 'congestion_index' in df.columns:
    df_cong = df[df['congestion_index'].notna()]
    current_obs = len(df_cong)
    current_countries = df_cong['country'].nunique()
    
    # TFT requirements
    tft_req_obs = 1000
    tft_req_countries = 10
    tft_req_years = 10
    
    gap_obs = max(0, tft_req_obs - current_obs)
    gap_countries = max(0, tft_req_countries - current_countries)
    
    print(f"\nTo enable TFT model, you need:")
    print(f"  • Observations: {current_obs} → {tft_req_obs} (need {gap_obs} more, {gap_obs/current_obs*100:.0f}% increase)")
    print(f"  • Countries: {current_countries} → {tft_req_countries} (need {gap_countries} more)")
    print(f"  • Years per country: {avg_years:.1f} → {tft_req_years}")
    
    print(f"\nEstimated data gathering effort:")
    if gap_countries > 0:
        years_needed = max(tft_req_years, 10)
        print(f"  • Add {gap_countries} countries × {years_needed} years = {gap_countries * years_needed} observations")
        print(f"  • Total cost: ~${gap_countries * 50}-{gap_countries * 100} (TomTom data)")
        print(f"  • Time: 2-4 weeks (data procurement + cleaning)")
    else:
        print(f"  • You have enough countries!")
        print(f"  • Need more years of data for existing countries")
        print(f"  • Or add more observations per country")

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

print("\n" + "=" * 80)
print("6. RECOMMENDATIONS")
print("=" * 80)

if 'congestion_index' in df.columns:
    df_cong = df[df['congestion_index'].notna()]
    current_obs = len(df_cong)
    
    if current_obs < 100:
        print("\n⚠️  CRITICAL: VERY LIMITED DATA")
        print("\nRecommended Actions (in order of priority):")
        print("\n1. ✓ USE PANEL FIXED EFFECTS (Recommended)")
        print("   • Already in pipeline (causal_modeling_dowhy.py)")
        print("   • Works with current data")
        print("   • Provides causal estimates")
        print("   • Highly interpretable")
        
        print("\n2. → PHILIPPINES DEEP DIVE (Best ROI)")
        print("   • Focus on Metro Manila city-level data")
        print("   • Cost: ~$500 for TomTom data")
        print("   • Time: 3-4 weeks")
        print("   • Outcome: Publishable case study")
        print("   • Run: scripts/philippines_deep_dive.py")
        
        print("\n3. → EXPAND DATASET (Long-term)")
        print("   • Target: 20+ countries, 10+ years each")
        print("   • Cost: $2-5K for TomTom historical data")
        print("   • Time: 2-4 weeks")
        print("   • Then: Revisit TFT and deep learning")
        
        print("\n4. ✗ DO NOT use TFT with current data")
        print("   • Needs 1000+ observations")
        print("   • Current: {} observations".format(current_obs))
        print("   • Will overfit and produce unreliable results")
        
    elif current_obs < 1000:
        print("\n⚠️  MODERATE DATA: Use simpler models")
        print("\nRecommended Actions:")
        print("\n1. ✓ Panel Fixed Effects (for causal inference)")
        print("2. ✓ ARIMA/Prophet (for forecasting)")
        print("   • Run: scripts/simple_time_series_models.py")
        print("3. → Expand data before attempting TFT")
        print("4. → Consider Philippines deep dive")
    else:
        print("\n✓ SUFFICIENT DATA for deep learning!")
        print("\nRecommended Actions:")
        print("1. ✓ Continue with TFT training")
        print("2. ✓ Compare with simpler models as baselines")
        print("3. ✓ Consider ensemble approaches")

print("\n" + "=" * 80)
print("7. QUICK ACTION ITEMS")
print("=" * 80)

print("\nToday (can do right now):")
print("  1. Read: docs/DATA_COVERAGE_ANALYSIS.md")
print("  2. Read: docs/PROJECT_ASSESSMENT_AND_IMPROVEMENTS.md")
print("  3. Read: NEXT_STEPS.md")
print("  4. Run: python scripts/simple_time_series_models.py")

print("\nThis Week:")
print("  1. Decide: Which strategic option? (A: Data, B: Pivot, C: Accept, D: Philippines)")
print("  2. Test: Dashboard (streamlit run scripts/dashboard_app.py)")
print("  3. Document: Where did transit_investment_gdp come from?")

print("\nThis Month:")
print("  1. If Option D: Get Metro Manila city-level data (~$500)")
print("  2. If Option A: Expand to 20+ countries ($2-5K)")
print("  3. If Option C: Accept limitations, publish as exploratory")
print("  4. If Option B: Pivot research question")

# ============================================================================
# CREATE VISUALIZATION
# ============================================================================

print("\n" + "=" * 80)
print("8. GENERATING VISUALIZATIONS")
print("=" * 80)

fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

# Plot 1: Overall coverage
ax1 = fig.add_subplot(gs[0, 0])
if len(coverage_df) > 0:
    bars = ax1.barh(coverage_df['Variable'], coverage_df['Coverage %'], color='steelblue', alpha=0.7)
    ax1.axvline(x=50, color='green', linestyle='--', linewidth=2, label='Good (>50%)')
    ax1.axvline(x=10, color='orange', linestyle='--', linewidth=2, label='Poor (10-50%)')
    ax1.axvline(x=1, color='red', linestyle='--', linewidth=2, label='Critical (<10%)')
    ax1.set_xlabel('Coverage (%)', fontsize=11)
    ax1.set_title('Outcome Variables Coverage', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=9)
    ax1.grid(True, alpha=0.3, axis='x')
    
    # Add percentage labels
    for i, (idx, row) in enumerate(coverage_df.iterrows()):
        ax1.text(row['Coverage %'] + 1, i, f"{row['Coverage %']:.1f}%", 
                va='center', fontsize=10)

# Plot 2: Countries with data
ax2 = fig.add_subplot(gs[0, 1])
if 'congestion_index' in df.columns and df['congestion_index'].notna().sum() > 0:
    df_cong = df[df['congestion_index'].notna()]
    country_obs = df_cong.groupby('country').size().sort_values(ascending=False).head(10)
    ax2.barh(range(len(country_obs)), country_obs.values, color='coral', alpha=0.7)
    ax2.set_yticks(range(len(country_obs)))
    ax2.set_yticklabels(country_obs.index, fontsize=10)
    ax2.set_xlabel('Observations', fontsize=11)
    ax2.set_title('Top 10 Countries with Congestion Data', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='x')

# Plot 3: Temporal coverage
ax3 = fig.add_subplot(gs[1, :])
if 'congestion_index' in df.columns and df['congestion_index'].notna().sum() > 0:
    df_cong = df[df['congestion_index'].notna()]
    year_counts = df_cong.groupby('year').size()
    ax3.bar(year_counts.index, year_counts.values, color='seagreen', alpha=0.7, width=0.8)
    ax3.set_xlabel('Year', fontsize=11)
    ax3.set_ylabel('Observations', fontsize=11)
    ax3.set_title('Congestion Data Coverage Over Time', fontsize=13, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')

# Plot 4: Model viability matrix
ax4 = fig.add_subplot(gs[2, :])

if 'congestion_index' in df.columns and df['congestion_index'].notna().sum() > 0:
    df_cong = df[df['congestion_index'].notna()]
    current_obs = len(df_cong)
    
    models = list(model_requirements.keys())
    required = [req['min_data'] for req in model_requirements.values()]
    
    # Create bars
    x = np.arange(len(models))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, required, width, label='Required', color='lightcoral', alpha=0.7)
    bars2 = ax4.bar(x + width/2, [current_obs]*len(models), width, label='Current', color='lightgreen', alpha=0.7)
    
    ax4.set_ylabel('Observations', fontsize=11)
    ax4.set_title('Model Requirements vs. Current Data', fontsize=13, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(models, rotation=15, ha='right', fontsize=10)
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_yscale('log')
    
    # Add viability markers
    for i, (model, req) in enumerate(model_requirements.items()):
        if current_obs >= req['min_data']:
            ax4.text(i, current_obs * 1.5, '✓', fontsize=16, ha='center', color='green', fontweight='bold')
        else:
            ax4.text(i, current_obs * 1.5, '✗', fontsize=16, ha='center', color='red', fontweight='bold')

plt.suptitle('TransPort-PH: Data Sufficiency Analysis', fontsize=16, fontweight='bold', y=0.995)

output_path = os.path.join(output_dir, 'data_sufficiency_analysis.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"\n✓ Visualization saved to: {output_path}")

# ============================================================================
# SAVE DETAILED REPORT
# ============================================================================

report = f"""
DATA SUFFICIENCY ANALYSIS REPORT
{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Based on: DATA_COVERAGE_ANALYSIS.md

1. OVERALL DATA COVERAGE
{'=' * 80}
Total observations: {total_rows:,}
Countries: {n_countries}
Year range: {year_min:.0f} - {year_max:.0f} ({year_range} years)
Average obs per country: {total_rows/n_countries:.1f}

2. OUTCOME VARIABLES COVERAGE
{'=' * 80}
"""

if len(coverage_df) > 0:
    report += coverage_df.to_string(index=False)
else:
    report += "No outcome variable data found"

report += f"""

3. MODEL VIABILITY
{'=' * 80}
"""

if 'congestion_index' in df.columns and df['congestion_index'].notna().sum() > 0:
    df_cong = df[df['congestion_index'].notna()]
    current_obs = len(df_cong)
    current_countries = df_cong['country'].nunique()
    years_per_country = df_cong.groupby('country')['year'].apply(lambda x: x.max() - x.min() + 1)
    avg_years = years_per_country.mean()
    
    report += f"""
Current Status:
  • Observations: {current_obs}
  • Countries: {current_countries}
  • Average years: {avg_years:.1f}

Viable Models:
"""
    
    for model, req in model_requirements.items():
        meets_data = current_obs >= req['min_data']
        meets_countries = current_countries >= req['min_countries']
        meets_years = avg_years >= req['min_years']
        viable = meets_data and meets_countries and meets_years
        
        status = "✓ VIABLE" if viable else "✗ NOT VIABLE"
        report += f"  {model}: {status}\n"
        if not viable:
            reasons = []
            if not meets_data:
                reasons.append(f"need {req['min_data'] - current_obs} more obs")
            if not meets_countries:
                reasons.append(f"need {req['min_countries'] - current_countries} more countries")
            if not meets_years:
                reasons.append(f"need {req['min_years'] - avg_years:.1f} more years avg")
            report += f"    Reasons: {', '.join(reasons)}\n"

report += f"""

4. RECOMMENDATIONS
{'=' * 80}

IMMEDIATE (use now):
  ✓ Panel Fixed Effects Regression (causal_modeling_dowhy.py)
  ✓ Descriptive analysis and visualization

SHORT-TERM (if >50 obs with congestion):
  → ARIMA/SARIMAX per country (simple_time_series_models.py)
  → Facebook Prophet (simple_time_series_models.py)

MEDIUM-TERM (Philippines focus):
  → Get Metro Manila city-level data (~$500)
  → Run philippines_deep_dive.py
  → Mixed methods study (quant + qualitative)

LONG-TERM (for deep learning):
  → Expand to 1,000+ observations
  → Add 20+ countries
  → Get 10+ years per country
  → Then revisit TFT training

5. STRATEGIC OPTIONS
{'=' * 80}

Option A: Invest in Data ($2-5K, 2-4 weeks)
  - Purchase comprehensive TomTom data
  - Enable deep learning models
  - Best for: Serious research/publication

Option B: Pivot Research Question ($0, 1-2 weeks)
  - Make transit_investment_gdp the outcome
  - Use GDP/urbanization as predictors
  - Best for: Leveraging existing data

Option C: Accept Limitations ($0, 1 week)
  - Proceed as exploratory study
  - Document constraints
  - Best for: Portfolio/proof-of-concept

Option D: Philippines Deep Dive (~$500, 3-4 weeks) ⭐ RECOMMENDED
  - Focus on Metro Manila
  - Mixed methods approach
  - Best for: Feasible, publishable research

6. NEXT STEPS
{'=' * 80}

READ:
  • docs/DATA_COVERAGE_ANALYSIS.md (detailed model guidance)
  • docs/PROJECT_ASSESSMENT_AND_IMPROVEMENTS.md (full assessment)
  • NEXT_STEPS.md (actionable items)

RUN:
  • python scripts/simple_time_series_models.py (viable models)
  • python scripts/philippines_deep_dive.py (case study)
  • streamlit run scripts/dashboard_app.py (visualize results)

DECIDE:
  • Which strategic option? (A, B, C, or D)
  • Budget for data acquisition?
  • Timeline for completion?
  • Publication vs. portfolio?

OUTPUTS:
  • Visualization: {output_path}
  • This report: {os.path.join(data_dir, 'data_sufficiency_report.txt')}

{'=' * 80}
CONCLUSION: With {current_obs if 'congestion_index' in df.columns and df['congestion_index'].notna().sum() > 0 else 0} observations, focus on simpler models
and strategic data expansion before attempting deep learning.
{'=' * 80}
"""

report_path = os.path.join(data_dir, 'data_sufficiency_report.txt')
with open(report_path, 'w') as f:
    f.write(report)

print(f"\n✓ Detailed report saved to: {report_path}")

print("\n" + "=" * 80)
print("DATA SUFFICIENCY ANALYSIS COMPLETE")
print("=" * 80)
print("\nKey Findings:")
if 'congestion_index' in df.columns and df['congestion_index'].notna().sum() > 0:
    df_cong = df[df['congestion_index'].notna()]
    current_obs = len(df_cong)
    
    if current_obs < 100:
        print("  ✗ CRITICAL: Very limited data (<100 observations)")
        print("  → Use Panel FE, avoid TFT")
        print("  → Focus on Philippines or data expansion")
    elif current_obs < 1000:
        print("  ⚠ MODERATE: Use simpler models (100-1000 observations)")
        print("  → ARIMA, Prophet viable")
        print("  → Expand data before TFT")
    else:
        print("  ✓ SUFFICIENT: Deep learning viable (1000+ observations)")
        print("  → TFT can be trained")
        print("  → Compare with simpler baselines")
else:
    print("  ✗ NO congestion data found")
    print("  → Check data sources and gathering process")

print("\nSee report and visualization for detailed recommendations.")
print("=" * 80)
