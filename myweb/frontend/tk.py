"""
A tkinter-based frontend for interacting with myweb.
"""

from myweb.backend import db, query, utils

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as tk_message

class ButtonBox:
    """
    Contains a horizontal button box.
    """
    def __init__(self, parent):
        self.frame = tk.Frame(parent)
        self.buttons = []

    def add(self, **config):
        """
        Adds a new button.
        """
        self.buttons.append(ttk.Button(self.frame, **config))

    def pack(self, **config):
        """
        Packs all the buttons and the frame.
        """
        self.frame.pack(**config)
        for button in self.buttons:
            button.pack(side=tk.LEFT, fill=tk.X, expand=True)

class CreateTab:
    """
    A tab which allows an article to be created.
    """
    def __init__(self, app, url=None):
        self.app = app
        self.frame = tk.Frame(None)
        self.url = ttk.Entry(self.frame)
        if url is not None:
            # Insert the default URL, if there is one given
            self.url.insert('end', url)

        self.edit = tk.Text(self.frame, wrap=tk.WORD)
        self.tags = tk.Entry(self.frame)

        self.buttons = ButtonBox(self.frame)
        self.buttons.add(text='Save', command=self.on_save)
        self.buttons.add(text='Close', command=self.on_close)
        self.pack()

    def pack(self):
        """
        Packs all of the widgets in this frame.
        """
        self.url.pack(fill=tk.X)
        self.edit.pack(fill=tk.BOTH, expand=True)
        self.tags.pack(fill=tk.X)
        self.buttons.pack(fill=tk.X)

    def get_widget(self):
        """
        Gets the frame holding all of this tab's widgets.
        """
        return self.frame

    def on_save(self):
        """
        Tries to save everything to the database, or shows an error message.
        """
        article_url = self.url.get()
        article_text = self.edit.get('0.0', 'end')
        article_tags = self.tags.get()

        url = article_url.strip()
        tags = set(article_tags.split())
        links = utils.get_links(article_text)
        try:
            # Tk adds an extra newline, which we need to strip
            article_text = article_text[:-1]

            db.create_article(url, article_text, links, tags)
            tk_message.showinfo('OK', 'Successfully saved article')
            self.app.close(self)
        except IOError:
            tk_message.showerror('Error', 'Article already exists')

    def on_close(self):
        """
        Closes this tab, regardless of whether any content has been entered.
        """
        self.app.close(self)

class EditTab:
    """
    A tab which allows an article to be changed.
    """
    def __init__(self, app, url):
        self.app = app
        self.url = url
        self.frame = tk.Frame(None)
        self.title = ttk.Label(self.frame, text=url)
        self.edit = tk.Text(self.frame, wrap=tk.WORD)
        self.tags = tk.Entry(self.frame)

        self.buttons = ButtonBox(self.frame)
        self.buttons.add(text='Save', command=self.on_save)
        self.buttons.add(text='Close', command=self.on_close)

        self.pack()
        self.load_page()

    def get_url(self):
        """
        Gets the URL this is viewing.
        """
        return self.url

    def load_page(self):
        """
        Loads all the data from the database.
        """
        article = db.get_article(self.url)

        self.tags.delete('0', 'end')
        self.tags.insert('end', ' '.join(article.tags))

        self.edit.delete('0.0', 'end')
        self.edit.insert('end', article.content)

    def pack(self):
        """
        Packs all of the widgets in this frame.
        """
        self.title.pack(fill=tk.X)
        self.edit.pack(fill=tk.BOTH, expand=True)
        self.tags.pack(fill=tk.X)
        self.buttons.pack(fill=tk.X)

    def get_widget(self):
        """
        Gets the frame holding all of this tab's widgets.
        """
        return self.frame

    def on_save(self):
        """
        Tries to save everything to the database, or shows an error message.
        """
        article_text = self.edit.get('0.0', 'end')
        article_tags = self.tags.get()

        tags = set(article_tags.split())
        links = utils.get_links(article_text)
        try:
            # Tk adds an extra newline, which we need to strip
            article_text = article_text[:-1]

            db.update_article(self.url, article_text, links, tags)
            tk_message.showinfo('OK', 'Successfully saved article')
        except IOError:
            tk_message.showerror('Error', 'No article exists for that URL')
            self.app.close(self)

    def on_close(self):
        """
        Closes this tab, regardless of whether any content has been entered.
        """
        self.app.close(self)

