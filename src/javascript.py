from typing import Literal

type Position = Literal["beforebegin", "afterbegin", "beforeend", "afterend"]


def func_wrap(js: str):
    return f"(() => {{ {js} }})();"


def async_func_wrap(js: str):
    return f"(async () => {{ {js} }})();"


def insert_html(selector: str, position: Position, html: str):
    return f"document.querySelector({selector}).insertAdjacentHTML('{position}', '{html}');"


def ensure_run_once(id: str):
    return f"""
if (window[_{id}]) return;
window[_{id}] = true;
"""
