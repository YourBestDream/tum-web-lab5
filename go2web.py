import argparse
import socket
from urllib.parse import urlparse

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
    return sock


def main():
    parser = argparse.ArgumentParser(
        prog="go2web",
        description="Simple HTTP client CLI"
    )
    parser.add_argument(
        "-h", "--help",
        action="help",
        help="show this help message and exit"
    )
    parser.parse_args()

if __name__ == "__main__":
    main()