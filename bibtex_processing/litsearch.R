# Clear workspace
rm(list = ls())
gc()


# Load packages -----------------------------------------------------------
# Install packages from GitHub (remove #s if you need this section)
#install.packages("remotes")
#library(remotes)
#install_github("elizagrames/litsearchr", ref="main")
library(litsearchr)
library(bibliometrix)  
library(bibliometrixData)
library(dplyr)
library(ggplot2)
library(ggraph)


# Settings ----------------------------------------------------------------
### Set working directory

wd <-"C:/Users/Lachmuth/OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V/Dokumente/BONARES_Repository/paper/submitted/GitHub/data/"
#wd <- "C:/"
setwd(wd)


# Package litsearchr ----------------------------------------------------------------
## Import WoS records ------------------------------------------------------------
lit_records<-
  litsearchr::import_results(
    file = "savedrecs.bib",
    verbose = TRUE
  )

head(lit_records)
str(lit_records)
nrow(lit_records)

## Define stopwords --------------------------------------------------------
stopwords_SL <-c("assess", "assessed", "assesses", "assessing",  "based", #,"assessment", "assessments"
                 "follow", "followed", "following", "follows", "primary", "versus", "that is", "e.g.", 
                 "however", "in particular", "versus", "follow", "followed", "following", "follows", "potential", "study")

all_stopwords <- c(get_stopwords("English"), stopwords_SL)


## Extract author keywords -------------------------------------------------
author_keywords<-extract_terms(keywords=lit_records[, "keywords"], method="tagged", min_n=1,max_n=3, min_freq=2)


## Get abstracts and titles -----------------------------------------------------
titles_abstracts <- paste(lit_records$abstract,lit_records$title,  collapse = "; ")

### Extract further common terms from abstracts and titles using "fakerake" method -----------------------------------
raked_keywords <- 
  extract_terms(
    text = lit_records[, c("title","abstract")], 
    method = "fakerake",
    min_freq = 2, 
    ngrams = TRUE,
    min_n = 2,
    max_n = 3,
    stopwords = all_stopwords, 
    language = "English"
  )
 
raked_keywords

### Concatenate (all) real keywords and raked keywords
all_keywords <- unique(append(author_keywords, raked_keywords))
length(all_keywords)


# Network analysis --------------------------------------------------------
dfm<-
  create_dfm(elements = paste(lit_records[, "title"], lit_records[, "abstract"]), #
             features = unique(all_keywords))#[-81]


# NEW TRY -----------------------------------------------------------------
# From old code
df_original <- as.data.frame(dfm)

# Reformat column name 26 to be able to address columns by name
colnames(df_original)[26]<-"Alley-cropping agroforestry"# required for next line to work
df_original<-df_original %>% dplyr::rename_all(make.names)


# Create a function to combine similar terms and make binary
combine_similar_terms <- function(df, term_groups, new_names) {
  # Verify all new_names are unique and not in term_groups
  for(i in seq_along(term_groups)) {
    # Sum all related terms
    df[[new_names[i]]] <- rowSums(df[, term_groups[[i]], drop = FALSE])
    # Convert to binary
    df[[new_names[i]]] <- as.integer(df[[new_names[i]]] > 0)
    # Remove original columns
    df <- df[, !(names(df) %in% term_groups[[i]])]
  }
  return(df)
}

# Define groups of similar terms and their new names
term_groups <- list(
  c("long.term.experiments", "long.term.field", "long.term.field.experiments",
    "long.term.field.experiment", "agricultural.long.term", "agricultural.long.term.field"),
  c("agricultural.experimental", "agricultural.experimental.field"),
  c("agricultural.landscape", "agricultural.landscapes"),
  c("Alley.cropping.agroforestry", "alley.cropping", "alley.cropping.agroforestry"),
  c("bayesian.sequential", "bayesian.sequential.updating"),
  c("change.impacts", "climate.change.impacts"),
  c("experimental.field", "experimental.field.plots"),
  c("language.processing", "natural.language", "natural.language.processing"),
  c("multivariate.water", "multivariate.water.quality", "water.quality"),
  c("organic.carbon", "organic.carbon.stocks"),
  c("precision.weighing", "precision.weighing.lysimeters")
)

# Create new umbrella terms for the term groups
new_names <- c("LTE", "agric.exp.field", "agric.landscape",
               "alley.crop.agroforestry", "bayes.seq.updating",
               "clim.change.impacts", "exp.field.plots",
               "nat.language.processing", "water.qual",
               "org.carb", "prec.weighing")


# Apply the function to combine terms
df <- combine_similar_terms(df_original, term_groups, new_names)

# Convert to matrix
dfm_new <- as.matrix(df)



## Network graph (Figure 6) -----------------------------------------------------------
# Important terms are in the edge of the graph
graph<-
  create_network(search_dfm = dfm_new,
                 min_studies = 2,
                 min_occ = 2)


# Plot Figure 6
network_graph<-ggraph(graph, layout="stress") +
  coord_fixed() +
  expand_limits(x=c(-3.5, 4.5), y=c(-2, 2)) +
  geom_edge_link(aes(alpha=weight)) +
  geom_node_point(shape="circle filled", fill="white") +
  geom_node_text(aes(label=name), hjust="outward", check_overlap=F, size = 3.5) +
  guides(edge_alpha=FALSE)
network_graph
ggsave(plot = network_graph,paste0(wd,"Figure 6.png"), width = 20, height = 12,units ="cm")



# Package bibliometrix ------------------------------------------------------------
## Import WoS records ------------------------------------------------------------
M <- convert2df(
  file = "savedrecs.bib", 
  dbsource = "isi",
  format = "bibtex",
  remove.duplicates = TRUE
)



# Sankey Plot (Figure 5) -------------------------------------------------------------
Sankey_graph <- threeFieldsPlot(M, fields = c("AU_CO","SC", "ID"), n = c(25, 25, 25))


