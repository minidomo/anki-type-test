import tomllib
import json
import os
from datetime import datetime

with open("build.toml", "rb") as build_data:
    build = tomllib.load(build_data)

    data = dict(
        package=build["manifest"]["package"],
        name=build["manifest"]["name"],
        mod=int(datetime.now().timestamp()),
    )

    dest_path = os.path.join(os.getcwd(), build["dest"])

    with open(f"{dest_path}/manifest.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
