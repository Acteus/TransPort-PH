"""
Causal Modeling with DoWhy
===========================
This script builds a causal graph, performs identification checks, and estimates causal effects
of transit investment on congestion and air quality outcomes.

Treatment: transit_investment_gdp
Outcomes: congestion_index, pm25
Confounders: gdp_per_capita, population_density, log_gdp_per_capita
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dowhy import CausalModel
import networkx as nx
import os
from datetime import datetime

# Set up directories
data_dir = '../data'
output_dir = '../output'
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("CAUSAL MODELING WITH DOWHY")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Load clean panel data
df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))
print(f"\nLoaded clean panel: {df.shape}")
print(f"Countries: {df['country'].nunique()}")
print(f"Year range: {df['year'].min():.0f} - {df['year'].max():.0f}")

# ========================================================================
# DEFINE CAUSAL VARIABLES
# ========================================================================

# Treatment: Transit investment as % of GDP
treatment = 'transit_investment_gdp'

# Outcomes: We'll analyze two separate outcomes
outcomes = ['congestion_index', 'pm25']

# Confounders: Variables that affect both treatment and outcomes
confounders = [
    'gdp_per_capita',           # Economic development affects both investment capacity and outcomes
    'population_density',        # Population density drives both need for transit and congestion
    'log_gdp_per_capita',       # Log-transformed GDP to capture non-linear effects
]

# Additional controls (not confounders but helpful)
additional_controls = [
    'year',                     # Time trends
]

print("\n" + "=" * 80)
print("CAUSAL STRUCTURE DEFINITION")
print("=" * 80)
print(f"\nTreatment variable: {treatment}")
print(f"Outcome variables: {', '.join(outcomes)}")
print(f"Confounders: {', '.join(confounders)}")
print(f"Additional controls: {', '.join(additional_controls)}")

# ========================================================================
# PREPARE DATA
# ========================================================================

print("\n" + "=" * 80)
print("DATA PREPARATION")
print("=" * 80)

# Select relevant columns and remove missing values
analysis_vars = [treatment] + outcomes + confounders + additional_controls + ['country']
df_analysis = df[analysis_vars].copy()

print(f"\nBefore cleaning: {len(df_analysis)} observations")
print("\nMissing values by variable:")
print(df_analysis.isnull().sum())

# Drop rows with missing values in key variables
df_clean = df_analysis.dropna(subset=[treatment] + confounders)
print(f"\nAfter removing missing treatment/confounders: {len(df_clean)} observations")

# ========================================================================
# BUILD CAUSAL GRAPH
# ========================================================================

print("\n" + "=" * 80)
print("CAUSAL GRAPH CONSTRUCTION")
print("=" * 80)

# Define causal graph in GML format (more robust than DOT)
# This represents our theoretical understanding of causal relationships

# Create graph string without special characters that might cause parsing issues
causal_graph = """digraph {
gdp_per_capita -> transit_investment_gdp;
log_gdp_per_capita -> transit_investment_gdp;
gdp_per_capita -> congestion_index;
gdp_per_capita -> pm25;
log_gdp_per_capita -> congestion_index;
log_gdp_per_capita -> pm25;
population_density -> transit_investment_gdp;
population_density -> congestion_index;
population_density -> pm25;
year -> transit_investment_gdp;
year -> congestion_index;
year -> pm25;
year -> gdp_per_capita;
year -> population_density;
transit_investment_gdp -> congestion_index;
transit_investment_gdp -> pm25;
}"""

print("Causal graph structure (DOT format):")
print(causal_graph)

# Test if graph can be parsed
try:
    import networkx as nx
    from networkx.drawing.nx_pydot import read_dot
    import pydot
    
    # Try to parse the graph
    P_list = pydot.graph_from_dot_data(causal_graph)
    if P_list and len(P_list) > 0:
        test_graph = nx.DiGraph(nx.drawing.nx_pydot.from_pydot(P_list[0]))
        print(f"✓ Graph successfully parsed: {len(test_graph.nodes())} nodes, {len(test_graph.edges())} edges")
    else:
        print("⚠️  Warning: Graph parsing returned empty result, but will continue")
except Exception as e:
    print(f"⚠️  Warning: Could not validate graph parsing: {e}")
    print("   (This is OK - DoWhy will handle it internally)")

# Visualize the causal graph
fig, ax = plt.subplots(figsize=(14, 10))
G = nx.DiGraph()

# Add nodes
nodes = ['transit_investment_gdp', 'congestion_index', 'pm25', 
         'gdp_per_capita', 'log_gdp_per_capita', 'population_density', 'year']
G.add_nodes_from(nodes)

# Add edges based on causal graph
edges = [
    ('gdp_per_capita', 'transit_investment_gdp'),
    ('log_gdp_per_capita', 'transit_investment_gdp'),
    ('gdp_per_capita', 'congestion_index'),
    ('gdp_per_capita', 'pm25'),
    ('log_gdp_per_capita', 'congestion_index'),
    ('log_gdp_per_capita', 'pm25'),
    ('population_density', 'transit_investment_gdp'),
    ('population_density', 'congestion_index'),
    ('population_density', 'pm25'),
    ('year', 'transit_investment_gdp'),
    ('year', 'congestion_index'),
    ('year', 'pm25'),
    ('year', 'gdp_per_capita'),
    ('year', 'population_density'),
    ('transit_investment_gdp', 'congestion_index'),
    ('transit_investment_gdp', 'pm25'),
]
G.add_edges_from(edges)

# Create layout
pos = {
    'year': (0, 3),
    'gdp_per_capita': (-2, 2),
    'log_gdp_per_capita': (-1, 2),
    'population_density': (1, 2),
    'transit_investment_gdp': (0, 1),
    'congestion_index': (-1, 0),
    'pm25': (1, 0),
}

# Color nodes by type
node_colors = []
for node in G.nodes():
    if node == 'transit_investment_gdp':
        node_colors.append('lightgreen')  # Treatment
    elif node in ['congestion_index', 'pm25']:
        node_colors.append('lightcoral')  # Outcomes
    else:
        node_colors.append('lightblue')   # Confounders

nx.draw(G, pos, with_labels=True, node_color=node_colors, 
        node_size=3000, font_size=9, font_weight='bold',
        arrows=True, arrowsize=20, edge_color='gray',
        arrowstyle='->', connectionstyle='arc3,rad=0.1',
        ax=ax)

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='lightgreen', label='Treatment'),
    Patch(facecolor='lightcoral', label='Outcomes'),
    Patch(facecolor='lightblue', label='Confounders/Controls')
]
ax.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.title('Causal Graph: Transit Investment Effects', fontsize=14, pad=20)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'causal_graph.png'), dpi=300, bbox_inches='tight')
plt.close()
print(f"\n✓ Causal graph saved to: {output_dir}/causal_graph.png")

# ========================================================================
# CAUSAL ANALYSIS: OUTCOME 1 - CONGESTION INDEX
# ========================================================================

print("\n" + "=" * 80)
print("CAUSAL ANALYSIS 1: EFFECT ON CONGESTION INDEX")
print("=" * 80)

# Filter data for congestion analysis
df_congestion = df_clean.dropna(subset=['congestion_index'])
print(f"\nObservations with congestion data: {len(df_congestion)}")

if len(df_congestion) > 50:  # Need sufficient data
    # Create causal model with error handling
    try:
        model_congestion = CausalModel(
            data=df_congestion,
            treatment=treatment,
            outcome='congestion_index',
            common_causes=confounders + additional_controls,
            graph=causal_graph
        )
    except Exception as e:
        print(f"\n⚠️  Warning: Could not create model with graph: {e}")
        print("   Trying alternative approach without graph...")
        try:
            # Try without the graph (will rely on common_causes specification)
            model_congestion = CausalModel(
                data=df_congestion,
                treatment=treatment,
                outcome='congestion_index',
                common_causes=confounders + additional_controls
            )
            print("✓ Model created successfully without graph specification")
        except Exception as e2:
            print(f"✗ Failed to create model: {e2}")
            print("   Skipping causal analysis for congestion...")
            model_congestion = None
    
    if model_congestion is not None:
        print("\n--- Model Created ---")
        print(model_congestion)
        
        # Step 1: Identification
        print("\n--- STEP 1: IDENTIFICATION ---")
        identified_estimand = model_congestion.identify_effect(proceed_when_unidentifiable=True)
        print(identified_estimand)
    else:
        print("\n⚠️  Skipping analysis due to model creation failure")
        identified_estimand = None
    
    # Step 2: Estimation using multiple methods
    if model_congestion is not None and identified_estimand is not None:
        print("\n--- STEP 2: ESTIMATION ---")
        
        # Method 1: Backdoor adjustment (Linear Regression)
        print("\nMethod 1: Backdoor Adjustment (Linear Regression)")
        try:
            estimate_lr = model_congestion.estimate_effect(
                identified_estimand,
                method_name="backdoor.linear_regression",
                confidence_intervals=True,
                test_significance=True
            )
            print(estimate_lr)
            print(f"\nEstimated effect: {estimate_lr.value:.6f}")
            print(f"Interpretation: A 1% increase in transit investment (as % of GDP) is associated with")
            print(f"                a {estimate_lr.value:.4f} unit change in congestion index")
        except Exception as e:
            print(f"Linear regression failed: {e}")
            estimate_lr = None
        
        # Method 2: Propensity Score Matching
        print("\nMethod 2: Propensity Score Matching")
        try:
            estimate_psm = model_congestion.estimate_effect(
                identified_estimand,
                method_name="backdoor.propensity_score_matching",
                confidence_intervals=False
            )
            print(estimate_psm)
            print(f"\nEstimated effect (PSM): {estimate_psm.value:.6f}")
        except Exception as e:
            print(f"Propensity score matching failed: {e}")
            estimate_psm = None
        
        # Method 3: Instrumental Variable (if we had instruments)
        # Skipping for now as we don't have clear instruments
        
        # Step 3: Refutation tests
        print("\n--- STEP 3: REFUTATION TESTS ---")
        
        if estimate_lr is not None:
            # Refutation 1: Random common cause
            print("\nRefutation Test 1: Adding Random Common Cause")
            try:
                refute_random = model_congestion.refute_estimate(
                    identified_estimand,
                    estimate_lr,
                    method_name="random_common_cause"
                )
                print(refute_random)
            except Exception as e:
                print(f"Random common cause test failed: {e}")
            
            # Refutation 2: Placebo treatment
            print("\nRefutation Test 2: Placebo Treatment")
            try:
                refute_placebo = model_congestion.refute_estimate(
                    identified_estimand,
                    estimate_lr,
                    method_name="placebo_treatment_refuter",
                    placebo_type="permute"
                )
                print(refute_placebo)
            except Exception as e:
                print(f"Placebo treatment test failed: {e}")
            
            # Refutation 3: Data subset validation
            print("\nRefutation Test 3: Data Subset Validation")
            try:
                refute_subset = model_congestion.refute_estimate(
                    identified_estimand,
                    estimate_lr,
                    method_name="data_subset_refuter",
                    subset_fraction=0.8
                )
                print(refute_subset)
            except Exception as e:
                print(f"Data subset test failed: {e}")
else:
    print(f"Insufficient data for congestion analysis (n={len(df_congestion)})")

# ========================================================================
# CAUSAL ANALYSIS: OUTCOME 2 - PM2.5
# ========================================================================

print("\n" + "=" * 80)
print("CAUSAL ANALYSIS 2: EFFECT ON PM2.5 AIR QUALITY")
print("=" * 80)

# Filter data for PM2.5 analysis
df_pm25 = df_clean.dropna(subset=['pm25'])
print(f"\nObservations with PM2.5 data: {len(df_pm25)}")

if len(df_pm25) > 50:
    # Create causal model with error handling
    try:
        model_pm25 = CausalModel(
            data=df_pm25,
            treatment=treatment,
            outcome='pm25',
            common_causes=confounders + additional_controls,
            graph=causal_graph
        )
    except Exception as e:
        print(f"\n⚠️  Warning: Could not create model with graph: {e}")
        print("   Trying alternative approach without graph...")
        try:
            model_pm25 = CausalModel(
                data=df_pm25,
                treatment=treatment,
                outcome='pm25',
                common_causes=confounders + additional_controls
            )
            print("✓ Model created successfully without graph specification")
        except Exception as e2:
            print(f"✗ Failed to create model: {e2}")
            print("   Skipping causal analysis for PM2.5...")
            model_pm25 = None
    
    if model_pm25 is not None:
        print("\n--- Model Created ---")
        print(model_pm25)
        
        # Step 1: Identification
        print("\n--- STEP 1: IDENTIFICATION ---")
        identified_estimand_pm25 = model_pm25.identify_effect(proceed_when_unidentifiable=True)
        print(identified_estimand_pm25)
        
        # Step 2: Estimation
        print("\n--- STEP 2: ESTIMATION ---")
        
        # Linear Regression
        print("\nMethod: Backdoor Adjustment (Linear Regression)")
        try:
            estimate_pm25 = model_pm25.estimate_effect(
                identified_estimand_pm25,
                method_name="backdoor.linear_regression",
                confidence_intervals=True,
                test_significance=True
            )
            print(estimate_pm25)
            print(f"\nEstimated effect: {estimate_pm25.value:.6f}")
            print(f"Interpretation: A 1% increase in transit investment (as % of GDP) is associated with")
            print(f"                a {estimate_pm25.value:.4f} µg/m³ change in PM2.5 concentration")
        except Exception as e:
            print(f"PM2.5 estimation failed: {e}")
            estimate_pm25 = None
        
        # Step 3: Refutation tests
        print("\n--- STEP 3: REFUTATION TESTS ---")
        
        if estimate_pm25 is not None:
            try:
                refute_pm25 = model_pm25.refute_estimate(
                    identified_estimand_pm25,
                    estimate_pm25,
                    method_name="random_common_cause"
                )
                print(refute_pm25)
            except Exception as e:
                print(f"PM2.5 refutation failed: {e}")
    else:
        print("\n⚠️  Skipping PM2.5 analysis due to model creation failure")
else:
    print(f"Insufficient data for PM2.5 analysis (n={len(df_pm25)})")

# ========================================================================
# SUMMARY REPORT
# ========================================================================

print("\n" + "=" * 80)
print("CAUSAL ANALYSIS SUMMARY")
print("=" * 80)

summary_report = f"""
CAUSAL MODELING REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'=' * 80}

