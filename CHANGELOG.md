# Changelog

All notable changes to the TransPort-PH project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-13

### Added
- Complete project reorganization with improved directory structure
- Centralized configuration system in `config/config.py`
- Comprehensive README.md with project overview and documentation
- Proper .gitignore for Python projects
- Requirements.txt with versioned dependencies
- Modular source code organization:
  - `src/data_collection/` - Data gathering modules
  - `src/preprocessing/` - Data cleaning and transformation
  - `src/models/` - Machine learning models
  - `src/analysis/` - Analysis and evaluation
  - `src/visualization/` - Dashboard and plots
  - `src/utils/` - Utility functions
- Wrapper scripts for easy execution:
  - `run_dashboard.py` - Launch Streamlit dashboard
  - `run_pipeline.py` - Execute full pipeline
- Contributing guidelines (CONTRIBUTING.md)
- MIT License (LICENSE)
- Changelog (CHANGELOG.md)
- Package setup configuration (setup.py)

### Changed
- Refactored path handling to use pathlib instead of os.path
- Updated scripts to use centralized configuration
- Improved code organization and modularity
- Enhanced documentation structure

### Fixed
- Inconsistent path handling across scripts
- Hard-coded file paths replaced with config-based paths

## [Pre-1.0.0] - Before 2024-11-13

### Implemented
- World Bank data collection
- DPWH, JICA, LTFRB, PSA, SWS data gathering
- OpenAQ air quality data integration
- TomTom traffic data collection
- Data preprocessing pipeline:
  - Data inspection and quality checks
  - Missing value handling
  - Outlier detection and winsorization
  - Feature engineering
  - Panel data merging
- Temporal Fusion Transformer (TFT) model training
- Causal inference with DoWhy
- Counterfactual policy simulations
- Interactive Streamlit dashboard
- Comprehensive exploratory data analysis
- Sensitivity analysis and model validation
- 7,430+ observations across 275 countries/regions
- Model performance: 0.24 validation loss (QuantileLoss)

---

## Version History Summary

- **1.0.0** (2024-11-13): Major reorganization and production-ready release
- **Pre-1.0.0**: Initial development and feature implementation

