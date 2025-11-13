import pandas as pd
import matplotlib.pyplot as plt
import os

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))

countries = ['Singapore', 'Colombia', 'Philippines']  # Bogota is in Colombia

for country in countries:
    subset = df[df['country'] == country]
    if not subset.empty:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot congestion
        ax1.plot(subset['year'], subset['congestion_index'], marker='o', color='red')
        ax1.set_title(f'Congestion Index - {country}')
        ax1.set_xlabel('Year')
        ax1.set_ylabel('Congestion Index')
        ax1.grid(True, alpha=0.3)
        
        # Plot investment
        ax2.plot(subset['year'], subset['transit_investment_gdp'], marker='s', color='blue')
        ax2.set_title(f'Transit Investment (% GDP) - {country}')
        ax2.set_xlabel('Year')
        ax2.set_ylabel('Transit Investment (% GDP)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'{country}_trends.png'), dpi=300, bbox_inches='tight')
        plt.close()
    else:
        print(f"No data found for {country}")

print(f"Time trends analysis complete. Outputs saved to {output_dir}")