from storm.locals import *
import inspect
import logging
from pprint import pprint


def open(dbname = "cookbook.db"):
	logging.debug("Opening database {0}".format(dbname))
	db = create_database( "sqlite:{0}".format(dbname) )
	return db
	#self.store = Store(db)
