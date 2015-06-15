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
from knife.bbcfood import BBCFood

SAMPLES = ['http://www.bbc.co.uk/food/recipes/quailpoachedandroast_88477', # no-image, 4 stages 
'http://www.bbc.co.uk/food/recipes/chicken_with_asparagus_44206' # images and unicode
]

def parse_recipe_by_url(fetchurl):
	# find recipe by url
	book = Store( cookbook.open() )
	res = book.find(Webpage, Webpage.url == unicode(fetchurl, 'utf-8')).one()
	book.close()
	# if found, parse it
	if res:
		bbc = bbcfood.RecipeParser(res.html)

def main():
	try:
		for r in SAMPLES:
			parse_recipe_by_url(r)
	except KeyboardInterrupt, e:
		logging.info("Seems like you want to exit")
	finally:
		# report before finishing
		logging.info("Recipes fetched: {0}, saved: {1}, duplicated: {2}.".format(fetched, saved, duplicated))
		logging.info("Finished. Goodbye!")

if __name__ == '__main__':
	#logging.basicConfig(filename="importer.bbcfood.log")
	logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s %(message)s")
	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	# add the handler to the root logger
	logging.getLogger('').addHandler(console)
	main()
