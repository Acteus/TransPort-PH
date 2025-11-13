# Data Coverage Analysis & Solutions

## Current Data Situation

### Dataset Overview
- **Total Panel Data**: 6,101 rows covering multiple countries from 2000-2019
- **Congestion Index Coverage**: Only 11 rows
  - Philippines: 6 observations (2015-2019)
  - Singapore: 5 observations (2015-2019)

### The Problem
**Temporal Fusion Transformer (TFT) requires:**
- ❌ Minimum 1,000+ observations (we have 11)
- ❌ Multiple time series groups, ideally 10+ countries (we have 2)
- ❌ Longer time periods, ideally 10+ years (we have 5 years)
- ❌ Rich temporal patterns to learn (insufficient with 2 countries)

**Current status**: ❌ **INSUFFICIENT DATA FOR DEEP LEARNING MODELS**

---

## Solution Options

### ✅ **Option 1: Use Simpler Time Series Models** (RECOMMENDED)

Given your limited data, these models are more appropriate:

#### A. **Panel Fixed Effects Regression** (Already in pipeline)
- ✅ Works with small datasets
- ✅ Handles country-specific effects
- ✅ Interpretable coefficients
- ✅ Already implemented in your pipeline

#### B. **ARIMA/SARIMAX per Country**
```python
# Example for Philippines
from statsmodels.tsa.statespace.sarimax import SARIMAX

model = SARIMAX(
    philippines_data['congestion_index'],
    exog=philippines_data[['transit_investment_gdp', 'gdp_per_capita']],
    order=(1, 0, 1),  # (p,d,q)
    seasonal_order=(0, 0, 0, 0)
)
```

#### C. **Facebook Prophet**
```python
from prophet import Prophet

model = Prophet()
# Add regressors
model.add_regressor('transit_investment_gdp')
model.add_regressor('gdp_per_capita')
model.fit(df_prophet)
```

#### D. **Simple LSTM** (Minimal Architecture)
- Much lighter than TFT
- Can work with 10+ observations
- Less prone to overfitting

---

### 🔄 **Option 2: Expand Your Dataset**

#### A. **Impute Missing Congestion Values**

Use available features to predict congestion for other countries:

```python
# Train a regression model on available congestion data
from sklearn.ensemble import RandomForestRegressor

# Use countries with congestion data
X_train = df[df['congestion_index'].notna()][features]
y_train = df[df['congestion_index'].notna()]['congestion_index']

# Predict for others
X_predict = df[df['congestion_index'].isna()][features]
imputed_values = model.predict(X_predict)
```

**Pros**: Increases dataset size
**Cons**: Imputed values may not be accurate; adds uncertainty

#### B. **Gather More Congestion Data**

TomTom Traffic Index provides data for many cities:
- Expand to more Asian countries
- Get historical data back to 2008-2010 if available
- Include major cities within countries

**Target**: At least 20 countries × 10 years = 200+ observations

#### C. **Use Alternative Target Variables**

Consider variables with better coverage in your dataset:
- `modal_share_public` (public transport usage %)
- `pm25` (air pollution, proxy for traffic)
- `gdp_per_capita` (economic outcome)
- Composite index combining multiple outcomes

---

### 🔧 **Option 3: Modify TFT to Work with Limited Data** (NOT RECOMMENDED)

While possible, this will likely produce poor results:

```python
# Ultra-minimal TFT configuration
training = TimeSeriesDataSet(
    df_train,
    time_idx='time_idx',
    target='congestion_index',
    group_ids=['country'],
    min_encoder_length=1,
    max_encoder_length=2,  # Very short
    min_prediction_length=1,
    max_prediction_length=1,  # Only 1 step ahead
    time_varying_known_reals=['time_idx', 'transit_investment_gdp'],
    time_varying_unknown_reals=['congestion_index'],
    allow_missing_timesteps=True,
)

# Tiny model
tft = TemporalFusionTransformer.from_dataset(
    training,
    hidden_size=8,  # Very small
    lstm_layers=1,
    attention_head_size=1,
    dropout=0.3,  # Higher to prevent overfitting
)
```

