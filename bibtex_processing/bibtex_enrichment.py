import bibtexparser
import requests
import time
import configparser
import json

# === Define input and output paths ===

INPUT_BIBTEX_PATH = 'C:/Users/Lachmuth/OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V/Dokumente/FAIRagro/Use Case 4/LTE_text_processing/input/V140_documented/V140_documented_raw.bib'
OUTPUT_BIBTEX_PATH = 'C:/Users/Lachmuth/OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V/Dokumente/FAIRagro/Use Case 4/LTE_text_processing/output/V140_documented/V140_documented_rich.bib'
OUTPUT_JSONLD_PATH = 'C:/Users/Lachmuth/OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V/Dokumente/FAIRagro/Use Case 4/LTE_text_processing/output/V140_documented/V140_documented_schemaorg.json'
OUTPUT_LOG_PATH = 'C:/Users/Lachmuth/OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V/Dokumente/FAIRagro/Use Case 4/LTE_text_processing/output/V140_documented/scopus_query_log.txt'


# Load API key from config file
config = configparser.ConfigParser()
config.read('config.ini')
SCOPUS_API_KEY = config['SCOPUS']['API_KEY']
SCOPUS_API_DOI_URL = 'https://api.elsevier.com/content/abstract/doi/'
SCOPUS_API_SEARCH_URL = 'https://api.elsevier.com/content/search/scopus'

# Load the BibTeX file
with open(INPUT_BIBTEX_PATH, 'r', encoding='utf-8') as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

enriched_entries = []
schemaorg_entries = []
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

def extract_authors(metadata):
    authors = metadata.get('authors', {}).get('author', [])
    author_list = []
    for author in authors:
        name = author.get('ce:indexed-name', '')
        afid = author.get('afid', '')
        affiliation = ''
        if isinstance(afid, list):
            affiliation = ', '.join([a.get('$', '') for a in afid])
        elif isinstance(afid, dict):
            affiliation = afid.get('$', '')
        author_list.append(f"{name} ({affiliation})" if affiliation else name)
    return '; '.join(author_list)

def extract_author_keywords(metadata):
    authkeywords = metadata.get('authkeywords')
    if not authkeywords:
        return ''
    keywords = authkeywords.get('author-keyword', [])
    if isinstance(keywords, list):
        return '; '.join([kw.get('$', '') for kw in keywords])
    elif isinstance(keywords, dict):
        return keywords.get('$', '')
    return ''

def extract_indexed_keywords(metadata):
    idxterms = metadata.get('idxterms')
    if not idxterms:
        return ''
    mainterms = idxterms.get('mainterm', [])
    if isinstance(mainterms, list):
        return '; '.join([kw.get('$', '') for kw in mainterms])
    elif isinstance(mainterms, dict):
        return mainterms.get('$', '')
    return ''

def ensure_string_fields(entry):
    for key, value in entry.items():
        if not isinstance(value, str):
            entry[key] = "" if value is None else str(value)
    return entry

def convert_to_schemaorg(entry):
    return {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": entry.get("title", ""),
        "abstract": entry.get("abstract", ""),
        "keywords": entry.get("keywords", "").split("; "),
        "author": [
            {"@type": "Person", "name": name.strip()}
            for name in entry.get("authors_affiliations", "").split("; ")
        ],
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "DOI",
            "value": entry.get("doi", "")
        },
        "isPartOf": {
            "@type": "PublicationIssue",
            "issueNumber": entry.get("issue", ""),
            "volumeNumber": entry.get("volume", ""),
            "isPartOf": {
                "@type": "Periodical",
                "name": entry.get("journal", ""),
                "issn": entry.get("issn", "")
            }
        },
        "pagination": entry.get("pages", ""),
        "publisher": {
            "@type": "Organization",
            "name": entry.get("publisher", "")
        },
        "datePublished": entry.get("pub_year", ""),
        "citation": {
            "@type": "CreativeWork",
            "citationCount": entry.get("citedby_count", "")
        },
        "funding": entry.get("funding", "").split("; "),
        "about": entry.get("subject_areas", "").split("; "),
        "license": entry.get("license", ""),
        "isAccessibleForFree": entry.get("open_access", "") == "1"
    }

