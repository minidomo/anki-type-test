from aqt import mw

_config = mw.addonManager.getConfig(__name__)
assert _config

history_limit = _config["history_limit"]
