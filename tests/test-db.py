"""
Tests used to make sure that the database layer works as it should.
"""

import myweb.backend.db as db
import myweb.backend.query as query

# The ARTICLES to create initially
ARTICLES = [
    db.Article('http://1.com/a', '1', {'http://1.com/b'}, set(),
            {'tag-1', 'tag-2'}),
    db.Article('http://1.com/b', '2', {'http://1.com/a'}, set(),
            {'tag-2', 'tag-3'})
]

# The ARTICLES to update from the previously article
NEW_ARTICLES = [
    # The idea here is to make sure that:
    #  - The content changes
    #  - The tag and link changing algorithm works
    db.Article('http://1.com/a', '3', set(), {'http://1.com/b'},
            {'tag-1', 'tag-9'}),
]

# The article to delete
DELETE_ARTICLES = [
    'http://1.com/a'
]

# The QUERIES to execute, and their expected results
QUERIES = [
    ('domain:1.com', {'http://1.com/a', 'http://1.com/b'}),
    ('links:http://1.com/a', {'http://1.com/b'}),
    ('linked:http://1.com/a', {'http://1.com/b'}),
    ('tag-1 OR tag-3', {'http://1.com/a', 'http://1.com/b'}),
    ('tag-1 AND tag-3', set()),
    ('NOT tag-1', {'http://1.com/b'}),
    ('url:http://1.com/b', {'http://1.com/b'})
]

db.load_database(':memory:')

# First, add the ARTICLES so we can test the QUERIES
for article in ARTICLES:
    db.create_article(article.url, article.content, article.links, article.tags)

# Then, go ahead and execute all the QUERIES and test their results
for the_query, answer in QUERIES:
    parsed_query = query.parse_query(the_query)
    result = db.execute_query(parsed_query)
    if result != answer:
        print('=== Query matching failed ===')
        print('Query:', the_query)
        print('Parsed Query:', query.node_to_string(parsed_query))
        sql, variables = db.sql_from_query(parsed_query)
        print('SQL:', sql)
        print('Variables:', variables)
        print('*' * 5)
        print('Expected Answer:', answer)
        print('Actual Answer:', result)
        assert False

# Update some ARTICLES
for article in NEW_ARTICLES:
    db.update_article(article.url, article.content, article.links, article.tags)
    new_article = db.get_article(article.url)

    if article != new_article:
        print('=== Article Matching Failed ===')
        print('URL:', article.url)
        print('Expected:', article)
        print('Actual:', new_article)
        assert False

# Delete an article
for article in DELETE_ARTICLES:
    db.delete_article(article)
    try:
        db.get_article(article)
    except KeyError:
        pass
    else:
        print('=== DB Failed To Delete Article ===')
        print('URL:', article)
        assert False
