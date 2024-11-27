# scholar scripts
Collection of scripts and notebooks for aggregating and formatting literary and podcast info and reviews from various sources

## Installation
```bash
$ python -m venv .venv
$ source .venv/Scripts/activate
$ pip install -r requirements
$ jupyter notebook
```

## Library Search Notebook
Query the Overdrive system for a set of libraries, using either a GoodReads `to-read` list, previous queries, or just a list containing dicts with `Author` and `Title` keys.  Each library is searched in parallel and the results are stored in a DataFrame for easy analysis. 

## App Exports Parsing Notebook
Code to parse GoodReads export files and Kindle highlights (via either the `My Clippings.txt` file or `read.amazon/notebook`)

## Webpage Parsing Notebook
This notebook is probably more useful as a template than as a tool, as it is geared to:
1. parse a specific website (Lex Fridman's)
2. parse a youTube search result into a markdown table for personal annotations