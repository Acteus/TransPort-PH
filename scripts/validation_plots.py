import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))

# Time trend for Philippines
ph = df[df['country'] == 'Philippines']
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Plot 1: Time trends
axes[0].plot(ph['year'], ph['congestion_index'], marker='o', label='Congestion', color='red')
ax2 = axes[0].twinx()
ax2.plot(ph['year'], ph['transit_investment_gdp'], marker='s', label='Investment', color='blue')
axes[0].set_xlabel('Year')
axes[0].set_ylabel('Congestion Index', color='red')
ax2.set_ylabel('Transit Investment (% GDP)', color='blue')
axes[0].set_title('Time Trends for Philippines')
axes[0].tick_params(axis='y', labelcolor='red')
ax2.tick_params(axis='y', labelcolor='blue')
axes[0].grid(True, alpha=0.3)

# Plot 2: Scatter - Investment vs Congestion
valid_data = df[['transit_investment_gdp', 'congestion_index']].dropna()
axes[1].scatter(valid_data['transit_investment_gdp'], valid_data['congestion_index'], alpha=0.5)
axes[1].set_xlabel('Transit Investment (% GDP)')
axes[1].set_ylabel('Congestion Index')
axes[1].set_title('Investment vs Congestion')
axes[1].grid(True, alpha=0.3)

# Add trend line
if len(valid_data) > 1:
    z = np.polyfit(valid_data['transit_investment_gdp'], valid_data['congestion_index'], 1)
    p = np.poly1d(z)
    axes[1].plot(valid_data['transit_investment_gdp'].sort_values(), 
                 p(valid_data['transit_investment_gdp'].sort_values()), 
                 "r--", alpha=0.8, label='Trend')
    axes[1].legend()

plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'validation_plots.png'), dpi=300, bbox_inches='tight')
plt.close()

print(f"Validation plots saved to {output_dir}")