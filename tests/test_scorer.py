import unittest
from src.scorer import score_lead

class TestScorer(unittest.TestCase):

    def test_score_lead(self):
        lead1 = {
            'emails': ['test@example.com'],
            'phones': ['123-456-7890'],
            'linkedin': 'linkedin.com/company/test',
            'has_contact_page': True,
            'has_pricing': False
        }
        self.assertEqual(score_lead(lead1), 85)

        lead2 = {
            'emails': ['test@example.com'],
            'phones': [],
            'linkedin': None,
            'has_contact_page': False,
            'has_pricing': True
        }
        self.assertEqual(score_lead(lead2), 50)

        lead3 = {}
        self.assertEqual(score_lead(lead3), 0)

if __name__ == '__main__':
    unittest.main()
