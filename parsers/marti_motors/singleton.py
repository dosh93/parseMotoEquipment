from parsers.browser_handler import BrowserHandler

_browser_handler_instance = None


def browser_handler():
    global _browser_handler_instance
    if _browser_handler_instance is None:
        _browser_handler_instance = BrowserHandler()
    return _browser_handler_instance
