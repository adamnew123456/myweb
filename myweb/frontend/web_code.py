"""
Storage for all of the HTML/Javascript which powers the web frontend.
"""

NOT_FOUND_PAGE = b'Not Found'

AJAX = b'''
function ajax(uri, data, headers, on_ready) {
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = (function() {
        if (xhr.readyState == 4) {
            on_ready(xhr.responseText);
        }
    });

    xhr.open('POST', uri, true);
    for (var key in headers) {
        xhr.setRequestHeader(key, headers[key].toString()); 
    }

    xhr.send(data);
}
'''

###############################################################################

SEARCH_PAGE = b'''
<html>
    <head><title>MyWeb Search</title></head>
    <body>
        <input type="text" id="query" style="width:100%" onkeyup="handle_keypress(event);" /> <br/>
        <ul id="results">
        </ul>
        <input type="button" value="Create" style="width:100%" onclick="do_new();" /><br/>
        <script>
%AJAX%

function handle_keypress(event) {
    if (event.keyCode == 13) { // Test for the Enter key
        do_search();
    }
}

function do_new() {
    window.location.pathname = '/new';
}

function do_search() {
    var query = document.getElementById("query").value;
    var query_body = JSON.stringify({'query': query});

    ajax('/ajax/query', query_body, {
            'Content-Type': 'application/json',
            'Content-Length': query_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);

        if (result['was-error']) {
            alert("Malformed query");
        } else {
            var articles = result['articles'];
            var result_list = document.getElementById('results');

            while (result_list.firstChild) {
                result_list.removeChild(result_list.firstChild);
            }

            for (var i = 0; i < articles.length; i++) {
                var uri = articles[i];

                var item_node = document.createElement('li');
                var link_node = document.createElement('a');
                var text_node = document.createTextNode(uri);

                link_node.href = '/view/' + encodeURIComponent(uri);

                result_list.appendChild(item_node);
                item_node.appendChild(link_node);
                link_node.appendChild(text_node);
            }
        }
    }));
}
        </script>
    </body>
</html>
'''.replace(b'%AJAX%', AJAX)

###############################################################################

NEW_PAGE = b'''
<html>
    <head><title>MyWeb - New Article</title></head>
    <body>
        <input type="text" style="width:100%" id="uri" /><br/>
        <textarea id="content" style="width:100%;height:75%"> </textarea> <br/>
        <input type="text" style="width:100%" id="tags" /><br/>
        <input type="button" value="Submit" style="width:100%" onclick="do_submit();" />
        <script>
%AJAX%

function do_submit() {
    var article_uri = document.getElementById("uri").value;
    var article_content = document.getElementById("content").value;
    var article_raw_tags = document.getElementById("tags").value;
    var article_tags = article_raw_tags.split(/[ \\t]/);

    var request_body = JSON.stringify({
            'uri': article_uri, 'content': article_content,
            'tags': article_tags})

    ajax('/ajax/submit-new', request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("That URL already has an article in the database");
        } else {
            alert("Article submitted successfully - please close this page");
        }
    }));
}
        </script>
    </body>
</html>
'''.replace(b'%AJAX%', AJAX)

################################################################################

EDIT_PAGE = b'''
<html>
    <head><title>MyWeb - Edit Article</title></head>
    <body>
        <h1 id="uri"> </h1>
        <textarea id="content" style="width:100%;height:75%" ></textarea><br/>
        <input type="text" style="width:100%" id="tags" /><br/>
        <input type="button" value="Submit" style="width:100%" onclick="do_submit();" />
        <script>
%AJAX%

function escapeHTML(s) { 
    return s.replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
}

function load_article_content() {
    var components = window.location.pathname.split('/');
    // componets[0] == ""
    // components[1] == "edit"
    // components[2] == <article-uri>
    var uri = components.slice(2).join('/');

    var request_body = JSON.stringify({'uri': decodeURIComponent(uri)});
    ajax('/ajax/get-article', request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("Viewing a non-existant URL - opening new page");
            window.location.pathname = '/new';
        } else {
            document.getElementById('uri').innerHTML = escapeHTML(decodeURIComponent(uri));
            document.getElementById('content').value = result['raw-content'];
            document.getElementById('tags').value = result['tags'].join(' ');
        }
    }));
}

function do_submit() {
    var components = window.location.pathname.split('/');
    var article_uri = decodeURIComponent(components[2]);

    var article_content = document.getElementById("content").value;
    var article_raw_tags = document.getElementById("tags").value;
    var article_tags = article_raw_tags.split(/[ \\t]/);

    var request_body = JSON.stringify({
            'uri': article_uri, 'content': article_content,
            'tags': article_tags})

    ajax('/ajax/submit-edit', request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("That URL already has an article in the database");
        } else {
            alert("Article updated successfully.");
        }
    }));
}

load_article_content();
        </script>
    </body>
</html>
'''.replace(b'%AJAX%', AJAX)

################################################################################

VIEW_PAGE = b'''
<html>
    <head><title>MyWeb - View Article</title></head>
    <body>
        <h1 id="uri"> </h1>
        <div id="content" style="width:100%"> </div><br/>
        <h3 id="tags"></h3>
        <input type="button" value="Edit" style="width:30%"" onclick="do_edit();" />
        <input type="button" value="Refresh" style="width:30%" onclick="load_article_content();" />
        <input type="button" value="Delete" style="width:30%" onclick="do_delete();" />
        <script>
%AJAX%

function escapeHTML(s) { 
    return s.replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
}

function load_article_content() {
    var components = window.location.pathname.split('/');
    // componets[0] == ""
    // components[1] == "view"
    // components[2] == <article-uri>
    var uri = components.slice(2).join('/');

    var request_body = JSON.stringify({'uri': decodeURIComponent(uri)});
    ajax('/ajax/get-article', request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("Viewing a non-existant URL - opening new page");
            window.location.pathname = '/new';
        } else {
            document.getElementById('uri').innerHTML = escapeHTML(decodeURIComponent(uri));
            document.getElementById('content').innerHTML = result['html-content'];

            var tags_elem = document.getElementById('tags');
            tags_elem.innerHTML = '';
            for (var i = 0; i < result['tags'].length; i++) {
                var tag = result['tags'][i];
                tags_elem.innerHTML += '(' + escapeHTML(tag) + ') ';
            }
        }
    }));
}

function do_edit() {
    var components = window.location.pathname.split('/');
    // componets[0] == ""
    // components[1] == "view"
    // components[2] == <article-uri>
    var uri = components.slice(2).join('/');

    window.location.pathname = '/edit/' + uri;
}

function do_delete() {
    var components = window.location.pathname.split('/');
    // componets[0] == ""
    // components[1] == "view"
    // components[2] == <article-uri>
    var uri = components.slice(2).join('/');

    var request_body = JSON.stringify({'uri': decodeURIComponent(uri)});
    ajax('/ajax/submit-delete', request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("Failed to delete");
        } else {
            alert("Successfully deleted this article - please close this window");
        }
    }));
}

load_article_content();
        </script>
    </body>
</html>
'''.replace(b'%AJAX%', AJAX)
