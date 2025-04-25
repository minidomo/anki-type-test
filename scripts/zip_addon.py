import tomllib
from shutil import make_archive, move
import os

with open("config.toml", "rb") as filein:
    config = tomllib.load(filein)

    dest_path = os.path.join(os.getcwd(), config["build"]["dest"])
    anki_addon_filename = f"{config['addon_name']}.ankiaddon"
    target_path = f"{config['package']['dest']}/{anki_addon_filename}"

    make_archive(target_path, "zip", dest_path)
    move(f"{target_path}.zip", target_path)
