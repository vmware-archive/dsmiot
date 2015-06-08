Pre-requisites
==============
The conda_requirements.txt file lists all the python modules that are pre-requisites for this app.

Code Organization
==================
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

Starting the app locally
========================
Run the following from the root directory:
```
python setup.py build;python setup.py install;python -m predim
```
This will bring up the app on http://localhost:9090

Pushing the app to PCF
======================
Run the following
```
cf push iotdemo  -b git://github.com/ihuston/python-conda-buildpack.git -c ".conda/bin/python predim/server.py" -t 180 
```
