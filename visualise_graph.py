import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import os
import glob


def read_csv_files(directory):
    edges_files = glob.glob(os.path.join(directory, 'edges.csv', '*.csv'))
    vertices_files = glob.glob(os.path.join(directory, 'vertices.csv', '*.csv'))
    
    if not edges_files or not vertices_files:
        raise FileNotFoundError(f"CSV files not found in {directory}")
    
    print("files:", edges_files, vertices_files)
    
    edges_df = pd.concat([pd.read_csv(f) for f in edges_files])
    vertices_df = pd.concat([pd.read_csv(f) for f in vertices_files])
    
    return edges_df, vertices_df

try:
    edges_df, vertices_df = read_csv_files('./results')
except FileNotFoundError as e:
    print(f"Error: {e}")
    print("Please ensure that the CSV files have been generated in the ./results directory.")
    exit(1)

# Create a graph
G = nx.from_pandas_edgelist(edges_df, 'src', 'dst', create_using=nx.DiGraph())

# Add node attributes
for _, row in vertices_df.iterrows():
    G.add_node(row['id'], type='user' if row['id'] in edges_df['src'].unique() else 'product')

# Separate users and products
users = [node for node, attr in G.nodes(data=True) if attr['type'] == 'user']
products = [node for node, attr in G.nodes(data=True) if attr['type'] == 'product']

# Set up the plot
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(G)

# Draw the graph
nx.draw_networkx_nodes(G, pos, nodelist=users, node_color='lightblue', node_size=500, label='Users')
nx.draw_networkx_nodes(G, pos, nodelist=products, node_color='lightgreen', node_size=300, label='Products')
nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True)

# Add labels
nx.draw_networkx_labels(G, pos)

plt.title("User-Product Recommendation Graph", fontsize=16)
plt.legend(fontsize=10)
plt.axis('off')

# Save the plot
plt.tight_layout()
plt.savefig('./results/recommendation_graph.png', dpi=300, bbox_inches='tight')
plt.close()

# Create a degree distribution plot
degrees = [d for n, d in G.degree()]
plt.figure(figsize=(10, 6))
plt.hist(degrees, bins=20, edgecolor='black')
plt.title("Degree Distribution", fontsize=16)
plt.xlabel("Degree", fontsize=12)
plt.ylabel("Count", fontsize=12)
plt.savefig('./results/degree_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# Create a bar plot of top 10 products by recommendation count
product_counts = edges_df['dst'].value_counts().nlargest(10)
plt.figure(figsize=(12, 6))
product_counts.plot(kind='bar')
plt.title("Top 10 Recommended Products", fontsize=16)
plt.xlabel("Product ID", fontsize=12)
plt.ylabel("Recommendation Count", fontsize=12)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('./results/top_products.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization complete. Check the results directory for the generated images.")
