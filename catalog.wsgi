activate_this = "/var/www/udacity-catalog/venv/bin/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0,"/var/www/udacity-catalog/")

from project import app as application
application.secret_key = 'super_secret_key'
