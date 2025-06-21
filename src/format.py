from datetime import timedelta
from typing import Literal


def format_short_time(
    time: float | timedelta,
    decimals: int | Literal["raw"] = "raw",
    decimals_if_only_seconds: int | Literal["raw"] | None = None,
) -> str:
    cur_time = time if isinstance(time, timedelta) else timedelta(seconds=time)

    def resolve_decimals(decimals: int):
        return decimals if decimals != 0 else None

    if cur_time.total_seconds() < 60:
        target_decimals = (
            decimals_if_only_seconds
            if decimals_if_only_seconds is not None
            else decimals
        )

        seconds = cur_time.total_seconds()

        if target_decimals != "raw":
            seconds = min(round(seconds, resolve_decimals(target_decimals)), 60)

        return "1:00" if seconds == 60 else f"{seconds}s"

    mm, ss = divmod(cur_time.seconds, 60)
    hh, mm = divmod(mm, 60)

    ss += cur_time.microseconds / 10**6

    if decimals != "raw":
        ss = round(ss, resolve_decimals(decimals))

    if hh > 0:
        return f"{hh}:{mm:02d}:{ss}"

    return f"{mm}:{ss}"
