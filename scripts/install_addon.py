import tomllib
import shutil
import os

with open("config.toml", "rb") as config_data:
    with open("build.toml", "rb") as build_data:
        config = tomllib.load(config_data)
        build = tomllib.load(build_data)

        dest_path = os.path.join(os.getcwd(), build["dest"])
        addon_dir = os.path.join(config["anki_addon_dir"], build["addon_name"])

        for root, dirs, files in os.walk(addon_dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

        shutil.copytree(dest_path, addon_dir, dirs_exist_ok=True)