DATA SUMMARY:
- Total observations: {len(df_clean)}
- Countries: {df_clean['country'].nunique()}
- Years: {df_clean['year'].min():.0f} - {df_clean['year'].max():.0f}

CAUSAL STRUCTURE:
- Treatment: {treatment}
- Outcomes: {', '.join(outcomes)}
- Confounders: {', '.join(confounders)}
- Controls: {', '.join(additional_controls)}

IDENTIFICATION STRATEGY:
- Method: Backdoor adjustment
- Confounders controlled: GDP per capita, population density, time trends
- Assumptions: No unobserved confounders, correct causal graph

RESULTS:
1. Effect on Congestion Index
   - Observations: {len(df_congestion)}
   - Estimated effect: See detailed output above
   - Refutation tests: Passed/Failed - see above

2. Effect on PM2.5
   - Observations: {len(df_pm25)}
   - Estimated effect: See detailed output above
   - Refutation tests: Passed/Failed - see above

CAUSAL GRAPH:
- Saved to: {output_dir}/causal_graph.png
- Represents theoretical understanding of causal relationships
- Green = Treatment, Red = Outcomes, Blue = Confounders

INTERPRETATION:
The causal analysis estimates the effect of transit investment on urban outcomes
while controlling for confounding variables. The backdoor adjustment method
accounts for common causes that affect both treatment and outcomes.

LIMITATIONS:
1. Assumes no unobserved confounders (untestable)
2. Linear effect assumption (may not capture non-linearities)
3. Limited data availability for some countries/years
4. Potential measurement error in variables
5. External validity concerns (generalization to other contexts)

RECOMMENDATIONS:
1. Interpret effects cautiously given data limitations
2. Consider heterogeneous effects across countries
3. Validate with domain knowledge and expert judgment
4. Use findings to inform policy, not as definitive proof
"""

# Save summary report
report_path = os.path.join(data_dir, 'causal_analysis_report.txt')
with open(report_path, 'w') as f:
    f.write(summary_report)

print(summary_report)
print(f"\n✓ Full report saved to: {report_path}")

print("\n" + "=" * 80)
print("CAUSAL MODELING COMPLETE")
print("=" * 80)

