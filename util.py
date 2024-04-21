import os
import re
from collections import Counter

import ollama
import pandas as pd
import requests
from bs4 import BeautifulSoup

categories = (
    ("Dining", "Dining, meals at restaurants, cafes, and fast food outlets. Excludes grocery and supermarkets."),
    ("Supermarket", "Supermarkets, grocery stores, including food items, beverages, and household supplies."),
    ("Healthcare", "Hospitals, clinics, pharmacy, and healthcare facilities; includes prescriptions and medical consultations."),
    ("Pets", "Expenses for pet care, including food, medications, grooming, and veterinary services."),
    ("Shopping", "Shopping, clothing, shopping, electronics, home goods, and personal care products at retail locations."),
    ("Transport", "Local transportation expenses including public transit, taxis, and personal vehicle costs such as fuel and maintenance."),
    ("Utilities", "Monthly utility bills including electricity, water, gas, internet services, and cable TV."),
    ("Personal Care", "Personal grooming and beauty services at locations such as barbershops, beauty salons, and spas. Includes haircuts, styling, facials, and grooming.")
)

valid_labels = {name.lower(): name for name, _ in categories}
valid_labels['undefined'] = 'Undefined'


def load_data(file_path):
    return pd.read_csv(file_path, header=None, names=['Date', 'Description', 'Transaction Type', 'Amount'])


def refine_query(query):
    role = ('Refine text into a Google search query. '
            'Remove meaningless characters. '
            'Do not provide any other output only the text to be searched on google.')
    prompt = (f'Text: {query}')

    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': role},
            {'role': 'user', 'content': prompt}
        ]
    )

    response_content = response['message']['content']
    return response_content


def refine_description(description, scraped):
    # role = ('Translate any token that is not english word to English. Summarize the description into 20 words. Do not explain what you are doing just provide the sentence (raw without any interaction)')
    # scraped_joined = ", ".join(scraped)
    # prompt = (f'Description: {description} '
    #           f'Scrape: {scraped_joined}. ')

    prompt = f'This is an expense that appeared in my credit card statement: {description}, what could it be? Write a sentence starting by: `This credit card expense description is probably from ...'
    response = ollama.chat(
        model='llama3',
        messages=[
            # {'role': 'system', 'content': role},
            {'role': 'user', 'content': prompt}
        ]
    )

    response_content = response['message']['content']

    return response_content


def scrape(description, refine=True):
    if refine:
        description = refine_query(description)  # use llama3 to refine query

    prep_description = description.replace(' ', '+')
    url = f'https://www.google.com/search?q={prep_description}'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    headings = soup.find_all('h3')

    # Extract text from each heading and store it in a list
    heading_texts = [info.getText() for info in headings]
    return heading_texts


def clean_description(description):
    # Convert to lowercase
    cleaned_description = description.lower()

    # Remove special characters
    cleaned_description = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned_description)

    # Remove excess spaces
    cleaned_description = re.sub(r'\s+', ' ', cleaned_description)

    # Remove characters that are alone within the string
    cleaned_description = re.sub(r'(?<=\s)\S(?=\s)', '', cleaned_description)

    return cleaned_description.strip()


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


# Load description_mapping.csv
def load_description_mapping():
    mapping_file = 'description_mapping.csv'
    if os.path.exists(mapping_file):
        return pd.read_csv(mapping_file)
    else:
        return pd.DataFrame(columns=['Description', 'Headings', 'Labels'])


# Load description_mapping.csv
def load_description_mapping(output_file):
    mapping = set()
    mapping_file = output_file
    if os.path.exists(mapping_file):
        description_mapping = pd.read_csv(mapping_file)
        # Iterate over descriptions to update the mapping set
        for desc in description_mapping['Description']:
            mapping.add(desc.lower())
        return description_mapping, mapping
    else:
        return pd.DataFrame(columns=['Description', 'Headings', 'Labels']), mapping
