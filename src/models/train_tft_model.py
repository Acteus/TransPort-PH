"""
Temporal Fusion Transformer (TFT) Training Script
==================================================
This script trains a TFT model using PyTorch and pytorch-forecasting library
to forecast congestion and other urban outcomes based on transit investment.

The TFT model is designed for multi-horizon time series forecasting with
interpretable attention mechanisms.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import torch
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import QuantileLoss, SMAPE, MAE
from lightning.pytorch import Trainer
from lightning.pytorch.callbacks import EarlyStopping, ModelCheckpoint
from lightning.pytorch.loggers import TensorBoardLogger
import os
import sys
from datetime import datetime
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
torch.manual_seed(42)
np.random.seed(42)

# Set up directories (use absolute paths based on script location)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
data_dir = os.path.join(project_dir, 'data')
output_dir = os.path.join(project_dir, 'output')
model_dir = os.path.join(project_dir, 'models')
os.makedirs(output_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)

print("=" * 80)
print("TEMPORAL FUSION TRANSFORMER (TFT) TRAINING")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

# Check for GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"\nUsing device: {device}")
if device == 'cuda':
    print(f"GPU: {torch.cuda.get_device_name(0)}")

# ========================================================================
# LOAD AND PREPARE DATA
# ========================================================================

print("\n" + "=" * 80)
print("DATA LOADING AND PREPARATION")
print("=" * 80)

# Load clean panel data
df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))
print(f"\nLoaded clean panel: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Ensure year is numeric
df['year'] = pd.to_numeric(df['year'], errors='coerce')

# Drop rows with missing critical values
df_model = df.dropna(subset=['country', 'year', 'congestion_index'])
print(f"After removing missing country/year/target: {df_model.shape}")

# Check if we have any data
if len(df_model) == 0:
    print("\n✗ ERROR: No valid data after filtering!")
    print("  Please check that clean_panel.csv has:")
    print("  - Valid 'country' column")
    print("  - Valid 'year' column") 
    print("  - Valid 'congestion_index' column")
    sys.exit(1)

# Create time index (continuous integer starting from 0)
min_year = df_model['year'].min()
df_model['time_idx'] = (df_model['year'] - min_year).astype(int)

print(f"\nTime index range: {df_model['time_idx'].min()} to {df_model['time_idx'].max()}")
print(f"Year range: {df_model['year'].min():.0f} to {df_model['year'].max():.0f}")

# Country statistics
country_counts = df_model.groupby('country').size().sort_values(ascending=False)
print(f"\nNumber of countries: {len(country_counts)}")
print(f"Observations per country (top 10):")
print(country_counts.head(10))

# Filter countries with sufficient data (at least 5 observations to be more lenient)
min_obs = 5
valid_countries = country_counts[country_counts >= min_obs].index
df_model = df_model[df_model['country'].isin(valid_countries)]
print(f"\nCountries after filtering (>={min_obs} obs): {len(valid_countries)}")
print(f"Total observations: {len(df_model)}")

# Final check
if len(df_model) == 0:
    print("\n✗ ERROR: No countries with sufficient observations!")
    print(f"  Tried minimum of {min_obs} observations per country")
    sys.exit(1)

# Fill missing values with forward fill and then backward fill, then median
numeric_cols = df_model.select_dtypes(include=[np.number]).columns
for col in numeric_cols:
    if col not in ['time_idx', 'year']:
        # Forward fill within each country
        df_model[col] = df_model.groupby('country')[col].transform(
            lambda x: x.fillna(method='ffill').fillna(method='bfill')
        )
        # Fill any remaining with median
        df_model[col] = df_model[col].fillna(df_model[col].median())

# Verify no missing values in key columns
print("\nMissing values after imputation:")
print(df_model[['country', 'time_idx', 'congestion_index', 'transit_investment_gdp', 
                'gdp_per_capita', 'population_density']].isnull().sum())

# ========================================================================
# DEFINE TIME SERIES DATASET
# ========================================================================

print("\n" + "=" * 80)
print("TIME SERIES DATASET CONFIGURATION")
print("=" * 80)

# Split into train and validation
# For time series, we'll do a temporal split: use earlier years for training
# and later years for validation, ensuring all countries appear in both sets
# This approach is more realistic for time series forecasting

# Strategy: For each country, split at a time point (e.g., 80% of their timeline)
train_list = []
val_list = []

for country in df_model['country'].unique():
    country_data = df_model[df_model['country'] == country].sort_values('time_idx')
    n_obs = len(country_data)
    
    # Use 80% for training, 20% for validation
    train_size = max(1, int(n_obs * 0.8))  # At least 1 observation for training
    
    train_list.append(country_data.iloc[:train_size])
    if n_obs > train_size:  # Only add to validation if we have data left
        val_list.append(country_data.iloc[train_size:])

df_train = pd.concat(train_list, ignore_index=True)
df_val = pd.concat(val_list, ignore_index=True) if val_list else pd.DataFrame()

print(f"\nTrain set: {len(df_train)} observations")
if len(df_train) > 0:
    print(f"  Year range: {df_train['year'].min():.0f} - {df_train['year'].max():.0f}")
    print(f"  Countries: {df_train['country'].nunique()}")

print(f"\nValidation set: {len(df_val)} observations")
if len(df_val) > 0:
    print(f"  Year range: {df_val['year'].min():.0f} - {df_val['year'].max():.0f}")
    print(f"  Countries: {df_val['country'].nunique()}")
    
    # Check that validation countries are in training (categorical encoding requirement)
    val_countries = set(df_val['country'].unique())
    train_countries = set(df_train['country'].unique())
    unknown_countries = val_countries - train_countries
    if unknown_countries:
        print(f"\n⚠ WARNING: Validation has countries not in training: {unknown_countries}")
        print("  Filtering validation set to only include training countries...")
        df_val = df_val[df_val['country'].isin(train_countries)]
        print(f"  Validation set after filtering: {len(df_val)} observations")
else:
    print("\n⚠ WARNING: Empty validation set, will use a small portion of training data")

# Check if we have enough data
if len(df_train) < 10:
    print("\n" + "=" * 80)
    print("INSUFFICIENT DATA FOR TFT MODEL")
    print("=" * 80)
    print(f"\n✗ ERROR: Not enough training data")
    print(f"  Current: {len(df_train)} training samples")
    print(f"  Required: At least 1000+ samples for meaningful TFT training")
    print(f"  Current: {df_model['country'].nunique()} countries")
    print(f"  Required: At least 10+ countries with time series data")
    print("\n" + "-" * 80)
    print("RECOMMENDATIONS:")
    print("-" * 80)
    print("1. Use simpler time series models:")
    print("   - Panel Fixed Effects Regression (already in pipeline)")
    print("   - ARIMA/SARIMAX per country")
    print("   - Facebook Prophet")
    print("   - Simple LSTM with minimal architecture")
    print("\n2. Expand your dataset:")
    print("   - Gather more congestion data from TomTom (more countries/years)")
    print("   - Impute missing congestion values using ML")
    print("   - Consider alternative target variables with better coverage")
    print("\n3. See DATA_COVERAGE_ANALYSIS.md for detailed guidance")
    print("=" * 80 + "\n")
    sys.exit(1)
    
if len(df_val) < 5:
    print("\n⚠ WARNING: Very small validation set, results may not be reliable")

# Define prediction and encoder lengths
# Reduced to work with limited data (9 years total: 2015-2023)
max_encoder_length = 3  # Use 3 years of history (reduced from 5)
max_prediction_length = 2  # Predict 2 years ahead (reduced from 3)

print(f"\nEncoder length: {max_encoder_length} time steps")
print(f"Prediction length: {max_prediction_length} time steps")
print(f"  (Adjusted for limited time range: {df_model['year'].max() - df_model['year'].min() + 1} years)")

# Static variables (don't change over time for each group)
# In our case, country is static but we'll encode it as categorical
static_categoricals = []
static_reals = []

# Time-varying known reals (known in advance)
# These include variables we can plan or predict
time_varying_known_reals = [
    'time_idx',
    'transit_investment_gdp',  # Policy variable
    'year',
]

# Time-varying unknown reals (not known in advance)
# These are outcomes or variables we need to forecast
time_varying_unknown_reals = [
    'gdp_per_capita',
    'population_density',
]

# Target variable
target = 'congestion_index'

# Ensure all required columns exist
all_required = (time_varying_known_reals + time_varying_unknown_reals + 
                [target] + ['country'])
for col in all_required:
    if col not in df_train.columns:
        print(f"WARNING: Column {col} not found in data")

print("\nVariable configuration:")
print(f"  Target: {target}")
print(f"  Time-varying known: {time_varying_known_reals}")
print(f"  Time-varying unknown: {time_varying_unknown_reals}")

# Create TimeSeriesDataSet for training
try:
    training = TimeSeriesDataSet(
        df_train,
        time_idx='time_idx',
        target=target,
        group_ids=['country'],
        min_encoder_length=max_encoder_length // 2,
        max_encoder_length=max_encoder_length,
        min_prediction_length=1,
        max_prediction_length=max_prediction_length,
        static_categoricals=static_categoricals,
        static_reals=static_reals,
        time_varying_known_reals=time_varying_known_reals,
        time_varying_unknown_reals=time_varying_unknown_reals,
        target_normalizer=GroupNormalizer(
            groups=['country'],
            transformation='softplus'
        ),
        add_relative_time_idx=True,
        add_target_scales=True,
        add_encoder_length=True,
        allow_missing_timesteps=True,
    )
    
    print("\n✓ Training dataset created successfully")
    print(f"  Number of samples: {len(training)}")
    
except Exception as e:
    print(f"\n✗ Error creating training dataset: {e}")
    print("\nAttempting with minimal configuration...")
    
    # Fallback: simpler configuration
    training = TimeSeriesDataSet(
        df_train,
        time_idx='time_idx',
        target=target,
        group_ids=['country'],
        max_encoder_length=max_encoder_length,
        max_prediction_length=max_prediction_length,
        time_varying_known_reals=['time_idx', 'transit_investment_gdp'],
        time_varying_unknown_reals=['congestion_index'],
        allow_missing_timesteps=True,
    )
    print("✓ Training dataset created with minimal configuration")

# Create validation dataset
# IMPORTANT: Pass the full dataset (train + val concatenated) so validation samples
# can access encoder history from the training period
df_full = pd.concat([df_train, df_val], ignore_index=True).sort_values(['country', 'time_idx'])
validation = TimeSeriesDataSet.from_dataset(training, df_full, predict=True, stop_randomization=True)
print(f"✓ Validation dataset created")
print(f"  Number of samples: {len(validation)}")

# Create dataloaders
batch_size = 32
train_dataloader = training.to_dataloader(train=True, batch_size=batch_size, num_workers=0)
val_dataloader = validation.to_dataloader(train=False, batch_size=batch_size, num_workers=0)

print(f"\n✓ DataLoaders created (batch_size={batch_size})")
print(f"  Train batches: {len(train_dataloader)}")
print(f"  Validation batches: {len(val_dataloader)}")

# ========================================================================
# CONFIGURE AND TRAIN TFT MODEL
# ========================================================================

print("\n" + "=" * 80)
print("MODEL CONFIGURATION AND TRAINING")
print("=" * 80)

# Configure model
tft_config = {
    'hidden_size': 32,  # Hidden size of LSTM layers
    'lstm_layers': 2,   # Number of LSTM layers
    'dropout': 0.1,
    'output_size': 7,   # Quantile outputs for probabilistic forecasting
    'loss': QuantileLoss(),
    'attention_head_size': 4,
    'max_encoder_length': max_encoder_length,
    'static_categoricals': [],
    'static_reals': [],
    'time_varying_categoricals_encoder': [],
    'time_varying_categoricals_decoder': [],
    'categorical_groups': {},
    'time_varying_reals_encoder': time_varying_known_reals + time_varying_unknown_reals,
    'time_varying_reals_decoder': time_varying_known_reals + [target],
    'x_reals': [],
    'x_categoricals': [],
    'hidden_continuous_size': 16,
    'hidden_continuous_sizes': {},
    'embedding_sizes': {},
    'embedding_paddings': [],
    'embedding_labels': {},
    'learning_rate': 0.001,
    'log_interval': 10,
    'log_val_interval': 1,
    'reduce_on_plateau_patience': 4,
}

print("\nModel configuration:")
for key, value in tft_config.items():
    if not isinstance(value, (dict, list)) or len(str(value)) < 50:
        print(f"  {key}: {value}")

# Create model with custom validation to avoid plotting errors
class TFTWithoutPlotting(TemporalFusionTransformer):
    """TFT model that skips plotting during validation to avoid histogram errors."""
    
    def create_log(self, x, y, out, batch_idx, **kwargs):
        """Override create_log to skip plotting but keep loss calculation."""
        # Calculate losses but skip plotting
        log = {}
        
        # Get the loss
        if hasattr(self, 'loss'):
            log['loss'] = self.loss(out['prediction'], y[0])
        
        # Log metrics without plotting (only if metrics attribute exists)
        if hasattr(self, 'metrics') and self.metrics is not None:
            for metric_name, metric in self.metrics.items():
                try:
                    log[f'val_{metric_name}'] = metric(out['prediction'], y[0])
                except Exception:
                    # Skip metrics that fail
                    pass
        
        return log
    
    def log_interpretation(self, outputs):
        """Override to skip interpretation logging that causes errors."""
        # Skip interpretation logging during training to avoid KeyError
        pass
    
    def on_epoch_end(self, outputs):
        """Override to skip interpretation logging at epoch end."""
        # Just log the basic metrics without interpretation
        if len(outputs) > 0:
            # Calculate average loss
            avg_loss = torch.stack([x["loss"] for x in outputs if "loss" in x]).mean()
            self.log("val_loss", avg_loss, prog_bar=True)

try:
    tft = TFTWithoutPlotting.from_dataset(
        training,
        learning_rate=tft_config['learning_rate'],
        hidden_size=tft_config['hidden_size'],
        attention_head_size=tft_config['attention_head_size'],
        dropout=tft_config['dropout'],
        hidden_continuous_size=tft_config['hidden_continuous_size'],
        loss=tft_config['loss'],
        log_interval=tft_config['log_interval'],
        reduce_on_plateau_patience=tft_config['reduce_on_plateau_patience'],
    )
    
    print("\n✓ TFT model initialized (with plotting disabled)")
    print(f"  Total parameters: {sum(p.numel() for p in tft.parameters()):,}")
    print(f"  Trainable parameters: {sum(p.numel() for p in tft.parameters() if p.requires_grad):,}")
    
except Exception as e:
    print(f"\n✗ Error initializing TFT model: {e}")
    raise

# Configure trainer with validation enabled
checkpoint_callback = ModelCheckpoint(
    dirpath=model_dir,
    filename='tft-{epoch:02d}-{val_loss:.2f}',
    save_top_k=3,
    verbose=True,
    monitor='val_loss',
    mode='min',
    save_last=True,
)

early_stop_callback = EarlyStopping(
    monitor='val_loss',
    min_delta=1e-4,
    patience=10,
    verbose=True,
    mode='min'
)

logger = TensorBoardLogger(
    save_dir=output_dir,
    name='tft_logs'
)

trainer = Trainer(
    max_epochs=50,
    accelerator='cpu' if device == 'cpu' else 'auto',
    devices=1 if device == 'cpu' else 'auto',
    gradient_clip_val=0.1,
    callbacks=[checkpoint_callback, early_stop_callback],
    logger=logger,
    log_every_n_steps=10,
    enable_progress_bar=True,
    num_sanity_val_steps=0,  # Disable sanity check but keep validation
    enable_checkpointing=True,
    enable_model_summary=True,
)

print("\n✓ Trainer configured")
print(f"  Max epochs: {trainer.max_epochs}")
print(f"  Early stopping patience: {early_stop_callback.patience}")
print(f"  Checkpoint directory: {model_dir}")

# ========================================================================
# TRAIN MODEL
# ========================================================================

print("\n" + "=" * 80)
print("TRAINING TFT MODEL")
print("=" * 80)
print(f"\nStarting training at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"This may take several minutes to hours depending on data size and hardware...\n")

try:
    # Train the model - using proper argument names
    trainer.fit(
        model=tft,
        train_dataloaders=train_dataloader,
        val_dataloaders=val_dataloader,
    )
    
    print("\n✓ Training completed successfully")
    print(f"  Best model checkpoint: {checkpoint_callback.best_model_path}")
    print(f"  Best validation loss: {checkpoint_callback.best_model_score:.4f}")
    
except Exception as e:
    print(f"\n✗ Training failed: {e}")
    import traceback
    traceback.print_exc()
    raise

# ========================================================================
# EVALUATE MODEL
# ========================================================================

print("\n" + "=" * 80)
print("MODEL EVALUATION")
print("=" * 80)

# Load best model
best_model_path = checkpoint_callback.best_model_path
best_tft = TemporalFusionTransformer.load_from_checkpoint(best_model_path)

print(f"\nLoaded best model from: {best_model_path}")

# Initialize metrics with default values
mae, rmse, mape = None, None, None
evaluation_success = False

# Make predictions on validation set
try:
    # Collect predictions and actuals batch by batch
    actuals_list = []
    preds_list = []
    
    best_tft.eval()
    with torch.no_grad():
        for batch in val_dataloader:
            # Unpack batch
            x, y = batch
            
            # Get predictions
            output = best_tft(x)
            
            # Extract predictions (quantile at 0.5 for point predictions)
            if isinstance(output, dict) and 'prediction' in output:
                pred = output['prediction'][:, :, 3]  # Middle quantile (0.5)
            else:
                pred = output
            
            # Extract actual values
            if isinstance(y, tuple):
                actual = y[0]  # First element is target
            else:
                actual = y
            
            # Convert to numpy
            actuals_list.append(actual.detach().cpu().numpy())
            preds_list.append(pred.detach().cpu().numpy())
    
    # Concatenate all batches
    actuals = np.concatenate(actuals_list, axis=0).flatten()
    preds = np.concatenate(preds_list, axis=0).flatten()
    
    # Calculate metrics
    mae = np.mean(np.abs(actuals - preds))
    rmse = np.sqrt(np.mean((actuals - preds) ** 2))
    mape = np.mean(np.abs((actuals - preds) / (actuals + 1e-8))) * 100
    evaluation_success = True
    
    print("\nValidation Metrics:")
    print(f"  MAE:  {mae:.4f}")
    print(f"  RMSE: {rmse:.4f}")
    print(f"  MAPE: {mape:.2f}%")
    
    # Visualize predictions vs actuals
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot 1: Scatter plot
    axes[0].scatter(actuals, preds, alpha=0.5, s=20)
    axes[0].plot([actuals.min(), actuals.max()], [actuals.min(), actuals.max()], 
                 'r--', lw=2, label='Perfect prediction')
    axes[0].set_xlabel('Actual Congestion Index', fontsize=12)
    axes[0].set_ylabel('Predicted Congestion Index', fontsize=12)
    axes[0].set_title(f'TFT Predictions vs Actuals\nMAE={mae:.4f}, RMSE={rmse:.4f}', fontsize=13)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Residuals
    residuals = actuals - preds
    axes[1].hist(residuals, bins=30, alpha=0.7, edgecolor='black')
    axes[1].axvline(x=0, color='r', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Residual (Actual - Predicted)', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Distribution of Residuals', fontsize=13)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'tft_evaluation.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n✓ Evaluation plot saved to: {output_dir}/tft_evaluation.png")
    
except Exception as e:
    print(f"\n✗ Evaluation failed: {e}")
    import traceback
    traceback.print_exc()

# ========================================================================
# INTERPRET MODEL (VARIABLE IMPORTANCE)
# ========================================================================

print("\n" + "=" * 80)
print("MODEL INTERPRETATION")
print("=" * 80)

try:
    # Get a single batch for interpretation
    batch = next(iter(val_dataloader))
    
    # Get variable importance
    interpretation = best_tft.interpret_output(batch, reduction='sum')
    
    # Extract variable importance - handle different output formats
    if isinstance(interpretation, dict):
        encoder_vars = interpretation.get('encoder_variables', {})
        decoder_vars = interpretation.get('decoder_variables', {})
    else:
        print("  Warning: Unexpected interpretation format, skipping...")
        raise ValueError("Could not extract variable importance from interpretation")
    
    if encoder_vars or decoder_vars:
        print("\nEncoder Variable Importance:")
        for var, importance in encoder_vars.items():
            print(f"  {var}: {importance:.4f}")
        
        print("\nDecoder Variable Importance:")
        for var, importance in decoder_vars.items():
            print(f"  {var}: {importance:.4f}")
        
        # Visualize variable importance
        fig, ax = plt.subplots(figsize=(10, 6))
        
        all_vars = list(encoder_vars.keys()) + list(decoder_vars.keys())
        all_importance = list(encoder_vars.values()) + list(decoder_vars.values())
        
        # Sort by importance
        sorted_indices = np.argsort(all_importance)[::-1]
        sorted_vars = [all_vars[i] for i in sorted_indices]
        sorted_importance = [all_importance[i] for i in sorted_indices]
        
        ax.barh(range(len(sorted_vars)), sorted_importance, alpha=0.7)
        ax.set_yticks(range(len(sorted_vars)))
        ax.set_yticklabels(sorted_vars, fontsize=10)
        ax.set_xlabel('Importance', fontsize=12)
        ax.set_title('TFT Variable Importance', fontsize=14, pad=15)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'tft_variable_importance.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"\n✓ Variable importance plot saved to: {output_dir}/tft_variable_importance.png")
    else:
        print("\n  No variable importance data available")
    
except Exception as e:
    print(f"\nCould not generate interpretation: {e}")
    import traceback
    traceback.print_exc()

# ========================================================================
# SAVE SUMMARY REPORT
# ========================================================================

print("\n" + "=" * 80)
print("GENERATING SUMMARY REPORT")
print("=" * 80)

# Format evaluation metrics section
if evaluation_success and mae is not None:
    eval_metrics_str = f"""EVALUATION METRICS:
