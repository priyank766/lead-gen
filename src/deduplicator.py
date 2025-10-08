import re
import json
from rapidfuzz import fuzz

def normalize_name(name: str) -> str:
    """
    Normalizes a company name by removing suffixes and converting to lowercase.

    Args:
        name: The company name to normalize.

    Returns:
        The normalized company name.
    """
    # Remove common suffixes like Inc, Ltd, LLC, etc.
    name = re.sub(r",?\s*(inc|ltd|llc|corp|corporation|gmbh|ag|bv|sa|sas|sarl)\.?$", "", name, flags=re.IGNORECASE)
    # Remove leading/trailing whitespace and convert to lowercase
    return name.strip().lower()

def normalize_domain(domain: str) -> str:
    """
    Normalizes a domain by removing www. and converting to lowercase.

    Args:
        domain: The domain to normalize.

    Returns:
        The normalized domain.
    """
    # Remove www. and leading/trailing whitespace, and convert to lowercase
    domain = re.sub(r"^www\.", "", domain, flags=re.IGNORECASE)
    return domain.strip().lower()

def deduplicate_leads(leads: list[dict]) -> list[dict]:
    """
    Deduplicates a list of leads based on domain and company name similarity.

    Args:
        leads: A list of lead dictionaries.

    Returns:
        A list of deduplicated lead dictionaries.
    """
    if not leads:
        return []

    # Normalize domains and names for comparison
    for lead in leads:
        if lead.get('domain'):
            lead['normalized_domain'] = normalize_domain(lead['domain'])
        if lead.get('company_name'):
            lead['normalized_name'] = normalize_name(lead['company_name'])

    merged_leads = []
    processed_indices = set()

    for i in range(len(leads)):
        if i in processed_indices:
            continue

        current_lead = leads[i]
        merged_lead = current_lead.copy()
        processed_indices.add(i)

        for j in range(i + 1, len(leads)):
            if j in processed_indices:
                continue

            other_lead = leads[j]

            # Merge based on exact domain match or high name similarity
            domain_match = (merged_lead.get('normalized_domain') and 
                            other_lead.get('normalized_domain') and 
                            merged_lead['normalized_domain'] == other_lead['normalized_domain'])
            
            name_similarity = 0
            if merged_lead.get('normalized_name') and other_lead.get('normalized_name'):
                name_similarity = fuzz.token_sort_ratio(merged_lead['normalized_name'], other_lead['normalized_name'])

            if domain_match or name_similarity > 90:
                # Merge logic: keep the one with more contact info
                if len(other_lead.get('emails', [])) + len(other_lead.get('phones', [])) > \
                   len(merged_lead.get('emails', [])) + len(merged_lead.get('phones', [])):
                    # Swap to keep the more complete lead
                    merged_lead, other_lead = other_lead, merged_lead
                
                # Union of contact info and source URLs
                merged_lead['emails'] = list(set(merged_lead.get('emails', []) + other_lead.get('emails', [])))
                merged_lead['phones'] = list(set(merged_lead.get('phones', []) + other_lead.get('phones', [])))
                merged_lead['source_urls'] = list(set(merged_lead.get('source_urls', []) + other_lead.get('source_urls', [])))

                processed_indices.add(j)

        # Clean up helper fields
        if 'normalized_domain' in merged_lead:
            del merged_lead['normalized_domain']
        if 'normalized_name' in merged_lead:
            del merged_lead['normalized_name']

        merged_leads.append(merged_lead)

    return merged_leads

def main():
    """
    Main function to test the deduplicator.
    """
    test_leads = [
        {'company_name': 'Acme Inc.', 'domain': 'acme.com', 'emails': ['test@acme.com'], 'source_urls': ['acme.com']},
        {'company_name': 'Acme', 'domain': 'www.acme.com', 'emails': ['info@acme.com'], 'phones': ['123-456-7890'], 'source_urls': ['acme.com/contact']},
        {'company_name': 'Beta Corp', 'domain': 'beta.com', 'emails': ['contact@beta.com'], 'source_urls': ['beta.com']},
        {'company_name': 'Acme Corporation', 'domain': 'acme.org', 'emails': ['hr@acme.org'], 'source_urls': ['acme.org']},
    ]

    deduplicated = deduplicate_leads(test_leads)
    print(json.dumps(deduplicated, indent=2))

if __name__ == "__main__":
    main()
