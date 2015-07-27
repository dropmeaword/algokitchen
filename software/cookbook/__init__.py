from storm.locals import *
import inspect
import logging
from pprint import pprint
import sys

thismodule = sys.modules[__name__]

def open(dbname = "cookbook.db"):
	logging.debug("Opening database {0}".format(dbname))
	db = create_database( "sqlite:{0}".format(dbname) )
	return db
	#self.store = Store(db)

def store(obj):
	# store recipe in db
	book = Store( thismodule.open() )
	book.add(obj)
	retval = book.commit()
	book.close()
	return retval
