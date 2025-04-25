import tomllib
from shutil import make_archive, move
import os

with open("build.toml", "rb") as filein:
    build = tomllib.load(filein)

    dest_path = os.path.join(os.getcwd(), build["dest"])
    anki_addon_filename = f"{build['addon_name']}.ankiaddon"
    target_path = f"{build['package']['dest']}/{anki_addon_filename}"

    make_archive(target_path, "zip", dest_path)
    move(f"{target_path}.zip", target_path)
