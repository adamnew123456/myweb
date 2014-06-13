"""
Storage for all of the HTML/Javascript which powers the web frontend.
"""

NOT_FOUND_PAGE = b'Not Found'

###############################################################################

SEARCH_PAGE = b'''
<html>
    <head><title>MyWeb Search</title></head>
    <body>
        <input type="text" id="query" style="width:100%" onkeyup="handle_keypress();" /> <br/>
        <ul id="results">
        </ul>
        <input type="button" style="width:100%" onclick="do_new();" /><br/>
        <script>
function handle_keypress(event) {
    if (event.keyCode == 13) { // Test for the Enter key
        do_search();
    }
}

function ajax(uri, data, headers, on_ready) {
    var xhr = new XMLHttpRequest();

    for (var key in headers) {
        xhr.setRequestHeader(key, headers[key].toString());
    }

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            callback(xhr.responseText);
        }
    }
    xhr.open('GET', uri, true);
    xhr.send(data);
}

function do_new() {
    window.location.pathname = '/new';
}

function do_search() {
    var query = document.getElementById("query").value;
    var query_uri = '/ajaz/query';
    var query_body = JSON.stringify({'query': query});

    ajax(query_uri, query_body, {
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

            while (result_list.firstChild)
            {
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
'''

###############################################################################

NEW_PAGE = b'''
<html>
    <head><title>MyWeb - New Article</title></head>
    <body>
        <input type="text" style="width:100%" id="uri" /><br/>
        <textarea id="content" style="width:100%;height:90%" /><br/>
        <input type="text" style="width:100%" id="tags" /><br/>
        <input type="button" value="Submit" style="width:100%" onclick="do_submit();" />
        <script>

function ajax(uri, data, headers, on_ready) {
    var xhr = new XMLHttpRequest();

    for (var key in headers) {
        xhr.setRequestHeader(key, headers[key].toString());
    }

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            callback(xhr.responseText);
        }
    }
    xhr.open('GET', uri, true);
    xhr.send(data);
}

function do_submit() {
    var article_uri = document.getElementById("uri").value;
    var article_content = document.getElementById("content").value;
    var article_raw_tags = document.getElementById("tags");
    var article_tags = article_raw_tags.split(/[ \\t]/);

    var request_uri = '/ajax/submit-new';
    var request_body = JSON.stringify({
            'uri': article_uri, 'content': article_content, '
            tags': article_tags})

    ajax(request_uri, request_body, {
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
'''

################################################################################

EDIT_PAGE = r'''
<html>
    <head><title>MyWeb - Edi Article</title></head>
    <body onload="load_article_content();">
        <input type="text" style="width:100%" id="uri" /><br/>
        <textarea id="content" style="width:100%;height:90%" /><br/>
        <input type="text" style="width:100%" id="tags" /><br/>
        <input type="button" value="Submit" style="width:100%" onclick="do_submit();" />
        <script>
function ajax(uri, data, headers, on_ready) {
    var xhr = new XMLHttpRequest();

    for (var key in headers) {
        xhr.setRequestHeader(key, headers[key].toString()); 
    }

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            callback(xhr.responseText);
        }
    }
    xhr.open('GET', uri, true);
    xhr.send(data);
}

function load_article_content() {
    var components = window.location.pathname.split('/');
    // componets[0] == ""
    // components[1] == "edit"
    // components[2] == <article-uri>

    var request_body = JSON.stringify({'uri': decodeURIComponent(components[2])});
    ajax('/ajax/get-article', request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("Viewing a non-existant URL - please close this page");
        } else {
            document.getElementById('content').value = result['raw-content'];
            document.getElementById('tags').value = result['tags'].join(' ');
        }
    }));
}

function do_submit() {
    var components = window.location.pathname.split('/');
    var article_uri = decodeURIComponent(components[2]);

    var article_content = document.getElementById("content").value;
    var article_raw_tags = document.getElementById("tags");
    var article_tags = article_raw_tags.split(/[ \\t]/);

    var request_uri = '/ajax/submit-edit';
    var request_body = JSON.stringify({
            'uri': article_uri, 'content': article_content, '
            tags': article_tags})

    ajax(request_uri, request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("That URL already has no article in the database");
        } else {
            alert("Article updated successfully.");
        }
    }));
}
        </script>
    </body>
</html>
'''

################################################################################

VIEW_PAGE = r'''
<html>
    <head><title>MyWeb - Edi Article</title></head>
    <body onload="load_article_content();">
        <input type="text" style="width:100%" id="uri" /><br/>
        <div id="content" style="width:100%;height:90%" /><br/>
        <i id="tags" /><br/>
        <input type="button" value="Edit" style="width:30%"" onclick="do_edit();" />
        <input type="button" value="Refresh" style="width:30%" onclick="load_article_content();" />
        <input type="button" value="Delete" style="width:30%" onclick="do_delete();" />
        <script>
function ajax(uri, data, headers, on_ready) {
    var xhr = new XMLHttpRequest();

    for (var key in headers) {
        xhr.setRequestHeader(key, headers[key].toString()); 
    }

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4) {
            callback(xhr.responseText);
        }
    }
    xhr.open('GET', uri, true);
    xhr.send(data);
}

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

    var request_body = JSON.stringify({'uri': decodeURIComponent(components[2])});
    ajax('/ajax/get-article', request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("Viewing a non-existant URL - please close this page");
        } else {
            document.getElementById('content').innerHTML = result['html-content'];
            document.getElementById('tags').innerHTML = escapeHTML(result[tags'].join(' '));
        }
    }));
}

function do_edit() {
    var components = window.location.pathname.split('/');
    window.location.pathname = '/edit/' + components[2];
}

function do_delete() {
    var components = window.location.pathname.split('/');
    // componets[0] == ""
    // components[1] == "view"
    // components[2] == <article-uri>

    var request_body = JSON.stringify({'uri': decodeURIComponent(components[2])});
    ajax('/ajax/get-article', request_body, {
            'Content-Type': 'application/json',
            'Content-Length': request_body.length
        },
    (function(result_text) {
        var result = JSON.parse(result_text);
        if (result['was-error']) {
            alert("Viewing a non-existant URL - please close this page");
        } else {
            document.getElementById('content').innerHTML = result['html-content'];
            document.getElementById('tags').innerHTML = escapeHTML(result[tags'].join(' '));
        }
    }));
}
        </script>
    </body>
</html>
'''
