import concurrent.futures
import json
import logging
import re
import time
from datetime import datetime
from enum import StrEnum

import requests
import toolz as tz
from bs4 import BeautifulSoup

import scholar_scripts.utils as u

log = logging.getLogger(__name__)


class LibraryCode(StrEnum):
    SEATTLE = "spl"
    DALLAS = "dallaslibrary"
    BOISE = "boise"


SUMMARY_FIELDS = ["title", "audiobook_available", "ebook_available", "library"]

OVERDRIVE_AVAIL_KEYS = {
    "availableCopies": "available",
    "ownedCopies": "owned",
    "holdsCount": "held",
    "estimatedWaitDays": "estimated_wait",
}

OVERDRIVE_TITLE_KEYS = {
    "title": "title",
    "subtitle": "subtitle",
    "publishDateText": "publish_date",
    "firstCreatorName": "author",
}

DATE_FMT = "%Y-%m-%d"


class Query(StrEnum):
    PREV_UNAVAIL = (
        "(`ebook_owned` > 0 and `ebook_available` < 1) or (`audiobook_owned` > 0 and `audiobook_available` < 1)"
    )
    AUDIOS_PREV_UNAVAIL = "`audiobook_owned` > 0 and `audiobook_available` < 1"
    AUDIOS_AVAIL = "`audiobook_available` >= 1"
    EBOOKS_PREV_UNAVAIL = "`ebook_owned` > 0 and `ebook_available` < 1"
    EBOOKS_AVAIL = "`ebook_available` >= 1"


def _as_iso_8601(date_str: str) -> str:
    if date_str:
        try:
            return datetime.strptime(date_str, "%m/%d/%Y").strftime(DATE_FMT)
        except ValueError:
            log.warn(f"Unexpected date format found: {date_str}")
            return date_str


def _parse_media_item(raw_items: list[dict]) -> dict:
    rval = {OVERDRIVE_TITLE_KEYS[k]: v for k, v in raw_items[0].items() if k in OVERDRIVE_TITLE_KEYS}
    rval = tz.update_in(rval, ["publish_date"], _as_iso_8601)
    for raw_item in raw_items:
        media_type = tz.get_in(["type", "id"], raw_item)
        for k, v in raw_item.items():
            if k in OVERDRIVE_AVAIL_KEYS:
                rval[f"{media_type}_{OVERDRIVE_AVAIL_KEYS[k]}"] = v
    return rval


def search_for_media(author: str, title: str, library: LibraryCode) -> dict:
    """search a library for a media item by title and author

    Args:
        author (str): author
        title (str): title
        library (LibraryCode): library to search

    Returns:
        dict: search results and query meta data
    """
    _url = f"https://{library}.overdrive.com/search/title?query={title}&creator={author}"
    t0 = time.time()
    log.debug(f"Making HTTP request {_url}")
    response = requests.get(_url)
    _meta = {
        "query_status_code": response.status_code,
        "query_time": time.time() - t0,
        "library": str(library.name).lower(),
        "query_url": _url,
        "query_title": title,
        "query_author": author,
        "requested_on": u.now_iso(),
    }
    soup = BeautifulSoup(response.text, "html.parser")
    if t := soup.find("script"):
        if m := re.search(r"\n\s*window.OverDrive.mediaItems(.+)\n", t.string):
            if raw := m.group():
                if _items := json.loads(raw[raw.find("{") : raw.rfind("}") + 1]):
                    rval = _parse_media_item(list(_items.values()))
                    return {**rval, **_meta}
    return _meta


def search_library(library: LibraryCode, book_list: list[dict], delay: float = 1.0) -> list[dict]:
    """Search a particular library for book availabilities

    Args:
        library (LibraryCode): library to search
        book_list (list[dict]): list of books to search for (by Title and Author)
        delay (float, optional): Seconds delay between Overdrive HHTP requests. Defaults to 1.0.

    Returns:
        list[dict]: search results for each book
    """
    results = []
    for book in book_list:
        _author = book.get("query_author") or u.clean_author(book["Author"])
        _title = book.get("query_title") or u.clean_title(book["Title"])
        try:
            _result = search_for_media(_author, _title, library)
            results.append(_result)
        except Exception as ex:
            log.warn(f"Exception raised processing {_title} :\n{ex}")
        time.sleep(delay)
    return results


def search_libraries(book_list: list[dict], delay: float = 1, libraries: list[LibraryCode] = None) -> list[dict]:
    """Search libraries in parallel for digital book availability

    Args:
        book_list (list[dict]): list of books to locate (by Title and Author)
        delay (float, optional): Seconds delay between Overdrive HHTP requests. Defaults to 1.
        libraries (list[LibraryCode]): List of libraries to search. Defaults to search all

    Returns:
        list[dict]: search results for each book
    """
    libs_to_search = libraries if libraries else LibraryCode
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(search_library, lib, book_list, delay) for lib in libs_to_search]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
        return [x for xs in results for x in xs]  # flatten
