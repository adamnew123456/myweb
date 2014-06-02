"""
Utilities which are common to multiple modules.
"""
from collections import namedtuple
import re
from urllib.parse import urlparse

URL_REGEX = re.compile(r'\[\[[^\]]+\]\]')

# Types used to indicate the return value of `get_list_chunks`
Link = namedtuple('Link', ['url'])
Text = namedtuple('Text', ['text'])

def normalize_url(url):
    """
    Normalizes a URL by stripping the terminating '/'.
    """
    while url.endswith('/'):
        url = url[:-1]
    return url

def get_domain(url):
    """
    Gets the domain of the given URL.
    """
    parsed_url = urlparse(normalize_url(url))
    return parsed_url.netloc

def get_links(text):
    """
    Parses out a list of links from a piece of text, returning a set of URLs.
    """
    urls = URL_REGEX.findall(text)
    return set(normalize_url(url[2:-2]) for url in urls)

def get_link_chunks(text):
    """
    Gets a list of elements, where each is either a:

     - Link
     - Text
    """
    items = []
    while text:
        match = URL_REGEX.search(text)

        # No match indicates that there isn't a link in the remaining text;
        # store it as a single Text node
        if match is None:
            items.append(Text(text))
            text = ''
        else:
            # First, get all the pre-link text in as a Text node
            link_start, link_end = match.span()
            pre_link = text[:link_start]
            items.append(Text(pre_link))

            # Then, get the link text
            link = text[link_start:link_end]
            raw_link = link[2:-2]
            items.append(Link(normalize_url(raw_link)))

            # Finally, strip off everything we just consumed
            text = text[link_end:]

    return items
