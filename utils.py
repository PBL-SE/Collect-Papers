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

# OpenCitations API base URL
opencitations_base_url = "https://opencitations.net/index/coci/api/v1/references/"

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

# Function to fetch references from OpenCitations
def fetch_references_from_opencitations(doi):
    if not doi:
        return []
    
    url = f"{opencitations_base_url}{doi}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        # Extract the 'cited' DOIs (references cited by the queried paper)
        references = [entry['cited'] for entry in data]
        
        # Deduplicate the references
        unique_references = list(set(references))
        
        return unique_references
    else:
        print(f"Failed to fetch references for DOI {doi}: {response.status_code}")
        return []

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

        # Fetch references from OpenCitations
        cited_papers = fetch_references_from_opencitations(doi)

        # Generate a unique paper ID
        paper_id = generate_id()

        # Generate unique author IDs and map them
        author_ids = [generate_id() for _ in authors]

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
    fieldnames = ["Paper ID", "Title", "Authors", "Published", "PDF Link", "Category", "DOI", "Author IDs", "Cited Papers"]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(papers)
