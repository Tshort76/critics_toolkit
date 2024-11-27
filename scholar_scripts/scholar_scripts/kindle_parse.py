import re
from operator import itemgetter
from pathlib import Path

import toolz as tz

HLITE_PAGE_RGX = re.compile(r"Page: (\d+)")
CLIPPINGS_PAGE_RGX = re.compile(r"page (\d+)")


def parse_highlight_file(filepath: Path) -> list[dict]:
    notes, note = [], {}
    with filepath.open(mode="r", encoding="utf-8") as fp:
        for line in fp.readlines():
            if "highlight |" in line:
                notes.append(note)
                note = {}
                if m := HLITE_PAGE_RGX.findall(line):
                    note["page"] = int(m[0])
            elif "text" not in note:
                note["text"] = line.strip()
            elif line and line.startswith("Note:"):
                note["note"] = line[5:].strip()

    return notes[1:]


# note is coming before the highlighted text
def parse_myclippings_file(my_clippings_path: Path) -> dict[str, list[dict]]:
    notes = []
    with my_clippings_path.open(mode="r", encoding="utf-8") as fp:
        blob, type_, bdepth = {}, None, 0
        for raw_line in fp.readlines():
            if raw_line.startswith("=========="):
                bdepth = 0
                if type_ != "note":  # notes precede highlighted text and I want to group them
                    notes.append(blob)
                    blob = {}
            else:
                if line := raw_line.strip():
                    bdepth += 1
                    if bdepth == 1:
                        blob["title"] = line.replace("\ufeff", "")
                    elif bdepth == 2:
                        type_ = "highlight" if "Highlight" in raw_line else "note"
                        if pg := CLIPPINGS_PAGE_RGX.findall(line):
                            blob["page"] = int(pg[0])
                    else:
                        blob["note" if type_ == "note" else "text"] = line

    return tz.groupby(itemgetter("title"), notes)


def write_to_file(output: Path, notes: list[dict]) -> None:
    """write notes to a text file for easy copy and paste.

    Args:
        output (Path): Output filepath for writing
        notes (list[dict]): notes containing 'text' with optional 'note'

    If a 'note' exists for a text item, the text is printed with a 'note:' line below
    """
    s = ""
    for n in notes:
        nt = f"\nnote: {n['note']}" if n.get("note") else ""
        s += f"{n['text']}  {nt}  \n\n"

    output.write_text(s, encoding="utf-8")
