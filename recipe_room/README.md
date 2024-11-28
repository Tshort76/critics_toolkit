# Recipe Room
A little library for reading my recipes from Obsidian and converting them into a static webpage

## Usage
Setup your environment variables:
```
RECIPES_MARKDOWN_DIR="resources/recipes"
RECIPES_IMAGE_DIR="resources/images"
```

From the project root, `tl_toolkit/recipe_room`, start your virtual environment and generate the site by running `python generate_site.py`.

This will convert the markdown files from RECIPES_MARKDOWN_DIR into HTML files in an `assets` folder, copying their images to a local `asset` folder, and then generating a `recipes.html` file.  This file plus the assets folder functions as a usable UI with a browser.  I update them to Gdrive (`recipe.html` and your `assets` folder should be at the same directory level).