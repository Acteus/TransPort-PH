import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print("=" * 80)
print("PANEL BALANCE CHECK REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

path = os.path.join(data_dir, 'worldbank_data.csv')
if os.path.exists(path):
    df = pd.read_csv(path)
    
    print(f"\nOriginal data shape: {df.shape}")
    print(f"Original countries: {df['country'].nunique()}")
    
    # Count years per country
    country_counts = df.groupby('country')['year'].count().sort_values(ascending=False)
    
    print("\nYears per country (top 10):")
    print(country_counts.head(10))
    
    # Define threshold
    min_years = 10
    valid_countries = country_counts[country_counts >= min_years].index
    filtered_countries = country_counts[country_counts < min_years].index
    
    print(f"\n{'='*60}")
    print(f"Threshold: >= {min_years} years")
    print(f"Countries kept: {len(valid_countries)}")
    print(f"Countries filtered out: {len(filtered_countries)}")
    print(f"{'='*60}")
    
    # Show filtered out countries
    if len(filtered_countries) > 0:
        print("\nFiltered out countries:")
        for country in filtered_countries:
            print(f"  {country}: {country_counts[country]} years")
    
    # Filter dataframe
    df_filtered = df[df['country'].isin(valid_countries)]
    
    print(f"\nFiltered data shape: {df_filtered.shape}")
    print(f"Rows removed: {len(df) - len(df_filtered)}")
    
    # Save filtered data
    df_filtered.to_csv(path, index=False)
    print(f"\n✓ Saved filtered data to: {path}")
    
    # Create balance report
    balance_report = pd.DataFrame({
        'country': country_counts.index,
        'years_of_data': country_counts.values,
        'kept': country_counts.values >= min_years
    })
    balance_report = balance_report.sort_values('years_of_data', ascending=False)
    
    report_path = os.path.join(data_dir, 'panel_balance_report.csv')
    balance_report.to_csv(report_path, index=False)
    print(f"✓ Balance report saved to: {report_path}")
    
    # Create visualization: Years per country
    plt.figure(figsize=(14, 8))
    colors = ['green' if x >= min_years else 'red' for x in country_counts.values]
    plt.barh(range(len(country_counts)), country_counts.values, color=colors, alpha=0.7)
    plt.yticks(range(len(country_counts)), country_counts.index, fontsize=8)
    plt.axvline(x=min_years, color='blue', linestyle='--', linewidth=2, label=f'Threshold ({min_years} years)')
    plt.xlabel('Number of Years', fontsize=12)
    plt.ylabel('Country', fontsize=12)
    plt.title(f'Panel Balance: Years of Data per Country\n(Green = Kept, Red = Filtered)', fontsize=14)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'panel_balance_chart.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Chart saved to: {output_dir}/panel_balance_chart.png")
    
    # Create distribution plot
    plt.figure(figsize=(10, 6))
    plt.hist(country_counts.values, bins=20, color='steelblue', alpha=0.7, edgecolor='black')
    plt.axvline(x=min_years, color='red', linestyle='--', linewidth=2, label=f'Threshold ({min_years} years)')
    plt.xlabel('Number of Years', fontsize=12)
    plt.ylabel('Number of Countries', fontsize=12)
    plt.title('Distribution of Data Coverage across Countries', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'panel_balance_distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✓ Distribution chart saved to: {output_dir}/panel_balance_distribution.png")
    
    # Create detailed text report
    txt_report_path = os.path.join(data_dir, 'panel_balance_report.txt')
    with open(txt_report_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("PANEL BALANCE CHECK REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"File analyzed: worldbank_data.csv\n")
        f.write(f"Threshold: >= {min_years} years of data\n\n")
        f.write("=" * 80 + "\n")
        f.write("SUMMARY:\n")
        f.write("=" * 80 + "\n")
        f.write(f"Original rows: {len(df)}\n")
        f.write(f"Original countries: {df['country'].nunique()}\n")
        f.write(f"Filtered rows: {len(df_filtered)}\n")
        f.write(f"Filtered countries: {len(valid_countries)}\n")
        f.write(f"Rows removed: {len(df) - len(df_filtered)}\n")
        f.write(f"Countries removed: {len(filtered_countries)}\n\n")
        f.write("=" * 80 + "\n")
        f.write("COUNTRIES KEPT:\n")
        f.write("=" * 80 + "\n\n")
        for country in valid_countries:
            f.write(f"  {country}: {country_counts[country]} years\n")
        f.write("\n")
        if len(filtered_countries) > 0:
            f.write("=" * 80 + "\n")
            f.write("COUNTRIES FILTERED OUT:\n")
            f.write("=" * 80 + "\n\n")
            for country in filtered_countries:
                f.write(f"  {country}: {country_counts[country]} years\n")
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("STATISTICS:\n")
        f.write("=" * 80 + "\n")
        f.write(f"Mean years per country: {country_counts.mean():.1f}\n")
        f.write(f"Median years per country: {country_counts.median():.1f}\n")
        f.write(f"Min years: {country_counts.min()}\n")
        f.write(f"Max years: {country_counts.max()}\n")
    
    print(f"✓ Detailed report saved to: {txt_report_path}")

else:
    print(f"File {path} not found")

print("\nPanel balance check complete.")