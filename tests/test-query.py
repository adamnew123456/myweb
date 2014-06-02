"""
Tests how the query parser builds QUERIES.
"""

from myweb.backend.query import *
QUERIES = [
    ('a AND b', And(Tag('b'), Tag('a'))),
    ('NOT a', Not(Tag('a'))),
    ('NOT a OR NOT b', Or(Not(Tag('b')), Not(Tag('a')))),
    ('NOT (a OR b)', Not(Or(Tag('b'), Tag('a')))),
    ('a OR (b AND c)', Or(And(Tag('c'), Tag('b')), Tag('a'))),
    ('url:a', Url('a')),
    ('tag:a', Tag('a')),
    ('domain:a', Domain('a')),
    ('links:a', Links('a')),
    ('linked:a', LinkedBy('a'))
]

for query, expected in QUERIES:
    parsed = parse_query(query)
    if parsed != expected:
        print('***** Parsing Query Failed *****')
        print('Query:', query)
        print('Parsed:', parsed)
        print('Expected:', expected)
        assert False
