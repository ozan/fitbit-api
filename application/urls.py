"""
URL dispatch route mappings and error handlers

"""

from flask import render_template

from application import app
from application import views


## URL dispatch rules

# Historic data API endpoints
app.add_url_rule('/weight', 'weight', view_func=views.weight)
app.add_url_rule('/sleep', 'sleep', view_func=views.sleep)
app.add_url_rule('/mood', 'mood', view_func=views.mood)

# App Engine warm up handler
# See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests
app.add_url_rule('/_ah/warmup', 'warmup', view_func=lambda: '')


## Error handlers
# Handle 404 errors
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Handle 500 errors
@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

