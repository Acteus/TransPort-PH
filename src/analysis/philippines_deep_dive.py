#!/usr/bin/env python3
"""
Philippines Deep Dive Analysis
===============================
Comprehensive analysis of transit infrastructure impact in the Philippines,
specifically focusing on Metro Manila.

Analysis Components:
1. Historical timeline of MRT/LRT development
2. Before/after analysis of major projects
3. Integration of JICA, LTFRB, DPWH, PSA, SWS data
4. Comparative analysis with other Philippine cities
5. International comparison (Manila vs. Jakarta, Bangkok, KL)
6. Policy scenario simulations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from scipy import stats

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (16, 12)

# Directories
data_dir = '../data'
output_dir = '../output'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, 'philippines'), exist_ok=True)

print("=" * 80)
print("PHILIPPINES DEEP DIVE ANALYSIS")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ========================================================================
# LOAD DATA
# ========================================================================

print("\n" + "=" * 80)
print("LOADING DATA")
print("=" * 80)

# Load all Philippines-relevant datasets
clean_panel = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))
ph_panel = clean_panel[clean_panel['country'] == 'Philippines'].copy()
print(f"\n✓ Philippines panel data: {ph_panel.shape}")

jica_data = pd.read_csv(os.path.join(data_dir, 'jica_mrt_lrt.csv'))
print(f"✓ JICA MRT/LRT data: {jica_data.shape}")

ltfrb_data = pd.read_csv(os.path.join(data_dir, 'ltfrb_data.csv'))
print(f"✓ LTFRB data: {ltfrb_data.shape}")

psa_data = pd.read_csv(os.path.join(data_dir, 'psa_data.csv'))
print(f"✓ PSA demographic data: {psa_data.shape}")

sws_data = pd.read_csv(os.path.join(data_dir, 'sws_satisfaction.csv'))
print(f"✓ SWS satisfaction survey: {sws_data.shape}")

dpwh_data = pd.read_csv(os.path.join(data_dir, 'dpwh_data.csv'))
print(f"✓ DPWH infrastructure data: {dpwh_data.shape}")

# Display column information
print("\n" + "-" * 80)
print("DATASET STRUCTURES:")
print("-" * 80)
for name, df in [('JICA', jica_data), ('LTFRB', ltfrb_data), 
                  ('PSA', psa_data), ('SWS', sws_data), ('DPWH', dpwh_data)]:
    print(f"\n{name} columns: {list(df.columns)}")

# ========================================================================
# METRO MANILA TRANSIT TIMELINE
# ========================================================================

print("\n" + "=" * 80)
print("METRO MANILA TRANSIT INFRASTRUCTURE TIMELINE")
print("=" * 80)

# Define major milestones
milestones = [
    {'year': 1984, 'event': 'LRT-1 Opening', 'type': 'Opening', 'line': 'LRT-1', 
     'length_km': 15, 'description': 'First light rail line, Roosevelt to Baclaran'},
    
    {'year': 1999, 'event': 'MRT-3 Opening', 'type': 'Opening', 'line': 'MRT-3',
     'length_km': 16.9, 'description': 'Heavy rail along EDSA, North Ave to Taft'},
    
    {'year': 2003, 'event': 'LRT-2 Opening', 'type': 'Opening', 'line': 'LRT-2',
     'length_km': 13.8, 'description': 'East-West line, Recto to Santolan'},
    
    {'year': 2004, 'event': 'LRT-1 South Extension', 'type': 'Extension', 'line': 'LRT-1',
     'length_km': 5.7, 'description': 'Baclaran to Bacoor (planned)'},
    
    {'year': 2015, 'event': 'LRT-1 Cavite Extension', 'type': 'Extension', 'line': 'LRT-1',
     'length_km': 11.7, 'description': 'Construction started'},
    
    {'year': 2016, 'event': 'LRT-2 East Extension', 'type': 'Extension', 'line': 'LRT-2',
     'length_km': 4.0, 'description': 'Santolan to Antipolo'},
    
    {'year': 2020, 'event': 'MRT-7 Construction', 'type': 'New Line', 'line': 'MRT-7',
     'length_km': 22.8, 'description': 'Under construction (delayed)'},
]

milestones_df = pd.DataFrame(milestones)
print("\nMajor Transit Milestones:")
print(milestones_df[['year', 'event', 'line', 'length_km']].to_string(index=False))

# Calculate cumulative network length
milestones_df['cumulative_km'] = 0
current_km = 0
for idx, row in milestones_df.iterrows():
    if row['type'] in ['Opening', 'Extension']:
        current_km += row['length_km']
    milestones_df.at[idx, 'cumulative_km'] = current_km

print(f"\nTotal rail network by 2020: ~{current_km:.1f} km")

# ========================================================================
# RIDERSHIP ANALYSIS (IF AVAILABLE IN JICA DATA)
# ========================================================================

print("\n" + "=" * 80)
print("RIDERSHIP ANALYSIS")
print("=" * 80)

# Check JICA data structure
print("\nJICA data preview:")
print(jica_data.head(10))

# Attempt to extract ridership trends
if 'year' in jica_data.columns:
    jica_summary = jica_data.groupby('year').agg({
        col: 'sum' for col in jica_data.columns if 'ridership' in col.lower() or 'passenger' in col.lower()
    })
    
    if not jica_summary.empty:
        print("\nRidership trends:")
        print(jica_summary)
else:
    print("\n⚠ JICA data does not have year column - manual interpretation needed")

# ========================================================================
# CONGESTION ANALYSIS
# ========================================================================

print("\n" + "=" * 80)
print("CONGESTION TRENDS")
print("=" * 80)

if 'congestion_index' in ph_panel.columns:
    congestion_data = ph_panel[ph_panel['congestion_index'].notna()].sort_values('year')
    
    if len(congestion_data) > 0:
        print(f"\nCongestion data available: {len(congestion_data)} years")
        print(f"Years: {congestion_data['year'].min():.0f} - {congestion_data['year'].max():.0f}")
        print("\nCongestion index by year:")
        print(congestion_data[['year', 'congestion_index']].to_string(index=False))
        
        # Calculate trend
        if len(congestion_data) > 2:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                congestion_data['year'], 
                congestion_data['congestion_index']
            )
            print(f"\nTrend analysis:")
            print(f"  Slope: {slope:.4f} (change per year)")
            print(f"  R-squared: {r_value**2:.4f}")
            print(f"  P-value: {p_value:.4f}")
            
            if slope > 0:
                print(f"  Interpretation: Congestion WORSENING at {slope:.2f} points/year")
            else:
                print(f"  Interpretation: Congestion IMPROVING at {abs(slope):.2f} points/year")
    else:
        print("\n⚠ No congestion data available for Philippines")
else:
    print("\n⚠ No congestion_index column in panel data")

# ========================================================================
# BEFORE/AFTER ANALYSIS
# ========================================================================

print("\n" + "=" * 80)
print("BEFORE/AFTER ANALYSIS OF MAJOR PROJECTS")
print("=" * 80)

# For projects where we have outcome data
projects_to_analyze = [
    {'year': 2003, 'name': 'LRT-2 Opening', 'window': 3},
    {'year': 2016, 'name': 'LRT-2 East Extension', 'window': 2},
]

for project in projects_to_analyze:
    year = project['year']
    name = project['name']
    window = project['window']
    
    print(f"\n{name} ({year}):")
    print("-" * 60)
    
    # Get data before and after
    before = ph_panel[(ph_panel['year'] >= year - window) & 
                      (ph_panel['year'] < year)]
    after = ph_panel[(ph_panel['year'] > year) & 
                     (ph_panel['year'] <= year + window)]
    
    if len(before) == 0 or len(after) == 0:
        print("  ⚠ Insufficient data for analysis")
        continue
    
    # Compare key metrics
    metrics = ['congestion_index', 'transit_investment_gdp', 'gdp_per_capita', 
               'population_density', 'pm25']
    
    for metric in metrics:
        if metric in ph_panel.columns:
            before_mean = before[metric].mean()
            after_mean = after[metric].mean()
            
            if pd.notna(before_mean) and pd.notna(after_mean):
                change = ((after_mean - before_mean) / before_mean) * 100
                print(f"  {metric}:")
                print(f"    Before: {before_mean:.2f}")
                print(f"    After: {after_mean:.2f}")
                print(f"    Change: {change:+.2f}%")

# ========================================================================
# COMPARATIVE ANALYSIS: PHILIPPINES VS NEIGHBORS
# ========================================================================

print("\n" + "=" * 80)
print("INTERNATIONAL COMPARISON")
print("=" * 80)

# Compare Philippines with similar Southeast Asian countries
comparison_countries = ['Philippines', 'Indonesia', 'Thailand', 'Malaysia', 'Vietnam']

comparison_data = clean_panel[clean_panel['country'].isin(comparison_countries)].copy()

print(f"\nCountries in comparison: {comparison_data['country'].unique()}")

# Calculate average metrics by country
country_summary = comparison_data.groupby('country').agg({
    'congestion_index': 'mean',
    'transit_investment_gdp': 'mean',
    'gdp_per_capita': 'mean',
    'population_density': 'mean',
    'pm25': 'mean'
}).round(2)

print("\nCountry Comparison (Averages):")
print(country_summary)

# Rank Philippines
for col in country_summary.columns:
    if country_summary[col].notna().any():
        rank = country_summary[col].rank(ascending=False)['Philippines']
        total = country_summary[col].notna().sum()
        print(f"\nPhilippines rank in {col}: {rank:.0f} out of {total:.0f}")

# ========================================================================
# SOCIAL IMPACT: SWS SATISFACTION DATA
# ========================================================================

print("\n" + "=" * 80)
print("PUBLIC SATISFACTION TRENDS (SWS DATA)")
print("=" * 80)

print("\nSWS data preview:")
print(sws_data.head())

# Analyze satisfaction trends if year column exists
if 'year' in sws_data.columns:
    satisfaction_cols = [col for col in sws_data.columns if 'satisfaction' in col.lower() 
                        or 'rating' in col.lower()]
    
    if satisfaction_cols:
        print(f"\nSatisfaction metrics available: {satisfaction_cols}")
        
        for col in satisfaction_cols:
            if sws_data[col].notna().any():
                print(f"\n{col}:")
                print(f"  Mean: {sws_data[col].mean():.2f}")
                print(f"  Trend: {'Improving' if sws_data[col].iloc[-1] > sws_data[col].iloc[0] else 'Declining'}")

# ========================================================================
# POLICY SCENARIO SIMULATION
# ========================================================================

print("\n" + "=" * 80)
print("POLICY SCENARIO SIMULATIONS")
print("=" * 80)

# Define counterfactual scenarios
scenarios = {
    'baseline': {'name': 'Status Quo', 'investment_multiplier': 1.0},
    'mrt7_delay': {'name': 'MRT-7 Further Delayed', 'investment_multiplier': 0.7},
    'brt_system': {'name': 'Implement BRT Network', 'investment_multiplier': 1.3},
    'aggressive': {'name': 'Aggressive Investment', 'investment_multiplier': 2.0},
}

print("\nScenario Definitions:")
for key, scenario in scenarios.items():
    print(f"  {scenario['name']}: {scenario['investment_multiplier']}x investment")

# Simple projection based on historical trends
if len(congestion_data) > 2:
    latest_congestion = congestion_data['congestion_index'].iloc[-1]
    latest_year = congestion_data['year'].iloc[-1]
    
    # Project 5 years forward
    projection_years = [latest_year + i for i in range(1, 6)]
    
    print(f"\nProjections from {latest_year:.0f}:")
    print(f"  Baseline congestion: {latest_congestion:.2f}")
    
    # Assume investment reduces congestion (simple linear model)
    investment_elasticity = -0.05  # 1% investment increase → 0.05% congestion decrease
    
    for scenario_key, scenario in scenarios.items():
        multiplier = scenario['investment_multiplier']
        effect = (multiplier - 1.0) * investment_elasticity * latest_congestion
        projected = latest_congestion + effect
        
        print(f"  {scenario['name']}: {projected:.2f} ({effect:+.2f})")

# ========================================================================
# VISUALIZATIONS
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

fig = plt.figure(figsize=(20, 24))
gs = fig.add_gridspec(6, 2, hspace=0.3, wspace=0.3)

# 1. Transit Network Growth Timeline
ax1 = fig.add_subplot(gs[0, :])
ax1.plot(milestones_df['year'], milestones_df['cumulative_km'], 
         marker='o', linewidth=3, markersize=10, color='darkblue')
for idx, row in milestones_df.iterrows():
    ax1.annotate(row['line'], 
                xy=(row['year'], row['cumulative_km']),
                xytext=(5, 5), textcoords='offset points',
                fontsize=9, alpha=0.8)
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Cumulative Rail Network (km)', fontsize=12, fontweight='bold')
ax1.set_title('Metro Manila Rail Network Expansion (1984-2020)', 
             fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.fill_between(milestones_df['year'], milestones_df['cumulative_km'], 
                 alpha=0.2, color='darkblue')

# 2. Philippines vs. Regional Peers - Congestion
ax2 = fig.add_subplot(gs[1, 0])
congestion_comparison = comparison_data[comparison_data['congestion_index'].notna()].groupby('country')['congestion_index'].mean().sort_values()
if len(congestion_comparison) > 0:
    colors = ['#d62728' if c == 'Philippines' else '#1f77b4' for c in congestion_comparison.index]
    congestion_comparison.plot(kind='barh', ax=ax2, color=colors)
    ax2.set_xlabel('Average Congestion Index', fontsize=12, fontweight='bold')
    ax2.set_title('Congestion: Philippines vs. Regional Peers', fontsize=13, fontweight='bold')
    ax2.invert_yaxis()
else:
    ax2.text(0.5, 0.5, 'No congestion data available', 
            ha='center', va='center', transform=ax2.transAxes)

# 3. Philippines vs. Regional Peers - Transit Investment
ax3 = fig.add_subplot(gs[1, 1])
investment_comparison = comparison_data.groupby('country')['transit_investment_gdp'].mean().sort_values()
colors = ['#d62728' if c == 'Philippines' else '#1f77b4' for c in investment_comparison.index]
investment_comparison.plot(kind='barh', ax=ax3, color=colors)
ax3.set_xlabel('Average Transit Investment (% GDP)', fontsize=12, fontweight='bold')
ax3.set_title('Transit Investment: Philippines vs. Regional Peers', fontsize=13, fontweight='bold')
ax3.invert_yaxis()

# 4. Philippines Time Series - Multiple Metrics
ax4 = fig.add_subplot(gs[2, :])
ph_sorted = ph_panel.sort_values('year')
ax4_right = ax4.twinx()

if 'congestion_index' in ph_sorted.columns and ph_sorted['congestion_index'].notna().any():
    congestion_plot = ph_sorted[ph_sorted['congestion_index'].notna()]
    ax4.plot(congestion_plot['year'], congestion_plot['congestion_index'], 
            marker='o', linewidth=2, markersize=8, color='red', label='Congestion Index')

ax4_right.plot(ph_sorted['year'], ph_sorted['transit_investment_gdp'], 
              marker='s', linewidth=2, markersize=6, color='blue', 
              label='Transit Investment', alpha=0.7)

# Add milestone markers
for milestone in milestones:
    if milestone['year'] >= ph_sorted['year'].min() and milestone['year'] <= ph_sorted['year'].max():
        ax4.axvline(milestone['year'], color='green', linestyle='--', alpha=0.3, linewidth=2)

ax4.set_xlabel('Year', fontsize=12, fontweight='bold')
ax4.set_ylabel('Congestion Index', fontsize=12, fontweight='bold', color='red')
ax4_right.set_ylabel('Transit Investment (% GDP)', fontsize=12, fontweight='bold', color='blue')
ax4.set_title('Philippines: Congestion vs. Transit Investment Over Time', 
             fontsize=14, fontweight='bold')
ax4.tick_params(axis='y', labelcolor='red')
ax4_right.tick_params(axis='y', labelcolor='blue')
ax4.legend(loc='upper left')
ax4_right.legend(loc='upper right')
ax4.grid(True, alpha=0.3)

# 5. GDP per Capita Growth
ax5 = fig.add_subplot(gs[3, 0])
ax5.plot(ph_sorted['year'], ph_sorted['gdp_per_capita'], 
        marker='o', linewidth=2, color='green')
ax5.set_xlabel('Year', fontsize=12, fontweight='bold')
ax5.set_ylabel('GDP per Capita (USD)', fontsize=12, fontweight='bold')
ax5.set_title('Philippines GDP per Capita Growth', fontsize=13, fontweight='bold')
ax5.grid(True, alpha=0.3)
ax5.fill_between(ph_sorted['year'], ph_sorted['gdp_per_capita'], alpha=0.2, color='green')

# 6. Population Density
ax6 = fig.add_subplot(gs[3, 1])
ax6.plot(ph_sorted['year'], ph_sorted['population_density'], 
        marker='o', linewidth=2, color='purple')
ax6.set_xlabel('Year', fontsize=12, fontweight='bold')
ax6.set_ylabel('Population Density (per km²)', fontsize=12, fontweight='bold')
ax6.set_title('Philippines Population Density Trend', fontsize=13, fontweight='bold')
ax6.grid(True, alpha=0.3)

# 7. Comparative Time Series - Select Countries
ax7 = fig.add_subplot(gs[4, :])
for country in comparison_countries:
    country_data = comparison_data[
        (comparison_data['country'] == country) & 
        (comparison_data['congestion_index'].notna())
    ].sort_values('year')
    
    if len(country_data) > 0:
        linestyle = '--' if country == 'Philippines' else '-'
        linewidth = 3 if country == 'Philippines' else 2
        ax7.plot(country_data['year'], country_data['congestion_index'], 
                marker='o', label=country, linewidth=linewidth, linestyle=linestyle)

ax7.set_xlabel('Year', fontsize=12, fontweight='bold')
ax7.set_ylabel('Congestion Index', fontsize=12, fontweight='bold')
ax7.set_title('Congestion Trends: Regional Comparison', fontsize=14, fontweight='bold')
ax7.legend(fontsize=11)
ax7.grid(True, alpha=0.3)

# 8. Scenario Projections
ax8 = fig.add_subplot(gs[5, :])
if len(congestion_data) > 2:
    # Historical
    ax8.plot(congestion_data['year'], congestion_data['congestion_index'], 
            marker='o', linewidth=3, markersize=10, color='black', label='Historical', zorder=3)
    
    # Projections
    latest_year = congestion_data['year'].iloc[-1]
    latest_congestion = congestion_data['congestion_index'].iloc[-1]
    projection_years = [latest_year + i for i in range(1, 6)]
    
    for scenario_key, scenario in scenarios.items():
        multiplier = scenario['investment_multiplier']
        # Simple projection with diminishing returns
        projections = []
        current = latest_congestion
        
        for i, year in enumerate(projection_years):
            # Investment effect with diminishing returns
            effect = (multiplier - 1.0) * investment_elasticity * current * (0.9 ** i)
            current = current + effect + (slope * (i + 1))  # Add trend
            projections.append(current)
        
        ax8.plot([latest_year] + projection_years, 
                [latest_congestion] + projections,
                marker='o', linewidth=2, linestyle='--', label=scenario['name'], alpha=0.7)
    
    ax8.axvline(latest_year, color='gray', linestyle=':', linewidth=2, alpha=0.5)
    ax8.text(latest_year, ax8.get_ylim()[1]*0.95, 'Projection →', 
            fontsize=10, ha='center')
    
    ax8.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax8.set_ylabel('Projected Congestion Index', fontsize=12, fontweight='bold')
    ax8.set_title('Policy Scenario Projections (2024-2028)', fontsize=14, fontweight='bold')
    ax8.legend(fontsize=10, loc='best')
    ax8.grid(True, alpha=0.3)

plt.suptitle('PHILIPPINES TRANSPORT INFRASTRUCTURE: COMPREHENSIVE ANALYSIS', 
            fontsize=18, fontweight='bold', y=0.995)

output_path = os.path.join(output_dir, 'philippines', 'philippines_comprehensive_analysis.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Comprehensive visualization saved: {output_path}")

# ========================================================================
# GENERATE DETAILED REPORT
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING DETAILED REPORT")
print("=" * 80)

report_path = os.path.join(data_dir, 'philippines_deep_dive_report.txt')

with open(report_path, 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("PHILIPPINES TRANSPORT INFRASTRUCTURE: DEEP DIVE ANALYSIS\n")
    f.write("=" * 80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("EXECUTIVE SUMMARY:\n")
    f.write("-" * 80 + "\n")
    f.write(f"- Data coverage: {ph_panel['year'].min():.0f} - {ph_panel['year'].max():.0f}\n")
    f.write(f"- Observations: {len(ph_panel)}\n")
    f.write(f"- Rail network growth: {current_km:.1f} km (1984-2020)\n")
    f.write(f"- Major projects: {len(milestones)} milestones tracked\n\n")
    
    f.write("KEY FINDINGS:\n")
    f.write("-" * 80 + "\n")
    
    if len(congestion_data) > 2:
        f.write(f"1. CONGESTION TRENDS:\n")
        f.write(f"   - Congestion trend: {slope:.4f} points/year\n")
        f.write(f"   - Interpretation: {'Worsening' if slope > 0 else 'Improving'}\n")
        f.write(f"   - Statistical significance: {'Yes' if p_value < 0.05 else 'No'} (p={p_value:.4f})\n\n")
    
    f.write(f"2. TRANSIT INFRASTRUCTURE:\n")
    f.write(f"   - LRT-1: Opened 1984, {milestones_df[milestones_df['line']=='LRT-1']['length_km'].sum():.1f} km\n")
    f.write(f"   - MRT-3: Opened 1999, 16.9 km\n")
    f.write(f"   - LRT-2: Opened 2003, {milestones_df[milestones_df['line']=='LRT-2']['length_km'].sum():.1f} km\n\n")
    
    f.write(f"3. REGIONAL COMPARISON:\n")
    rank_data = country_summary.loc['Philippines']
    for col in ['congestion_index', 'transit_investment_gdp']:
        if pd.notna(rank_data[col]):
            rank = country_summary[col].rank(ascending=False)['Philippines']
            total = country_summary[col].notna().sum()
            f.write(f"   - {col}: Rank {rank:.0f}/{total:.0f} among peers\n")
    f.write("\n")
    
    f.write("POLICY RECOMMENDATIONS:\n")
    f.write("-" * 80 + "\n")
    f.write("1. Accelerate MRT-7 completion to expand network coverage\n")
    f.write("2. Implement Bus Rapid Transit (BRT) as cost-effective alternative\n")
    f.write("3. Improve first/last-mile connectivity to existing rail stations\n")
    f.write("4. Integrate fare systems across LRT/MRT lines\n")
    f.write("5. Invest in maintenance to improve service reliability\n\n")
    
    f.write("DATA LIMITATIONS:\n")
    f.write("-" * 80 + "\n")
    f.write(f"- Congestion data: Only {len(congestion_data)} years available\n")
    f.write("- No city-level disaggregation (Metro Manila vs. other cities)\n")
    f.write("- Limited ridership data (dependent on JICA sources)\n")
    f.write("- No detailed project cost data\n\n")
    
    f.write("NEXT STEPS:\n")
    f.write("-" * 80 + "\n")
    f.write("1. Obtain Metro Manila-specific congestion data from TomTom\n")
    f.write("2. Gather detailed ridership data from DOTr/LRTA/MRTC\n")
    f.write("3. Conduct surveys on user satisfaction and mode choice\n")
    f.write("4. Analyze spatial distribution of congestion relief\n")
    f.write("5. Model network effects of proposed MRT-7 and other projects\n")

print(f"\n✓ Report saved: {report_path}")

print("\n" + "=" * 80)
print("PHILIPPINES DEEP DIVE COMPLETE")
print("=" * 80)
print("\nOutputs:")
print(f"- Comprehensive visualization: {output_path}")
print(f"- Detailed report: {report_path}")
print("\nKey Insights:")
print(f"- Rail network expanded from 15 km (1984) to ~{current_km:.1f} km (2020)")
if len(congestion_data) > 2:
    print(f"- Congestion trend: {slope:.4f} points/year ({'worsening' if slope > 0 else 'improving'})")
print(f"- Philippines has {len(milestones)} major transit milestones since 1984")
print("\nRecommendation: Focus on Metro Manila city-level data for richer analysis")

