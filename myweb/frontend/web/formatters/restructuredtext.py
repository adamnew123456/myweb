"""
Processes articles composed as restructuredtext via docutils.
"""

import docutils.core
import io
import urllib.parse

from myweb.backend import utils

def to_html(article_text, backlinks):
    """
    Converts the article to HTML, using restructuredtext as an intermediary.
    """
    rest_buffer = io.StringIO()

    for chunk in utils.get_link_chunks(article_text):
        if isinstance(chunk, utils.Text):
            print(chunk.text, end='', file=rest_buffer)
        else:
            print('`{title} <{url}>`_'.format(
                        url=urllib.parse.quote(chunk.url, ''),
                        title=chunk.url),
                    end='',
                    file=rest_buffer)

    print('\n\n----------', end='', file=rest_buffer)
    print('\n\n**Backlinks**\n\n', end='', file=rest_buffer)

    for link in backlinks:
        print(' - `{title} <{url_title}>`_'.format(
                    url_title=urllib.parse.quote(link, ''),
                    title=link),
                file=rest_buffer)

    rest_value = rest_buffer.getvalue()
    return str(docutils.core.publish_string(rest_value, writer_name='html'), 'utf-8')
