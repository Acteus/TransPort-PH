# TransPort-PH Data Processing & Analysis Pipeline

## Overview

This directory contains a comprehensive data science pipeline for analyzing transit infrastructure investments and their effects on urban outcomes in the Philippines and comparative countries.

## Pipeline Structure

The pipeline is organized into 5 phases:

### Phase 1: Data Gathering (11 scripts)
Scripts that collect data from various sources:

1. **`data_gathering_worldbank.py`** - World Bank indicators (GDP, population, urbanization)
2. **`data_gathering_tomtom.py`** - TomTom traffic congestion data
3. **`data_gathering_uitp.py`** - UITP modal share data
4. **`data_gathering_psa.py`** - Philippine Statistics Authority demographic data
5. **`data_gathering_ltfrb.py`** - LTFRB fleet and fare data
6. **`data_gathering_openaq.py`** - OpenAQ air quality (PM2.5) data
7. **`data_gathering_overpass.py`** - OpenStreetMap infrastructure data via Overpass API
8. **`data_gathering_adb.py`** - Asian Development Bank project loans
9. **`data_gathering_jica.py`** - JICA MRT/LRT data
10. **`data_gathering_sws.py`** - Social Weather Stations satisfaction surveys
11. **`data_gathering_dpwh.py`** - DPWH road and infrastructure data

### Phase 2: Data Preparation (8 scripts)
Scripts that clean, standardize, and prepare data:

12. **`data_inspection.py`** - Comprehensive data quality checks
    - Checks for duplicates, missing values, outliers
    - Validates data types and ranges
    - Identifies mismatches across datasets
    - Generates inspection reports

13. **`data_standardization.py`** - Country name and year standardization
    - Normalizes country names (handles aliases, variants)
    - Filters years to 2000-2024 range
    - Ensures consistent data types
    - Creates standardization report

14. **`handle_missing_values.py`** - Intelligent missing value imputation
    - Time-invariant variables: no imputation
    - Smooth trends (GDP, population): linear interpolation
    - Sparse variables (transit data): forward/backward fill
    - Generates before/after reports

15. **`feature_engineering.py`** - Creates derived features
    - Log transformations (GDP, population)
    - Dummy variables (high GDP, high investment)
    - Urbanization rate calculation
    - Lagged variables (transit_invest_lag1, lag2)
    - Growth rates (GDP growth)
    - Road per capita metrics

16. **`outlier_winsorization.py`** - Outlier detection and treatment
    - Two-tailed winsorization at 1st and 99th percentiles
    - Preserves sample size vs. deletion
    - Detailed outlier reports
    - Visualization of winsorized values

17. **`panel_balance.py`** - Panel balance and filtering
    - Counts years per country
    - Filters countries with <10 years of data
    - Generates balance reports and visualizations
    - Ensures adequate time series length

18. **`train_test_split.py`** - Time-based data splitting
    - Train: years 2000-2019
    - Test: years 2020-2024 (holdout)
    - Prevents data leakage
    - Validates split quality

19. **`merge_panel.py`** - Merges all data sources
    - Left joins on country-year
    - Handles OSM data (country-only merge)
    - Creates final clean panel structure
    - Generates merge reports

### Phase 3: Exploratory Data Analysis (5 scripts)
Scripts for visual and statistical exploration:

20. **`validation_plots.py`** - Initial validation checks
    - Time trends for key countries
    - Investment vs. congestion scatter plots
    - Visual sanity checks

21. **`eda_univariate.py`** - Univariate analysis
    - Histograms with KDE for all numeric variables
    - Missingness heatmap
    - Summary statistics tables
    - Distribution visualizations

22. **`eda_time_trends.py`** - Time series analysis per country
    - Country-specific time trends
    - Congestion and investment over time
    - Focus countries: Philippines, Singapore, Colombia

23. **`eda_correlation_clustering.py`** - Multivariate analysis
    - Correlation matrix and heatmap
    - Strong correlation identification (|r| > 0.7)
    - Hierarchical clustering of countries
    - PCA visualization of country clusters

