#!/usr/bin/env python3
import argparse, socket, ssl, os, hashlib, json
from urllib.parse import urlparse, quote_plus
from bs4 import BeautifulSoup

CACHE_DIR = os.path.expanduser("./.go2web_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_http(raw_url, allow_redirects=True, max_redirects=3, accept="*/*"):
    """Perform HTTP/HTTPS GET via raw sockets."""
    def _inner(url, redirects_left):
        parsed = urlparse(url)
        scheme = parsed.scheme or "http"
        host = parsed.netloc
        port = 443 if scheme=="https" else 80
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query

        # Check cache
        key = hashlib.sha256(f"{url}|{accept}".encode()).hexdigest()
        cache_file = os.path.join(CACHE_DIR, key)
        if os.path.exists(cache_file):
            return json.load(open(cache_file, "r"))

        # Open socket
        sock = socket.create_connection((host, port), timeout=5)
        if scheme=="https":
            ctx = ssl.create_default_context()
            sock = ctx.wrap_socket(sock, server_hostname=host)

        # Send request
        req = [
            f"GET {path} HTTP/1.1",
            f"Host: {host}",
            f"Accept: {accept}",
            "Connection: close",
            "", ""
        ]
        sock.sendall("\r\n".join(req).encode())

        # Receive all
        data = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk: break
            data += chunk
        sock.close()

        hdr, body = data.split(b"\r\n\r\n", 1)
        hdr_lines = hdr.decode(errors="ignore").split("\r\n")
        status = int(hdr_lines[0].split()[1])
        headers = dict(
            line.split(":",1) for line in hdr_lines[1:] if ":" in line
        )

        # Handle redirects
        if allow_redirects and status in (301,302,303,307,308) and "Location" in headers:
            if redirects_left > 0:
                return _inner(headers["Location"].strip(), redirects_left-1)

        result = {"status": status, "headers": headers, "body": body.decode(errors="ignore")}
        # Cache only 200 OK
        if status==200:
            json.dump(result, open(cache_file, "w"))
        return result

    return _inner(raw_url, max_redirects)

def strip_html(html):
    """Return plain text from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)

def cmd_fetch(args):
    resp = fetch_http(args.u)
    if resp["status"] != 200:
        print(f"[Error] HTTP {resp['status']}")
        return
    print(strip_html(resp["body"]))

def cmd_search(args):
    term = quote_plus(" ".join(args.s))
    url = f"https://duckduckgo.com/html/?q={term}"
    resp = fetch_http(url, accept="text/html")
    if resp["status"] != 200:
        print(f"[Error] HTTP {resp['status']}")
        return
    soup = BeautifulSoup(resp["body"], "html.parser")
    links = soup.select("a.result__a")[:10]
    for i, a in enumerate(links,1):
        title = a.get_text()
        href  = a.get("href")
        print(f"{i}. {title}\n   {href}")

def main():
    p = argparse.ArgumentParser(prog="go2web",
        description="Simple raw-socket HTTP client & search CLI")
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", metavar="URL", help="GET URL", nargs=1, dest="u")
    group.add_argument("-s", metavar="TERM", help="search term", nargs="+", dest="s")
    args = p.parse_args()

    if args.u:
        args.u = args.u[0]
        cmd_fetch(args)
    else:
        cmd_search(args)

if __name__=="__main__":
    main()
