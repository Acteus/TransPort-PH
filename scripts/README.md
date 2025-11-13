# TransPort-PH Scripts

This directory contains all the scripts for the TransPort-PH project, organized by phase.

## Quick Start

Run all scripts in the correct order:
```bash
cd scripts
python run_all.py
```

Options:
- `--skip-gathering`: Skip data gathering (use existing data)
- `--skip-eda`: Skip exploratory data analysis visualizations

## Project Structure

### Phase 1: Data Gathering

Scripts that fetch data from various sources:

| Script | Description | Output |
|--------|-------------|--------|
| `data_gathering_worldbank.py` | Fetch World Bank economic indicators | `worldbank_data.csv` |
| `data_gathering_tomtom.py` | Fetch TomTom traffic congestion data | `tomtom_traffic_data.csv` |
| `data_gathering_uitp.py` | Fetch UITP public transit modal share | `uitp_modal_share.csv` |
| `data_gathering_psa.py` | Fetch PSA demographic data | `psa_data.csv` |
| `data_gathering_ltfrb.py` | Scrape LTFRB fleet and fare data | `ltfrb_data.csv` |
| `data_gathering_openaq.py` | Fetch OpenAQ air quality (PM2.5) | `openaq_pm25.csv` |
| `data_gathering_overpass.py` | Fetch OSM rail/road data via Overpass API | `overpass_data.csv` |
| `data_gathering_adb.py` | Scrape ADB transit loan projects | `adb_projects.csv` |
| `data_gathering_jica.py` | Extract MRT/LRT data from JICA sources | `jica_mrt_lrt.csv` |
| `data_gathering_sws.py` | Gather SWS satisfaction survey data | `sws_satisfaction.csv` |
| `data_gathering_dpwh.py` | Fetch DPWH infrastructure data | `dpwh_data.csv` |

### Phase 2: Data Preparation

Scripts that clean and prepare the data:

| Script | Description | Output |
|--------|-------------|--------|
| `data_inspection.py` | Inspect data quality, duplicates, outliers | `data_inspection_report.txt/csv` |
| `data_standardization.py` | Standardize country names and years (2000-2024) | Updates CSV files in place |
| `handle_missing_values.py` | Handle missing values by variable type | `missing_values_report.txt/csv` |
| `feature_engineering.py` | Create engineered features (logs, dummies, etc.) | `feature_engineering_report.txt/csv` |
| `outlier_winsorization.py` | Cap outliers at 99th percentile | Updates CSV files in place |
| `panel_balance.py` | Filter countries with >=10 years of data | `panel_balance_report.txt/csv` |
| `train_test_split.py` | Split into train (pre-2020) and test (2020+) | `worldbank_train.csv`, `worldbank_test.csv` |
| `merge_panel.py` | Merge all sources into clean panel | `clean_panel.csv`, `panel_merge_report.txt/csv` |

### Phase 3: Exploratory Data Analysis

Scripts that generate visualizations and insights:

| Script | Description | Output |
|--------|-------------|--------|
| `validation_plots.py` | Sanity check plots (time trends, scatter) | `validation_plots.png` |
| `eda_univariate.py` | Univariate distributions and missingness | `*_dist.png`, `missingness.png`, `univariate_summary.csv` |
| `eda_time_trends.py` | Time trends for key countries | `*_trends.png` |
| `eda_correlation_clustering.py` | Correlation matrix and hierarchical clustering | `correlation_matrix.png/csv`, `country_clustering.png` |
| `eda_scatter_loess.py` | Scatter plots with Loess smoothing | `scatter_loess_*.png` |

### Phase 4: Model Preparation

Scripts that prepare data for modeling:

| Script | Description | Output |
|--------|-------------|--------|
| `prepare_tft_dataset.py` | Prepare time series data for TFT model | TFT-ready dataset |

## Key Variables

As defined in `plan.txt`:

### Treatment Variable
- `transit_investment_gdp`: Public transit investment as % of GDP

### Outcome Variables
- `congestion_index`: Traffic congestion level
- `pm25`: Air quality (PM2.5 levels)

### Mechanism Variables
- `modal_share_public`: Public transit modal share
- `farebox_recovery`: Transit fare recovery ratio

### Confounders
- `gdp_per_capita`: GDP per capita
- `population_density`: Population density
- `road_density`: Road network density
- `urbanization_rate`: Urbanization rate

### Engineered Features
- `log_gdp_per_capita`: Log-transformed GDP
- `log_population`: Log-transformed population
- `high_invest_dummy`: High investment indicator
- `transit_invest_dummy`: Any investment indicator
- `transit_invest_lag1/lag2`: Lagged investment variables
- `road_per_capita`: Road km per 1000 people

## Output Directory Structure

All visualizations and reports are saved to `../output/`:

```
output/
├── data_inspection_report.txt
├── data_inspection_summary.csv
├── missing_values_report.txt
├── feature_engineering_report.txt
├── panel_merge_report.txt
├── panel_balance_report.txt
├── panel_balance_chart.png
├── correlation_matrix.png
├── country_clustering.png
├── *_dist.png (distribution plots)
├── *_trends.png (time trend plots)
├── scatter_loess_*.png (scatter plots)
└── validation_plots.png
```

## Dependencies

Install required packages:
```bash
pip install -r ../requirements.txt
```

Key packages:
- pandas, numpy: Data manipulation
- matplotlib, seaborn, plotly: Visualization
- scikit-learn: Clustering, PCA
- scipy, statsmodels: Statistical analysis
- requests, beautifulsoup4: Web scraping
- pytorch-forecasting: Time series forecasting

## Notes

1. **Data Gathering**: Some scripts may require API keys or may timeout. Fallback data is provided.
2. **Missing Values**: Handled differently based on variable type (time-invariant, smooth trends, sparse)
3. **Country Filtering**: Only countries with >=10 years of data are kept in final panel
4. **Time Split**: Train on pre-2020, test on 2020-2024 for simulation validation

## Troubleshooting

**Script fails with "Module not found"**:
```bash
pip install -r ../requirements.txt
```

**Script fails with "File not found"**:
- Ensure you're running from the `scripts/` directory
- Or use `run_all.py` which handles paths correctly

**API timeouts or errors**:
- Scripts have fallback data when APIs fail
- Use `--skip-gathering` to skip data gathering if files already exist

## Next Steps

After running the pipeline:
1. Review reports in `output/` directory
2. Check `clean_panel.csv` for final dataset
3. Proceed to causal modeling (DoWhy, causal graphs)
4. Run simulation and forecasting (TFT model)
5. Build Streamlit dashboard

## Contact

For issues or questions about the scripts, refer to `plan.txt` for project overview.
