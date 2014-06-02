"""
Tests used to make sure that the database layer works as it should.
"""

import myweb.backend.utils as utils

SAMPLE_TEXT = 'This is a link to [[a]] and [[b]] but not [[]]'

LINKS = utils.get_LINKS(SAMPLE_TEXT)
assert LINKS == {'a', 'b'}

CHUNKS = utils.get_link_CHUNKS(SAMPLE_TEXT)
assert CHUNKS == [
    utils.Text('This is a link to '),
    utils.Link('a'),
    utils.Text(' and '),
    utils.Link('b'),
    utils.Text(' but not [[]]')
]