**Problems**:
- Will likely overfit
- Poor generalization
- Unreliable predictions
- Not statistically valid

---

## Recommended Action Plan

### **Phase 1: Use What Works Now** ✅

1. **Continue with Panel Fixed Effects**
   - Already working
   - Statistically valid for your data size
   - Interpretable results

2. **Add Simple ARIMA Models**
   - One model per country
   - Use transit investment as exogenous variable
   - Good for short-term forecasting

3. **Implement Prophet**
   - Easy to use
   - Handles missing data well
   - Good for trend analysis

### **Phase 2: Expand Dataset** 📊

1. **Gather More Congestion Data**
   - Contact TomTom for historical data
   - Add more Southeast Asian countries
   - Target: 20+ countries, 2008-2019

2. **Consider Imputation**
   - Use ML to impute missing congestion values
   - Validate imputation accuracy
   - Document uncertainty

3. **Alternative Targets**
   - Explore `modal_share_public` as target
   - Check coverage of other outcome variables
   - Consider composite indices

### **Phase 3: Revisit Deep Learning** 🤖

Only after you have:
- ✅ 500+ observations minimum (preferably 1,000+)
- ✅ 10+ countries
- ✅ 10+ years of data per country
- ✅ Sufficient temporal variation

Then consider:
- TFT (Temporal Fusion Transformer)
- DeepAR
- N-BEATS
- Transformer models

---

## Implementation: Skip TFT Training

Add to your `run_all.py`:

```python
# Check data sufficiency before TFT
df = pd.read_csv('../data/clean_panel.csv')
congestion_data = df['congestion_index'].notna().sum()

if congestion_data < 100:
    print(f"⚠️  WARNING: Only {congestion_data} observations with congestion_index")
    print("   Skipping TFT training (requires 1000+ observations)")
    print("   Using simpler models instead...")
    skip_tft = True
else:
    skip_tft = False

if not skip_tft:
    run_script('prepare_tft_dataset.py')
    run_script('train_tft_model.py')
```

---

## Quick Comparison: Model Requirements

| Model | Min Data | Countries | Years | Complexity | Interpretability |
|-------|----------|-----------|-------|------------|------------------|
| **Panel FE** | 20+ | 2+ | 3+ | Low | ⭐⭐⭐⭐⭐ |
| **ARIMA** | 10+ | 1 | 5+ | Low | ⭐⭐⭐⭐ |
| **Prophet** | 20+ | 1 | 3+ | Low | ⭐⭐⭐⭐ |
| **Simple LSTM** | 50+ | 3+ | 5+ | Medium | ⭐⭐⭐ |
| **TFT** | 1000+ | 10+ | 10+ | High | ⭐⭐⭐ |
| **DeepAR** | 1000+ | 10+ | 10+ | High | ⭐⭐ |

**Legend**: ⭐ = Better

---

## Next Steps

1. **Immediate**: 
   - Modify `run_all.py` to skip TFT when data insufficient
   - Add ARIMA/Prophet models to pipeline
   - Document data limitations in reports

2. **Short-term** (1-2 weeks):
   - Research TomTom data availability
   - Explore imputation strategies
   - Test alternative target variables

3. **Long-term** (1-3 months):
   - Expand dataset to 20+ countries
   - Gather 10+ years of data
   - Revisit deep learning models

---

## Questions to Consider

1. **Is congestion the right target?**
   - Do you have better coverage for modal share or pollution?
   
2. **Can you get more data?**
   - TomTom historical data
   - Other traffic data sources
   - City-level instead of country-level?

3. **What's your prediction goal?**
   - Policy impact (simpler models fine)
   - Precise forecasting (need more data)
   - Causal inference (current approach works)

---

**Conclusion**: With only 11 observations, **skip TFT entirely** and use panel regression, ARIMA, or Prophet. Focus on data expansion before attempting deep learning.
