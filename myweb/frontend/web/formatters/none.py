"""
A plain-HTML formatter which only formats links.
"""
import io
import html
import urllib.parse

from myweb.backend import utils

def to_html(article_text, backlinks):
    """
    Converts an article into simple HTML.
    """
    html_buffer = io.StringIO()

    print('<pre>', end='', file=html_buffer)
    for chunk in utils.get_link_chunks(article_text):
        if isinstance(chunk, utils.Text):
            print(html.escape(chunk.text), end='', file=html_buffer)
        else:
            print('<a href="/view/{}">'.format(
                        urllib.parse.quote(chunk.url, '')),
                    end='', file=html_buffer)

            print(chunk.url, '</a>', end='', file=html_buffer)

    print('<hr/><ul>', end='', file=html_buffer)
    for link in backlinks:
        print('<li>', end='', file=html_buffer)
        print('<a href="/view/{}">'.format(urllib.parse.quote(link, '')),
                end='', file=html_buffer)
        print(link, '</a></li>', end='', file=html_buffer)

    print('</ul></pre>', end='', file=html_buffer)
    return html_buffer.getvalue()
