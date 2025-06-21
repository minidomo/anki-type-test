from aqt import mw, gui_hooks
from aqt.webview import AnkiWebView, WebContent
from . import javascript

_js: list[str] = []
_css: list[str] = []


def get_web_exports_fnames() -> tuple[list[str], list[str]]:
    addon_package = mw.addonManager.addonFromModule(__name__)

    global _js, _css
    js = [f"/_addons/{addon_package}/{e}" for e in _js]
    css = [f"/_addons/{addon_package}/{e}" for e in _css]
    return (js, css)


def js_insert_web_exports():
    js, css = get_web_exports_fnames()
    js_code = []

    if len(js):
        html = "\n".join(map(mw.web.bundledScript, js))
        js_code.append(javascript.insert_html("body", "beforeend", html))

    if len(css):
        html = "\n".join(map(mw.web.bundledCSS, css))
        js_code.append(javascript.insert_html("head", "beforeend", html))

    return "\n".join(js_code)


def init_web_exports(pattern: str, js: list[str] = [], css: list[str] = []):
    mw.addonManager.setWebExports(__name__, pattern)

    global _js, _css
    _js.extend(js)
    _css.extend(css)

    gui_hooks.webview_did_inject_style_into_page.append(
        _on_webview_did_inject_style_into_page
    )
    gui_hooks.webview_will_set_content.append(_on_webview_will_set_content)


def _on_webview_will_set_content(web_content: WebContent, context: object | None):
    js, css = get_web_exports_fnames()
    web_content.js.extend(js)
    web_content.css.extend(css)


def _on_webview_did_inject_style_into_page(webview: AnkiWebView):
    js = javascript.func_wrap(
        f"{javascript.ensure_run_once('inject-web-exports')} {js_insert_web_exports()}"
    )
    webview.eval(js)
