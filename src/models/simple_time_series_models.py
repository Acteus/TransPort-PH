#!/usr/bin/env python3
"""
Simple Time Series Models for Transit Impact Analysis
======================================================
This script implements simpler time series models recommended in DATA_COVERAGE_ANALYSIS.md
when deep learning models like TFT are not feasible due to limited data.

Models implemented:
1. Panel Fixed Effects Regression (already in pipeline via causal_modeling_dowhy.py)
2. ARIMA/SARIMAX per country (for countries with 10+ observations)
3. Facebook Prophet (for countries with 20+ observations)

These models work well with limited data and provide interpretable results.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')
import os
from datetime import datetime

# Set up directories
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
data_dir = os.path.join(project_dir, 'data')
output_dir = os.path.join(project_dir, 'output', 'simple_models')
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("SIMPLE TIME SERIES MODELS FOR LIMITED DATA")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
print("\nBased on recommendations from DATA_COVERAGE_ANALYSIS.md")
print("These models work with limited observations (unlike TFT which needs 1000+)")

# Load data
df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))
print(f"\nLoaded data: {df.shape}")

# Filter to only observations with congestion data
df_congestion = df[df['congestion_index'].notna()].copy()
print(f"Observations with congestion data: {len(df_congestion)}")

# Count observations per country
country_counts = df_congestion.groupby('country').size().sort_values(ascending=False)
print(f"\nCountries with congestion data: {len(country_counts)}")
print("\nObservations per country:")
print(country_counts)

# ============================================================================
# MODEL 1: ARIMA/SARIMAX PER COUNTRY
# ============================================================================

print("\n" + "=" * 80)
print("MODEL 1: ARIMA/SARIMAX PER COUNTRY")
print("=" * 80)
print("\nRequirements: 10+ observations per country")
print("Strengths: Captures temporal patterns, handles trends/seasonality")
print("Use case: Short-term forecasting, trend analysis")

# Filter countries with sufficient data for ARIMA
min_obs_arima = 10
countries_arima = country_counts[country_counts >= min_obs_arima].index
print(f"\nCountries with {min_obs_arima}+ observations: {len(countries_arima)}")
print(f"Countries: {list(countries_arima)}")

arima_results = []

if len(countries_arima) > 0:
    fig, axes = plt.subplots(min(3, len(countries_arima)), 1, figsize=(12, 4*min(3, len(countries_arima))))
    if len(countries_arima) == 1:
        axes = [axes]
    
    for idx, country in enumerate(list(countries_arima)[:3]):  # Plot first 3
        print(f"\nFitting ARIMA for {country}...")
        
        # Get country data
        country_data = df_congestion[df_congestion['country'] == country].sort_values('year')
        
        # Prepare data
        y = country_data['congestion_index'].values
        years = country_data['year'].values
        
        # Add exogenous variables if available
        exog_vars = ['transit_investment_gdp', 'gdp_per_capita', 'population_density']
        exog_available = [col for col in exog_vars if col in country_data.columns and country_data[col].notna().all()]
        
        if len(exog_available) > 0:
            X = country_data[exog_available].values
            print(f"  Using exogenous variables: {exog_available}")
        else:
            X = None
            print(f"  No exogenous variables available")
        
        # Split into train/test (80/20)
        split_idx = int(len(y) * 0.8)
        if split_idx < 5:  # Need at least 5 for training
            split_idx = len(y) - 2  # Leave 2 for test
        
        y_train, y_test = y[:split_idx], y[split_idx:]
        years_train, years_test = years[:split_idx], years[split_idx:]
        
        if X is not None:
            X_train, X_test = X[:split_idx], X[split_idx:]
        else:
            X_train, X_test = None, None
        
        try:
            # Fit SARIMAX model (ARIMA with exogenous variables)
            # Using simple order (1,0,1) to avoid overfitting with limited data
            model = SARIMAX(
                y_train,
                exog=X_train,
                order=(1, 0, 1),  # (p,d,q)
                seasonal_order=(0, 0, 0, 0),  # No seasonality with limited data
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            results = model.fit(disp=False, maxiter=100)
            
            # Make predictions
            if X_test is not None:
                predictions = results.forecast(steps=len(y_test), exog=X_test)
            else:
                predictions = results.forecast(steps=len(y_test))
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, predictions)
            rmse = np.sqrt(mean_squared_error(y_test, predictions))
            mape = np.mean(np.abs((y_test - predictions) / (y_test + 1e-8))) * 100
            
            arima_results.append({
                'country': country,
                'n_obs': len(y),
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'model': 'SARIMAX'
            })
            
            print(f"  ✓ MAE: {mae:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}%")
            
            # Plot
            if idx < 3:
                axes[idx].plot(years_train, y_train, 'o-', label='Training', linewidth=2)
                axes[idx].plot(years_test, y_test, 'o-', label='Actual', linewidth=2)
                axes[idx].plot(years_test, predictions, 's--', label='Predicted', linewidth=2)
                axes[idx].set_xlabel('Year', fontsize=11)
                axes[idx].set_ylabel('Congestion Index', fontsize=11)
                axes[idx].set_title(f'{country} - ARIMA/SARIMAX\nMAE={mae:.3f}, RMSE={rmse:.3f}', fontsize=12)
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3)
        
        except Exception as e:
            print(f"  ✗ ARIMA failed for {country}: {e}")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'arima_forecasts.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n✓ ARIMA plots saved to: {output_dir}/arima_forecasts.png")
else:
    print(f"\n⚠ No countries with {min_obs_arima}+ observations for ARIMA")

# ============================================================================
# MODEL 2: FACEBOOK PROPHET
# ============================================================================

print("\n" + "=" * 80)
print("MODEL 2: FACEBOOK PROPHET")
print("=" * 80)
print("\nRequirements: 20+ observations per country")
print("Strengths: Handles missing data, trends, holidays; easy to use")
print("Use case: Robust forecasting with uncertainty intervals")

# Filter countries with sufficient data for Prophet
min_obs_prophet = 20
countries_prophet = country_counts[country_counts >= min_obs_prophet].index
print(f"\nCountries with {min_obs_prophet}+ observations: {len(countries_prophet)}")
print(f"Countries: {list(countries_prophet)}")

prophet_results = []

if len(countries_prophet) > 0:
    fig, axes = plt.subplots(min(3, len(countries_prophet)), 1, figsize=(12, 4*min(3, len(countries_prophet))))
    if len(countries_prophet) == 1:
        axes = [axes]
    
    for idx, country in enumerate(list(countries_prophet)[:3]):  # Plot first 3
        print(f"\nFitting Prophet for {country}...")
        
        # Get country data
        country_data = df_congestion[df_congestion['country'] == country].sort_values('year')
        
        # Prepare data for Prophet (needs 'ds' and 'y' columns)
        prophet_df = pd.DataFrame({
            'ds': pd.to_datetime(country_data['year'].astype(int).astype(str) + '-01-01'),
            'y': country_data['congestion_index'].values
        })
        
        # Add regressors if available
        regressor_vars = ['transit_investment_gdp', 'gdp_per_capita', 'population_density']
        regressors_added = []
        for var in regressor_vars:
            if var in country_data.columns and country_data[var].notna().all():
                prophet_df[var] = country_data[var].values
                regressors_added.append(var)
        
        # Split into train/test
        split_idx = int(len(prophet_df) * 0.8)
        if split_idx < 10:  # Need at least 10 for Prophet
            split_idx = len(prophet_df) - 2
        
        train_df = prophet_df.iloc[:split_idx]
        test_df = prophet_df.iloc[split_idx:]
        
        try:
            # Initialize Prophet
            model = Prophet(
                yearly_seasonality=False,  # Not enough data for seasonality
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05  # Conservative to avoid overfitting
            )
            
            # Add regressors
            for reg in regressors_added:
                model.add_regressor(reg)
            
            # Fit model
            model.fit(train_df)
            
            # Make predictions
            predictions = model.predict(test_df)
            
            # Calculate metrics
            y_test = test_df['y'].values
            y_pred = predictions['yhat'].values
            
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-8))) * 100
            
            prophet_results.append({
                'country': country,
                'n_obs': len(prophet_df),
                'mae': mae,
                'rmse': rmse,
                'mape': mape,
                'model': 'Prophet'
            })
            
            print(f"  ✓ MAE: {mae:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}%")
            if regressors_added:
                print(f"  Regressors: {regressors_added}")
            
            # Plot
            if idx < 3:
                axes[idx].plot(train_df['ds'], train_df['y'], 'o-', label='Training', linewidth=2)
                axes[idx].plot(test_df['ds'], test_df['y'], 'o-', label='Actual', linewidth=2)
                axes[idx].plot(predictions['ds'], predictions['yhat'], 's--', label='Predicted', linewidth=2)
                axes[idx].fill_between(
                    predictions['ds'],
                    predictions['yhat_lower'],
                    predictions['yhat_upper'],
                    alpha=0.2,
                    label='Uncertainty'
                )
                axes[idx].set_xlabel('Year', fontsize=11)
                axes[idx].set_ylabel('Congestion Index', fontsize=11)
                axes[idx].set_title(f'{country} - Facebook Prophet\nMAE={mae:.3f}, RMSE={rmse:.3f}', fontsize=12)
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3)
        
        except Exception as e:
            print(f"  ✗ Prophet failed for {country}: {e}")
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'prophet_forecasts.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n✓ Prophet plots saved to: {output_dir}/prophet_forecasts.png")
else:
    print(f"\n⚠ No countries with {min_obs_prophet}+ observations for Prophet")

# ============================================================================
# SUMMARY AND COMPARISON
# ============================================================================

print("\n" + "=" * 80)
print("MODEL COMPARISON SUMMARY")
print("=" * 80)

# Combine results
all_results = arima_results + prophet_results

if len(all_results) > 0:
    results_df = pd.DataFrame(all_results)
    
    print("\nIndividual Model Performance:")
    print(results_df.to_string(index=False))
    
    # Average performance by model type
    print("\nAverage Performance by Model:")
    avg_performance = results_df.groupby('model')[['mae', 'rmse', 'mape']].mean()
    print(avg_performance)
    
    # Create comparison visualization
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    metrics = ['mae', 'rmse', 'mape']
    titles = ['Mean Absolute Error (MAE)', 'Root Mean Squared Error (RMSE)', 'Mean Absolute % Error (MAPE)']
    
    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        results_df.boxplot(column=metric, by='model', ax=axes[idx])
        axes[idx].set_title(title, fontsize=12)
        axes[idx].set_xlabel('Model', fontsize=11)
        axes[idx].set_ylabel(metric.upper(), fontsize=11)
        axes[idx].grid(True, alpha=0.3)
    
    plt.suptitle('Model Performance Comparison', fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'model_comparison.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"\n✓ Comparison plot saved to: {output_dir}/model_comparison.png")
    
else:
    print("\n⚠ No models could be trained due to insufficient data")
    print("  Minimum requirements:")
    print(f"  - ARIMA: {min_obs_arima}+ observations per country")
    print(f"  - Prophet: {min_obs_prophet}+ observations per country")

# ============================================================================
# RECOMMENDATIONS
# ============================================================================

print("\n" + "=" * 80)
print("RECOMMENDATIONS")
print("=" * 80)

print("\n1. CURRENT DATA STATUS:")
print(f"   • Total countries with congestion data: {len(country_counts)}")
print(f"   • Countries suitable for ARIMA: {len(countries_arima)}")
print(f"   • Countries suitable for Prophet: {len(countries_prophet)}")

print("\n2. BEST MODELS FOR CURRENT DATA:")
if len(all_results) > 0:
    best_model = results_df.loc[results_df['mae'].idxmin()]
    print(f"   • Best performing: {best_model['model']} for {best_model['country']}")
    print(f"   • MAE: {best_model['mae']:.4f}")
    print(f"   • Use Panel FE for causal inference (already in pipeline)")
    print(f"   • Use ARIMA/Prophet for forecasting")
else:
    print("   • Panel Fixed Effects Regression (use causal_modeling_dowhy.py)")
    print("   • Wait until you have more data for time series models")

print("\n3. TO ENABLE DEEP LEARNING (TFT):")
print("   Need to expand dataset to:")
print("   • 1,000+ observations (current: {})".format(len(df_congestion)))
print("   • 20+ countries (current: {})".format(len(country_counts)))
print("   • 10+ years per country")
print("   See DATA_COVERAGE_ANALYSIS.md for expansion strategies")

print("\n4. NEXT STEPS:")
print("   • Continue using Panel FE for causal analysis")
print("   • Use ARIMA/Prophet for countries with sufficient data")
print("   • Focus on Philippines deep dive (Option D)")
print("   • Gather more data before attempting TFT")

# ============================================================================
# SAVE REPORT
# ============================================================================

report = f"""
SIMPLE TIME SERIES MODELS REPORT
{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Based on: DATA_COVERAGE_ANALYSIS.md

DATA SUMMARY:
- Total observations with congestion: {len(df_congestion)}
- Countries with congestion data: {len(country_counts)}
- Countries suitable for ARIMA: {len(countries_arima)}
- Countries suitable for Prophet: {len(countries_prophet)}

MODELS TRAINED:
1. ARIMA/SARIMAX: {len(arima_results)} countries
2. Facebook Prophet: {len(prophet_results)} countries

"""

if len(all_results) > 0:
    report += "\nMODEL PERFORMANCE:\n"
    report += results_df.to_string(index=False)
    report += "\n\nAVERAGE PERFORMANCE:\n"
    report += avg_performance.to_string()
    
    best_model = results_df.loc[results_df['mae'].idxmin()]
    report += f"\n\nBEST MODEL: {best_model['model']} for {best_model['country']}"
    report += f"\n  MAE: {best_model['mae']:.4f}"
    report += f"\n  RMSE: {best_model['rmse']:.4f}"
    report += f"\n  MAPE: {best_model['mape']:.2f}%"
else:
    report += "\nNo models could be trained due to insufficient data.\n"

report += f"""

RECOMMENDATIONS:
1. Use Panel Fixed Effects for causal inference (already in pipeline)
2. Use ARIMA/Prophet for forecasting (countries with sufficient data)
3. Do NOT use TFT until dataset expanded to 1,000+ observations
4. Focus on Philippines deep dive or data expansion

For more details, see:
- DATA_COVERAGE_ANALYSIS.md
- PROJECT_ASSESSMENT_AND_IMPROVEMENTS.md
- NEXT_STEPS.md

OUTPUTS:
- ARIMA forecasts: {output_dir}/arima_forecasts.png
- Prophet forecasts: {output_dir}/prophet_forecasts.png
- Model comparison: {output_dir}/model_comparison.png
- This report: {data_dir}/simple_models_report.txt
"""

report_path = os.path.join(data_dir, 'simple_models_report.txt')
with open(report_path, 'w') as f:
    f.write(report)

print(f"\n✓ Report saved to: {report_path}")

print("\n" + "=" * 80)
print("SIMPLE TIME SERIES MODELS COMPLETE")
print("=" * 80)
print("\nKey Takeaway:")
print("  With limited data, simpler models (Panel FE, ARIMA, Prophet) are more")
print("  appropriate than deep learning (TFT). Focus on data expansion or narrow")
print("  scope (Philippines) before attempting complex models.")
print("=" * 80)
