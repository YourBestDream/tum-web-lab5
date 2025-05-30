import unittest
from urllib.parse import quote_plus

class SearchTest(unittest.TestCase):
    def test_url_build(self):
        term = "foo bar"
        self.assertEqual(
            f"https://duckduckgo.com/html/?q={quote_plus(term)}",
            "https://duckduckgo.com/html/?q=foo+bar"
        )

if __name__ == "__main__":
    unittest.main()