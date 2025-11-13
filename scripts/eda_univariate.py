import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))

# Univariate plots
numeric_cols = df.select_dtypes(include=[float, int]).columns
for col in numeric_cols:
    plt.figure(figsize=(8, 6))
    sns.histplot(df[col].dropna(), kde=True)
    plt.title(f'Distribution of {col}')
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.savefig(os.path.join(output_dir, f'{col}_dist.png'), dpi=300, bbox_inches='tight')
    plt.close()

# Missingness
plt.figure(figsize=(12, 8))
sns.heatmap(df.isnull(), cbar=False, yticklabels=False)
plt.title('Missingness Heatmap')
plt.xlabel('Variables')
plt.savefig(os.path.join(output_dir, 'missingness.png'), dpi=300, bbox_inches='tight')
plt.close()

# Save summary statistics
summary = df.describe()
summary.to_csv(os.path.join(data_dir, 'univariate_summary.csv'))

print(f"EDA univariate complete. Images saved to {output_dir}, summary to {data_dir}")