- MAE: {mae:.4f}
- RMSE: {rmse:.4f}
- MAPE: {mape:.2f}%"""
else:
    eval_metrics_str = """EVALUATION METRICS:
- Evaluation not available (see errors above)"""

summary_report = f"""
TEMPORAL FUSION TRANSFORMER (TFT) TRAINING REPORT
{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DATA SUMMARY:
- Training observations: {len(df_train)}
- Validation observations: {len(df_val)}
- Countries: {len(valid_countries)}
- Time range: {df_model['year'].min():.0f} - {df_model['year'].max():.0f}
- Train years: {df_train['year'].min():.0f} - {df_train['year'].max():.0f}
- Validation years: {df_val['year'].min():.0f} - {df_val['year'].max():.0f}

MODEL CONFIGURATION:
- Architecture: Temporal Fusion Transformer
- Target variable: {target}
- Encoder length: {max_encoder_length} time steps
- Prediction length: {max_prediction_length} time steps
- Hidden size: {tft_config['hidden_size']}
- LSTM layers: {tft_config['lstm_layers']}
- Attention heads: {tft_config['attention_head_size']}
- Dropout: {tft_config['dropout']}
- Learning rate: {tft_config['learning_rate']}

TIME-VARYING VARIABLES:
Known reals: {', '.join(time_varying_known_reals)}
Unknown reals: {', '.join(time_varying_unknown_reals)}

TRAINING:
- Device: {device}
- Batch size: {batch_size}
- Max epochs: {trainer.max_epochs}
- Early stopping patience: {early_stop_callback.patience}
- Best model: {checkpoint_callback.best_model_path}
- Best validation loss: {checkpoint_callback.best_model_score:.4f}

{eval_metrics_str}

OUTPUTS:
- Model checkpoints: {model_dir}/
- Evaluation plot: {output_dir}/tft_evaluation.png
- Variable importance: {output_dir}/tft_variable_importance.png
- TensorBoard logs: {output_dir}/tft_logs/

INTERPRETATION:
The TFT model provides multi-horizon probabilistic forecasts of {target}
based on historical patterns and known future values of policy variables
like transit investment. The attention mechanism identifies which time steps
and variables are most important for predictions.

NEXT STEPS:
1. Review variable importance to understand key drivers
2. Examine attention patterns for different countries
3. Use model for scenario analysis and policy simulation
4. Validate predictions against domain knowledge
5. Consider ensemble with other models for robustness
"""

# Save report
report_path = os.path.join(data_dir, 'tft_training_report.txt')
with open(report_path, 'w') as f:
    f.write(summary_report)

print(summary_report)
print(f"\n✓ Full report saved to: {report_path}")

print("\n" + "=" * 80)
print("TFT TRAINING COMPLETE")
print("=" * 80)
print(f"\nBest model saved to: {checkpoint_callback.best_model_path}")
print(f"To view TensorBoard logs, run:")
print(f"  tensorboard --logdir {output_dir}/tft_logs")
print("=" * 80)

