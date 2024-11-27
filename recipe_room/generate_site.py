import logging
import json
from pathlib import Path
from string import Template
import toolz as tz
from typing import Union

import markdown_parse as md
import constants as c

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

CACHE_PATH = Path(c.RECIPES_META_CACHE)


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Path):
            return str(obj)
        return super().default(obj)


def _build_recipe_cell(data: dict) -> str:
    title, cuisine = data["title"], data.get("cuisine", "")
    image = next(iter(data.get("images", [])), None)
    image = image if Path(image).exists() else c.DEFAULT_IMAGE
    border_color = c.CUISINE_COLORS.get(cuisine, "#e9f9fb")
    return f"""
        <div class="recipe-card" style="border-color: {border_color};" recipe-name="{title}" recipe-cuisine="{cuisine.lower()}" recipe-category="{data.get('category','').lower()}">
            <a href="{data['html_url']}">
                <img src="{image}" alt="{title}">
                <div class="caption">{title}</div>
            </a>
        </div>
        """


def build_html_grid(recipes: list[dict]) -> str:

    grid_contents = ""
    for d in recipes:
        grid_contents += _build_recipe_cell(d)

    with open("resources/template_grid_view.html", "r", encoding="utf-8") as fp:
        return Template(fp.read()).safe_substitute(grid_contents=grid_contents)


# Main function to read the markdown files and generate the HTML page
def generate_recipe_grid_html(recipes_folder: Path = None, recipes_data: list[dict] = None) -> str:
    if recipes_folder:
        recipes_data = [md.parse_markdown(x) for x in sorted(recipes_folder.glob("*.md"))]
    html_content = build_html_grid(recipes_data)

    # Write the HTML content to the output file
    with open(c.OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    return c.OUTPUT_HTML


def _rename_to_html(s: Path) -> str:
    return s.with_suffix(".html").name.lower().replace(" ", "_").strip()


def _update_cache(recipes: dict):
    with open(CACHE_PATH, mode="w", encoding="utf-8") as fp:
        json.dump({k: tz.dissoc(v, "content") for k, v in recipes.items()}, fp, cls=JsonEncoder, indent=2)


def _if_stale(recipe_file: Path, html_path: Path, cache: dict) -> float:
    last_modified = recipe_file.stat().st_mtime
    if last_modified != tz.get_in([recipe_file.name, "last_modified_at"], cache, 0.0):
        return last_modified
    if not html_path.exists():
        return last_modified


def build_site(recipes_md_folder: Union[Path, str]):
    if isinstance(recipes_md_folder, str):
        recipes_md_folder = Path(recipes_md_folder)
    recipes_html_path = Path(c.RECIPE_HTML_DIR)
    recipes_html_path.mkdir(parents=True, exist_ok=True)
    Path(c.RECIPE_IMAGES_DIR).mkdir(parents=True, exist_ok=True)

    recipes_data = {}
    if CACHE_PATH.exists():
        with open(CACHE_PATH, "r", encoding="utf-8") as fp:
            recipes_data = json.load(fp)

    for recipe_file in sorted(recipes_md_folder.glob("*.md")):
        html_path = recipes_html_path.joinpath(_rename_to_html(recipe_file))
        if last_modified := _if_stale(recipe_file, html_path, recipes_data):
            recipes_data[recipe_file.name] = md.parse_markdown(recipe_file)
            md.as_html_file(output_path=html_path, recipe_data=recipes_data[recipe_file.name])
            # TODO copy images to FOLDER_RECIPE_IMAGES
            recipes_data[recipe_file.name]["html_url"] = str(html_path)
            recipes_data[recipe_file.name]["last_modified_at"] = last_modified  # or check file hash ...
        else:
            log.info(f"No changes to {recipe_file.name} , skipping")
        break

    generate_recipe_grid_html(recipes_data=list(recipes_data.values()))
    _update_cache(recipes_data)


# Run the script
if __name__ == "__main__":
    # f = generate_recipe_grid_html(Path(c.RECIPE_MARKDOWN_DIR))
    # log.info(f"GENERATED FILE: {f}")
    build_site(Path(c.RECIPE_MARKDOWN_DIR))
