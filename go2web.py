import argparse

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