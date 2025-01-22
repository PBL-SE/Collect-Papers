import requests
import csv
import os
import uuid
from xml.etree import ElementTree as ET

# Ensure the output directory exists
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# ArXiv API base URL
base_url = "http://export.arxiv.org/api/query"

# Function to fetch data from arXiv API
def fetch_arxiv_data(category="cs.ai", max_results=100):
    params = {
        "search_query": f"cat:{category}",
        "start": 0,
        "max_results": max_results
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")


def generate_id():
    return str(uuid.uuid4())

# Function to parse XML response and extract metadata
def parse_arxiv_data(xml_data, category):
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall("atom:entry", namespace):
        title = entry.find("atom:title", namespace).text.strip()
        authors = [author.find("atom:name", namespace).text.strip() for author in entry.findall("atom:author", namespace)]
        published = entry.find("atom:published", namespace).text.strip()
        pdf_link = entry.find("atom:link[@type='application/pdf']", namespace).attrib["href"]

        # Extract DOI (if available)
        doi = None
        doi_link = entry.find("atom:link[@rel='related'][@title='doi']", namespace)
        if doi_link is not None and 'href' in doi_link.attrib:
            doi = doi_link.attrib['href'].replace("http://dx.doi.org/", "")

        # Generate a unique paper ID
        paper_id = generate_id()

        # Generate unique author IDs and map them
        author_ids = [generate_id() for _ in authors]

        # Cited papers: Placeholder for now
        cited_papers = []

        papers.append({
            "Paper ID": paper_id,
            "Title": title,
            "Authors": ", ".join(authors),
            "Published": published,
            "PDF Link": pdf_link,
            "Category": category,
            "DOI": doi,
            "Author IDs": ", ".join(author_ids),
            "Cited Papers": ", ".join(cited_papers)
        })

    return papers

# Function to save data into a CSV file
def save_to_csv(papers, filename):
    # Define the fieldnames to match the new CSV structure
    fieldnames = ["Paper ID", "Title", "Authors", "Published", "PDF Link", "Category", "DOI", "Author IDs", "Cited Papers"]
    
    # Open the file in write mode and ensure proper encoding
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        # Write the header row
        writer.writeheader()
        
        # Write all the paper data
        writer.writerows(papers)
