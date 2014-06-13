"""
A web interface to the myweb database.

This is to make it easy to use myweb without having to open an external
application.

Note that, if you want to, you can use this with mod_wsgi instead of the
builtin wsgiref server.
"""

import html
import json
import urllib.parse
from wsgiref import simple_server

from myweb.backend import db, query, utils
from myweb.frontend.web_code import *

def make_headers(header_dict):
    """
    Creates a list of headers for WSGI from a dict.
    """
    # Note: WSGI accepts headers in the form:
    #
    #    [ (header_a, value_a), (header_b, value_b), ...]
    headers = []
    for header_name in header_dict:
        header_raw_value = header_dict[header_name]

        if isinstance(header_raw_value, (list, tuple)):
            # If a list-like object is given, that means we should send multiple
            # values for the same header
            for header_value in header_raw_value:
                headers.append((header_name, str(header_value)))
        else:
            headers.append(header_name, str(header_raw_value))

    return headers

def process_article_to_html(article_text, backlinks):
    """
    Produces HTML from an article, and its list of backlinks.
    """
    article_html = ""

    for chunk in utils.get_link_chunks(article_text):
        if isinstance(chunk, utils.Text):
            article_html += html.escape(chunk.text)
        else:
            article_html += '<a href="/view/{url_title}"> {title} </a>'.format(
                url_title=urllib.parse.quote(chunk.url), title=chunk.url)

    article_html += '<hr/><ul>'
    for link in backlinks:
        article_html += '<li><a href="/view/{url_title}"> {title} </a></li>'.format(
            url_title=urllib.parse.quote(link), title=link)
    article_html += '</ul>'
        
    return article_html

def generate_404(environ, start_response):
    """
    Generates an error when loading a nonexistent page.
    """
    start_response('404 NOT FOUND',
            make_headers({
                'Content-Length': len(NOT_FOUND_PAGE),
                'Content-Type': 'text/plain'
            }))
    return [NOT_FOUND_PAGE]

def generate_html_page(page_data):
    """
    Generates a function which returns the HTML for a page.
    """
    def page_maker(environ, start_response):
        start_response('200 OK',
                make_headers{(
                    'Content-Length': len((page_data),
                    'Content-Type': 'text/html'
                }))
        return [page_data]
    return page_maker

generate_search_page = generate_html_page(SEARCH_PAGE)
generate_new_page = generate_html_page(NEW_PAGE)
generate_edit_page = generate_html_page(EDIT_PAGE)
generate_view_page = generate_html_page(VIEW_PAGE)

def handle_ajax_request(environ, start_response):
    """
    Handles requests sent by the web browser.

    This function takes in a JSON request, and emits JSON as a result.
    """
    path_parts = environ['PATH_INFO'].split('/')
    ajax_request = path_parts[1]

    # All requests must provide some form of input - if there isn't any, then 
    content_length = environ.get('CONTENT_LENGTH', 0)
    if content_length == 0:
        result = None
    else:
        utf8_input = str(environ['wsgi.input'].read(), 'utf-8')
        request_body = json.loads(utf8_input)

        if ajax_request == 'query':
            # The /ajax/query request take in JSON of the following form:
            #
            #  { "query": "..." }
            #
            # It produces JSON of the following form:
            #
            #  { "was-error": true, "articles": []} or
            #  { "was-error": false, "articles": [...]}
            query_text = request_body['query']
            try:
                parsed_query = query.parse_query(query_text)
                result = list(db.execute_query(parsed))
            except SyntaxError:
                result = []
        elif ajax_request == 'get-aritcle':
            # The /ajax/get-article request takes in JSON of the following form:
            #
            # {"uri": "..."}
            #
            # It produces JSON of the following form:
            #
            #  {"was-error": true} or
            #  {"was-error": false, "raw-content": "...", "html-content": "...", 
            #       "tags": [...]}
            #
            # Note that the "html-content" field is in fact HTML, and the links
            # and backlinks are pre-processed by the server. Thus, the result 
            # can be easily inserted into a <div>, while "raw-content" is not 
            # processed and is intended to be used for editing.
            article_uri = request_body['uri']

            try:
                article = db.get_article(article_uri)
                result = {
                    'raw-content': article.content,
                    'html-content': process_article_to_html(article.content, article.backlinks),
                    'backlinks': list(article.backlinks),
                    'tags': list(article.tags)}
            except IOError:
                result = {'was-error': True}
        elif ajax_request == 'submit-new':
            # The /ajax/submit-new requests takes in JSON of the following form:
            #
            # {"uri": "...", "content": "...", "tags": [...]}
            #
            # It produces JSON of the following form:
            #
            #  {"was-error": true} or {"was-error": false}
            article_uri = request_body['uri']
            article_content = request_body['content']
            article_tags = set(request_body['tags'])
            article_links = utils.get_links(article_content)

            try:
                db.create_article(article_url, article_content,
                        article_links, article_tags)
                result = {'was-error': False}
            except IOError:
                result = {'was-error': True}
        elif ajax_request == 'submit-edit':
            # The /ajax/submit-edit requests takes in JSON of the following form:
            #
            # {"uri": "...", "content": "...", "tags": [...]}
            #
            # It produces JSON of the following form:
            #
            #  {"was-error": true} or {"was-error": false}
            article_uri = request_body['uri']
            article_content = request_body['content']
            article_tags = set(request_body['tags'])
            article_links = utils.get_links(article_content)

            try:
                db.update_article(article_url, article_content,
                        article_links, article_tags)
                result = {'was-error': False}
            except IOError:
                result = {'was-error': True}
        elif ajax_request = 'submit-delete':
            # The /ajax/submit-delete requests takes in JSON of the following form:
            #
            # {"uri": "..."}
            #
            # It produces JSON of the following form:
            #
            #  {"was-error": true} or {"was-error": false}
            article_uri = request_body['uri']
            try:
                db.delete_article(article_uri)
                result = {'was-error': False}
            except IOError:
                result = {'was-error': True}
        else:
            result = None

    json_response = bytes(json.dumps(result), 'utf-8')
    start_response('200 OK', 
            make_headers({
                'Content-Length': len(json_response),
                'Content-Type': 'application/json'
            }))

    return [json_response]

def application(environ, start_response):
    """
    Handles web requests.
    """

    """
    The 'site map' looks like the following:

    |- /new
    |- /edit/{urlencoded-title}
    |- /view/{urlencoded-title}
    \- /ajax
     |- /ajax/query {does searches based upon a query}
     |- /ajax/get-article {gets all the information about an article}
     |- /ajax/submit-new {submits a new article}
     |- /ajax/submit-edit {submits a new version of an article}
     \- /ajax/submit-delete {deletes an existing article}
    """

    if environ['PATH_INFO'] == '/':
        return generate_search_page(environ, start_response)
    elif environ['PATH_INFO'] == '/new':
        return generate_new_page(environ, start_response)
    elif environ['PATH_INFO'] == '/edit':
        return generate_edit_page(environ, start_response)
    elif environ['PATH_INFO'].startswith('/view'):
        return generate_view_page(environ, start_response)
    elif environ['PATH_INFO'].startswith('/ajax'):
        return handle_ajax_request(envirion, start_response)
    else:
        return generate_404(environ, start_response)

def main():
    http = simple_server.make_server('', 8080, application)
