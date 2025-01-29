import requests
import csv
import os
from xml.etree import ElementTree as ET

# Ensure the output directory exists
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

# ArXiv API base URL
base_url = "http://export.arxiv.org/api/query"

# OpenCitations API base URL
opencitations_base_url = "https://opencitations.net/index/coci/api/v1/references/"

# Function to fetch data from arXiv API
def fetch_arxiv_data(category, max_results):
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
        references = [entry['cited'] for entry in data]
        return list(set(references))  # Deduplicate references
    else:
        print(f"Failed to fetch references for DOI {doi}: {response.status_code}")
        return []

# Function to parse XML response and extract metadata
# Function to parse XML response and extract metadata
def parse_arxiv_data(xml_data, category):
    namespace = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall("atom:entry", namespace):
        arxiv_id = entry.find("atom:id", namespace).text.split("/")[-1]  # Extract arXiv ID
        title = entry.find("atom:title", namespace).text.strip()
        authors = []
        
        for author in entry.findall("atom:author", namespace):
            name = author.find("atom:name", namespace).text.strip()
            affiliation = author.find("arxiv:affiliation", namespace)
            affiliation_text = affiliation.text.strip() if affiliation is not None else "Unknown"
            authors.append(f"{name} ({affiliation_text})")

        published = entry.find("atom:published", namespace).text.strip()
        pdf_link = entry.find("atom:link[@type='application/pdf']", namespace).attrib["href"]
        summary = entry.find("atom:summary", namespace).text.strip()
        
        comment = entry.find("arxiv:comment", namespace)
        comment_text = comment.text.strip() if comment is not None else "None"
        
        journal_ref = entry.find("arxiv:journal_ref", namespace)
        journal_ref_text = journal_ref.text.strip() if journal_ref is not None else "None"
        
        # Extract DOI (if available)
        doi = None
        doi_link = entry.find("atom:link[@rel='related'][@title='doi']", namespace)
        if doi_link is not None and 'href' in doi_link.attrib:
            doi = doi_link.attrib['href'].replace("http://dx.doi.org/", "")

        # Fetch references from OpenCitations
        cited_papers = fetch_references_from_opencitations(doi)

        papers.append({
            "ArXiv ID": arxiv_id,
            "Title": title,
            "Authors": ", ".join(authors),
            "Published": published,
            "PDF Link": pdf_link,
            "Summary": summary,
            "Category": category,
            "Comment": comment_text,
            "Journal Ref": journal_ref_text,
            "DOI": doi,
            "Cited Papers": ", ".join(cited_papers)
        })
    
    return papers

# Function to save data into a CSV file
def save_to_csv(papers, filename):
    fieldnames = ["ArXiv ID", "Title", "Authors", "Published", "PDF Link", "Category", "DOI", "Cited Papers", "Comment", "Journal Ref", "Summary"]
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(papers)

