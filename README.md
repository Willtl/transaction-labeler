# Financial Transaction Data Enhancement and Classification

This project aims to enhance financial transaction data through web scraping and use a Large Language Model (LLM) for labeling and classification tasks.

The `util.py` module contains functions for scraping additional information from transaction descriptions. This information is then used to provide more context for classification.

There are two implementations for classification:

- **Using Ollama**: This implementation utilizes the Ollama platform and the `ollama` package for interaction. The `categorize_description` function categorizes transactions using the Llama2 model.
- **Using OpenAI GPT**: This implementation utilizes the OpenAI API and the `openai` package for interaction. The `categorize_description` function categorizes transactions using the GPT-4 model.

## Usage

1. Ensure you have the necessary dependencies installed.
2. **For Llama 2 Implementation:**
    - Follow the installation instructions for your operating system on [ollama.com](https://ollama.com/).
    - Install the Ollama Python package using `pip install ollama`.
3. **For OpenAI GPT Implementation:**
    - Replace `org_key` and `api_key` with your organization key and API key for accessing the OpenAI API in the code.
4. Place your transaction data files in the `static/csv` folder.
5. Run `process_files(folder_path)` to enhance and classify the transaction data.

## Requirements

- Python 3.x
- Necessary Python packages (`ollama`, `openai`, `pandas`, etc.)

## Notes

This project is a proof-of-concept and may require further customization or refinement for production use. It's designed for experimentation and checking the performance of various models in simple tasks.
