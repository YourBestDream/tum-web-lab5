import unittest
from go2web import fetch_http

class FetchTest(unittest.TestCase):
    def test_parse_status(self):
        hdr, _ = fetch_http("http://example.com")
        self.assertIn("HTTP/1.1 200", hdr.split("\r\n")[0])

if __name__ == "__main__":
    unittest.main()