import bibtexparser
import requests
import time
import configparser

# Load API key from config file
config = configparser.ConfigParser()
config.read('config.ini')
#import bib
SCOPUS_API_KEY = config['SCOPUS']['API_KEY']

SCOPUS_API_DOI_URL = 'https://api.elsevier.com/content/abstract/doi/'
SCOPUS_API_SEARCH_URL = 'https://api.elsevier.com/content/search/scopus'

# Load the BibTeX file
with open('C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\input\\V140_documented\\V140_documented_raw.bib', 'r', encoding='utf-8') as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

enriched_entries = []
not_found_log = []

def query_scopus_by_doi(doi):
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': SCOPUS_API_KEY
    }
    response = requests.get(SCOPUS_API_DOI_URL + doi, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def query_scopus_by_title_author(title, authors):
    headers = {
        'Accept': 'application/json',
        'X-ELS-APIKey': SCOPUS_API_KEY
    }
    query = f'TITLE("{title}")'
    if authors:
        query += f' AND AUTH("{authors}")'
    params = {'query': query}
    response = requests.get(SCOPUS_API_SEARCH_URL, headers=headers, params=params)
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
            
            entry['abstract'] = str(coredata.get('dc:description', '') or '')
            entry['keywords'] = str(coredata.get('dcterms:subject', '') or '')
            entry['copyright'] = str(coredata.get('prism:copyright', '') or '')
            entry['license'] = str(coredata.get('openaccess', '') or '')

            enriched_entries.append(entry)
        else:
            not_found_log.append(f"DOI not found: {doi}")
    else:
        title = entry.get('title', '')
        authors = entry.get('author', '')
        data = query_scopus_by_title_author(title, authors)
        if data and 'search-results' in data and 'entry' in data['search-results']:
            result = data['search-results']['entry'][0]
            entry['abstract'] = str(coredata.get('dc:description', '') or '')
            entry['keywords'] = str(coredata.get('dcterms:subject', '') or '')
            entry['copyright'] = str(coredata.get('prism:copyright', '') or '')
            entry['license'] = str(coredata.get('openaccess', '') or '')
            enriched_entries.append(entry)
        else:
            not_found_log.append(f"No DOI and no match found for entry: {title}")
    time.sleep(1)  # Respect API rate limits

# Write enriched BibTeX file
enriched_db = bibtexparser.bibdatabase.BibDatabase()
enriched_db.entries = enriched_entries
with open('C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\output\\V140_documented\\V140_documented_rich.bib', 'w', encoding='utf-8') as enriched_file:
    bibtexparser.dump(enriched_db, enriched_file)

# Write log file
with open('C:\\Users\\Lachmuth\\OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V\\Dokumente\\FAIRagro\\Use Case 4\\LTE_text_processing\\output\\V140_documented\\scopus_query_log.txt', 'w') as log_file:
    for line in not_found_log:
        log_file.write(line + '\n')
