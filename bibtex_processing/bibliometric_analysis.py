
import bibtexparser
import nltk
import re
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from itertools import combinations
from collections import defaultdict

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords


# === Define input and output paths ===
INPUT_BIBTEX_PATH = 'C:/Users/Lachmuth/OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V/Dokumente/FAIRagro/Use Case 4/LTE_text_processing/output/V140_documented/V140_documented_rich.bib'

# === Load BibTeX File ===
with open(INPUT_BIBTEX_PATH, 'r', encoding='utf-8') as bibfile:
    bib_database = bibtexparser.load(bibfile)

# === Extract Abstracts ===
abstracts = [entry.get('abstract', '').lower() for entry in bib_database.entries if 'abstract' in entry]


# === Preprocess Text ===
stop_words = set(stopwords.words('english'))

def preprocess(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text.lower()
cleaned_abstracts = [preprocess(abs) for abs in abstracts]

# === Vectorize with CountVectorizer ===
vectorizer = CountVectorizer(
    min_df=2,
    ngram_range=(1, 2),  # Capture bigrams 
    #token_pattern=r'\b\w+\b',
    stop_words='english'  # Use built-in stopword list
)
X = vectorizer.fit_transform(cleaned_abstracts)

print(vectorizer.get_feature_names_out())
terms = vectorizer.get_feature_names_out()
bigrams = [term for term in terms if len(term.split()) == 2]
print(bigrams)


# === Build Co-occurrence Matrix ===
co_occurrence = defaultdict(int)
for doc in cleaned_abstracts:
    tokens = set(doc.split())
    filtered_tokens = [t for t in tokens if t in terms]
    for term1, term2 in combinations(filtered_tokens, 2):
        co_occurrence[(term1, term2)] += 1

# === Build Network Graph ===
G = nx.Graph()
for (term1, term2), weight in co_occurrence.items():
    if weight > 1:  # filter weak connections
        G.add_edge(term1, term2, weight=weight)

# === Visualize Network ===
plt.figure(figsize=(12, 12))
pos = nx.spring_layout(G, k=0.15)
edges = G.edges()
weights = [G[u][v]['weight'] for u,v in edges]

nx.draw_networkx_nodes(G, pos, node_size=300, node_color='skyblue')
nx.draw_networkx_edges(G, pos, edgelist=edges, width=[w * 0.5 for w in weights], alpha=0.6)
nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

plt.title('Filtered Keyword Co-occurrence Network')
plt.axis('off')
plt.tight_layout()
#plt.savefig('filtered_keyword_network.png')
plt.show()
