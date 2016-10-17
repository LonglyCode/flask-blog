# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import markdown
from flask import Markup
from pygments.formatters.html import HtmlFormatter

# def force_unicode(value, encoding='utf-8', errors='strict'):
#     """
#     Convert bytes or any other Python instance to string.
#     """
#     if isinstance(value, compat.text_type):
#         return value
#     return value.decode(encoding, errors)


def pygmented_markdown(text, flatpages=None):
    extensions=[]
    if HtmlFormatter is None:
        original_extensions = extensions
        extensions = []

        for extension in original_extensions:
            if extension.startswith('codehilite'):
                continue
            extensions.append(extension)
    elif not extensions:
        extensions = ['codehilite']

    return markdown.markdown(text, extensions)

def pygments_style_defs(style='default'):
    formatter = HtmlFormatter(style=style)
    return formatter.get_style_defs('.codehilite')

def markdown_render(text,codehilite=True):
    exts =[
        'abbr', 'attr_list', 'def_list', 'sane_lists', 'fenced_code',
        'tables', 'toc', 'wikilinks',
    ]

    if codehilite:
        # exts.append('codehilite(guess_lang=True,linenums=True)')
        exts.append('codehilite(guess_lang=True)')

    return Markup(markdown.markdown(
        text,
        extensions=exts,
        safe_mode=False,
    ))

def keywords_split(keywords):
    return keywords.replace(u',', ' ') \
                   .replace(u';', ' ') \
                   .replace('+', ' ') \
                   .replace('；', ' ') \
                   .replace('，', ' ') \
                   .replace('　', ' ') \
                   .split(' ')
