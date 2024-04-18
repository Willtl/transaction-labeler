from openai import OpenAI

from util import *


def categorize_description(description, client):
    category_descriptions = '\n'.join([f"{name}: {desc}" for name, desc in categories])
    prompt = (f"Read the following credit card expense description carefully:\n\n'{description}'\n\n"
              f"Categorize this expense as one of the following, or Undefined if the description lacks sufficient detail. Use 'Undefined' sparingly.\n\n{category_descriptions}\n\n"
              f"Important: Provide only the label (one word) as output.")
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a concise assistant focused on accurately categorizing expense types."
            },
            {
                "role": "user", "content": prompt
            },
        ],
        temperature=0.0,
    )
    label = response.choices[0].message.content

    return label, prompt


def process_files(folder_path):
    description_mapping, mapping = load_description_mapping()
    org_key = 'org_key'
    api_key = 'your_api_key'

    client = OpenAI(
        organization=org_key,
        api_key=api_key
    )

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
                    label, prompt_used = categorize_description(expense_description, client)

                    # Update mapping to ensure we don't process repeated descriptions
                    mapping.add(description)

                    # Update description_mapping.csv
                    new_row = pd.DataFrame([{'Description': description, 'Headings': headings, 'Labels': label}])
                    description_mapping = pd.concat([description_mapping, new_row], ignore_index=True)

                    # Save updated description_mapping.csv to disk
                    description_mapping.to_csv('description_mapping.csv', index=False)
                    print('ADDED', description)
                else:
                    print('SKIP', description)


if __name__ == "__main__":
    folder_path = 'static/csv'
    process_files(folder_path)
