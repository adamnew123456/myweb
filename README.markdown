# A Brief Guide To myweb

## The Purpose of myweb

The design of myweb was based on my experiences with reddit, and I wanted
a tool to store, organize, and search through commentary about web pages.
I wanted, essentially, a heavily-stripped down of the core ideas behind
reddit, but which would be:

 - __Single user__ (I would use it for commentary, not social interaction)
 - __Taggable__ (To make it easier to sort pages, other than by domain or URL)
 - __Searchable__ (Both by URL, but also by tags)
 - __Hyperlinked__ (To make referring to other commentary easier)

## Frontends

There are currently two frontends to myweb:

 - `myweb-tk` is a Tkinter-based frontend, which is discussed below.
 - `myweb-web` is an HTML frontend powered by the wsgiref server. It can be
   accessed at port 8080 on localhost.

Note that the web frontend handles restructuredtext if you have the docutils
module installed (note that restructuredtext handling cannot be disabled if
docutils is installed without modifying web.py).

## The myweb UI

### Searches

The first tab that opens up when you launch myweb is the Search Tab. The search
tab contains three controls:

 - The "Add Article" button
 - The search box
 - The search results list

The language used to search myweb is meant to encompass most of the relationships
you would want to express, given the model that myweb uses to store its data.

A brief overview of the language follows:

- A search expression can be parenthesized, in order to make operator precedence
  clear. The default precedence is that `NOT` binds tighter than the binary
  operators.
- An expression can contain a search term defined by the following terms:
 - `tag:some-tag` indicates a request for articles tagged with `some-tag`
 - `domain:example.com` indicates a request for articles about the site `example.com`
   and any pages under `example.com`
 - `links:url` indicates an article which links to an article about `url`.
 - `linked:url` indicates an article which is linked by an article about `url`.
 - `url:url` indicates an article about `url`.
- Search expressions can be joined by `AND` and `OR`, or can be preceeded by `NOT`.
- If you want to get a list of all articles, then it is only necessary to use
  the basic rules of logic. The search query `x OR NOT x` matches every article
  in the database, and it should be easy to see why.

Type in a query, and press Enter - this should cause a list of results to appear
in the list below (or not, if there were no matching articles). You can double-click
on one of these articles to view it in a new tab.

Clicking the "Add Article" button opens a new tab which allows you to submit a new
article.

## Reading Articles

Reading articles is simply a matter of browsing. myweb recognizes links to other
myweb articles, and all you have to do is click on them to open up the link.

The article viewer has a simple interface, so I'll describe the purpose of the
buttons only - the rest of the interface should be obvious.

The first button, "Edit", opens up a tab which allows you to edit the article
shown in the viewing tab.

The second button, "Refresh", loads the latest version of the article. This is
useful when editing an article, so that way you can see how your changes take
effect.

The third button is "Delete", which will delete the current article.

The fourth, "Close", will close the current tab.

## Editing Articles

When editing an article, the UI will contain a few important elements. The most
important is the editor, which takes up most of the screen, and allows you to
enter article text. You can enter text freeform, with the exception of links.

Links can be entered into an article by typing something like 
`[[http://example.com]]`. In the viewer, this will be rendered as a clickable
hyperlink.

The list of tags is below the editor. Tags are separated with spaces, and can
contain anything but spaces. It is recommended that you not use parentheses,
since this will interfere with the query language, but myweb won't stop you.

To save your article, click "Save"; to close the editor, click "Close".
