# This script enriches BibTeX entries with metadata from the Scopus API based on DOIs.
# It reads a BibTeX file, queries the Scopus API for each DOI, and writes the enriched entries to a new BibTeX file.
# It also logs entries that could not be found or did not have a DOI.
# Import necessary libraries
import bibtexparser
import requests
import time
import configparser


# Load API key from config file
config = configparser.ConfigParser()
config.read('config.ini')
SCOPUS_API_KEY = config['SCOPUS']['API_KEY']
SCOPUS_API_URL = 'https://api.elsevier.com/content/abstract/doi/'

# Load the BibTeX file
with open('C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\input\\V140_documented\\V140_documented_raw.bib', 'r') as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

enriched_entries = []
not_found_log = []

def query_scopus_by_doi(doi):
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': SCOPUS_API_KEY
    }
    response = requests.get(SCOPUS_API_URL + doi, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

# Process each entry
for entry in bib_database.entries:
    doi = entry.get('doi')
    if doi:
        data = query_scopus_by_doi(doi)
        if data and 'abstracts-retrieval-response' in data:
            metadata = data['abstracts-retrieval-response']
            coredata = metadata.get('coredata', {})
            entry['abstract'] = coredata.get('dc:description', '')
            entry['keywords'] = coredata.get('dcterms:subject', '')
            entry['copyright'] = coredata.get('prism:copyright', '')
            entry['license'] = coredata.get('openaccess', '')
            enriched_entries.append(entry)
        else:
            not_found_log.append(f"DOI not found: {doi}")
    else:
        not_found_log.append(f"No DOI for entry: {entry.get('title', 'Unknown Title')}")
    time.sleep(1)  # Respect API rate limits

# Write enriched BibTeX file
enriched_db = bibtexparser.bibdatabase.BibDatabase()
enriched_db.entries = enriched_entries
with open('C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\output\\V140_documented\\V140_documented_rich.bib', 'w') as enriched_file:
    bibtexparser.dump(enriched_db, enriched_file)

# Write log file
with open('scopus_query_log.txt', 'w') as log_file:
    for line in not_found_log:
        log_file.write(line + '\n')


