import os
import logging
import json
import bottle
from bottle import Bottle, route, template, get, post, request

__app__ = Bottle()

def init(wwwpath='../webapp/www', debug=True):
    """ Initialize logging and HTTP engine """
    logging.getLogger('').handlers = [] # clear any existing log handlers
    logging.basicConfig(level=logging.DEBUG)

    bottle.TEMPLATES.clear()  # clear template cache
    logging.debug( "Setting template path to {0}".format(wwwpath) )
    bottle.TEMPLATE_PATH.insert(0, wwwpath)

@route('/ping')
def hello():
    return "pong"

## Request handlers
@route('/', method='GET')
def home():
    logging.info("Get root!!!" )
    return bottle.template('index', title="algokitchen .:. pantry")

@route('/resources/<filename:path>')
def server_static(filename):
    root = os.path.join(os.getcwd(), '../webapp/www')
    logging.info("Requesting resource {0} in {1}".format(filename, root) )
    return bottle.static_file(filename, root=root)
