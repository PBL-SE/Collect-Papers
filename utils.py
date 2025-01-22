import requests
import csv
import os
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

# Function to parse XML response and extract metadata
def parse_arxiv_data(xml_data):
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall("atom:entry", namespace):
        title = entry.find("atom:title", namespace).text.strip()
        authors = ", ".join([author.find("atom:name", namespace).text.strip()
                             for author in entry.findall("atom:author", namespace)])
        published = entry.find("atom:published", namespace).text.strip()
        pdf_link = entry.find("atom:link[@type='application/pdf']", namespace).attrib["href"]
        papers.append({"Title": title, "Authors": authors, "Published": published, "PDF Link": pdf_link})
    return papers

# Function to save data into a CSV file
def save_to_csv(papers, filename):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "Authors", "Published", "PDF Link"])
        writer.writeheader()
        writer.writerows(papers)

