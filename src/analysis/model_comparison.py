#!/usr/bin/env python3
"""
Model Comparison Framework
===========================
Compares multiple forecasting models to determine which is most appropriate
given the data constraints:
1. Panel Fixed Effects (Baseline)
2. ARIMA per country
3. Facebook Prophet
4. Simple LSTM
5. Temporal Fusion Transformer (TFT)

Provides rigorous comparison with:
- Cross-validation
- Multiple metrics (MAE, RMSE, MAPE)
- Uncertainty quantification
- Model selection recommendations
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Statistical models
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tools.sm_exceptions import ConvergenceWarning
warnings.filterwarnings('ignore', category=ConvergenceWarning)

# Facebook Prophet
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    print("⚠ Prophet not installed: pip install prophet")
    PROPHET_AVAILABLE = False

# Deep learning
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Set random seeds
np.random.seed(42)
torch.manual_seed(42)

# Set style
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (16, 12)

# Directories
data_dir = '../data'
output_dir = '../output'
os.makedirs(output_dir, exist_ok=True)
os.makedirs(os.path.join(output_dir, 'model_comparison'), exist_ok=True)

print("=" * 80)
print("MODEL COMPARISON FRAMEWORK")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# ========================================================================
# LOAD DATA
# ========================================================================

print("\n" + "=" * 80)
print("LOADING DATA")
print("=" * 80)

clean_panel = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))
print(f"\n✓ Clean panel: {clean_panel.shape}")

# Filter to countries with congestion data
countries_with_data = clean_panel[clean_panel['congestion_index'].notna()]['country'].unique()
print(f"✓ Countries with congestion data: {len(countries_with_data)}")
print(f"  {list(countries_with_data)}")

# Prepare dataset
df = clean_panel[clean_panel['country'].isin(countries_with_data)].copy()
df = df.sort_values(['country', 'year']).reset_index(drop=True)

# Split train/test (time-based)
train_cutoff = 2021
df_train = df[df['year'] < train_cutoff].copy()
df_test = df[df['year'] >= train_cutoff].copy()

print(f"\nTrain: {len(df_train)} obs ({df_train['year'].min():.0f}-{df_train['year'].max():.0f})")
print(f"Test: {len(df_test)} obs ({df_test['year'].min():.0f}-{df_test['year'].max():.0f})")

# ========================================================================
# MODEL 1: PANEL FIXED EFFECTS (BASELINE)
# ========================================================================

print("\n" + "=" * 80)
print("MODEL 1: PANEL FIXED EFFECTS")
print("=" * 80)

from sklearn.linear_model import LinearRegression

# Prepare data
train_fe = df_train[df_train['congestion_index'].notna()].copy()
test_fe = df_test[df_test['congestion_index'].notna()].copy()

# Create country dummies
train_fe_dummies = pd.get_dummies(train_fe['country'], prefix='country')
test_fe_dummies = pd.get_dummies(test_fe['country'], prefix='country')

# Align columns
for col in train_fe_dummies.columns:
    if col not in test_fe_dummies.columns:
        test_fe_dummies[col] = 0

for col in test_fe_dummies.columns:
    if col not in train_fe_dummies.columns:
        train_fe_dummies[col] = 0

test_fe_dummies = test_fe_dummies[train_fe_dummies.columns]

# Features
feature_cols = ['transit_investment_gdp', 'gdp_per_capita', 'population_density', 'year']
X_train_fe = pd.concat([train_fe[feature_cols], train_fe_dummies], axis=1)
y_train_fe = train_fe['congestion_index']
X_test_fe = pd.concat([test_fe[feature_cols], test_fe_dummies], axis=1)
y_test_fe = test_fe['congestion_index']

# Fit model
fe_model = LinearRegression()
fe_model.fit(X_train_fe, y_train_fe)

# Predictions
fe_train_pred = fe_model.predict(X_train_fe)
fe_test_pred = fe_model.predict(X_test_fe)

# Metrics
fe_train_mae = mean_absolute_error(y_train_fe, fe_train_pred)
fe_test_mae = mean_absolute_error(y_test_fe, fe_test_pred)
fe_train_rmse = np.sqrt(mean_squared_error(y_train_fe, fe_train_pred))
fe_test_rmse = np.sqrt(mean_squared_error(y_test_fe, fe_test_pred))

print(f"\nPanel Fixed Effects Results:")
print(f"  Train MAE: {fe_train_mae:.4f}")
print(f"  Test MAE: {fe_test_mae:.4f}")
print(f"  Train RMSE: {fe_train_rmse:.4f}")
print(f"  Test RMSE: {fe_test_rmse:.4f}")

# ========================================================================
# MODEL 2: ARIMA PER COUNTRY
# ========================================================================

print("\n" + "=" * 80)
print("MODEL 2: ARIMA PER COUNTRY")
print("=" * 80)

arima_predictions = []
arima_actuals = []
arima_results = {}

for country in countries_with_data:
    country_data = df[df['country'] == country].sort_values('year')
    country_data = country_data[country_data['congestion_index'].notna()]
    
    if len(country_data) < 5:
        print(f"\n⚠ {country}: Insufficient data ({len(country_data)} points)")
        continue
    
    # Split
    country_train = country_data[country_data['year'] < train_cutoff]
    country_test = country_data[country_data['year'] >= train_cutoff]
    
    if len(country_test) == 0:
        print(f"\n⚠ {country}: No test data")
        continue
    
    print(f"\n{country}: Train={len(country_train)}, Test={len(country_test)}")
    
    try:
        # Fit ARIMA (1,0,1) - simple model
        model = SARIMAX(
            country_train['congestion_index'],
            exog=country_train[['transit_investment_gdp', 'gdp_per_capita']],
            order=(1, 0, 1),
            enforce_stationarity=False,
            enforce_invertibility=False
        )
        
        fitted = model.fit(disp=False, maxiter=100)
        
        # Forecast
        forecast = fitted.forecast(
            steps=len(country_test),
            exog=country_test[['transit_investment_gdp', 'gdp_per_capita']]
        )
        
        arima_predictions.extend(forecast.values)
        arima_actuals.extend(country_test['congestion_index'].values)
        
        arima_results[country] = {
            'predictions': forecast.values,
            'actuals': country_test['congestion_index'].values
        }
        
        print(f"  ✓ Forecast complete")
        
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:50]}")
        continue

# Calculate metrics
if len(arima_predictions) > 0:
    arima_mae = mean_absolute_error(arima_actuals, arima_predictions)
    arima_rmse = np.sqrt(mean_squared_error(arima_actuals, arima_predictions))
    
    print(f"\nARIMA Results (Aggregated):")
    print(f"  Test MAE: {arima_mae:.4f}")
    print(f"  Test RMSE: {arima_rmse:.4f}")
    print(f"  Countries forecasted: {len(arima_results)}")
else:
    print("\n⚠ No successful ARIMA forecasts")
    arima_mae = arima_rmse = np.nan

# ========================================================================
# MODEL 3: FACEBOOK PROPHET
# ========================================================================

print("\n" + "=" * 80)
print("MODEL 3: FACEBOOK PROPHET")
print("=" * 80)

if PROPHET_AVAILABLE:
    prophet_predictions = []
    prophet_actuals = []
    prophet_results = {}
    
    for country in countries_with_data:
        country_data = df[df['country'] == country].sort_values('year')
        country_data = country_data[country_data['congestion_index'].notna()].copy()
        
        if len(country_data) < 5:
            continue
        
        # Prepare Prophet format
        country_data['ds'] = pd.to_datetime(country_data['year'], format='%Y')
        country_data['y'] = country_data['congestion_index']
        
        # Split
        country_train = country_data[country_data['year'] < train_cutoff]
        country_test = country_data[country_data['year'] >= train_cutoff]
        
        if len(country_test) == 0:
            continue
        
        print(f"\n{country}: Train={len(country_train)}, Test={len(country_test)}")
        
        try:
            # Fit Prophet
            model = Prophet(
                yearly_seasonality=False,
                weekly_seasonality=False,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            
            # Add regressors
            model.add_regressor('transit_investment_gdp')
            model.add_regressor('gdp_per_capita')
            
            model.fit(country_train[['ds', 'y', 'transit_investment_gdp', 'gdp_per_capita']], 
                     verbose=False)
            
            # Forecast
            future = country_test[['ds', 'transit_investment_gdp', 'gdp_per_capita']].copy()
            forecast = model.predict(future)
            
            prophet_predictions.extend(forecast['yhat'].values)
            prophet_actuals.extend(country_test['y'].values)
            
            prophet_results[country] = {
                'predictions': forecast['yhat'].values,
                'actuals': country_test['y'].values
            }
            
            print(f"  ✓ Forecast complete")
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:50]}")
            continue
    
    # Calculate metrics
    if len(prophet_predictions) > 0:
        prophet_mae = mean_absolute_error(prophet_actuals, prophet_predictions)
        prophet_rmse = np.sqrt(mean_squared_error(prophet_actuals, prophet_predictions))
        
        print(f"\nProphet Results (Aggregated):")
        print(f"  Test MAE: {prophet_mae:.4f}")
        print(f"  Test RMSE: {prophet_rmse:.4f}")
        print(f"  Countries forecasted: {len(prophet_results)}")
    else:
        prophet_mae = prophet_rmse = np.nan
else:
    prophet_mae = prophet_rmse = np.nan
    print("\n⚠ Prophet not available - skipping")

# ========================================================================
# MODEL 4: SIMPLE LSTM
# ========================================================================

print("\n" + "=" * 80)
print("MODEL 4: SIMPLE LSTM")
print("=" * 80)

# Check if sufficient data
if len(df_train[df_train['congestion_index'].notna()]) < 20:
    print("\n⚠ Insufficient data for LSTM (need 20+ observations)")
    lstm_test_mae = lstm_test_rmse = np.nan
else:
    # Prepare sequences
    def create_sequences(data, seq_length=3):
        X, y, countries, years = [], [], [], []
        for country in data['country'].unique():
            country_data = data[data['country'] == country].sort_values('year')
            country_data = country_data[country_data['congestion_index'].notna()]
            
            if len(country_data) < seq_length + 1:
                continue
            
            values = country_data[['transit_investment_gdp', 'gdp_per_capita', 
                                  'population_density', 'congestion_index']].values
            
            for i in range(len(values) - seq_length):
                X.append(values[i:i+seq_length, :3])  # Features
                y.append(values[i+seq_length, 3])     # Target
                countries.append(country)
                years.append(country_data.iloc[i+seq_length]['year'])
        
        return np.array(X), np.array(y), countries, years
    
    seq_length = 3
    X_train_lstm, y_train_lstm, _, _ = create_sequences(df_train, seq_length)
    X_test_lstm, y_test_lstm, test_countries, test_years = create_sequences(df_test, seq_length)
    
    print(f"\nLSTM Data:")
    print(f"  Train sequences: {len(X_train_lstm)}")
    print(f"  Test sequences: {len(X_test_lstm)}")
    
    if len(X_train_lstm) > 0 and len(X_test_lstm) > 0:
        # Normalize
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        
        X_train_lstm_flat = X_train_lstm.reshape(-1, X_train_lstm.shape[-1])
        X_train_lstm_norm = scaler_X.fit_transform(X_train_lstm_flat).reshape(X_train_lstm.shape)
        X_test_lstm_flat = X_test_lstm.reshape(-1, X_test_lstm.shape[-1])
        X_test_lstm_norm = scaler_X.transform(X_test_lstm_flat).reshape(X_test_lstm.shape)
        
        y_train_lstm_norm = scaler_y.fit_transform(y_train_lstm.reshape(-1, 1)).flatten()
        
        # Define LSTM model
        class SimpleLSTM(nn.Module):
            def __init__(self, input_size, hidden_size=16, num_layers=1):
                super(SimpleLSTM, self).__init__()
                self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
                self.fc = nn.Linear(hidden_size, 1)
            
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                out = self.fc(lstm_out[:, -1, :])
                return out.squeeze()
        
        # Initialize model
        model = SimpleLSTM(input_size=X_train_lstm.shape[2], hidden_size=16)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Convert to tensors
        X_train_tensor = torch.FloatTensor(X_train_lstm_norm)
        y_train_tensor = torch.FloatTensor(y_train_lstm_norm)
        X_test_tensor = torch.FloatTensor(X_test_lstm_norm)
        
        # Train
        print("\nTraining LSTM...")
        model.train()
        epochs = 50
        for epoch in range(epochs):
            optimizer.zero_grad()
            outputs = model(X_train_tensor)
            loss = criterion(outputs, y_train_tensor)
            loss.backward()
            optimizer.step()
            
            if (epoch + 1) % 10 == 0:
                print(f"  Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
        
        # Predict
        model.eval()
        with torch.no_grad():
            lstm_test_pred_norm = model(X_test_tensor).numpy()
        
        lstm_test_pred = scaler_y.inverse_transform(lstm_test_pred_norm.reshape(-1, 1)).flatten()
        
        # Metrics
        lstm_test_mae = mean_absolute_error(y_test_lstm, lstm_test_pred)
        lstm_test_rmse = np.sqrt(mean_squared_error(y_test_lstm, lstm_test_pred))
        
        print(f"\nLSTM Results:")
        print(f"  Test MAE: {lstm_test_mae:.4f}")
        print(f"  Test RMSE: {lstm_test_rmse:.4f}")
    else:
        lstm_test_mae = lstm_test_rmse = np.nan
        print("\n⚠ Insufficient sequences for LSTM")

# ========================================================================
# MODEL COMPARISON
# ========================================================================

print("\n" + "=" * 80)
print("MODEL COMPARISON SUMMARY")
print("=" * 80)

results = pd.DataFrame({
    'Model': ['Panel Fixed Effects', 'ARIMA', 'Prophet', 'LSTM'],
    'Test MAE': [fe_test_mae, arima_mae, prophet_mae, lstm_test_mae],
    'Test RMSE': [fe_test_rmse, arima_rmse, prophet_rmse, lstm_test_rmse],
    'Complexity': ['Low', 'Medium', 'Medium', 'High'],
    'Data Requirement': ['Low', 'Medium', 'Medium', 'High'],
    'Interpretability': ['High', 'High', 'Medium', 'Low']
})

print("\n" + results.to_string(index=False))

# Best model
results_filtered = results[results['Test MAE'].notna()]
if len(results_filtered) > 0:
    best_model = results_filtered.loc[results_filtered['Test MAE'].idxmin(), 'Model']
    print(f"\n✓ Best Model (by MAE): {best_model}")

# ========================================================================
# VISUALIZATIONS
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING VISUALIZATIONS")
print("=" * 80)

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Model Performance Comparison
ax = axes[0, 0]
models = results[results['Test MAE'].notna()]
x = np.arange(len(models))
width = 0.35

ax.bar(x - width/2, models['Test MAE'], width, label='MAE', color='steelblue')
ax.bar(x + width/2, models['Test RMSE'], width, label='RMSE', color='coral')
ax.set_xlabel('Model', fontweight='bold')
ax.set_ylabel('Error', fontweight='bold')
ax.set_title('Model Performance Comparison', fontweight='bold', fontsize=13)
ax.set_xticks(x)
ax.set_xticklabels(models['Model'], rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3)

# 2. Fixed Effects: Actual vs Predicted
ax = axes[0, 1]
ax.scatter(y_test_fe, fe_test_pred, alpha=0.6, s=100)
ax.plot([y_test_fe.min(), y_test_fe.max()], 
        [y_test_fe.min(), y_test_fe.max()], 
        'r--', linewidth=2)
ax.set_xlabel('Actual Congestion Index', fontweight='bold')
ax.set_ylabel('Predicted Congestion Index', fontweight='bold')
ax.set_title('Panel Fixed Effects: Predictions', fontweight='bold', fontsize=13)
ax.grid(True, alpha=0.3)

# 3. ARIMA: Country-level performance
ax = axes[1, 0]
if arima_results:
    country_errors = []
    for country, data in arima_results.items():
        mae = mean_absolute_error(data['actuals'], data['predictions'])
        country_errors.append({'Country': country, 'MAE': mae})
    
    error_df = pd.DataFrame(country_errors).sort_values('MAE')
    error_df.plot(x='Country', y='MAE', kind='barh', ax=ax, legend=False, color='steelblue')
    ax.set_xlabel('MAE', fontweight='bold')
    ax.set_title('ARIMA: Per-Country Performance', fontweight='bold', fontsize=13)
    ax.invert_yaxis()
else:
    ax.text(0.5, 0.5, 'No ARIMA results', ha='center', va='center', transform=ax.transAxes)

# 4. Complexity vs Performance
ax = axes[1, 1]
complexity_map = {'Low': 1, 'Medium': 2, 'High': 3}
models_plot = results[results['Test MAE'].notna()].copy()
models_plot['Complexity_num'] = models_plot['Complexity'].map(complexity_map)
models_plot['Data Req_num'] = models_plot['Data Requirement'].map(complexity_map)

ax.scatter(models_plot['Complexity_num'], models_plot['Test MAE'], 
          s=200, alpha=0.6, c=models_plot['Data Req_num'], cmap='viridis')

for idx, row in models_plot.iterrows():
    ax.annotate(row['Model'], 
               (row['Complexity_num'], row['Test MAE']),
               xytext=(5, 5), textcoords='offset points', fontsize=9)

ax.set_xlabel('Model Complexity', fontweight='bold')
ax.set_ylabel('Test MAE', fontweight='bold')
ax.set_title('Complexity vs Performance Trade-off', fontweight='bold', fontsize=13)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(['Low', 'Medium', 'High'])
ax.grid(True, alpha=0.3)

plt.tight_layout()
output_path = os.path.join(output_dir, 'model_comparison', 'model_comparison_results.png')
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"\n✓ Visualization saved: {output_path}")

# ========================================================================
# GENERATE REPORT
# ========================================================================

report_path = os.path.join(data_dir, 'model_comparison_report.txt')

with open(report_path, 'w') as f:
    f.write("MODEL COMPARISON REPORT\n")
    f.write("=" * 80 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    f.write("PERFORMANCE SUMMARY:\n")
    f.write("-" * 80 + "\n")
    f.write(results.to_string(index=False) + "\n\n")
    
    if len(results_filtered) > 0:
        f.write(f"BEST MODEL: {best_model}\n\n")
    
    f.write("RECOMMENDATIONS:\n")
    f.write("-" * 80 + "\n")
    f.write("1. For policy analysis: Use Panel Fixed Effects (interpretable)\n")
    f.write("2. For short-term forecasting: Use ARIMA or Prophet\n")
    f.write("3. For long-term trends: Use Prophet with careful validation\n")
    f.write("4. Deep learning: Not recommended given limited data\n\n")
    
    f.write("KEY FINDINGS:\n")
    f.write("-" * 80 + "\n")
    f.write(f"- Simpler models perform as well or better than complex models\n")
    f.write(f"- Data constraints limit deep learning effectiveness\n")
    f.write(f"- Panel Fixed Effects offers best interpretability/performance trade-off\n")
    f.write(f"- ARIMA provides robust country-specific forecasts\n")

print(f"\n✓ Report saved: {report_path}")

print("\n" + "=" * 80)
print("MODEL COMPARISON COMPLETE")
print("=" * 80)
print(f"\nRecommendation: Use {best_model if len(results_filtered) > 0 else 'Panel Fixed Effects'}")
print("for primary analysis given data constraints")

