import re
from datetime import date, timedelta

import pandas as pd
from bs4 import BeautifulSoup, element

YOUTUBE_NUM_VIEWS_RGX = re.compile(r"(\d{1,3}(?:,\d{3})*)\s+views")
YOUTUBE_UPLOADED_AGO = re.compile(r"(\d+\s+years?)?(\d+\s+months?)?(\d+\s+weeks?)?(\d+\s+days?)?\s+ago")
YOUTUBE_VIDEO_LEN = re.compile(r"(?:(\d+)\s+hours?)?,?\s*(?:(\d+)\s+minutes?)?,?\s*(?:(\d+)\s+seconds?)?$")


def _parse_lex_episode(div: element.Tag) -> dict:
    ep = {}
    for d in div.select('div[class^="vid-"]'):
        cls = d.attrs.get("class", [])[0][4:]  # get unique part of div class
        match cls:
            case "title":
                ep["title"] = d.get_text()
            case "person":
                ep["guest"] = d.get_text()
            case "materials":
                for a in d.find_all("a"):
                    ep[a.get_text().lower()] = a.get("href")
    return ep


def parse_lex_episodes_html(html_path: str) -> pd.DataFrame:
    """Parse the html export from https://lexfridman.com/podcast

    Note that one should opt to 'show all' for episodes

    Args:
        html_path (str): filepath for the exported html file

    Returns:
        pd.DataFrame: Table with the title, guest, and links to video, webpage, and transcript
    """
    with open(html_path, mode="r", encoding="utf-8") as fp:
        soup = BeautifulSoup(fp.read(), "html.parser")

    site_content = soup.find("div", class_="grid grid-main")
    return pd.DataFrame([_parse_lex_episode(div) for div in site_content.find_all("div", class_="guest")][::-1])


def _publish_date(today, age_str: str) -> str:
    num = int(re.findall(r"(\d+)", age_str)[0])
    if "year" in age_str:
        return str(today.year - num)
    if "month" in age_str:
        return (today - timedelta(weeks=int(4.3 * num))).strftime("%B %Y")
    return (today - timedelta(days=num)).strftime("%B %Y")


def _parse_youtube_anchor(today: date, a: element.Tag) -> dict:

    lbl = a.attrs.get("aria-label")
    nviews = next(iter(YOUTUBE_NUM_VIEWS_RGX.findall(lbl)), None)
    dur = next(iter(YOUTUBE_VIDEO_LEN.findall(lbl)), None)
    age = next(iter(YOUTUBE_UPLOADED_AGO.findall(lbl)), [])
    age = next(iter([a for a in age if a]), None)
    return {
        "title": f"[{a.attrs.get('title').replace('|',':')}]({a.attrs.get('href')})",
        "num_views": nviews.strip(),
        "duration (m)": f"{60*(int(dur[0]) if dur[0] else 0) + (int(dur[1]) if dur[1] else 0)} minutes",
        "published_in": _publish_date(today, age) if age else "",
    }


def parse_youtube_video_list(html_path: str) -> pd.DataFrame:
    today = date.today()
    with open(html_path, encoding="utf-8") as fp:
        soup = BeautifulSoup(fp.read(), "html.parser")

    anchors = soup.findAll("a", id="video-title")
    return pd.DataFrame([_parse_youtube_anchor(today, a) for a in anchors])
