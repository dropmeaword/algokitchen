from storm.locals import *
import inspect
import logging
from pprint import pprint

class Chef:
	def __init__(self, dbname = "cookbook.db"):
		db = create_database( "sqlite:{0}".format(dbname) )
		self.store = Store(db)

	def initialize():
		try:
			import chef.models
		except ImportError as e:
			logging.exception("Failed to import models")

		def predicate(c):
			#print c.__module__
			return inspect.isclass(c) and c.__module__ == 'chef.models'

		classes = inspect.getmembers(chef.models, predicate)
		print("*"*60)
		print("Adding types to database:")
		pprint(classes)
		print("*"*60)
		for name, obj in classes:
			print("{0}<{1}>".format(name, obj))
			mdl = obj()
			#store.add(mdl)
			pprint(mdl)
			pprint(mdl.__storm_table__)
			self.store.add(mdl)

		self.store.commit()

	def test():
		self.store.execute('UPDATE bars SET bar_name=? WHERE bar_id like ?', []) 
		self.store.commit()
