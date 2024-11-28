import logging
from pathlib import Path
from string import Template

import markdown2
import constants as c

log = logging.getLogger(__name__)


def _format_title(raw_title: Path) -> str:
    return raw_title.with_suffix("").name.lower().strip()


def _as_img(md_link: str) -> str:
    p = Path(md_link)
    return f'<img src="{md_link if p.exists() else c.DEFAULT_IMAGE}" alt="{p.name}">'


def parse_markdown(markdown_file: Path, meta_only: bool = False) -> dict:
    log.debug(f"Parsing markdown file: {markdown_file}")
    images_src_path = Path(c.RECIPES_IMAGE_SOURCE_DIR)
    content, images, metadata, in_contents = "", [], {}, False
    with open(markdown_file, "r", encoding="utf-8") as fp:
        for line in fp.readlines():
            if in_contents:
                if line.startswith("![["):
                    image_path = images_src_path.joinpath(line.strip()[3:-2])
                    if image_path.exists():
                        images.append(image_path)
                        content += _as_img(image_path) + "\n"
                else:
                    content += line + "\n"
            elif line.startswith("---") and metadata:
                in_contents = True
                if meta_only:
                    break
            else:
                s = line.split(":")
                if len(s) == 2:
                    metadata[s[0].strip()] = s[1].strip()

    return {
        **metadata,
        **{
            "content": content,
            "title": _format_title(markdown_file),
            "markdown_url": markdown_file.as_uri(),
            "images": images,
        },
    }


def convert_recipe_to_html(markdown_file: str = None, recipe_data: dict = None) -> str:
    """Convert a recipe from markdown format (as a file or parsed dict) into html

    Args:
        markdown_file (str): path to the markdown file containing the recipe
        recipe_data (dict, optional): dictionary containing parsed recipe

    Returns:
        str: html string of the content
    """
    assert markdown_file or recipe_data
    if markdown_file:
        recipe_data = parse_markdown(markdown_file)

    # Convert Markdown to HTML
    html_content = markdown2.markdown(recipe_data["content"], extras=["tables"])

    with open(c.RECIPE_HTML_TEMPLATE, "r", encoding="utf-8") as fp:
        return Template(fp.read()).safe_substitute(
            title=recipe_data.get("title", ""),
            cuisine=recipe_data.get("cuisine", ""),
            category=recipe_data.get("category", ""),
            servings=recipe_data.get("servings", "").replace('"', ""),
            content=html_content,
        )


def as_html_file(output_path: Path, markdown_file: str = None, recipe_data: dict = None) -> Path:
    """Convert a recipe from markdown format (as a file or parsed dict) into html, optionally saving as a file

    Args:
        output_path (pathlib.Path): path to which the resulting html is written
        markdown_file (str): path to the markdown file containing the recipe
        recipe_data (dict, optional): dictionary containing parsed recipe

    Returns:
        Path: path to html file if successfully created, otherwise None
    """
    html = convert_recipe_to_html(markdown_file=markdown_file, recipe_data=recipe_data)
    try:
        with open(output_path, "w", encoding="utf-8") as fp:
            fp.write(html)
            log.debug(f"Successfully generated recipe html file: {output_path}")
            return output_path
    except Exception as ex:
        log.error(f"Error during html file creation for {markdown_file}.\n\n{ex}")
    return html
