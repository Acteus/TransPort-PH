"""
Validation Script for Counterfactual Simulations
=================================================
This script validates the counterfactual simulation outputs by:
1. Checking internal consistency
2. Comparing with historical data
3. Testing sensitivity to parameters
4. Assessing plausibility of estimates
5. Generating validation report
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Directories
data_dir = '../data'
output_dir = '../output'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("COUNTERFACTUAL SIMULATION VALIDATION")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ========================================================================
# LOAD DATA
# ========================================================================

print("\n" + "=" * 80)
print("LOADING DATA")
print("=" * 80)

# Load simulation results
summary_path = os.path.join(output_dir, 'counterfactual_summary.csv')
if not os.path.exists(summary_path):
    print("\n✗ ERROR: Simulation results not found!")
    print("  Please run deep_counterfactual_simulation.py first")
    exit(1)

summary_df = pd.read_csv(summary_path)
print(f"\n✓ Loaded simulation summary: {len(summary_df)} scenarios")

# Load clean panel data
clean_panel_path = os.path.join(data_dir, 'clean_panel.csv')
if os.path.exists(clean_panel_path):
    df = pd.read_csv(clean_panel_path)
    print(f"✓ Loaded clean panel: {df.shape}")
else:
    print("⚠ Clean panel not found, using summary only")
    df = None

# Load individual scenario files
scenario_data = {}
for scenario_key in ['baseline', 'low_investment', 'moderate_increase', 
                     'high_investment', 'aggressive', 'optimal']:
    scenario_path = os.path.join(output_dir, f'counterfactual_{scenario_key}.csv')
    if os.path.exists(scenario_path):
        scenario_data[scenario_key] = pd.read_csv(scenario_path)
        print(f"✓ Loaded scenario: {scenario_key}")

print(f"\nTotal scenarios loaded: {len(scenario_data)}")

# ========================================================================
# VALIDATION TESTS
# ========================================================================

print("\n" + "=" * 80)
print("RUNNING VALIDATION TESTS")
print("=" * 80)

validation_results = {
    'tests': [],
    'passed': 0,
    'failed': 0,
    'warnings': 0
}

def add_test_result(test_name, passed, message, severity='info'):
    """Add a validation test result"""
    result = {
        'test': test_name,
        'passed': passed,
        'message': message,
        'severity': severity
    }
    validation_results['tests'].append(result)
    
    if severity == 'critical' and not passed:
        validation_results['failed'] += 1
        print(f"  ✗ FAIL: {test_name}")
        print(f"    {message}")
    elif not passed:
        validation_results['warnings'] += 1
        print(f"  ⚠ WARNING: {test_name}")
        print(f"    {message}")
    else:
        validation_results['passed'] += 1
        print(f"  ✓ PASS: {test_name}")

# ========================================================================
# TEST 1: Data Completeness
# ========================================================================

print("\n--- Test 1: Data Completeness ---")

# Check if all scenarios have data
missing_scenarios = []
for scenario in summary_df['Scenario']:
    scenario_key = scenario.lower().replace(' ', '_').replace('(', '').replace(')', '')
    scenario_key = scenario_key.replace('+', '').replace('-', '').replace('%', '')
    if not any(scenario_key in key for key in scenario_data.keys()):
        missing_scenarios.append(scenario)

if len(missing_scenarios) == 0:
    add_test_result(
        "All scenarios have detailed data",
        True,
        f"All {len(summary_df)} scenarios have complete data files"
    )
else:
    add_test_result(
        "All scenarios have detailed data",
        False,
        f"Missing data for scenarios: {', '.join(missing_scenarios)}",
        'warning'
    )

# ========================================================================
# TEST 2: Internal Consistency
# ========================================================================

print("\n--- Test 2: Internal Consistency ---")

# Check that impacts align with investment changes
consistency_issues = []
for _, row in summary_df.iterrows():
    if 'Multiplier' in str(row.get('Investment Multiplier', '')):
        continue
    
    try:
        multiplier = float(row.get('Investment Multiplier', 1.0))
        impact = row['Relative Impact (%)']
        
        # For increased investment, expect decreased congestion (negative impact)
        if multiplier > 1.0 and impact > 0:
            consistency_issues.append(f"{row['Scenario']}: increased investment but positive impact")
        elif multiplier < 1.0 and impact < 0:
            consistency_issues.append(f"{row['Scenario']}: decreased investment but negative impact")
    except:
        pass

if len(consistency_issues) == 0:
    add_test_result(
        "Investment-impact direction consistency",
        True,
        "All scenarios show expected direction of impact"
    )
else:
    add_test_result(
        "Investment-impact direction consistency",
        False,
        f"Issues found: {'; '.join(consistency_issues)}",
        'warning'
    )

# ========================================================================
# TEST 3: Magnitude Plausibility
# ========================================================================

print("\n--- Test 3: Magnitude Plausibility ---")

# Check if impacts are within reasonable bounds
# Based on literature, expect: 1% investment increase -> 0.1-0.5% congestion decrease
max_reasonable_elasticity = 0.8
implausible_scenarios = []

for _, row in summary_df.iterrows():
    try:
        multiplier = float(row.get('Investment Multiplier', 1.0))
        if multiplier == 1.0:
            continue
        
        impact = row['Relative Impact (%)']
        pct_investment_change = (multiplier - 1.0) * 100
        
        if pct_investment_change != 0:
            implied_elasticity = abs(impact / pct_investment_change)
            
            if implied_elasticity > max_reasonable_elasticity:
                implausible_scenarios.append(
                    f"{row['Scenario']}: elasticity={implied_elasticity:.2f}"
                )
    except:
        pass

if len(implausible_scenarios) == 0:
    add_test_result(
        "Impact magnitudes are plausible",
        True,
        f"All elasticities within reasonable range (<{max_reasonable_elasticity})"
    )
else:
    add_test_result(
        "Impact magnitudes are plausible",
        False,
        f"Implausible elasticities: {'; '.join(implausible_scenarios)}",
        'warning'
    )

# ========================================================================
# TEST 4: Monotonicity
# ========================================================================

print("\n--- Test 4: Monotonicity ---")

# Check if impacts monotonically increase with investment
sorted_df = summary_df.copy()
sorted_df['multiplier_numeric'] = pd.to_numeric(
    sorted_df['Investment Multiplier'], errors='coerce'
)
sorted_df = sorted_df.dropna(subset=['multiplier_numeric'])
sorted_df = sorted_df.sort_values('multiplier_numeric')

monotonic = True
for i in range(len(sorted_df) - 1):
    if sorted_df.iloc[i]['Relative Impact (%)'] > sorted_df.iloc[i+1]['Relative Impact (%)']:
        monotonic = False
        break

if monotonic:
    add_test_result(
        "Impact monotonically decreases with investment",
        True,
        "Higher investment consistently leads to lower congestion"
    )
else:
    add_test_result(
        "Impact monotonically decreases with investment",
        False,
        "Some scenarios break monotonicity - may indicate model limitations",
        'warning'
    )

# ========================================================================
# TEST 5: Historical Validation
# ========================================================================

print("\n--- Test 5: Historical Validation ---")

if df is not None and 'year' in df.columns:
    # Check if baseline matches historical averages
    recent_years = df['year'] >= df['year'].max() - 10
    historical_avg = df[recent_years]['congestion_index'].mean()
    
    baseline_row = summary_df[summary_df['Scenario'].str.contains('Baseline', case=False)]
    if len(baseline_row) > 0:
        baseline_sim = baseline_row['Baseline Congestion'].values[0]
        
        # Allow 20% deviation
        deviation = abs(baseline_sim - historical_avg) / historical_avg
        
        if deviation < 0.2:
            add_test_result(
                "Baseline matches historical data",
                True,
                f"Deviation: {deviation*100:.1f}% (within acceptable range)"
            )
        else:
            add_test_result(
                "Baseline matches historical data",
                False,
                f"Deviation: {deviation*100:.1f}% (exceeds 20% threshold)",
                'warning'
            )
else:
    add_test_result(
        "Baseline matches historical data",
        False,
        "Historical data not available for comparison",
        'info'
    )

# ========================================================================
# TEST 6: Cross-Country Variance
# ========================================================================

print("\n--- Test 6: Cross-Country Variance ---")

if len(scenario_data) > 0:
    # Check if there's reasonable variance across countries
    for scenario_key, data in scenario_data.items():
        if 'country' in data.columns and 'congestion_index_cf' in data.columns:
            country_impacts = data.groupby('country').apply(
                lambda x: ((x['congestion_index_cf'] - x['congestion_index']) / 
                          x['congestion_index'] * 100).mean()
            )
            
            variance = country_impacts.std()
            
            # Expect at least some variance (>1% std dev)
            if variance > 1.0:
                add_test_result(
                    f"Cross-country variance ({scenario_key})",
                    True,
                    f"Std dev: {variance:.2f}% (indicates country-specific effects)"
                )
            else:
                add_test_result(
                    f"Cross-country variance ({scenario_key})",
                    False,
                    f"Std dev: {variance:.2f}% (suspiciously uniform)",
                    'warning'
                )
            break  # Only test one scenario

# ========================================================================
# TEST 7: Missing Values
# ========================================================================

print("\n--- Test 7: Missing Values ---")

missing_issues = []
for scenario_key, data in scenario_data.items():
    missing_counts = data.isnull().sum()
    critical_cols = ['country', 'year', 'congestion_index', 'congestion_index_cf']
    
    for col in critical_cols:
        if col in missing_counts and missing_counts[col] > 0:
            missing_issues.append(f"{scenario_key}.{col}: {missing_counts[col]} missing")

if len(missing_issues) == 0:
    add_test_result(
        "No missing critical values",
        True,
        "All scenarios have complete data for key variables"
    )
else:
    add_test_result(
        "No missing critical values",
        False,
        f"Missing values found: {'; '.join(missing_issues)}",
        'critical'
    )

# ========================================================================
# GENERATE VALIDATION VISUALIZATIONS
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING VALIDATION VISUALIZATIONS")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Impact vs Investment relationship
ax = axes[0, 0]
valid_df = summary_df.copy()
valid_df['multiplier_numeric'] = pd.to_numeric(
    valid_df['Investment Multiplier'], errors='coerce'
)
valid_df = valid_df.dropna(subset=['multiplier_numeric'])

ax.scatter(valid_df['multiplier_numeric'], valid_df['Relative Impact (%)'],
          s=100, alpha=0.6, edgecolors='black')

# Add trend line
if len(valid_df) > 2:
    z = np.polyfit(valid_df['multiplier_numeric'], valid_df['Relative Impact (%)'], 1)
    p = np.poly1d(z)
    x_trend = np.linspace(valid_df['multiplier_numeric'].min(), 
                         valid_df['multiplier_numeric'].max(), 100)
    ax.plot(x_trend, p(x_trend), 'r--', linewidth=2, label='Trend')

ax.set_xlabel('Investment Multiplier', fontsize=12)
ax.set_ylabel('Relative Impact (%)', fontsize=12)
ax.set_title('Investment-Impact Relationship', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()

# Plot 2: Distribution of impacts
ax = axes[0, 1]
ax.hist(summary_df['Relative Impact (%)'], bins=15, alpha=0.7, 
        edgecolor='black', color='steelblue')
ax.axvline(x=0, color='red', linestyle='--', linewidth=2)
ax.set_xlabel('Relative Impact (%)', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.set_title('Distribution of Scenario Impacts', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

# Plot 3: Baseline vs Counterfactual comparison
ax = axes[1, 0]
x = np.arange(len(summary_df))
width = 0.35

bars1 = ax.bar(x - width/2, summary_df['Baseline Congestion'], width,
              label='Baseline', alpha=0.7, color='gray', edgecolor='black')
bars2 = ax.bar(x + width/2, summary_df['Counterfactual Congestion'], width,
              label='Counterfactual', alpha=0.7, color='steelblue', edgecolor='black')

ax.set_ylabel('Congestion Index', fontsize=12)
ax.set_title('Baseline vs Counterfactual Comparison', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(summary_df['Scenario'], rotation=45, ha='right', fontsize=8)
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

# Plot 4: Validation test results
ax = axes[1, 1]
test_summary = {
    'Passed': validation_results['passed'],
    'Warnings': validation_results['warnings'],
    'Failed': validation_results['failed']
}

colors = ['green', 'orange', 'red']
bars = ax.bar(test_summary.keys(), test_summary.values(), 
              color=colors, alpha=0.7, edgecolor='black')

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
           f'{int(height)}',
           ha='center', va='bottom', fontsize=14, fontweight='bold')

ax.set_ylabel('Number of Tests', fontsize=12)
ax.set_title('Validation Test Summary', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plot_path = os.path.join(output_dir, 'validation_results.png')
plt.savefig(plot_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ Validation plots saved to: {plot_path}")

# ========================================================================
# SENSITIVITY ANALYSIS
# ========================================================================

print("\n" + "=" * 80)
print("SENSITIVITY ANALYSIS")
print("=" * 80)

# Test sensitivity to elasticity parameter
elasticity_values = np.linspace(-0.1, -0.6, 10)
baseline_investment = 2.0  # Assume 2% of GDP baseline
high_investment = 4.0  # Double to 4%

sensitivity_results = []
for elasticity in elasticity_values:
    pct_change = (high_investment - baseline_investment) / baseline_investment * 100
    expected_impact = pct_change * elasticity
    sensitivity_results.append({
        'elasticity': elasticity,
        'impact': expected_impact
    })

sensitivity_df = pd.DataFrame(sensitivity_results)

print("\nElasticity Sensitivity:")
print(f"  Range: {elasticity_values.min():.2f} to {elasticity_values.max():.2f}")
print(f"  Impact range: {sensitivity_df['impact'].min():.1f}% to {sensitivity_df['impact'].max():.1f}%")

# Plot sensitivity
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(sensitivity_df['elasticity'], sensitivity_df['impact'], 
        marker='o', linewidth=2, markersize=8)
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax.axvline(x=-0.3, color='red', linestyle='--', alpha=0.5, label='Baseline elasticity')
ax.set_xlabel('Elasticity', fontsize=12)
ax.set_ylabel('Expected Impact (%)', fontsize=12)
ax.set_title('Sensitivity to Elasticity Parameter', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend()

sensitivity_plot_path = os.path.join(output_dir, 'sensitivity_analysis.png')
plt.savefig(sensitivity_plot_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"✓ Sensitivity plot saved to: {sensitivity_plot_path}")

# ========================================================================
# GENERATE VALIDATION REPORT
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING VALIDATION REPORT")
print("=" * 80)

# Calculate overall score
total_tests = len(validation_results['tests'])
critical_failures = sum(1 for t in validation_results['tests'] 
                       if t['severity'] == 'critical' and not t['passed'])

if critical_failures > 0:
    overall_status = "FAILED"
    status_symbol = "✗"
elif validation_results['warnings'] > 0:
    overall_status = "PASSED WITH WARNINGS"
    status_symbol = "⚠"
else:
    overall_status = "PASSED"
    status_symbol = "✓"

report = f"""
COUNTERFACTUAL SIMULATION VALIDATION REPORT
{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERALL STATUS: {status_symbol} {overall_status}

SUMMARY:
- Total tests: {total_tests}
- Passed: {validation_results['passed']} ({validation_results['passed']/total_tests*100:.1f}%)
- Warnings: {validation_results['warnings']} ({validation_results['warnings']/total_tests*100:.1f}%)
- Failed: {validation_results['failed']} ({validation_results['failed']/total_tests*100:.1f}%)

DETAILED TEST RESULTS:
{'-' * 80}
"""

for i, test in enumerate(validation_results['tests'], 1):
    status = "✓ PASS" if test['passed'] else ("✗ FAIL" if test['severity'] == 'critical' else "⚠ WARN")
    report += f"\n{i}. {test['test']}\n"
    report += f"   Status: {status}\n"
    report += f"   {test['message']}\n"

report += f"""
{'-' * 80}

SENSITIVITY ANALYSIS:
- Elasticity range tested: {elasticity_values.min():.2f} to {elasticity_values.max():.2f}
- Impact range: {sensitivity_df['impact'].min():.1f}% to {sensitivity_df['impact'].max():.1f}%
- Results show {"high" if sensitivity_df['impact'].std() > 5 else "moderate"} sensitivity to parameter choice

RECOMMENDATIONS:

1. DATA QUALITY:
   {"✓ Simulation data appears complete and consistent" if critical_failures == 0 else "⚠ Address critical data quality issues identified above"}

2. MODEL VALIDATION:
   {"✓ Impact estimates are within plausible ranges" if len(implausible_scenarios) == 0 else "⚠ Some elasticity estimates may be too high - consider refinement"}

3. UNCERTAINTY:
   - Consider reporting confidence intervals
   - Account for parameter uncertainty in elasticity estimates
   - Validate against additional historical periods if available

4. NEXT STEPS:
   - Conduct out-of-sample validation if additional data becomes available
   - Compare with alternative causal inference methods
   - Refine elasticity estimates using machine learning models
   - Incorporate heterogeneous treatment effects by country characteristics

OUTPUTS:
- Validation plots: {plot_path}
- Sensitivity analysis: {sensitivity_plot_path}
- This report: {os.path.join(data_dir, 'validation_report.txt')}

CONCLUSION:
{"The counterfactual simulations pass all critical validation tests and can be used for policy analysis, with appropriate caveats about uncertainty." if overall_status == "PASSED" else "Review and address the issues identified above before using simulation results for policy decisions."}
"""

# Save report
report_path = os.path.join(data_dir, 'validation_report.txt')
with open(report_path, 'w') as f:
    f.write(report)

print(report)
print(f"\n✓ Validation report saved to: {report_path}")

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
print(f"\nOverall Status: {status_symbol} {overall_status}")
print(f"View detailed results in: {report_path}")
print("=" * 80)
