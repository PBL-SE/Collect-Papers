import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load the dataset
file_path = 'output/arxiv_dump.csv'
data = pd.read_csv(file_path)

# Limit to the first 1000 rows
subset_data = data.head(1000)

# Initialize a directed graph
citation_graph = nx.DiGraph()

# Iterate through the dataset to add edges
for _, row in subset_data.iterrows():
    citing_paper = row['DOI']  # Current paper DOI
    if pd.isna(citing_paper):  # Skip if DOI is missing
        continue
    
    # Parse cited papers (if any)
    cited_papers = row['Cited Papers']
    if pd.isna(cited_papers):  # Skip if no cited papers
        continue
    
    # Split cited papers into a list (assumes they are comma-separated)
    cited_papers_list = [doi.strip() for doi in cited_papers.split(',')]
    
    # Add edges to the graph
    for cited_paper in cited_papers_list:
        citation_graph.add_edge(citing_paper, cited_paper)

# Print basic graph statistics
print(f"Number of nodes: {citation_graph.number_of_nodes()}")
print(f"Number of edges: {citation_graph.number_of_edges()}")

# Plot the graph (simplified visualization for prototype)
plt.figure(figsize=(12, 8))
nx.draw(
    citation_graph,
    with_labels=False,
    node_size=10,
    edge_color='gray',  
    alpha=0.7,
    arrowsize=5
)
plt.title("Citation Graph (Prototype)")
plt.show()
