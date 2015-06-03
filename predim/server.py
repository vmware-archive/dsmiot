"""
   IoT demo: Server side components for the Pivotal Data Science Marketplace prototype app for IoT
   Author: Srivatsan Ramanujam <sramanujam@pivotal.io>, 28-May-2015
"""

import os
from flask import Flask, render_template
import pandas.io.sql as psql
import psycopg2
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def index():
    """
       Render homepage
    """
    return render_template('index.html', title='IOT demo')

@app.route('/')
@app.route('/home')
def home():
    """
       Homepage
    """
    logger.debug('In home()')
    return render_template('home.html')

@app.route('/about')
def about():
    """
       About page, listing background information about the app
    """
    logger.debug('In about()')
    return render_template('about.html')

@app.route('/contact')
def contact():
    """
       Contact page
    """
    logger.debug('In contact()')
    return render_template('contact.html')

@app.route('/<path:path>')
def static_proxy(path):
    """
       Serving static files
    """
    logger.debug('In static_proxy()')
    return app.send_static_file(path)

def main():
    """
       Start the application
    """
    if(os.getenv("VCAP_APP_PORT")):
        port = int(os.getenv("VCAP_APP_PORT"))
    else:
        #default port
        port = 9090
    app.run(host='0.0.0.0', debug=True, port=port)