24. **`eda_scatter_loess.py`** - Relationship exploration
    - Scatter plots with Loess smoothing
    - Key relationships: investment-congestion, GDP-outcomes
    - Linear trend comparison
    - Multi-panel combined visualizations

### Phase 4: Causal Modeling (1 script)
Advanced causal inference:

25. **`causal_modeling_dowhy.py`** - DoWhy causal analysis
    - Builds causal graph (DAG)
    - Defines treatment (transit_investment_gdp)
    - Defines outcomes (congestion_index, pm25)
    - Identifies confounders (GDP, population density, year)
    - Performs identification (backdoor adjustment)
    - Estimates causal effects (linear regression, PSM)
    - Runs refutation tests (random common cause, placebo, subset)
    - Generates causal graph visualization
    - Produces comprehensive causal analysis report

### Phase 5: Machine Learning Models (2 scripts)
Forecasting models:

26. **`prepare_tft_dataset.py`** - TFT dataset preparation
    - Creates time series format
    - Defines encoder/decoder lengths
    - Handles missing timesteps
    - Sets up time-varying variables

27. **`train_tft_model.py`** - Temporal Fusion Transformer training
    - Trains TFT model using PyTorch Lightning
    - Multi-horizon probabilistic forecasting
    - Attention-based architecture
    - Variable importance analysis
    - Model checkpointing and early stopping
    - TensorBoard logging
    - Generates evaluation metrics (MAE, RMSE, MAPE)
    - Produces prediction visualizations
    - Saves trained model

### Master Execution Script

28. **`run_all.py`** - Orchestrates entire pipeline
    - Runs all scripts in correct order
    - Handles errors gracefully
    - Generates execution summary
    - Command-line options:
      - `--skip-gathering`: Skip data gathering (use existing)
      - `--skip-eda`: Skip EDA visualizations

## Key Variables in Final Clean Panel

The final clean panel (`clean_panel.csv`) contains:

**Identifiers:**
- `country`: Country name (standardized)
- `year`: Year (2000-2024)

**Treatment Variable:**
- `transit_investment_gdp`: Transit investment as % of GDP

**Outcome Variables:**
- `congestion_index`: Traffic congestion level (%)
- `pm25`: Air quality (PM2.5 concentration in µg/m³)

**Confounders/Controls:**
- `gdp_per_capita`: GDP per capita (current USD)
- `population_density`: Population density (people/km²)
- `log_gdp_per_capita`: Log-transformed GDP per capita
- `modal_share_public`: Public transit modal share (%)

**Derived Features:**
- `transit_invest_lag1`: 1-year lagged transit investment
- `high_invest_dummy`: Binary indicator for high investment (top 25%)

## Execution Instructions

### Option 1: Run Entire Pipeline

```bash
cd scripts
python run_all.py
```

### Option 2: Run Selective Phases

```bash
# Skip data gathering (use existing data)
python run_all.py --skip-gathering

# Skip EDA visualizations
python run_all.py --skip-eda

# Skip both
python run_all.py --skip-gathering --skip-eda
```

### Option 3: Run Individual Scripts

```bash
# Example: Run only causal modeling
python causal_modeling_dowhy.py

# Example: Run only TFT training
python train_tft_model.py
```

## Output Structure

### Data Directory (`../data/`)
- `clean_panel.csv` - Final merged panel dataset
- `worldbank_train.csv` - Training split
- `worldbank_test.csv` - Test split
- `*_report.csv` - Various CSV reports
- `*_report.txt` - Detailed text reports

### Output Directory (`../output/`)
- `*.png` - All visualizations
- `tft_logs/` - TensorBoard logs
- `causal_graph.png` - Causal DAG visualization
- `tft_evaluation.png` - TFT model evaluation
- `correlation_matrix.png` - Correlation heatmap
- `*_trends.png` - Country-specific time trends
- `scatter_loess_*.png` - Scatter plots with smoothing

### Models Directory (`../models/`)
- `tft-*.ckpt` - TFT model checkpoints
- Best models saved during training

## Requirements

Install required packages:

