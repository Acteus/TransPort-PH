import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline
from statsmodels.nonparametric.smoothers_lowess import lowess
import os

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))

# Define key relationships to plot
relationships = [
    ('transit_investment_gdp', 'congestion_index', 'Transit Investment vs Congestion'),
    ('gdp_per_capita', 'congestion_index', 'GDP per Capita vs Congestion'),
    ('modal_share_public', 'congestion_index', 'Public Transit Modal Share vs Congestion'),
    ('population_density', 'congestion_index', 'Population Density vs Congestion'),
    ('transit_investment_gdp', 'pm25', 'Transit Investment vs PM2.5'),
    ('gdp_per_capita', 'pm25', 'GDP per Capita vs PM2.5'),
    # Additional relationships that include Singapore data
    ('gdp_per_capita', 'transit_investment_gdp', 'GDP per Capita vs Transit Investment'),
    ('population_density', 'transit_investment_gdp', 'Population Density vs Transit Investment'),
    ('population_density', 'gdp_per_capita', 'Population Density vs GDP per Capita')
]

print("Generating scatter plots with Loess smoothing...")

for x_var, y_var, title in relationships:
    if x_var in df.columns and y_var in df.columns:
        # Get clean data
        data = df[[x_var, y_var]].dropna()
        
        if len(data) > 10:  # Need enough points for smoothing
            fig, ax = plt.subplots(figsize=(10, 7))
            
            # Scatter plot
            ax.scatter(data[x_var], data[y_var], alpha=0.4, s=50, label='Data points')
            
            # Loess smoothing
            try:
                # Sort data by x for proper curve plotting
                data_sorted = data.sort_values(x_var)
                
                # Apply Lowess smoothing
                smoothed = lowess(data_sorted[y_var], data_sorted[x_var], 
                                 frac=0.3, it=3, return_sorted=True)
                
                # Plot smoothed curve
                ax.plot(smoothed[:, 0], smoothed[:, 1], 'r-', linewidth=2.5, 
                       label='Loess smooth', alpha=0.8)
                
                # Add linear trend for comparison
                z = np.polyfit(data[x_var], data[y_var], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(data[x_var].min(), data[x_var].max(), 100)
                ax.plot(x_trend, p(x_trend), 'g--', linewidth=2, 
                       label='Linear trend', alpha=0.6)
                
            except Exception as e:
                print(f"Could not apply Loess smoothing for {title}: {e}")
            
            # Calculate correlation
            corr = data[x_var].corr(data[y_var])
            
            ax.set_xlabel(x_var.replace('_', ' ').title(), fontsize=12)
            ax.set_ylabel(y_var.replace('_', ' ').title(), fontsize=12)
            ax.set_title(f'{title}\n(Correlation: {corr:.3f}, n={len(data)})', 
                        fontsize=14, pad=15)
            ax.legend(loc='best', fontsize=10)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            safe_title = title.replace(' ', '_').replace('/', '_')
            plt.savefig(os.path.join(output_dir, f'scatter_loess_{safe_title}.png'), 
                       dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"  Created: {safe_title}")
        else:
            print(f"  Skipped {title}: insufficient data (n={len(data)})")
    else:
        print(f"  Skipped {title}: variables not found")

# Create a combined multi-panel plot for key relationships
print("\nCreating combined multi-panel plot (first 6 plots)...")
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flatten()

for idx, (x_var, y_var, title) in enumerate(relationships[:6]):
    if idx >= 6:
        break
    
    ax = axes[idx]
    
    if x_var in df.columns and y_var in df.columns:
        data = df[[x_var, y_var]].dropna()
        
        if len(data) > 10:
            # Scatter
            ax.scatter(data[x_var], data[y_var], alpha=0.3, s=30)
            
            # Loess
            try:
                data_sorted = data.sort_values(x_var)
                smoothed = lowess(data_sorted[y_var], data_sorted[x_var], 
                                 frac=0.3, it=3, return_sorted=True)
                ax.plot(smoothed[:, 0], smoothed[:, 1], 'r-', linewidth=2, alpha=0.8)
            except:
                pass
            
            corr = data[x_var].corr(data[y_var])
            ax.set_xlabel(x_var.replace('_', ' ').title(), fontsize=10)
            ax.set_ylabel(y_var.replace('_', ' ').title(), fontsize=10)
            ax.set_title(f'{title}\n(r={corr:.3f})', fontsize=11)
            ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'scatter_loess_combined.png'), 
           dpi=300, bbox_inches='tight')
plt.close()

# Create a second combined plot for Singapore-inclusive relationships
if len(relationships) > 6:
    print("\nCreating combined multi-panel plot for Singapore-inclusive relationships...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    axes = axes.flatten()
    
    for idx, (x_var, y_var, title) in enumerate(relationships[6:9]):
        ax = axes[idx]
        
        if x_var in df.columns and y_var in df.columns:
            data = df[[x_var, y_var]].dropna()
            
            if len(data) > 10:
                # Scatter
                ax.scatter(data[x_var], data[y_var], alpha=0.3, s=30)
                
                # Loess
                try:
                    data_sorted = data.sort_values(x_var)
                    smoothed = lowess(data_sorted[y_var], data_sorted[x_var], 
                                     frac=0.3, it=3, return_sorted=True)
                    ax.plot(smoothed[:, 0], smoothed[:, 1], 'r-', linewidth=2, alpha=0.8)
                except:
                    pass
                
                corr = data[x_var].corr(data[y_var])
                ax.set_xlabel(x_var.replace('_', ' ').title(), fontsize=10)
                ax.set_ylabel(y_var.replace('_', ' ').title(), fontsize=10)
                ax.set_title(f'{title}\n(r={corr:.3f})', fontsize=11)
                ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'scatter_loess_singapore_inclusive.png'), 
               dpi=300, bbox_inches='tight')
    plt.close()

print(f"\nScatter plots with Loess smoothing complete. Outputs saved to {output_dir}")