class ViewTab:
    """
    A tab which allows an article to be read.
    """
    def __init__(self, app, url):
        self.app = app
        self.url = url
        self.frame = tk.Frame(None)
        self.title = ttk.Label(self.frame, text=url)
        self.view = tk.Text(self.frame, state=tk.DISABLED, wrap=tk.WORD)
        self.tags = tk.Label(self.frame)

        self.buttons = ButtonBox(self.frame)
        self.buttons.add(text='Edit', command=self.on_edit)
        self.buttons.add(text='Refresh', command=self.load_page)
        self.buttons.add(text='Delete', command=self.on_delete)
        self.buttons.add(text='Close', command=self.on_close)
        self.view_tags = set()

        self.pack()
        self.load_page()

    def get_url(self):
        """
        Gets the URL this is viewing.
        """
        return self.url

    def render_article(self, article):
        """
        Renders an article, along with all back-links.
        """
        for tag in self.view_tags:
            self.view.tag_delete(tag)
        self.view_tags.clear()

        # First, generate the main body text, and filter out any links
        for chunk in utils.get_link_chunks(article.content):
            if isinstance(chunk, utils.Text):
                self.view.insert('end', chunk.text)
            elif isinstance(chunk, utils.Link):
                link_tag = 'link-' + chunk.url
                if link_tag not in self.view_tags:
                    self.view_tags.add(link_tag)
                    self.view.tag_configure(link_tag,
                        underline=True, foreground='blue')
                    self.view.tag_bind(link_tag, '<Button-1>', self.open_link)

                self.view.insert('end', chunk.url, link_tag)

        # Then, add the backlinks
        self.view.insert('end', '\n\n<-----| Backlinks | ----->\n')
        for link in article.backlinks:
            link_tag = 'link-' + link
            if link_tag not in self.view_tags:
                self.view_tags.add(link_tag)
                self.view.tag_configure(link_tag,
                        underline=True, foreground='blue')
                self.view.tag_bind(link_tag, '<Button-1>', self.open_link)

            self.view.insert('end', ' - ')
            self.view.insert('end', link, link_tag)
            self.view.insert('end', '\n')

    def load_page(self):
        """
        Loads all the data from the database.
        """
        article = db.get_article(self.url)

        self.tags.configure(text=' '.join(article.tags))

        self.view.configure(state=tk.NORMAL)
        self.view.delete('0.0', 'end')
        self.render_article(article)
        self.view.configure(state=tk.DISABLED)

    def pack(self):
        """
        Packs all of the widgets in this frame.
        """
        self.title.pack(fill=tk.X)
        self.view.pack(fill=tk.BOTH, expand=True)
        self.tags.pack(fill=tk.X)
        self.buttons.pack(fill=tk.X)

    def get_widget(self):
        """
        Gets the frame holding all of this tab's widgets.
        """
        return self.frame

    def on_edit(self):
        """
        Starts editing this page.
        """
        self.app.edit(self.url)

    def on_close(self):
        """
        Closes this tab, regardless of whether any content has been entered.
        """
        self.app.close(self)

    def on_delete(self):
        """
        Deletes the article that this tab is viewing.
        """
        result = tk_message.askyesno('Delete?', 'Really delete?')
        if result:
            db.delete_article(self.url)
            self.app.close(self)

    def open_link(self, _):
        """
        Opens a link to another page.
        """
        for tag in self.view.tag_names(tk.CURRENT):
            if tag.startswith('link-'):
                url = tag.replace('link-', '')
                try:
                    self.app.view(url)
                except KeyError:
                    # If there isn't an article, then allow the user to create
                    # it if they want to. Like traditional wiki 'this does not
                    # exist' pages, but implicit instead of explicit
                    self.app.create(url)

