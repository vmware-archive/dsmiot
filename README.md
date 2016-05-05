Predictive Maintenance for Drilling Operations
=================================================

![Predictive Maintenance for Drilling Operations](https://github.com/pivotalsoftware/dsmiot/raw/gh-pages/img/predim_1080p.gif)

Pre-requisites
==============
The `conda_requirements.txt` file lists all the python packages that are available via `conda` and are pre-requisites for this app.
The `requirements.txt` file lists all python packages that are only available through `pip` and are pre-requisities for this app.

Code Organization
==================
```
dsmiot/ # root level folder containing all package files & app files
    README.md # This file
    conda_requirements.txt # file containing all `conda` packages needed by this app.
    requirements.txt # file containing all `pip` packages needed by this app (not available via `conda`)
    deploy # bash script to deploy this app (either locally or on PCF)
    setup.py # python packaging tools
    MANIFEST.in #Manifest file for python packaging (what files to include into the python package)
    LICENSE.txt #License for this app    
    predim/
        server.py #Main module containing all controller code
        static/
           css/ #All user specified css. These will be bundled & minified into "gen/user_css.css" by Flask-Assets.    
           data/   
           img/    
           js/ #All user specified javascript. These will all be bundled & minified into "gen/user_js.js" by Flask-Assets.    
           vendor/ #All bootstrap.js related files (css & javascript)
        templates/ #HTML templates
           layout.html  #Base layout from which every page will inherit. This also contains javascript & css inserts
           home.html #home page template
           about.html #about page template
           contact.html #contact page template
```

Starting the app locally
========================

1. Create a file ```predim/user.cred``` with the relevant database access credentials like the following. This file will not be added to your version control (the `.gitignore` file will filter it out):
```
[database_creds]
host: <YOUR HOSTNAME>
port: <YOUR PORT>
user: <YOUR USERNAME>
database: <YOUR DATABASE>
password: <YOUR PASSOWRD>
```
2. Ensure your local machine can talk to the environment where the data resides in (ex: you may need to connect to a VPN if your data resides on a cluster behind a firewall)
3. Run the following from the root directory
```
./deploy
```
This will bring up the app on http://localhost:9090

Pushing the app to PCF
======================

1. Push the app to your PCF instance (assuming you've set one up)
```
dsmiot [master●●] cf push predimcf  -f manifest.yml    
```
2. Create User Provided Service for database credentials (first time only)
```
dsmiot [master●●] cf cups predimcreds -p '{"host":"<HOST>","user":"<USER>","password":"<PASSWORD>", "database":"<DATABASE>", "port":"<PORT>" }'
```
3. Bind the User Provided Service to the app (first time only)
```
dsmiot [master●●] cf bind-service predimcf predimcreds
```
The app should now be accessible on your PCF instance. In our case, at http://predimcf.pcf1-sc.vchs.pivotal.io/
