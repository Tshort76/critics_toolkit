import os
from dotenv import load_dotenv

load_dotenv()

CUISINE_COLORS = {
    "Indian": "#f39735",
    "Mexican": "#a80000",
    "SE_Asian": "#d8c305",
    "Peasant": "#e9e9e9",
    "Italian": "#ffffff",
    "Mediterranean": "#3687e3",
}

RECIPE_HTML_DIR = "assets/recipes"
RECIPE_IMAGES_DIR = "assets/images"

RECIPES_META_CACHE = "resources/cache.json"
RECIPE_MARKDOWN_DIR = os.environ["RECIPES_MARKDOWN_DIR"]
RECIPES_IMAGE_SOURCE_DIR = os.environ["RECIPES_IMAGE_DIR"]
DEFAULT_IMAGE = "resources/image_not_found.jpg"
RECIPE_HTML_TEMPLATE = "resources/template_recipe.html"
OUTPUT_HTML = "recipes.html"
