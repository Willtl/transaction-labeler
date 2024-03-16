# Transaction Labeler

## Overview

A Python script designed for generating labeled datasets from financial transaction data. It
processes CSV files containing transaction details, extracts descriptive text from each transaction, and uses a
combination of web scraping and GPT-4 to categorize transactions. The primary goal is to create a dataset that can be
utilized for text classification tasks without relying on GPT-4 for future predictions.

## Features

- Reads transaction data from CSV files.
- Scrapes the web for additional context on transaction descriptions.
- Cleans and preprocesses scraped data.
- Utilizes OpenAI's GPT-4 to categorize transactions into predefined categories.
- Generates a labeled dataset ready for text classification.

## Data Format

CSV files should contain transactions with the following columns:

- Date
- Description
- Transaction Type (CR/DR)
- Amount

## Categories

Transactions are categorized into the following:

- Dining
- Supermarket
- Healthcare
- Pets
- Reimbursement
- Shopping
- Subscriptions
- Transport
- Travel
- Utilities
- Undefined (if the description lacks sufficient detail)

