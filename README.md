# Lead Generation Tool

This project is a lead generation tool that scrapes websites, extracts contact information, and scores leads. It provides a FastAPI interface to access the functionality.

## Features

*   Scrape websites for contact information.
*   Use LLMs to extract structured data from websites.
*   Deduplicate leads based on domain and company name.
*   Score leads based on the completeness of their data.
*   Export leads to a CSV file.

## Ethical Considerations

When using this tool, it is important to be mindful of the legal and ethical implications of web scraping. Always respect the `robots.txt` file of a website, and be considerate of the website's servers by not sending too many requests in a short period of time. It is your responsibility to use this tool in a responsible and ethical manner.

## Project Structure

```
├── .venv
├── .python-version
├── pyproject.toml
├── README.md
├── requirements.txt
├── uv.lock
├── demo.ipynb
├── main.py
├── src/
│   ├── __init__.py
│   ├── deduplicator.py
│   ├── enricher.py
│   ├── extractor.py
│   ├── scorer.py
│   └── scraper.py
└── tests/
    ├── test_deduplicator.py
    └── test_scorer.py
```

### File Descriptions

*   `main.py`: The main FastAPI application file.
*   `demo.ipynb`: A Jupyter notebook demonstrating how to use the API.
*   `src/scraper.py`: Contains the function for scraping web pages.
*   `src/extractor.py`: Contains the function for extracting structured data using an LLM.
*   `src/enricher.py`: Contains functions for extracting emails and phone numbers from text.
*   `src/deduplicator.py`: Contains the function for deduplicating leads.
*   `src/scorer.py`: Contains the function for scoring leads.
*   `tests/`: Contains the unit tests for the project.

## API Endpoints

The API is documented using Swagger UI, which is available at `http://127.0.0.1:8000/docs` when the server is running.

*   `POST /scrape/`: Scrapes a URL and returns the extracted emails and phone numbers.
*   `POST /extract/`: Scrapes a URL and uses an LLM to extract structured data.
*   `POST /process_leads/`: Deduplicates and scores a list of leads.
*   `POST /export_leads/`: Exports a list of leads to a CSV file.

## Installation

1.  Install `uv` by following the instructions here: https://github.com/astral-sh/uv
2.  Create a virtual environment:

    ```bash
    uv venv
    ```

3.  Install the dependencies:

    ```bash
    uv pip install -r requirements.txt
    ```

## Usage

1.  Start the FastAPI server:

    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```

2.  Open your browser and go to `http://127.0.0.1:8000/docs` to access the API documentation and test the endpoints.

## Testing

To run the unit tests, use the following command:

```bash
uv run python -m unittest discover tests
```