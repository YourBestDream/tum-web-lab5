# go2web

A simple command-line HTTP client.

## Usage

1) Install the requirements
```python
pip install -r requirements.txt
```
2) Run the desired option using python
```python
python go2web -h ## for help
python go2web -u <desired_url> ## for parsing human readable text from URL
python go2web -s <term> ## top 10 results for this specific term
```
## Features
- Follows HTTP redirects (301/302/etc.)
- Caches 200 OK responses under `./.go2web_cache`
- Honors `Accept` header for JSON vs HTML
## Demo
![demo](demo.gif)