```bash
pip install -r ../requirements.txt
```

Key dependencies:
- `pandas`, `numpy` - Data manipulation
- `matplotlib`, `seaborn`, `plotly` - Visualization
- `scikit-learn` - Machine learning utilities
- `scipy`, `statsmodels` - Statistical analysis
- `dowhy` - Causal inference
- `torch`, `pytorch-forecasting` - Deep learning
- `requests`, `beautifulsoup4` - Web scraping

## Data Quality Checks

Each script performs comprehensive quality checks:

1. **Duplicates**: Identified and reported
2. **Missing values**: Tracked before/after imputation
3. **Outliers**: Detected using z-scores and winsorized
4. **Data types**: Validated and corrected
5. **Ranges**: Years filtered to 2000-2024
6. **Country names**: Standardized across all sources
7. **Panel balance**: Countries filtered to >=10 years

## Causal Inference Framework

The causal modeling script implements a rigorous framework:

1. **Causal Graph**: Explicitly defines assumed causal relationships
2. **Identification**: Uses backdoor criterion to identify causal effects
3. **Estimation**: Multiple methods (linear regression, PSM)
4. **Refutation**: Tests robustness to assumptions

**Causal Question**: What is the effect of transit investment on congestion and air quality?

**Identification Strategy**: Backdoor adjustment controlling for GDP, population density, and time trends

**Assumptions**:
- No unobserved confounders (conditional ignorability)
- Correct causal graph specification
- Sufficient overlap (common support)

## TFT Model Architecture

The Temporal Fusion Transformer provides:

1. **Multi-horizon forecasting**: Predict multiple time steps ahead
2. **Probabilistic predictions**: Quantile outputs for uncertainty
3. **Attention mechanisms**: Interpretable variable importance
4. **Time-varying covariates**: Handles both known and unknown future values
5. **Group-specific patterns**: Country-level random effects

**Model Configuration**:
- Hidden size: 32
- LSTM layers: 2
- Attention heads: 4
- Encoder length: 5 years
- Prediction length: 3 years
- Loss: Quantile loss for probabilistic forecasts

## Best Practices Implemented

1. **No shortcuts**: Full implementation of all steps
2. **Comprehensive documentation**: Every script documented
3. **Detailed reporting**: CSV and text reports for all steps
4. **Visualizations**: Sanity checks at every stage
5. **Reproducibility**: Random seeds set, deterministic operations
6. **Data leakage prevention**: Strict time-based splitting
7. **Robust error handling**: Try-except blocks, graceful failures
8. **Validation**: Multiple checks throughout pipeline

## Troubleshooting

### Common Issues

1. **Missing data files**: Ensure data gathering scripts ran successfully
2. **Memory errors**: Reduce batch sizes in TFT training
3. **GPU not available**: TFT will fallback to CPU (slower)
4. **API timeouts**: Data gathering may need retries
5. **Causal model errors**: May need more data or different specifications

### Debugging

- Check individual script outputs before running full pipeline
- Review `*_report.txt` files for detailed diagnostics
- Use `--skip-gathering` if data already exists
- Run scripts individually to isolate issues

## Next Steps

After running the pipeline:

1. **Review Reports**: Check all `*_report.txt` files
2. **Validate Results**: Examine visualizations in `output/`
3. **Inspect Clean Panel**: Review `clean_panel.csv` structure
4. **Causal Interpretation**: Read causal analysis report carefully
5. **Model Evaluation**: Check TFT evaluation metrics
6. **Scenario Analysis**: Use trained TFT model for policy simulation
7. **Robustness Checks**: Vary model specifications and test sensitivity

## Citation & Acknowledgments

Data sources:
- World Bank Open Data
- TomTom Traffic Index
- UITP Statistics Brief
- Philippine Statistics Authority
- OpenAQ
- OpenStreetMap
- Asian Development Bank
- JICA
- DPWH

## Contact & Support

For questions or issues:
1. Review this README
2. Check individual script docstrings
3. Examine report files
4. Refer to requirements.txt for package versions

## License

This pipeline is for research and educational purposes.

