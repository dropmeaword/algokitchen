import random, string, time
import logging
import chef
import requests
import urllib
import csv
from pympler import muppy, summary
from chef.models import *
from storm.locals import *
import knife
import cookbook
from knife import bbcfood
import unicodedata

import nltk
from nltk.tag import pos_tag, map_tag

stats = {}
stats['recipes'] = 0
stats['failed'] = 0
stats['recipes_added'] = 0
stats['foodstuffs'] = 0
stats['foodstuffs_added'] = 0
stats['ingredients'] = 0
stats['ingredients_added'] = 0

def main():
	book = None
	try:
		book = Store( cookbook.open() )
		res = book.find(Webpage)
		#book.close()
		# if found, parse it
		if res:
			for r in res:
				logging.info("importing: {0}".format(r.url) )
				try:
					parser = bbcfood.RecipeParser(r.url.encode('ascii'), r.html, book)
					stats['recipes'] += 1
					stats['foodstuffs'] += parser.stats['foodstuffs']
					stats['foodstuffs_added'] += parser.stats['foodstuffs_added']
					stats['ingredients'] += parser.stats['ingredients']
					stats['ingredients_added'] += parser.stats['ingredients_added']
					logging.info( "{0} ingredients found, {1} foodstuffs.".format(parser.stats['ingredients'], parser.stats['foodstuffs']) )
				except KeyboardInterrupt as e:
					raise
				except Exception as e:
					stats['failed'] += 1
					# ad to our list of failures so that we can try some other time
					f = Fail()
					f.url = r.url.encode('ascii')
					f.reason = str(e)
					book.add(f)
					book.commit()

		logging.info( "{0} recipes imported, {1} ingredients found of which {2} were unique, {3} foodstuffs found of which {4} were unique. Failed with {5} recipes.".format(stats['recipes'], stats['ingredients'], stats['ingredients_added'], stats['foodstuffs'], stats['foodstuffs_added'], stats['failed']) )
	except KeyboardInterrupt, e:
		logging.info("Seems like you want to exit")
	finally:
		if book: book.close()
		# report before finishing
		logging.info("Finished. Goodbye!")

if __name__ == '__main__':
	#logging.basicConfig(filename="importer.bbcfood.log")
	logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s %(message)s")
	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	# add the handler to the root logger
	logging.getLogger('').addHandler(console)
	main()
