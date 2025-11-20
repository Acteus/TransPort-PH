# TransPort-PH: Transportation Policy Analysis for the Philippines

[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/status-beta-orange)]()
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**TransPort-PH** is a machine learning and causal inference framework for analyzing transportation policies, forecasting congestion, and evaluating economic impacts in the Philippines and globally.

## 🚀 Key Features

*   **Forecasting**: Temporal Fusion Transformer (TFT) for multi-horizon time series predictions.
*   **Causal Analysis**: DoWhy framework for robust policy impact assessment.
*   **Simulation**: Counterfactual scenarios for "what-if" analysis.
*   **Interactive Dashboard**: Streamlit-based tool for visualization.
*   **Rich Data**: Integrates World Bank, DPWH, and other sources (7,430+ observations).

## ⚡ Quick Start

### Installation

```bash
git clone https://github.com/Acteus/TransPort-PH.git
cd TransPort-PH
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Usage

**Run Dashboard** (Visualization & Analysis)
```bash
streamlit run src/visualization/dashboard_app.py
```

**Run Full Pipeline** (Data Collection -> Analysis)
```bash
python src/utils/run_all.py
```

## 📂 Project Structure

*   `src/`: Main source code (data collection, models, analysis, visualization).
*   `data/`: Processed datasets (World Bank, etc.).
*   `config/`: Configuration settings.
*   `docs/`: Detailed documentation.

## 📊 Data & Methodology

**Sources**: World Bank, DPWH, JICA, LTFRB, PSA, OpenAQ, TomTom.

**Methods**:
*   **ML**: Temporal Fusion Transformer (TFT)
*   **Causal**: DoWhy (Treatment Effect Estimation)
*   **Validation**: Sensitivity analysis & baseline comparisons (ARIMA, LSTM)

**Key Results**:
*   Significantly expanded data coverage (275 regions).
*   TFT model achieves 0.24 validation loss, outperforming baselines.
*   Actionable insights on transit investment vs. congestion.

## 📚 Documentation

*   [Quick Start Guide](docs/QUICK_START.md)
*   [Dashboard Guide](docs/DASHBOARD_GUIDE.md)

## 📄 License & Citation

MIT License. See [LICENSE](LICENSE).

```bibtex
@software{transport_ph_2024,
  title={TransPort-PH: Transportation Policy Analysis for the Philippines},
  author={[Your Name]},
  year={2024},
  url={https://github.com/Acteus/TransPort-PH}
}
```
