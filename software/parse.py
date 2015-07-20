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


SAMPLES = ['http://www.bbc.co.uk/food/recipes/quailpoachedandroast_88477', # no-image, 4 stages
'http://www.bbc.co.uk/food/recipes/chicken_with_asparagus_44206' # images and unicode
]

def tag_ingredient(txt):
	""" POS tag ingredient line """
	text = nltk.word_tokenize(txt)
	posTagged = pos_tag(text)
	simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]
	print(simplifiedTags)

def parse_recipe_by_url(fetchurl):
	# find recipe by url
	book = Store( cookbook.open() )
	res = book.find(Webpage, Webpage.url == unicode(fetchurl, 'utf-8')).any()
	book.close()
	# if found, parse it
	if res:
		recipe = bbcfood.RecipeParser(res.html)
		for ing in recipe.ingredients:
			import unicodedata
			unicodedata.numeric(ing)
			tag_ingredient(ing.encode('utf-8'))

def main():
	try:
		for r in SAMPLES:
			parse_recipe_by_url(r)
	except KeyboardInterrupt, e:
		logging.info("Seems like you want to exit")
	finally:
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
