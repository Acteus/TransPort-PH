import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform
import os

data_dir = '../data'
output_dir = '../output'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

df = pd.read_csv(os.path.join(data_dir, 'clean_panel.csv'))

# Select numeric columns
numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
numeric_data = df[numeric_cols].dropna()

# Correlation Analysis
if len(numeric_data) > 0:
    print("Generating correlation matrix...")
    corr_matrix = numeric_data.corr()
    
    # Plot correlation heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
    plt.title('Correlation Matrix of Numeric Variables', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'correlation_matrix.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save correlation matrix to CSV
    corr_matrix.to_csv(os.path.join(data_dir, 'correlation_matrix.csv'))
    
    # Find strong correlations
    corr_threshold = 0.7
    strong_corr = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            if abs(corr_matrix.iloc[i, j]) > corr_threshold:
                strong_corr.append({
                    'Variable 1': corr_matrix.columns[i],
                    'Variable 2': corr_matrix.columns[j],
                    'Correlation': corr_matrix.iloc[i, j]
                })
    
    if strong_corr:
        strong_corr_df = pd.DataFrame(strong_corr)
        strong_corr_df = strong_corr_df.sort_values('Correlation', key=abs, ascending=False)
        strong_corr_df.to_csv(os.path.join(data_dir, 'strong_correlations.csv'), index=False)
        print(f"Found {len(strong_corr)} strong correlations (|r| > {corr_threshold})")

# Hierarchical Clustering of Countries
print("Performing hierarchical clustering...")

# Aggregate data by country (mean of all numeric variables)
country_features = df.groupby('country')[numeric_cols].mean()
country_features_clean = country_features.dropna()

if len(country_features_clean) > 2:
    # Standardize features for clustering
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(country_features_clean)
    
    # Perform hierarchical clustering
    linkage_matrix = linkage(scaled_features, method='ward')
    
    # Plot dendrogram
    plt.figure(figsize=(14, 8))
    dendrogram(linkage_matrix, labels=country_features_clean.index.tolist(),
               leaf_rotation=90, leaf_font_size=10)
    plt.title('Hierarchical Clustering of Countries', fontsize=14, pad=20)
    plt.xlabel('Country', fontsize=12)
    plt.ylabel('Distance', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'country_clustering.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # Identify clusters (cut at a reasonable height)
    from scipy.cluster.hierarchy import fcluster
    n_clusters = min(5, len(country_features_clean) // 2)  # Adaptive number of clusters
    clusters = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
    
    # Save cluster assignments
    cluster_df = pd.DataFrame({
        'country': country_features_clean.index,
        'cluster': clusters
    })
    cluster_df = cluster_df.sort_values('cluster')
    cluster_df.to_csv(os.path.join(data_dir, 'country_clusters.csv'), index=False)
    
    # Print cluster summary
    print("\nCountry Clusters:")
    for cluster_id in range(1, n_clusters + 1):
        countries_in_cluster = cluster_df[cluster_df['cluster'] == cluster_id]['country'].tolist()
        print(f"Cluster {cluster_id}: {', '.join(countries_in_cluster)}")
    
    # Visualize clusters in 2D using PCA
    from sklearn.decomposition import PCA
    pca = PCA(n_components=2)
    pca_features = pca.fit_transform(scaled_features)
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(pca_features[:, 0], pca_features[:, 1], 
                         c=clusters, cmap='viridis', s=100, alpha=0.6)
    
    # Label each point with country name
    for i, country in enumerate(country_features_clean.index):
        plt.annotate(country, (pca_features[i, 0], pca_features[i, 1]),
                    fontsize=8, alpha=0.8)
    
    plt.colorbar(scatter, label='Cluster')
    plt.title('Country Clusters (PCA Visualization)', fontsize=14, pad=20)
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', fontsize=12)
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'country_clusters_pca.png'), dpi=300, bbox_inches='tight')
    plt.close()

print(f"\nCorrelation and clustering analysis complete. Images saved to {output_dir}, data to {data_dir}")
