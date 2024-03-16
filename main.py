import os
import re
from collections import Counter

import pandas as pd
import requests
from bs4 import BeautifulSoup
from openai import OpenAI


def load_data(file_path):
    return pd.read_csv(file_path, header=None, names=['Date', 'Description', 'Transaction Type', 'Amount'])


def scrape(description):
    prep_description = description.replace(' ', '+')
    url = f'https://www.google.com/search?q={prep_description}'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    headings = soup.find_all('h3')

    # Extract text from each heading and store it in a list
    heading_texts = [info.getText() for info in headings]
    return heading_texts


def clean_headings(headings, n=2):
    cleaned_headings = set()
    common_suffixes = ['linkedin', 'instagram', 'twitter', 'facebook', 'youtube', 'apple', 'google play', 'app store', 'wikipedia']

    for heading in headings:
        heading = heading.lower()
        heading = re.sub(r'\d+|\b\w\b', '', heading)  # Remove numbers and single characters in one go
        heading = re.sub(r"[^\w\s']", '', heading).strip()

        for suffix in common_suffixes:
            heading = re.sub(r'\b' + suffix + r'\b', '', heading)  # Use word boundaries to refine removal

        if len(heading.split()) >= 2:
            cleaned_headings.add(heading)

    n_grams = Counter()
    for heading in cleaned_headings:
        words = heading.split()
        for i in range(len(words) - n + 1):
            n_gram = ' '.join(words[i:i + n])
            n_grams[n_gram] += 1

    filtered_headings = set()
    for heading in cleaned_headings:
        words = heading.split()
        filtered_heading = []
        for i in range(len(words) - n + 1):
            n_gram = ' '.join(words[i:i + n])
            if n_grams[n_gram] == 1:
                filtered_heading.extend(words[i:i + n - 1])
        filtered_heading.append(words[-1])
        filtered_headings.add(' '.join(filtered_heading))

    return list(filtered_headings)


def categorize_description(description, client):
    categories = (
        ("Dining", "Restaurants, cafes, food delivery."),
        ("Supermarket", "Grocery stores, food markets."),
        ("Healthcare", "Hospitals, clinics, pharmacies."),
        ("Pets", "Pet stores, vet services, supplies."),
        ("Reimbursement", "Refunds, returns, compensation."),
        ("Shopping", "Clothing, fashion, electronics, home goods."),
        ("Subscriptions", "Streaming, magazines, software."),
        ("Transport", "Public transport, taxis, fuel."),
        ("Travel", "Airlines, hotels, vacation, currencies in (eur, chf, usd, brl, etc)."),
        ("Utilities", "Electricity, water, gas, telecom.")
    )

    category_descriptions = '\n'.join([f"{name}: {desc}" for name, desc in categories])
    prompt = f"Read the following credit card expense description carefully:\n\n'{description}'\n\nCategorize this expense as one of the following, or Undefined if the description lacks sufficient detail. Use 'Undefined' sparingly.\n\n{category_descriptions}\n\nImportant: Provide only the label (one word) as output."
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


# Load description_mapping.csv
def load_description_mapping():
    mapping_file = 'description_mapping.csv'
    if os.path.exists(mapping_file):
        return pd.read_csv(mapping_file)
    else:
        return pd.DataFrame(columns=['Description', 'Headings', 'Labels'])


# Load description_mapping.csv
def load_description_mapping():
    mapping = set()
    mapping_file = 'description_mapping.csv'
    if os.path.exists(mapping_file):
        description_mapping = pd.read_csv(mapping_file)
        # Iterate over descriptions to update the mapping set
        for desc in description_mapping['Description']:
            mapping.add(desc.lower())
        return description_mapping, mapping
    else:
        return pd.DataFrame(columns=['Description', 'Headings', 'Labels']), mapping


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
