import tomllib
from os import path
from shutil import copy

with open("config.toml", "rb") as file:
    data = tomllib.load(file)

    addon_dir = path.join(data["anki_addon_dir"], data["addon_name"])

    filename = "__init__.py"
    copy(filename, f"{addon_dir}/{filename}")
