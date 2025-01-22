from utils import fetch_arxiv_data, parse_arxiv_data, save_to_csv
import os

# List of categories to query
categories = [
    'ai', 'ar', 'cc', 'ce', 'cg', 'cl', 'cr', 'cv', 'cy', 'db',
    'dc', 'dl', 'dm', 'et', 'fl', 'gl', 'gr', 'gt', 'hc', 'ir',
    'it', 'lg', 'lo', 'ma', 'mm', 'ms', 'na', 'ne', 'ni', 'oh',
    'os', 'pf', 'pl', 'ro', 'sc', 'sd', 'se', 'si', 'sy',
]

# Output directory and file
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "arxiv_dump.csv")

# Main script to fetch and aggregate results
all_papers = []

for category in categories:
    print(f"Fetching papers for category: cs.{category}")
    try:
        # Fetch and parse data
        xml_data = fetch_arxiv_data(category=f"cs.{category}", max_results=100)
        papers = parse_arxiv_data(xml_data, category)
        all_papers.extend(papers)
    except Exception as e:
        print(f"Error fetching papers for category cs.{category}: {e}")

# Save all results to a single CSV file
save_to_csv(all_papers, output_file)

print(f"Aggregated data saved successfully to {output_file}")
