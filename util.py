import os
import re
from collections import Counter

import pandas as pd
import requests
from bs4 import BeautifulSoup

categories = (
    ("Dining", "Expense related to dining out: restaurants, cafes, fast-food outlets, and food delivery services. This category encompasses meals consumed outside."),
    ("Supermarket", "Expense from grocery stores, supermarkets, and food markets. This category covers purchases of food items, beverages, household supplies, and other essentials."),
    ("Healthcare", "Expense associated with healthcare services, including hospitals, clinics, pharmacies, medical consultations, prescriptions, and medical supplies."),
    ("Pets", "Expense related to pet care, such as purchases from pet stores, veterinary services, grooming, pet food, medications, and other pet-related Expense."),
    ("Reimbursement", "Refunds, returns, or compensation received for previously incurred Expense."),
    ("Shopping", "Expense from various retail purchases, including clothing, fashion accessories, electronics, gadgets, home goods, and personal care products."),
    ("Subscriptions", "Expense for subscription-based services, such as streaming platforms, magazines, newspapers, online software, membership fees, and other "
                      "regular payments such haircuts, etc."),
    ("Transport", "Expense related to transportation, such as public transport fares, taxi rides, fuel purchases, vehicle maintenance, parking fees, and toll charges."),
    ("Travel", "Expense incurred while traveling, including airline tickets, hotel accommodations, vacation packages, rental cars, travel insurance, and Expense in "
               "foreign currencies."),
    ("Utilities", "Expense for essential services such as electricity, water, gas, internet, cable television, phone bills, and other utilities required for daily living.")
)

valid_labels = {name.lower(): name for name, _ in categories}
valid_labels['undefined'] = 'Undefined'


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
