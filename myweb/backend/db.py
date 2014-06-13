"""
An interface on top of a database, which stores articles along with associated
metadata.
"""

from collections import namedtuple
import os
import os.path
import sqlite3
import sys
import zlib

import myweb.backend.query as query
import myweb.backend.utils as utils

# The connected database - there's meant to be only one, which is why this is a
# module and not a class
DB = None
CURSOR = None

# The default database path, which can be passed to `load_database'
if 'HOME' in os.environ: # Unix-likes
    DEFAULT_DB = os.path.join(os.environ['HOME'], '.myweb')
elif 'AppData' in os.environ: # Windows
    DEFAULT_DB = os.path.join(os.environ['AppData'], 'myweb.sqlite')
else:
    print('Cannot find suitable location for database - set either $HOME or %APPDATA%')
    sys.exit(1)

# How much to compress the article data by
COMPRESS = 6

# How to package results returned by 'get_article'
Article = namedtuple('Article',
        ['url', 'content', 'links', 'backlinks', 'tags'])

class Queries:
    "Longer queries are stored here, rather than inline, for readability"
    create_article_table = '''
CREATE TABLE IF NOT EXISTS ARTICLES(Url STRING PRIMARY KEY, 
        Article BLOB, 
        Domain STRING)'''
    create_links_table = '''
CREATE TABLE IF NOT EXISTS LINKS(Url STRING, Linked STRING, 
        PRIMARY KEY (Url, Linked))'''
    create_tags_table = '''
CREATE TABLE IF NOT EXISTS TAGS(Url STRING, Tag STRING, 
        PRIMARY KEY (Url, Tag))'''
    search_base_query = '''
SELECT ARTICLES.Url FROM ARTICLES 
WHERE '''
    count_matching_urls = '''
SELECT COUNT(Articles.Url) FROM ARTICLES WHERE Url = ?'''
    check_tag = '''
EXISTS (SELECT 1 FROM TAGS WHERE Tag = ? AND Url = ARTICLES.Url)'''
    check_domain = '''
ARTICLES.Domain = ?'''
    check_links = '''
EXISTS (SELECT 1 FROM LINKS WHERE Linked = ? AND Url = ARTICLES.Url)'''
    check_linked = '''
EXISTS (SELECT 1 FROM LINKS WHERE Url = ? AND Linked = ARTICLES.Url)'''
    check_url = '''
ARTICLES.Url = ?'''

def load_database(path):
    """
    Loads the database from a file, which is then used for the whole module.
    @note The globals `DB` and `CURSOR` are configured here.
    """
    global DB
    DB = sqlite3.connect(path)

    global CURSOR
    CURSOR = DB.cursor()

    # Create the requisite tables - the tables are documented in schema.markdown
    # for the relationships and meaning between these tables.
    CURSOR.execute(Queries.create_article_table)
    CURSOR.execute(Queries.create_links_table)
    CURSOR.execute(Queries.create_tags_table)

def sql_from_query(query_node):
    """
    Outputs templated SQL, as well as the list of templates to fill them.
    The return value is a tuple:
     - The raw SQL to insert
     - The variables to add to the query formatter
    """
    simple_types = {
        query.Tag: (Queries.check_tag, 'tag'),
        query.Domain: (Queries.check_domain, 'domain'),
        query.Links: (Queries.check_links, 'url'),
        query.LinkedBy: (Queries.check_linked, 'url'),
        query.Url: (Queries.check_url, 'url')
    }

    if isinstance(query_node, tuple(simple_types)):
        query_template, attr_name = simple_types[type(query_node)]
        attr_value = getattr(query_node, attr_name)
        return (query_template, (attr_value,))
    elif isinstance(query_node, query.And):
        sql_1, variables_1 = sql_from_query(query_node.oper_1)
        sql_2, variables_2 = sql_from_query(query_node.oper_2)
        return ('({query1}) AND ({query2})'.format(
                    query1=sql_1, query2=sql_2),
                variables_1 + variables_2)
    elif isinstance(query_node, query.Or):
        sql_1, variables_1 = sql_from_query(query_node.oper_1)
        sql_2, variables_2 = sql_from_query(query_node.oper_2)
        return ('({query1}) OR ({query2})'.format(
                    query1=sql_1, query2=sql_2),
                variables_1 + variables_2)
    elif isinstance(query_node, query.Not):
        sql, variables = sql_from_query(query_node.expr)
        return ('NOT (' + sql + ')', variables)

