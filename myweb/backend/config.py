"""
A small configuration handler, which is intended to be reasonably cross platform
with respect to path names.
"""

import configparser
import os, os.path

# Attempt some form of platform independence with regards to the location of
# the configuration file, and the page database.
if 'HOME' in os.environ:
    # Unix-like - either XDG, or classic Unix
    HOME = os.environ['HOME']
    DB_PATH = os.path.join(HOME, '.myweb.sqlite')

    if '.config' in os.listdir(HOME):
        # Use XDG-style locations
        CONFIG_PATH = os.path.join(HOME, '.config', 'myweb.cfg')
    else:
        # Not XDG, but still Unix
        CONFIG_PATH = os.path.join(HOME, '.myweb.cfg')
elif 'APPDATA' in os.environ:
    # Windows
    APPDATA = os.environ['APPDATA']

    # Create the configuration directory if it doesn't exist already
    if not os.path.isdir(os.path.join(APPDATA, 'myweb')):
        os.mkdir(os.path.join(APPDATA, 'myweb'))

    CONFIG_PATH = os.path.join(APPDATA, 'myweb', 'myweb.cfg')
    DB_PATH = os.path.join(APPDATA, 'myweb', 'myweb.sqlite')

DEFAULTS = {'myweb': {'db': DB_PATH}}
def load_config(defaults):
    """
    Loads the configuration file, filling any defaults as necessary.

    The defaults are given as follows:
        {'section-name': {'key': 'value', 'key': 'value', ...}, ...}

    Note that there must be defaults for every option which is of interest, as
    the ConfigParser instance itself is not returned, but a dict of the same form
    as the defaults dict.
    """
    defaults.update(DEFAULTS)

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    options = {}
    for section in defaults:
        section_options = {}

        if section not in config:
            for opt_name in defaults[section]:
                opt_default = defaults[section][opt_name]
                section_options[opt_name] = opt_default
        else:
            config_section = config[section]
            for opt_name, opt_default in defaults[section].items():
                section_options[opt_name] = config_section.get(
                        opt_name, opt_default)

        options[section] = section_options

    return options