# Process each entry
for entry in bib_database.entries:
    doi = entry.get('doi')
    if doi:
        data = query_scopus_by_doi(doi)
    else:
        title = entry.get('title', '')
        authors = entry.get('author', '')
        data = query_scopus_by_title_author(title, authors)

    if data and 'abstracts-retrieval-response' in data:
        metadata = data['abstracts-retrieval-response']
        coredata = metadata.get('coredata', {})
        entry['title'] = str(coredata.get('dc:title', ''))
        entry['abstract'] = str(coredata.get('dc:description', ''))
        entry['keywords'] = str(coredata.get('dcterms:subject', ''))
        entry['copyright'] = str(coredata.get('prism:copyright', ''))
        #entry['license'] = str(coredata.get('openaccess', ''))
        entry['journal'] = str(coredata.get('prism:publicationName', ''))
        entry['volume'] = str(coredata.get('prism:volume', ''))
        entry['issue'] = str(coredata.get('prism:issueIdentifier', ''))
        entry['pages'] = str(coredata.get('prism:pageRange', ''))
        entry['issn'] = str(coredata.get('prism:issn', ''))
        entry['publisher'] = str(coredata.get('dc:publisher', ''))
        entry['pub_year'] = str(coredata.get('prism:coverDate', '')[:4])
        entry['eid'] = str(coredata.get('eid', ''))
        entry['citedby_count'] = str(coredata.get('citedby-count', ''))
        entry['authors_affiliations'] = str(extract_authors(metadata))
        entry['author_keywords'] = str(extract_author_keywords(metadata))
        entry['indexed_keywords'] = str(extract_indexed_keywords(metadata))
        open_access_flag = coredata.get('openaccessFlag', '')
        reuse_license = coredata.get('openaccess', '')  # May contain license type like CC-BY
        # Combine both into a descriptive license field
        if open_access_flag == '1':
        entry['license'] = f"Open Access; {reuse_license}" if reuse_license else "Open Access"
        else:
        entry['license'] = reuse_license if reuse_license else "Restricted Access"


        subject_areas = metadata.get('subject-areas', {}).get('subject-area', [])
        if isinstance(subject_areas, list):
            entry['subject_areas'] = '; '.join([sa.get('$', '') for sa in subject_areas])
        elif isinstance(subject_areas, dict):
            entry['subject_areas'] = subject_areas.get('$', '')

        entry['open_access'] = coredata.get('openaccessFlag', '')

        funding = metadata.get('item', {}).get('xocs:funding-list', {}).get('xocs:funding', [])
        if isinstance(funding, list):
            funders = [f.get('xocs:funding-agency', '') for f in funding]
            entry['funding'] = '; '.join(funders)
        elif isinstance(funding, dict):
            entry['funding'] = funding.get('xocs:funding-agency', '')

        enriched_entries.append(entry)
        schemaorg_entries.append(convert_to_schemaorg(entry))
    else:
        not_found_log.append(f"Entry not enriched: {entry.get('title', '') or doi}")
    time.sleep(1)  # Respect API rate limits

# Write enriched BibTeX file
enriched_db = bibtexparser.bibdatabase.BibDatabase()
enriched_db.entries = [ensure_string_fields(e) for e in enriched_entries]
with open(OUTPUT_BIBTEX_PATH, 'w', encoding='utf-8') as enriched_file:
    bibtexparser.dump(enriched_db, enriched_file)

# Write schema.org JSON-LD file
with open(OUTPUT_JSONLD_PATH, 'w', encoding='utf-8') as json_file:
    json.dump(schemaorg_entries, json_file, indent=2, ensure_ascii=False)

# Write log file
with open(OUTPUT_LOG_PATH, 'w') as log_file:
    for line in not_found_log:
        log_file.write(line + '\n')
