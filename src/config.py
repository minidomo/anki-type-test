from typing import Any, cast
from aqt import mw


def _config():
    return cast(dict[str, Any], mw.addonManager.getConfig(__name__))


def stat_display_limit() -> int:
    return _config()["stat_display_limit"]


def word_stat_color_letter_correct() -> str:
    return _config()["word_stat.color.letter_correct"]


def word_stat_color_letter_incorrect() -> str:
    return _config()["word_stat.color.letter_incorrect"]


def word_stat_color_letter_missing() -> str:
    return _config()["word_stat.color.letter_missing"]


def word_stat_color_letter_extra() -> str:
    return _config()["word_stat.color.letter_extra"]


def word_stat_color_duration() -> str:
    return _config()["word_stat.color.duration"]
