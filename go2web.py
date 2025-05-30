import argparse
import socket
from urllib.parse import urlparse

def fetch_http(url):
    """Perform a basic HTTP GET request over sockets."""
    pass


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