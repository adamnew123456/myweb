A Brief Guide To MyWeb
======================

MyWeb is a system for storing commentary about web pages. It was designed
around my experiences with Reddit, but with different goals:

- *Single-User* - I use MyWeb for commentary, not social interaction
- *Taggable*
- *Searchable*- A general searching system, utilizing the full power of
  boolean expressions, is built into the core of MyWeb.
- *Hyperlinked*- It is easy to browse MyWeb by following links between articles.

Frontends
---------

There are currently two frontends which are available:

- A Tkinter frontend, which can be run as ``myweb-tk``.
- A HTML frontend, powered by the ``wsgiref`` module, which can be run as
  ``myweb-web``.

Query Syntax
------------

The query syntax provided by myweb utilizes the full power of boolean
expressions - parentheses included.

Here's an example query showing off all the features:::

    url:http://www.example.com OR NOT (
        domain:example.com AND 
            links:http://example.com OR
                linked:http://example.com OR
                    tag:some-tag OR
                        some-tag)

Here are the important details:

- Parentheses are supported - by default, the *NOT* operator binds tighter 
  than *AND* and *OR* - if you want to negate an *AND*, for example, then use
  ``NOT (a AND b)``.
- The boolean operators *NOT*, *OR* and *AND* are supported and do what you
  would expect.
- ``url:http://example.com`` produces articles which are about the given URL.
- ``domain:example.com`` produces articles whose URL is on the given domain.
- ``links:http://example.com`` produces articles which contain links to the URL.
- ``linked:http://example.com`` produces articles which are linked to by the URL.
- ``tag:some-tag`` and ``some-tag`` produce articles which have the given tag.

Configuration
-------------

These frontends can be configured by a configuration file, which can be located
in one of three places:

- Windows users will find it under ``%APPDATA\myweb\myweb.cfg``
- If ``$HOME/.config`` exists, then the configuration will be located at ``$HOME/.config/myweb.cfg``
- If ``$HOME/.config`` *does not* exist, then the configuration will be at ``$HOME/.myweb.cfg``

The configuration file currently accepts the following options:::

    [myweb]
    db = /wherever/you/want/the/database.sqlite
    [web]
    port = 8080
    formatter = none
    [tk]
    theme = classic

myweb Section
~~~~~~~~~~~~~

- *db* is the path to the database file, where all of the MyWeb articles are
  stored. MyWeb attempts to find a sensible default for your platform:
 
  - On Windows, it will be located at ``%APPDATA%\myweb\myweb.sqlite``
  - On \*nix, it will be located at ``$HOME/.myweb.sqlite``

tk Section
~~~~~~~~~~

- *theme* is the theme to use for the Tk UI. You can get a list of these themes
  by running ``python3 -c 'import tkinter.ttk as T; s = T.STyle(); print(s.theme_names())'``
  at your command line.

web Section
~~~~~~~~~~~

- *port* is the port to run the HTTP server on.
- *formatter* is the method which is used to format articles. Currently a
  formatter called ``restructuredtext`` is supported which uses ``docutils``,
  as well as a formatter called ``none`` which uses plain HTML.
