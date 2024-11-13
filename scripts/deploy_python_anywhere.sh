#! /bin/bash

# this script can deploy wave-guide to pythonanywhere.
# There are a few manual steps before and after the script runs.


#PRE SCRIPT MANUAL STEPS

# 1. clone this repository into your pythonanywhere account 
# git clone https://github.com/jmc91/wave_guide.git

#2. go into this directory in the pythonanywere console
# cd wave_guide

# 3. copy the .env file into the wave_guide directory

# 4. run this script

# create virtual environment
# https://help.pythonanywhere.com/pages/Virtualenvs
mkvirtualenv myvirtualenv --python=/usr/bin/python3.7;
workon myvirtualenv;
pip install -r requirements.txt;

# update wsgi configuration
cp ./wsgi_pytonanywhere.py /var/www/waveguide_pythonanywhere_com_wsgi.py

#POST SCRIPT MANUAL STEPS

# 1. Go to the Web tab, and in the Virtualenv section, 
# enter the path: /home/myusername/.virtualenvs/myvirtualenv

# 2. Go to the Web tab, and reload the app
