"""
A command-line based frontend for interacting with myweb.
"""

from myweb.backend import config, db, query, utils

import argparse
import os
import re
import sys
import tempfile

HELP = """myweb-cli - A command-line interface to myweb.
Usage:
    myweb-cli <command> <args>

Commands:
    search QUERY
        Searches the database using the given query.
    print URL
        Shows the content of the URL, including backlinks, to stdout.
    view [--no-backlinks] URL
        Dumps the content of the given URL to stdout.
    view-backlinks URL
        Dumps the list of backlinks for the given URL to stdout.
    view-tags URL
        Dumps the list of tags for the given URL to stdout.
    create URL [TAG...]
        Creates a new article with the given tag, and with the contents of
        the article coming from stdin.
    update URL
        Updates the content of the URL from the contents of stdin.
    edit URL
        Invokes $VISUAL (or $EDITOR) on the content of the given URL, and then
        saves the result back into the database.
    set-tags URL [TAG...]
        Updates the list of tags for the URL.
    delete
        Removes the given URL from the database.
    help
        Show a complete help page.
"""

def load_config():
    """
    Loads a configuration object.
    """
    return config.load_config({})

def init_db(config_opts):
    """
    Loads the database.
    """
    db.load_database(config_opts['myweb']['db'])
        
def main():
    "Parses the command line and initializes the given action."
    arg_parser = argparse.ArgumentParser()
    sub_args = arg_parser.add_subparsers(help='Commands', dest='command')

    help_parser = sub_args.add_parser('help',
        help='Shows a complete help page')
    
    search_parser = sub_args.add_parser('search',
        help='Search the database, printing out a list of matching URLs')
    search_parser.add_argument('QUERY',
        help='A well-formed myweb query')

    print_parser = sub_args.add_parser('print',
        help='Prints the article for the URL, plus backlinks, to stdout.')
    print_parser.add_argument('URL',
        help='A URL which exists in the database')

    view_parser = sub_args.add_parser('view',
        help='Dump the article for the URL to stdout')
    view_parser.add_argument('URL',
        help='A URL which exists in the database')

    view_backlinks_parser = sub_args.add_parser('view-backlinks',
        help='Dumps the backlinks of the given article to stdout')
    view_backlinks_parser.add_argument('URL',
        help='A URL which exists in the database')

    view_tags_parser = sub_args.add_parser('view-tags',
        help='Dumps the tags of the given article to stdout')
    view_tags_parser.add_argument('URL',
        help='A URL which exists in the database')

    create_parser = sub_args.add_parser('create',
        help='Adds the article for the URL by reading stdin')
    create_parser.add_argument('URL',
        help='A URL which does not exist in the database')
    create_parser.add_argument('TAGS', nargs='+',
        help='The tags to give to the new article')

    update_parser = sub_args.add_parser('update',
        help='Replaces the article for the URL by reading stdin')
    update_parser.add_argument('URL',
        help='A URL which exists in the database')

    edit_parser = sub_args.add_parser('edit',
        help='Invokes $VISUAL (or $EDITOR) to edit an article')
    edit_parser.add_argument('URL',
        help='A URL which exists in the database')

    set_tags_parser = sub_args.add_parser('set-tags',
        help='Sets the list of tags on an article')
    set_tags_parser.add_argument('URL',
        help='A URL which exists in the database')
    set_tags_parser.add_argument('TAGS', nargs='+',
        help='The tags to give to the article')

    delete_parser = sub_args.add_parser('delete',
        help='Removes an article from the database')
    delete_parser.add_argument('URL',
        help='A URL which exists in the database')

    arg_context = arg_parser.parse_args(sys.argv[1:])

    if arg_context.command is None:
        # We weren't provided with a command, so show the short help listing
        arg_parser.print_usage()
        return 1
    elif arg_context.command == 'help':
        arg_parser.print_help()
    elif arg_context.command == 'search':
        config_opts = load_config()
        init_db(config_opts)

        try:
            parsed = query.parse_query(arg_context.QUERY)
            arg_contexts = db.execute_query(parsed)

            for arg_context in arg_contexts:
                print(arg_context)
        except (IndexError, SyntaxError) as ex:
            print('Invalid query string "{}"'.format(arg_context.QUERY),
                file=sys.stderr)
            print('\t' + str(ex), file=sys.stderr)
            return 1
    elif arg_context.command == 'print':
        config_opts = load_config()
        init_db(config_opts)

        try:
            article = db.get_article(arg_context.URL)
        except KeyError:
            print('No article exists for', arg_context.URL,
                file=sys.stderr)
            return 1

        print(article.content)
        
        print('\n----- Backlinks -----')
        for backlink in article.backlinks:
            print(' - ', backlink)

        print('\n----- Tags -----')
        for tag in article.tags:
            print(' - ', tag)
    elif arg_context.command == 'view':
        config_opts = load_config()
        init_db(config_opts)

        try:
            article = db.get_article(arg_context.URL)
        except KeyError:
            print('No article exists for', arg_context.URL,
                file=sys.stderr)
            return 1

        print(article.content)
    elif arg_context.command == 'view-backlinks':
        config_opts = load_config()
        init_db(config_opts)

        try:
            article = db.get_article(arg_context.URL)
        except KeyError:
            print('No article exists for', arg_context.URL,
                file=sys.stderr)
            return 1

        for backlink in article.backlinks:
            print(backlink)
    elif arg_context.command == 'view-tags':
        config_opts = load_config()
        init_db(config_opts)

        try:
            article = db.get_article(arg_context.URL)
        except KeyError:
            print('No article exists for', arg_context.URL,
                file=sys.stderr)
            return 1

        for tag in article.tags:
            print(tag)
    elif arg_context.command == 'create':
        config_opts = load_config()
        init_db(config_opts)

        article = sys.stdin.read()
        tags = set(arg_context.TAGS)
        links = utils.get_links(article)
        try:
            db.create_article(arg_context.URL, article, links, tags)
        except KeyError:
            print('Article for', arg_context.URL, 'already exists',
                file=sys.stderr)
            return 1
    elif arg_context.command == 'update':
        config_opts = load_config()
        init_db(config_opts)

        article = sys.stdin.read()
        try:
            old_article = db.get_article(arg_context.URL)
            links = utils.get_links(article)
            db.update_article(arg_context.URL, article, links, 
                old_article.tags)
        except KeyError:
            print('Article for', arg_context.URL, 'does not exist',
                file=sys.stderr)
            return 1
    elif arg_context.command == 'edit':
        config_opts = load_config()
        init_db(config_opts)

        if not os.environ.get('VISUAL', ''):
            if not os.environ.get('EDITOR', ''):
                print('No setting for $VISUAL or $EDITOR', file=sys.stderr)
                return 1
            else:
                editor = os.environ['EDITOR']
        else:
            editor = os.environ['VISUAL']

        try:
            article = db.get_article(arg_context.URL)

            # Dump the article to a temp file, so that the editor has
            # something to edit (we *could* pass the text in via stdin, but
            # if the user screwed up, they would have no original copy to
            # work from - you can't run :e! in Vim on stdin, for example).
            with tempfile.NamedTemporaryFile(mode='w+') as article_file:
                article_file.write(article.content)
                article_file.flush()

                os.system(editor + ' ' + article_file.name)

                article_file.seek(0)
                new_article_text = article_file.read()

            links = utils.get_links(new_article_text)
            db.update_article(arg_context.URL, new_article_text, links,
                article.tags)
                
        except KeyError:
            print('Article for', arg_context.URL, 'does not exist',
                file=sys.stderr)
            return 1
    elif arg_context.command == 'set-tags':
        config_opts = load_config()
        init_db(config_opts)

        try:
            old_article = db.get_article(arg_context.URL)
            tags = set(arg_context.TAGS)
            db.update_article(arg_context.URL, old_article.content,
                old_article.links, tags)
        except KeyError:
            print('Article for', arg_context.URL, 'does not exist',
                file=sys.stderr)
            return 1
    elif arg_context.command == 'delete':
        config_opts = load_config()
        init_db(config_opts)
        
        db.delete_article(arg_context.URL)
