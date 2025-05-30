import argparse
import socket
import ssl
import json
from urllib.parse import urlparse
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import os, hashlib

CACHE_DIR = os.path.expanduser("~/.go2web_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def strip_html(html: str) -> str:
    """Strip HTML tags to produce plain text."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)
 
def fetch_http(url, accept="*/*"):
    """Perform a basic HTTP GET request over sockets."""
    key = hashlib.sha256(f"{url}|{accept}".encode()).hexdigest()
    cache_file = os.path.join(CACHE_DIR, key + ".json")
    if os.path.exists(cache_file):
        obj = json.load(open(cache_file))
        return obj["hdr"], obj["body"].encode()
    parsed = urlparse(url)
    if allow_redirects and status in (301,302,303,307,308):
        loc = headers.get("Location")
        if loc and max_redirects > 0:
            return fetch_http(loc, allow_redirects, max_redirects-1, accept)

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
        f"Accept: {accept}\r\n"
        "Connection: close\r\n\r\n"
     )
    sock.sendall(req.encode())
    data = b""
    while chunk := sock.recv(4096):
        data = chunk
    sock.close()
    hdr, body = data.split(b"\r\n\r\n", 1)
    result = {"hdr": hdr, "body": body.decode()}
    if status == 200:
        json.dump(result, open(cache_file, "w"))
    return hdr, body

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