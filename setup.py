from setuptools import setup

setup(name='myweb',
    packages = ['myweb', 'myweb.frontend', 'myweb.backend', 'myweb.frontend.web', 'myweb.frontend.web.formatters'],
    entry_points = {
        'console_scripts':
            ['myweb-tk = myweb.frontend.tk:main',
             'myweb-web = myweb.frontend.web.server:main',
             'myweb-cli = myweb.frontend.cli:main']
    },
    author = 'Adam Marchetti',
    version = '0.31',
    description = 'Hyperlinked website commentary',
    author_email = 'adamnew123456@gmail.com',
    keywords = ['web', 'commenary', 'hyperlink'],
    classifiers = [
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: End Users',
        'Development Status :: 4 - Beta',
        'Topic :: Utilities'
    ],
    long_description = """myweb

A way to store hyperlinked notes about pages, organize them with tags, and
search through them.
""")
