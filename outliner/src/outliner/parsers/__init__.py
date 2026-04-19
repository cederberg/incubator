from . import rst, markdown

# Ordered: more specific parsers before catch-all parsers
_PARSERS = [rst, markdown]


def get_parser(syntax: str):
    for mod in _PARSERS:
        if mod.SYNTAX == syntax:
            return mod.parse
    return None
