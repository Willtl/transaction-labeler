from sentence_transformers import SentenceTransformer, util

from util import *

model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)
output_file = f'./static/output/labeled_expenses_{model_name}.csv'
similarity_threshold = 0.15  # minimum acceptable similarity to assign a specific category


def categorize_description(description, scraped, refine=True):
    if refine:
        description = refine_description(description, scraped)
    else:
        description = ' '.join([description] + scraped)

    # Generate embedding for the given description
    description_embedding = model.encode(description, convert_to_tensor=True)

    best_category = 'Undefined'
    highest_similarity = 0  # Initialize with 0, adjust threshold based on validation results

    # Iterate over category descriptions to compute similarity
    print('Description', description)
    for category, cat_desc in categories:
        cat_embedding = model.encode(cat_desc, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(description_embedding, cat_embedding).item()
        print(f"    Similarity with {category}: {similarity:.4f} >>> {cat_desc}")
        # Select the category with the highest similarity if it is higher than the current best
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_category = category

    if highest_similarity < similarity_threshold:
        best_category = 'Undefined'

    return best_category




def process_files(folder_path):
    description_mapping, mapping = load_description_mapping(output_file)

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            df = load_data(file_path)

            for index, row in df.iterrows():
                tr_type = row['Transaction Type']
                if tr_type == 'CR':
                    continue

                description = row['Description'].lower()
                cleaned_description = clean_description(description)
                if description not in mapping:
                    headings = scrape(cleaned_description)
                    headings = clean_headings(headings)[:5]
                    label = categorize_description(cleaned_description, headings)

                    # Update mapping to ensure we don't process repeated descriptions
                    mapping.add(description)

                    # Update description_mapping.csv
                    new_row = pd.DataFrame([{'Description': description, 'Headings': headings, 'Labels': label}])
                    description_mapping = pd.concat([description_mapping, new_row], ignore_index=True)

                    # Save updated description_mapping.csv to disk
                    description_mapping.to_csv(output_file, index=False)
                    print('ADDED', description, label)
                else:
                    print('SKIP', description)


if __name__ == "__main__":
    folder_path = 'static/csv'
    process_files(folder_path)
