# This file contains the WSGI configuration required to serve up your
# web application at http://waveguide.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#

# +++++++++++ GENERAL DEBUGGING TIPS +++++++++++
# getting imports and sys.path right can be fiddly!
# We've tried to collect some general tips here:
# https://help.pythonanywhere.com/pages/DebuggingImportError


import sys

path = '/home/waveguide/wave_guide'
if path not in sys.path:
    sys.path.append(path)

from dotenv import load_dotenv
load_dotenv('/home/waveguide/wave_guide/.env')

from app import app as application # noqa