class SearchTab:
    """
    Handles retrieving URLs based upon queries.
    """
    def __init__(self, app):
        self.app = app
        self.frame = tk.Frame()
        self.add = ttk.Button(self.frame, text='Add Article', command=self.on_add)
        self.query = ttk.Entry(self.frame)
        self.items = tk.Listbox(self.frame)

        self.items.bind('<Double-Button-1>', self.on_select)
        self.query.bind('<Return>', self.on_search)

        self.pack()

    def pack(self):
        """
        Packs all the search tabs.
        """
        self.add.pack(fill=tk.X)
        self.query.pack(fill=tk.X)
        self.items.pack(fill=tk.BOTH, expand=True)

    def get_widget(self):
        """
        Gets the main frame.
        """
        return self.frame

    def on_select(self, _):
        """
        Opens up a viewer for a particular URL.
        """
        selections = self.items.curselection()
        if not selections:
            return

        for selection in selections:
            url = self.items.get(selection)
            self.app.view(url)

    def on_add(self):
        """
        Adds a new article.
        """
        self.app.create()

    def on_search(self, _):
        """
        Refreshes the search box with the result of a query.
        """
        try:
            self.items.delete('0', 'end')

            query_text = self.query.get()

            # An empty query just clears the search box
            if not query_text.strip():
                return

            parsed = query.parse_query(self.query.get())
            results = db.execute_query(parsed)
            self.items.insert('end', *results)
        except SyntaxError as ex:
            tk_message.showerror('Error', str(ex))

class App:
    """
    The main container, under the root window.

    This hosts a tab bar, and takes requests for creating new types of windows.
    """
    def __init__(self, window):
        self.root = window
        self.tab_bar = ttk.Notebook(window)
        # Store each tab, along with the id of its widget, so that we can find
        # out if a tab exists and focus it instead of creating a new one
        self.tabs = {}

        search_tab = SearchTab(self)
        self.tab_bar.add(search_tab.get_widget(), text='Search')

    def pack(self, **kwargs):
        """
        Packs the tab bar.
        """
        self.tab_bar.pack(**kwargs)

    def create_tab(self, tab, text):
        """
        Creates a new tab, given something with a get_widget method.
        """
        widget = tab.get_widget()
        self.tab_bar.add(widget, text=text)
        self.tabs[tab] = '.' + widget.winfo_name()

        # Select the newly created tab
        last_index = self.tab_bar.index(tk.END)
        self.tab_bar.select(last_index - 1)

    def select_tab(self, tab):
        """
        Selects an existing tab.
        """
        tab_list = self.tab_bar.tabs()
        tab_index = tab_list.index(self.tabs[tab])
        self.tab_bar.select(tab_index)

    def create(self, url=None):
        """
        Opens a tab for creating a new article.
        """
        tab = CreateTab(self, url)
        self.create_tab(tab, 'Creating')

    def find_existing_tab(self, tab_type, url):
        """
        Finds an existing tab, or returns None.
        """
        for tab in self.tabs:
            if isinstance(tab, tab_type) and tab.get_url() == url:
                return tab
        return None

    def edit(self, url):
        """
        Opens up an editing window for the given URL.
        """
        existing_tab = self.find_existing_tab(EditTab, url)
        if existing_tab is not None:
            self.select_tab(existing_tab)
        else:
            tab = EditTab(self, url)
            self.create_tab(tab, 'Editing ' + url)

    def view(self, url):
        """
        Opens up a viewing window for the given URL.
        """
        existing_tab = self.find_existing_tab(ViewTab, url)
        if existing_tab is not None:
            self.select_tab(existing_tab)
        else:
            tab = ViewTab(self, url)
            self.create_tab(tab, 'Viewing ' + url)

    def close(self, tab):
        """
        Closes the given tab.
        """
        widget = tab.get_widget()
        self.tab_bar.forget(widget)
        if tab in self.tabs:
            del self.tabs[tab]

def main():
    "Initializes the database, and loads the UI"
    root = tk.Tk()
    root.wm_title('myweb')

    if db.DEFAULT_DB is not None:
        db.load_database(db.DEFAULT_DB)
    else:
        tk_message.showerror('Error', "Don't know where to store the database. "
                "Please set  either %AppData% or $HOME.")
        return

    style = ttk.Style()
    style.theme_use('alt')

    app = App(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
