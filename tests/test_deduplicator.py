import unittest
from src.deduplicator import deduplicate_leads

class TestDeduplicator(unittest.TestCase):

    def test_deduplicate_leads(self):
        leads = [
            {'company_name': 'Acme Inc.', 'domain': 'acme.com', 'emails': ['test@acme.com'], 'source_urls': ['acme.com']},
            {'company_name': 'Acme', 'domain': 'www.acme.com', 'emails': ['info@acme.com'], 'phones': ['123-456-7890'], 'source_urls': ['acme.com/contact']},
            {'company_name': 'Beta Corp', 'domain': 'beta.com', 'emails': ['contact@beta.com'], 'source_urls': ['beta.com']},
            {'company_name': 'Acme Corporation', 'domain': 'acme.org', 'emails': ['hr@acme.org'], 'source_urls': ['acme.org']},
        ]

        deduplicated = deduplicate_leads(leads)

        self.assertEqual(len(deduplicated), 2)
        self.assertEqual(deduplicated[0]['company_name'], 'Acme')
        self.assertEqual(len(deduplicated[0]['emails']), 3)
        self.assertEqual(len(deduplicated[0]['phones']), 1)
        self.assertEqual(len(deduplicated[0]['source_urls']), 3)

if __name__ == '__main__':
    unittest.main()
