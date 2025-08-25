import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tabulate import tabulate
import os

# Define base, "output", "# Define base directory
base_dir = os.path.expanduser("C:/Users/Lachmuth/OneDrive - Leibniz-Zentrum für Agrarlandschaftsforschung (ZALF) e.V/Dokumente/FAIRagro/Use Case 4/LTE_text_processing/")  # or any preferred path

# Input and output paths
input_file = os.path.join(base_dir, "input", "metadata_LTEmap_20250728.csv")
heatmap_file = os.path.join(base_dir,"output","lte_metadata_coverage_heatmap.png")
most_missing_csv = os.path.join(base_dir, "output", "top_25_most_missing_metadata.csv")
least_missing_csv = os.path.join(base_dir, "output", "top_25_least_missing_metadata.csv")
most_missing_clean_csv = os.path.join(base_dir, "output", "top_25_most_missing_metadata_clean.csv")
least_missing_clean_csv = os.path.join(base_dir, "output", "top_25_least_missing_metadata_clean.csv")
least_missing_lte_csv = os.path.join(base_dir, "output", "top_50_LTE_least_missing_relevant_metadata.csv")

# Load the CSV file with specified delimiter and treat "Unknown" as missing
df_unfiltered = pd.read_csv(input_file, delimiter=';', na_values='Unknown')

df = df_unfiltered[
    (df_unfiltered['trial_category'] == 'Fertilization') &
    (df_unfiltered['landuse_type'] == 'Arable land') &
    (df_unfiltered['farming_category'] == 'Conventional')
]

# Replace "Unknown" with NaN to mark them as missing
df.replace("Unknown", pd.NA, inplace=True)

# Create a boolean DataFrame: True where data is present, False where it's missing
data_coverage = df.notna()

# Set up and save the heatmap
plt.figure(figsize=(15, 10))
sns.heatmap(data_coverage, cbar=False, cmap='viridis')
plt.title('Metadata Coverage in LTE Overview Map (July 2025)')
plt.xlabel('Columns')
plt.ylabel('Rows')
plt.tight_layout()
plt.savefig(heatmap_file, dpi=300)
plt.close()

# Calculate missing values per column
missing_counts = df.isna().sum()
missing_percentages = (missing_counts / len(df)) * 100

# Combine into a summary DataFrame
summary = pd.DataFrame({
    'Missing Values': missing_counts,
    'Percentage Missing': missing_percentages.round(2)
})

# Print summary to console
print(tabulate(summary.reset_index(), headers='keys', tablefmt='pretty'))
print(summary) 

# Sort and export the top 25 columns with most missing data
summary_sorted = summary.sort_values(by='Missing Values', ascending=False)
summary_sorted.head(25).to_csv(most_missing_csv)

# Sort and export the top 25 columns with least missing data
summary_sorted.tail(25).sort_values(by='Missing Values').to_csv(least_missing_csv)

# Print the least missing columns table
least_missing = summary_sorted.tail(25).sort_values(by='Missing Values')
print(tabulate(least_missing.reset_index(), headers='keys', tablefmt='pretty'))

# Remove less important metadata fields from the summary dataframe
summary_subset = summary.drop(index=['country', 'name', 'trial_institution', 'holder_category', 'site', 
                                    'latitude', 'longitude', 'miscellaneous','sources','agrovoc_keywords','position_exactness',
                                    'fertilization_trial', 'crop_rotation_trial', 'tillage_trial', 'irrigation_trial',
                                    'cover_crop_trial', 'grazing_trial', 'pest_weed_trial', 'other_trial', 
                                    'literature', 'website','networks','contact_email','contact_name','contact_name'])



# Sort and export the top 27 columns with most missing data
summary_subset_sorted = summary_subset.sort_values(by='Missing Values', ascending=False)
summary_subset_sorted.head(27).to_csv(most_missing_clean_csv)

# Sort and export the top 27 columns with least missing data
summary_subset_sorted.tail(27).sort_values(by='Missing Values').to_csv(least_missing_clean_csv)

# Subset df to the top least missing metadata columns
top_least_missing_columns = least_missing.index.tolist()
top_least_missing_df = df[top_least_missing_columns]

# Save the subset DataFrame to a CSV file, seprated by semicolon
#top_least_missing_df.to_csv(least_missing_clean_csv, sep=';', index=False)

# Select the 50 LTEs (rows) with the least missing metadata
top_least_missing_ltes = top_least_missing_df.head(50)

# Subset df (including all columns) to the rows with the 50 top least missing LTEs 
ltes_top_least_missing_metadata = df[df['index'].isin(top_least_missing_ltes['index'])]


# Save the subset DataFrame to a CSV file, separated by semicolon
ltes_top_least_missing_metadata.to_csv(least_missing_lte_csv, sep=';', index=False)