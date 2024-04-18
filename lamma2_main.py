import ollama

from util import *


def categorize_description(description):
    category_descriptions = '\n'.join([f"{name}: {desc}" for name, desc in categories])
    prompt = (f"Read the following credit card expense description carefully:\n\n'{description}'\n\n"
              f"Categorize this expense as one of the following, or Undefined if the description lacks sufficient detail. "
              f"If you are not at least 70% confident in your classification, please select 'Undefined'.\n\n"
              f"{category_descriptions}\n\nImportant: Provide only the label (one word) as output. Do not write anything except valid categories or Undefined.")

    response = ollama.chat(
        model='llama2',
        messages=[
            {'role': 'system', 'content': "You are a concise assistant focused on accurately categorizing expense types."},
            {'role': 'user', 'content': prompt}
        ]
    )

    response_content = response['message']['content']

    # Extract labels from the response
    words = response_content.strip().lower().split()

    # Search for the first valid label in the output
    for word in words:
        if word in valid_labels:
            return valid_labels[word], prompt

    return 'Undefined', prompt


def process_files(folder_path):
    description_mapping, mapping = load_description_mapping()

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            df = load_data(file_path)

            for index, row in df.iterrows():
                tr_type = row['Transaction Type']
                if tr_type == 'CR':
                    continue

                description = row['Description'].lower()

                if description not in mapping:
                    headings = scrape(description)
                    headings = clean_headings(headings)[:10]
                    expense_description = '\n'.join([description] + headings)
                    label, prompt_used = categorize_description(expense_description)

                    # Update mapping to ensure we don't process repeated descriptions
                    mapping.add(description)

                    # Update description_mapping.csv
                    new_row = pd.DataFrame([{'Description': description, 'Headings': headings, 'Labels': label}])
                    description_mapping = pd.concat([description_mapping, new_row], ignore_index=True)

                    # Save updated description_mapping.csv to disk
                    description_mapping.to_csv('./static/output/labeled_expenses_lamma2.csv', index=False)
                    print('ADDED', description, label)
                else:
                    print('SKIP', description)


if __name__ == "__main__":
    folder_path = 'static/csv'
    process_files(folder_path)
