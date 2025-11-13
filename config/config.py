"""
Configuration Management for TransPort-PH Project
==================================================
Centralized configuration for paths, settings, and parameters.
"""

import os
from pathlib import Path

# Project Root Directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Directory Paths
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
MODELS_DIR = PROJECT_ROOT / "models"
DOCS_DIR = PROJECT_ROOT / "docs"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Create directories if they don't exist
for directory in [DATA_DIR, OUTPUT_DIR, MODELS_DIR, DOCS_DIR, NOTEBOOKS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data Files (raw and processed)
RAW_DATA = {
    "worldbank": DATA_DIR / "worldbank_data.csv",
    "dpwh": DATA_DIR / "dpwh_data.csv",
    "jica": DATA_DIR / "jica_mrt_lrt.csv",
    "ltfrb": DATA_DIR / "ltfrb_data.csv",
    "psa": DATA_DIR / "psa_data.csv",
    "sws": DATA_DIR / "sws_satisfaction.csv",
    "openaq": DATA_DIR / "openaq_pm25.csv",
    "tomtom": DATA_DIR / "tomtom_traffic_data.csv",
    "overpass": DATA_DIR / "overpass_data.csv",
    "uitp": DATA_DIR / "uitp_modal_share.csv",
    "adb": DATA_DIR / "adb_projects.csv",
    "congestion": DATA_DIR / "congestion_comprehensive.csv",
}

PROCESSED_DATA = {
    "clean_panel": DATA_DIR / "clean_panel.csv",
    "clean_panel_train": DATA_DIR / "clean_panel_train.csv",
    "clean_panel_test": DATA_DIR / "clean_panel_test.csv",
}

# Output Files
OUTPUT_FILES = {
    "univariate_summary": OUTPUT_DIR / "univariate_summary.csv",
    "correlation_matrix": OUTPUT_DIR / "correlation_matrix.csv",
    "strong_correlations": OUTPUT_DIR / "strong_correlations.csv",
    "country_clusters": OUTPUT_DIR / "country_clusters.csv",
    "sensitivity_results": OUTPUT_DIR / "sensitivity_analysis_results.csv",
    "tft_logs": OUTPUT_DIR / "tft_logs",
}

# Model Files
MODEL_FILES = {
    "tft_best": MODELS_DIR / "tft_best.ckpt",
    "tft_last": MODELS_DIR / "last.ckpt",
}

# Model Training Parameters
MODEL_PARAMS = {
    "max_epochs": 50,
    "batch_size": 64,
    "learning_rate": 0.001,
    "hidden_size": 64,
    "attention_head_size": 4,
    "dropout": 0.1,
    "max_encoder_length": 5,
    "max_prediction_length": 3,
}

# Data Processing Parameters
DATA_PARAMS = {
    "test_size": 0.2,
    "random_state": 42,
    "winsorization_limits": (0.01, 0.99),
    "missing_threshold": 0.5,  # Maximum proportion of missing values allowed
}

# Analysis Parameters
ANALYSIS_PARAMS = {
    "correlation_threshold": 0.7,
    "n_clusters": 4,
    "confidence_level": 0.95,
}

# Plotting Parameters
PLOT_PARAMS = {
    "figsize": (12, 8),
    "dpi": 100,
    "style": "seaborn-v0_8-darkgrid",
    "color_palette": "husl",
}

# API Keys and Credentials (load from environment)
API_KEYS = {
    "tomtom": os.getenv("TOMTOM_API_KEY", ""),
    "openaq": os.getenv("OPENAQ_API_KEY", ""),
}

# Logging Configuration
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"

def get_path(category: str, key: str) -> Path:
    """
    Get a path from the configuration.
    
    Args:
        category: One of 'raw', 'processed', 'output', 'model'
        key: The specific file/directory key
    
    Returns:
        Path object
    """
    categories = {
        "raw": RAW_DATA,
        "processed": PROCESSED_DATA,
        "output": OUTPUT_FILES,
        "model": MODEL_FILES,
    }
    
    if category not in categories:
        raise ValueError(f"Unknown category: {category}")
    
    if key not in categories[category]:
        raise ValueError(f"Unknown key '{key}' in category '{category}'")
    
    return categories[category][key]

def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, create if it doesn't."""
    path.mkdir(parents=True, exist_ok=True)
    return path

