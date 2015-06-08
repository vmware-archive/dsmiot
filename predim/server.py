"""
   IoT demo: Server side components for the Pivotal Data Science Marketplace prototype app for IoT
   Author: Srivatsan Ramanujam <sramanujam@pivotal.io>, 28-May-2015
"""

import os
from flask import Flask, render_template
from flask.ext.assets import Bundle, Environment
import pandas.io.sql as psql
import psycopg2
import logging
import ConfigParser

#init app
app = Flask(__name__)

#init logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#init flask assets
bundles = {
    'user_js': Bundle(
           'js/heatmap.js',
           output='gen/user.js',
        ),
    'user_css': Bundle(
           'css/custom.css',
           output='gen/user.css'
        )   
}
assets = Environment(app)
assets.register(bundles)

#Initialize config parser
conf = ConfigParser.ConfigParser()

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
        default_port = 9090
        #Read database credentials from user supplied file
        basepath = os.path.dirname(__file__)
        conf.read(os.path.join(basepath,'user.cred'))
        logger.debug('Config sections:'+','.join(conf.sections()))
        #host, port, user, database, password
        host = conf.get('database_creds','host')
        port = conf.get('database_creds','port')
        user = conf.get('database_creds','user')
        database = conf.get('database_creds','database')
        password = conf.get('database_creds','password')
        conn = psycopg2.connect("""dbname='{database}' user='{user}' host='{host}' port='{port}' password='{password}'""".format
                     (
                         database=database,
                         host=host,
                         port=port,
                         user=user,
                         password=password
                     )
               )
        df = psql.read_sql('select x, x+random() as y from generate_series(1,10) x;',conn)
        logger.debug('Read SQL: {nrows}'.format(nrows=df.size))

    app.run(host='0.0.0.0', debug=True, port=default_port)
