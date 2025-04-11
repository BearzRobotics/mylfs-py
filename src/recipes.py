# SPDX-License-Identifier: GPL-2.0-only
#
# Copyright (C) 2025 Dakota James Owen Keeler
#
# This file is part of mylfs-py.
#
# mylfs-py is free software: you can redistribute it and/or modify
# it under the terms of version 2 of the GNU General Public License
# as published by the Free Software Foundation.
#
# mylfs-py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from dataclasses import dataclass, field
from typing import List, Optional
import shutil
import requests
from pathlib import Path
import hashlib
import re


# 3rd party
import yaml

# My local imports
from config import GlobalConfig
from util import ConsoleMSG 

@dataclass
class Recipe:
    name: str
    version: str
    
    license: Optional[str] = None
    buildsystem: Optional[str] = None
    tarball_name: Optional[str] = None
    tarball_path: Optional[str] = None
    release: Optional[str] = None
    urls: Optional[str] = field(default_factory=list)
    sha256: Optional[str] = None
    summary: Optional[str] = None
    homepage: Optional[str] = None
    description: Optional[str] = None
    phase: Optional[str] = None
    order: Optional[int] = None
    critical: bool = False
    builddeps: List[str] = field(default_factory=list)
    rundeps: List[str] = field(default_factory=list)
    buildsteps: Optional[str] = None
    cleanup: bool = True
    recipe_source: Optional[str] = None


# I tried to automate this loop -- come back to later
# from the import re
# this can be expanded later - if needed
def expandBuildStep(old_text: str, data: dict) -> str:
    # Replace known placeholders
    result = old_text
    for key in ["version", "name"]:
        placeholder = r"\{" + key + r"\}"
        if key in data:
            result = re.sub(placeholder, str(data[key]), result)
    return result


def load_recipe(template_path: Path, config: GlobalConfig) -> Recipe:
    with template_path.open("r") as f:
        data = yaml.safe_load(f)

    name = data["name"]
    version = data["version"]
    urls = data.get("url")
    if isinstance(urls, str):
        urls = [urls]
    elif urls is None:
        urls = []

    tarball_names = [Path(u).name for u in urls]
    main_tarball_name = tarball_names[0] if tarball_names else None
    main_tarball_path = (template_path.parent / main_tarball_name) if main_tarball_name else None

    if (config.debug):
        print(f"load_recipe: {tarball_names}")
        print(f"load_recipe: {main_tarball_name}")
        print(f"load_recipe: {main_tarball_path}")


    
    
    # set recipe_root path. If there is a url it points to source if not it points to static.
    # source is created with untaring the archive. -- static must be provided by the packager

    

    recipe_dir = Path(template_path.parent)
    rSource = recipe_dir / ("source" if urls else "static")
    
    if (config.debug):
        print(f"load_recipe: {recipe_dir}")
        print(f"load_recipe: {rSource}")

    return Recipe(
        name=name,
        version=version,
        license=data.get("license"),
        buildsystem=data.get("buildsystem"),
        tarball_name=main_tarball_name,
        tarball_path=str(main_tarball_path) if main_tarball_path else None,
        release=data.get("release"),
        urls=urls,
        sha256=data.get("sha256"),
        summary=data.get("summary"),
        homepage=data.get("homepage"),
        description=data.get("description"),
        phase=data.get("phase"),
        order=data.get("order"),
        critical=data.get("critical", False),
        builddeps=data.get("builddeps", []),
        rundeps=data.get("rundeps", []),
        buildsteps=expandBuildStep(data.get("buildsteps"), data),
        cleanup=data.get("cleanup", True),
        recipe_source=rSource, 
    )

def load_all_recipes(config: GlobalConfig) -> List[Recipe]:
    recipes = []
    root = Path(config.recipes_path)

    for template_path in root.rglob("template.yml"):
        try:
            recipe = load_recipe(template_path, config)
            recipes.append(recipe)
        except Exception as e:
            ConsoleMSG.failed(f"Failed to load recipe {template_path}: {e}")

    return recipes

# This function copies the recipe path given to inside the 
# build_path given. by defualt recipes/ mnt/lfs/
def recipes_to_builddir(config: GlobalConfig):
    chroot_recipes = Path(config.build_path) / "recipes"
    source_recipes = Path(config.recipes_path)

    if chroot_recipes.exists():
        shutil.rmtree(chroot_recipes)

    shutil.copytree(source_recipes, chroot_recipes)
    
def initialize_recipes(config):
    source_recipes = Path(config.recipes_path).resolve()
    target_recipes = Path(config.build_path) / "recipes"

    print(f"Initializing recipes from {source_recipes}")

    for template in source_recipes.rglob("template.yml"):
        recipe_dir = template.parent
        with open(template) as f:
            data = yaml.safe_load(f)

        urls = data.get("url")
        if isinstance(urls, str):
            urls = [urls]
        elif urls is None:
            urls = []

        for url in urls:
            tarball_name = Path(url).name
            tarball_path = recipe_dir / tarball_name

            if not tarball_path.exists():
                print(f"Downloading {tarball_name} to {recipe_dir}...")
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    with open(tarball_path, "wb") as f:
                        f.write(response.content)
                    print(f"Saved to {tarball_path}")
                except Exception as e:
                    ConsoleMSG.failed(f"Failed to download {url}: {e}")
            else:
                if (config.debug):
                    print(f"{tarball_name} already exists — skipping.")


    # Copy the entire recipes tree to the build path
    if target_recipes.exists():
        shutil.rmtree(target_recipes)
    shutil.copytree(source_recipes, target_recipes)

    # Update config to point to the build copy
    config.recipes_path = str(target_recipes)
