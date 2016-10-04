# -*- coding: utf-8 -*-

import markdown
from flask import Markup

def markdown_render(text,codehilite=True):
    exts =[
        'abbr', 'attr_list', 'def_list', 'sane_lists', 'fenced_code',
        'tables', 'toc', 'wikilinks',
    ]
    if codehilite:
        exts.append('codehilite(guess_lang=True,linenums=True)')

    return Markup(markdown.markdown(
        text,
        extensions=exts,
        safe_mode=False,
    ))
