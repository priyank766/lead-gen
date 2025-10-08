import requests
from bs4 import BeautifulSoup
from src.enricher import extract_emails, extract_phones


def scrape_url(url: str) -> str:
    """
    Fetches the HTML content of a given URL.

    Args:
        url: The URL to scrape.

    Returns:
        The HTML content of the page, or an empty string if the request fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""


def main():
    """
    Main function to test the scraper.
    """
    test_url = "https://www.google.com"
    html_content = scrape_url(test_url)
    if html_content:
        soup = BeautifulSoup(html_content, "html.parser")
        text = soup.get_text()
        emails = extract_emails(text)
        phones = extract_phones(text)
        print(f"Title: {soup.title.string}")
        print(f"Emails: {emails}")
        print(f"Phones: {phones}")


if __name__ == "__main__":
    main()
