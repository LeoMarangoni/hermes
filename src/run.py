#!/usr/bin/python
"""Execute this to start application."""
from flask import Flask, render_template
from views import ProjectsAPI, AccountsAPI, QueueAPI
from tasks import tasks

app = Flask(__name__)

view = ProjectsAPI.as_view('projects_api')
app.add_url_rule('/projects/', view_func=view, methods=['GET', 'POST'])
app.add_url_rule('/projects/<id>/', view_func=view, methods=['GET',
                                                             'PUT',
                                                             'DELETE'])
view = AccountsAPI.as_view('accounts_api')
app.add_url_rule('/projects/<p_id>/accounts/',
                 view_func=view,
                 methods=['GET', 'POST'])
app.add_url_rule('/projects/<p_id>/accounts/<int:a_id>/',
                 view_func=view,
                 methods=['GET', 'PUT', 'DELETE'])


view = QueueAPI.as_view('queue_api')
app.add_url_rule('/queue/',
                 view_func=view,
                 methods=['GET', 'DELETE'])
app.add_url_rule('/projects/<p_id>/queue/',
                 view_func=view,
                 methods=['GET', 'POST', 'DELETE'])
app.add_url_rule('/projects/<p_id>/accounts/<int:a_id>/queue/',
                 view_func=view,
                 methods=['GET', 'POST', 'DELETE'])


@app.after_request
def add_headers(response):
    """Add Access Control headers to each response."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route("/")
def index():
    """Welcome Message."""
    return render_template('index.html')


if __name__ == '__main__':
    task = tasks()
    app.run(debug=False, host="127.0.0.1", port=5500)
