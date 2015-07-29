from storm.locals import *
import inspect
import logging
from pprint import pprint

def image_from_url(url):
	"""Return a PIL image from a URL"""
	from PIL import Image
	import urllib, cStringIO

	fimg = cStringIO.StringIO(urllib.urlopen(url).read())
	return Image.open(fimg)

# from chef import Chef
#
# def process_recipes():
# 	pass
#
# def load_recipe():
# 	pass
#
#
# def main():
# 	c = Chef()
# 	c.initialize()
#
# if __name__ == '__main__':
# 	main()
#

class Chef:
	def __init__(self, dbname = "cookbook.db"):
		logging.debug("Opening database {0}".format(dbname))
		db = create_database( "sqlite:{0}".format(dbname) )
		self.store = Store(db)

	def initialize(self):
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
			mdl = obj()
			print("{0} -> {1} on table '{2}'".format(name, obj, mdl.__storm_table__))
			#store.add(mdl)
			pprint(mdl)
			self.store.add(mdl)

		self.store.commit()

	def test(self):
		from chef.models import Webpage

		wp = Webpage()
		wp.url = u"http://www.sevillasantajusta.tld"
		wp.html = u"<html><body></body></html>"
		wp.source = u"Sevilla"
		self.store.add(wp)

		# @todo how to select and update a record

		# add record manually
		self.store.execute("INSERT INTO webpage ('url', 'html', 'source') VALUES(?, ?, ?)", ['http://www.test.tld', '<html></html>', 'Test Food'])

		#self.store.execute('UPDATE bars SET bar_name=? WHERE bar_id like ?', [])
		self.store.commit()