def execute_query(query_tree):
    """
    Processes a query tree, returning a list of eligible URIs.
    """
    # Introduce the proper tables into the query before passing it off to
    # the query->sql converter
    base_query = Queries.search_base_query
    sql, variables = sql_from_query(query_tree)
    results = set(row[0] for row in DB.execute(base_query + sql, variables))
    return results

def create_article(url, content, links, tags):
    """
    Inserts a new article in the database.
    @raise KeyError If the article exists already.
    """
    url = utils.normalize_url(url)
    # First, ensure that no article by the given URI exists in the database
    # already
    count_set = set(row[0] for row in
            CURSOR.execute(Queries.count_matching_urls, (url,)))
    if count_set.pop() > 0:
        raise KeyError('Already have article about ' + url)

    content_bytes = bytes(content, 'utf-8')
    CURSOR.execute('INSERT INTO ARTICLES VALUES (?, ?, ?)',
        (url, zlib.compress(content_bytes, COMPRESS), utils.get_domain(url)))

    for link in links:
        CURSOR.execute('INSERT INTO LINKS VALUES (?, ?)', (url, link))

    for tag in tags:
        CURSOR.execute('INSERT INTO TAGS VALUES (?, ?)', (url, tag))

    DB.commit()

def update_multimap_table(url, table, column, values):
    """
    Updates a one-to-many table, by setting a list of values to a URI.

    This routine is meant to do this intelligently, by calculating the
    difference between the existing values and the new set of values, and
    adding/deleting as little as possible.
    """
    # First, figure out what rows are already in the DB
    existing_values = set(row[0] for row in
        CURSOR.execute('SELECT {} FROM {} WHERE Url = ?'.format(column, table),
            (url,)))

    # Then, get the difference between existing values and what should/should
    # not be in the table
    to_add = values - existing_values
    to_remove = existing_values - values

    # Finally, do the insertions/removals
    for val in to_add:
        CURSOR.execute('INSERT INTO {} VALUES (?, ?)'.format(table, column),
            (url, val))

    for val in to_remove:
        CURSOR.execute(
            'DELETE FROM {} WHERE Url = ? AND {} = ?'.format(table, column),
            (url, val))

def update_article(url, content, links, tags):
    """
    Updates an existing article in the database.
    @note Both links and tags must each be a set()
    @raise KeyError If the article doesn't yet exist.
    """
    url = utils.normalize_url(url)
    # First, ensure that 1 article by the given URI exists in the database
    # already
    count_set = set(row[0] for row in
            CURSOR.execute(Queries.count_matching_urls, (url,)))

    if count_set.pop() != 1:
        raise KeyError('Database has no article about ' + url)

    content_bytes = bytes(content, 'utf-8')
    CURSOR.execute('UPDATE ARTICLES SET Article = ? WHERE Url = ?',
        (zlib.compress(content_bytes, COMPRESS), url))

    # Update the tag/links tables
    update_multimap_table(url, 'TAGS', 'Tag', tags)
    update_multimap_table(url, 'LINKS', 'Linked', links)

    DB.commit()

def get_article(url):
    """
    Gets the content of an article, as an Article object.
    @raise KeyError If the article doesn't exist.
    """
    url = utils.normalize_url(url)
    # Get the content, and convert it from zlib compressed bytes to UTF-8
    try:
        article_row = next(
            CURSOR.execute('SELECT Article FROM ARTICLES WHERE Url = ?',
                (url,)))
        zlib_content_bytes = article_row[0]
    except StopIteration:
        raise KeyError('Database has no article about ' + url)

    content_bytes = zlib.decompress(zlib_content_bytes)
    content = content_bytes.decode('utf-8')

    # Get all the tags and links for the article
    tags = set(row[0] for row in
        CURSOR.execute('SELECT Tag FROM TAGS WHERE Url = ?', (url,)))
    links = set(row[0] for row in
        CURSOR.execute('SELECT Linked FROM LINKS WHERE Url = ?', (url,)))
    backlinks = set(row[0] for row in
        CURSOR.execute('SELECT Url FROM LINKS WHERE Linked = ?', (url,)))

    return Article(url, content, links, backlinks, tags)

def delete_article(url):
    """
    Deletes the article, along with its tags and links.
    """
    url = utils.normalize_url(url)
    CURSOR.execute('DELETE FROM ARTICLES WHERE Url = ?', (url,))
    CURSOR.execute('DELETE FROM TAGS WHERE Url = ?', (url,))
    CURSOR.execute('DELETE FROM LINKS WHERE Url = ?', (url,))

    DB.commit()
