from typing import Any, cast
from aqt import mw


def _config():
    return cast(dict[str, Any], mw.addonManager.getConfig(__name__))


def history_limit() -> int:
    return _config()["history_limit"]
