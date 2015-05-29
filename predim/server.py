"""
   IoT demo: Server side components for the Pivotal Data Science Marketplace prototype app for IoT
   Author: Srivatsan Ramanujam <sramanujam@pivotal.io>, 28-May-2015
"""

import os
from flask import Flask, render_template
import pandas.io.sql as psql
import psycopg2

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    """
       Render homepage
    """
    print '###In index()'
    #return 'Hello World'
    return render_template('index.html', title='IOT demo')


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
