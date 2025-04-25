import tomllib
import shutil
import os

with open("config.toml", "rb") as filein:
    config = tomllib.load(filein)

    dest_path = os.path.join(os.getcwd(), config["strip-types"]["dest"])
    addon_dir = os.path.join(config["anki_addon_dir"], config["addon_name"])

    for root, dirs, files in os.walk(addon_dir):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

    shutil.copytree(dest_path, addon_dir, dirs_exist_ok=True)
