import re

def extract_emails(text: str) -> list[str]:
    """
    Extracts email addresses from a given text.

    Args:
        text: The text to search for emails.

    Returns:
        A list of unique email addresses found in the text.
    """
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return list(set(re.findall(email_regex, text)))

def extract_phones(text: str) -> list[str]:
    """
    Extracts phone numbers from a given text.

    Args:
        text: The text to search for phone numbers.

    Returns:
        A list of unique phone numbers found in the text.
    """
    # This is a simple regex and might not catch all phone number formats
    phone_regex = r"\+?\d{1,3}?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
    return list(set(re.findall(phone_regex, text)))

def main():
    """
    Main function to test the enricher.
    """
    test_text = "Contact us at test@example.com or call +1 (123) 456-7890."
    emails = extract_emails(test_text)
    phones = extract_phones(test_text)
    print(f"Emails: {emails}")
    print(f"Phones: {phones}")

if __name__ == "__main__":
    main()
