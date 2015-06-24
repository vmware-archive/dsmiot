"""
   IoT demo: Server side components for the Pivotal Data Science Marketplace prototype app for IoT
   Author: Srivatsan Ramanujam <sramanujam@pivotal.io>, 28-May-2015
"""
import os
import json
from flask import Flask, render_template, jsonify, request
from flask.ext.assets import Bundle, Environment
import logging
from dbconnector import DBConnect
from sql.queries import *

#init app
app = Flask(__name__)

#init logger
logging.basicConfig(level= logging.DEBUG if not os.getenv('VCAP_APP_PORT') else logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#init flask assets
bundles = {
    'user_js': Bundle(
           'js/heatmap.js',
           'js/tseries.js',
           'js/modelcoefs.js',
           filters='jsmin' if os.getenv('VCAP_APP_PORT') else None, #minify if deploying on CF
           output='gen/user.js',
        ),
    'user_css': Bundle(
           'css/custom.css',
           filters='jsmin' if os.getenv('VCAP_APP_PORT') else None, #minify if deploying on CF
           output='gen/user.css'
        )   
}
assets = Environment(app)
assets.register(bundles)

#Initialize database connection objects
conn = DBConnect(logger)

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
    
@app.route('/settings')
def settings():
    """
       Settings page (for model building)
    """
    logger.debug('In settings()')
    return render_template('settings.html')    

@app.route('/<path:path>')
def static_proxy(path):
    """
       Serving static files
    """
    logger.debug('In static_proxy()')
    return app.send_static_file(path)

@app.route('/_drillrig_hmap')    
def drillrig_heatmap():
    """
        Populate the drill-rig heatmap
    """
    global conn
    INPUT_SCHEMA = 'iot'
    INPUT_TABLE = 'drilling_data_1000_arr_1hr_ahead_wid'
    sql = extract_predictions_for_heatmap(INPUT_SCHEMA, INPUT_TABLE)
    logger.info(sql)
    df = conn.fetchDataFrame(sql)
    logger.info('drillrig_heatmap: {0} rows'.format(len(df)))
    return jsonify(hmap=[{'well_id':r['well_id'], 'hour':r['hour'], 'prob':r['prob']} for indx, r in df.iterrows()])
    
@app.route('/_mdl_coefs')    
def fetch_model_coefficients():
    """
        Retrieve model coefficients
    """
    global conn
    INPUT_SCHEMA = 'iot'
    INPUT_TABLE = 'output_from_model_train'
    sql = extract_model_coefficients(INPUT_SCHEMA, INPUT_TABLE)
    logger.info(sql)
    df = conn.fetchDataFrame(sql)
    features = ['feature', 'coef']
    result = [{k:r[k] for k in features} for indx, r in df.iterrows()] 
    logger.info('mdlcoefs:'+str(len(result)))
    return jsonify(mdlcoefs = result)
    
@app.route('/_drillrig_tseries', methods=['GET'])    
def drillrig_tseries():
    """
        Populate the drill-rig time-series of features
    """
    global conn
    INPUT_SCHEMA = 'iot'
    INPUT_TABLE = 'drilling_data_1000'
    well_id = long(request.args.get('well_id'))
    hour_of_day = int(request.args.get('hour'))
    sql = extract_features_for_tseries(INPUT_SCHEMA, INPUT_TABLE, well_id, hour_of_day)
    logger.info(sql)
    df = conn.fetchDataFrame(sql)
    logger.info('drillrig_tseries: {0} rows'.format(len(df)))
    features = set(['ts_utc','rpm','depth','rpm','rop','wob','flow_in_rate','bit_position'])
    result = [{k:r[k] for k in features} for indx, r in df.iterrows()] 
    logger.info('tseries:'+str(len(result)))
    return jsonify(tseries= result)

def main():
    """
       Start the application
    """
    app_port = int(os.getenv('VCAP_APP_PORT')) if os.getenv('VCAP_APP_PORT') else 9090
    app.run(host='0.0.0.0', debug= True if not os.getenv('VCAP_APP_PORT') else False, port = app_port)
