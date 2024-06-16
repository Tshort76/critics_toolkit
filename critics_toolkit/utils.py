import logging
import os
from datetime import datetime
from importlib import reload
from logging.config import dictConfig

import pandas as pd


def configure_logging() -> None:
    reload(logging)
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "basic": {
                    "format": "%(asctime)s - %(levelname)s - (%(name)s) - %(message)s",
                    "datefmt": "%H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": logging.StreamHandler,
                    "formatter": "basic",
                }
            },
            "loggers": {
                "critics_tools": {
                    "level": logging.INFO,
                    "handlers": ["console"],
                    "propagate": False,
                }
            },
            "root": {"level": logging.INFO, "handlers": ["console"]},
        }
    )


log = logging.getLogger(__name__)


def now_iso() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def clean_name(s: str) -> str:
    parts = s.split()
    parts = ["".join([c for c in p.lower() if c.isalpha()]) for p in parts]
    return "+".join(parts)


def clean_author(s: str) -> str:
    names = s.split()
    return names[0].lower() + "+" + names[-1].lower()


def clean_title(s: str) -> str:
    end = s.find(":")
    if end > 0:
        s = s[:end]
    end = s.find("(")
    if end > 0:
        s = s[:end]
    return clean_name(s)


MD_FILE_TEMPLATE = """---
author: {author}
date: {date}
rating: {rating}
tags: [{tags}]
---
## Summary

## Reflections

## Quotes

## Raw Notes

"""


def as_markdown_file(book: dict) -> None:
    """Generates a markdown file for a book with Obsidian properties formatted.

    Args:
        book (dict): book details from goodreads properties

    Note: Files are stored in the 'outputs' directory
    """
    dt = book["Date Read"]
    if not pd.notna(dt):
        log.warn(f"Bad date, {dt}, for title: {book['Title']}")
        return
    with open(os.path.join("outputs", f"{book['Title']}.md"), "w") as fp:
        fp.write(
            MD_FILE_TEMPLATE.format(
                author=clean_author(book["Author"]).replace("+", " "),
                date=f"{dt[0:4]}-{dt[5:7]}-{dt[8:10]}",
                rating="+" * int(book["My Rating"]),
                tags=" " if pd.isna(book["Bookshelves"]) else book["Bookshelves"],
            )
        )
