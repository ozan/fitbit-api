"""
Primary App Engine app handler

"""

import os
import sys

# add libs to Python search path
src_path = os.path.abspath('src')
sys.path.append(src_path)

for f in os.listdir(src_path):
    pth = os.path.join(src_path, f)
    if os.path.isdir(pth):
        sys.path.append(pth)


from google.appengine.ext.webapp.util import run_wsgi_app
from application import app

run_wsgi_app(app)

