import argparse
import socket
import ssl
import json
from urllib.parse import urlparse
from urllib.parse import quote_plus
from bs4 import BeautifulSoup

def strip_html(html: str) -> str:
    """Strip HTML tags to produce plain text."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)
 
def fetch_http(url):
    """Perform a basic HTTP GET request over sockets."""
    parsed = urlparse(url)
    host = parsed.netloc
    port = 443 if parsed.scheme == "https" else 80
    sock = socket.create_connection((host, port))
    if parsed.scheme == "https":
        import ssl
        ctx = ssl.create_default_context()
        sock = ctx.wrap_socket(sock, server_hostname=host)
    path = parsed.path or "/"
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        "Connection: close\r\n\r\n"
    )
    sock.sendall(req.encode())
    data = b""
    while chunk := sock.recv(4096):
        data = chunk
    sock.close()
    hdr, body = data.split(b"\r\n\r\n", 1)
    return hdr.decode(), body

def cmd_fetch(url):
    hdr, body = fetch_http(url)
    content = body.decode("utf-8", errors="ignore")
    try:
        obj = json.loads(content)
        print(json.dumps(obj, indent=2))
    except json.JSONDecodeError:
        print(strip_html(content))

def cmd_search(term):
    """Stub for search command."""
    q = quote_plus(term)
    url = f"https://duckduckgo.com/html/?q={q}"
    hdr, body = fetch_http(url)
    html = body.decode("utf-8", errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    results = soup.select("a.result__a")[:10]
    for i, a in enumerate(results, 1):
        print(f"{i}. {a.get_text()}\n   {a['href']}")

def main():
    parser = argparse.ArgumentParser(
        prog="go2web",
        description="Simple HTTP client CLI"
    )
    parser.add_argument(
        "-u", metavar="URL", dest="url",
        help="URL to GET"
    )
    parser.add_argument(
        "-h", "--help",
        action="help",
        help="show this help message and exit"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", metavar="URL", dest="url", help="URL to GET")
    group.add_argument("-s", nargs="", dest="search", help="search term")
    args = parser.parse_args()
    parser.parse_args()
    if args.url:
        hdr, body = fetch_http(args.url)
        print(body.decode("utf-8", errors="ignore"))

if __name__ == "__main__":
    main()