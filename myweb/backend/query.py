"""
A parser for parenthesized search queries.
"""

from collections import namedtuple

And = namedtuple('And', ['oper_1', 'oper_2'])
Or = namedtuple('Or', ['oper_1', 'oper_2'])
Not = namedtuple('Not', ['expr'])

Tag = namedtuple('Tag', ['tag'])
Domain = namedtuple('Domain', ['domain'])
Links = namedtuple('Links', ['url'])
LinkedBy = namedtuple('LinkedBy', ['url'])
Url = namedtuple('Url', ['url'])

# Spaces-out parenthesis to make them easier to parse
EXPAND_PARENS = str.maketrans({'(': ' ( ', ')': ' ) '})
def parse_query(query_string):
    """
    Parses a query string, into a tree of nodes.

    Currently, the only deficiency is that parenthesis must have spaces around
    them.
    """
    expanded_query = query_string.translate(EXPAND_PARENS)
    words = expanded_query.split()

    # Take a flat word list, and convert it to a nested token list depending
    # upon where parenthesis fall.
    tokens = [] # Tokens in the current set of parens
    paren_stack = [] # Tokens in outer layers of parens
    try:
        for word in words:
            if word == '(':
                paren_stack.append(tokens)
                tokens = []
            elif word == ')':
                tmp = tokens
                tokens = paren_stack.pop()
                tokens.append(tmp)
            else:
                tokens.append(word)

        # If there are still entries on the outer layers, the user put in too
        # many '('
        if paren_stack:
            raise IndexError
    except IndexError:
        # The index error is produced when an extra ')' causes a non-existent
        # entry to be popped off the parentheses stack.
        raise SyntaxError('Parentheses nesting error')

    if len(tokens) == 1:
        token = tokens.pop()
        if isinstance(token, list):
            return wordlist_to_node(token)
        else:
            return word_to_node(token)
    else:
        return wordlist_to_node(tokens)

QUERY_WORD = {
    'domain:': Domain,
    'tag:': Tag,
    'links:': Links,
    'linked:': LinkedBy,
    'url:': Url
}

BINARY_OPS = {
    'AND': And,
    'OR': Or,
}

UNARY_OPS = {
    'NOT': Not
}

def word_to_node(word):
    """
    Converts a single 'word' into a node type.
    """
    assert isinstance(word, str)
    for prefix, constructor in QUERY_WORD.items():
        if word.startswith(prefix):
            word = word[len(prefix):]
            return constructor(word)

    # Everything which isn't a special query form is assumed to be a tag
    return Tag(word)

def handle_unary(operators, operands):
    """
    Handles unary operators.
    """
    operator = operators.pop()
    expr = operands.pop()
    operands.append(operator(expr))

def fold_operators(operators, operands):
    """
    Combines operators with operands.
    """
    is_binary = (lambda oper:
            oper in BINARY_OPS.values())

    is_unary = (lambda oper:
            oper in UNARY_OPS.values())

    try:
        while operators:
            last_oper = operators[-1]
            try:
                next_to_last_oper = operators[-2]
            except IndexError:
                next_to_last_oper = None

            if is_binary(last_oper) and len(operands) >= 2:
                # We have to handle precedence here, since if we ignore the
                # previous operator, we could do the following:
                #
                #   NOT A OR B ==> NOT (A OR B)
                #
                # When what we really want is:
                #
                #   NOT A OR B ==> (NOT A) OR B
                if is_unary(next_to_last_oper):
                    saved_binary_oper = operators.pop()
                    saved_second_oper = operands.pop()

                    handle_unary(operators, operands)

                    operators.append(saved_binary_oper)
                    operands.append(saved_second_oper)
                else:
                    operator = operators.pop()
                    second = operands.pop()
                    first = operands.pop()
                    operands.append(operator(first, second))
            elif is_unary(last_oper) and len(operands) >= 1:
                handle_unary(operators, operands)
            else:
                raise IndexError
    except IndexError:
        raise SyntaxError('Not enough operands for binary operator')

    while len(operands) > 1:
        second = operands.pop()
        first = operands.pop()
        operands.append(And(second, first))

    try:
        return operands.pop()
    except IndexError:
        raise SyntaxError('Empty query')

def wordlist_to_node(wordlist):
    """
    Converts a list of 'words' into a node type.
    """
    assert isinstance(wordlist, list)

    # Constructs a tree, by working through each token and pushing each
    # operator on a stack. When the operator can be used, it consumes
    # its arguments and pushes the result back onto the operator stack.
    operands = []
    operators = []

    while wordlist:
        token = wordlist.pop()

        # Note that this check must be first, otherwise this code will search
        # an *_OPS dict for a list, will will cause an 'unhashable type' error
        if isinstance(token, list):
            operands.append(wordlist_to_node(token))
        elif token in BINARY_OPS:
            operators.append(BINARY_OPS[token])
        elif token in UNARY_OPS:
            operators.append(UNARY_OPS[token])
        else:
            operands.append(word_to_node(token))

    return fold_operators(operators, operands)


def node_to_string(node):
    """
    Converts a node to a printable form.
    """
    formatting = {
        # Compound expressions
        And: lambda node: 'AND[{}, {}]'.format(
            node_to_string(node.oper_1),
            node_to_string(node.oper_2)),

        Or: lambda node: 'OR[{}, {}]'.format(
            node_to_string(node.oper_1),
            node_to_string(node.oper_2)),

        Not: lambda node: 'NOT[{}]'.format(node_to_string(node.expr)),

        # Simple expressions
        Tag: lambda node: 'tag:' + node.tag,
        Domain: lambda node: 'domain:' + node.domain,
        Links: lambda node: 'links:' + node.url,
        LinkedBy: lambda node: 'linked:' + node.url,
        Url: lambda node: 'url:' + node.url
    }

    if type(node) in formatting:
        return formatting[type(node)](node)
    else:
        return '?[{}]'.format(node)
