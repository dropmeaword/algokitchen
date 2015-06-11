import random, string, time
import logging
import chef
import requests
import urllib
import csv
from chef.models import *
import knife
from knife.bbcfood import BBCFood

duplicated = 0
fetched = 0
saved = 0

def fetch_all_recipes(filein="recipes.txt"):
	global duplicated, fetched, saved
	c = chef.Chef()
	with open(filein, "r") as fin:
		reader = csv.reader(fin, delimiter=',', skipinitialspace=True)
		for line in reader:
			uri = line[0]
			title = line[1]
			fetchurl = BBCFood.BASE_URL.format(uri)
			res = c.store.find(Webpage, Webpage.url == unicode(fetchurl, 'utf-8')).any()
			if not res:
				# sleep for a bit between requests
				nap = 2.0 / random.randrange(1, 8)
				time.sleep( nap )
				# do the actual fetching
				logging.debug( "Fetching recipe at {0}".format(fetchurl) )
				page = requests.get(fetchurl)
				fetched += 1

				if (page.status_code == 200):
					logging.debug("Saving webpage...")
					wp = Webpage()
					wp.title = unicode(title, 'utf-8')
					wp.url = unicode(fetchurl, 'utf-8')
					wp.source = unicode(BBCFood.__source__, 'utf-8')
					wp.html = page.text
					c.store.add(wp)
					c.store.commit()
					saved += 1
				else:
					logging.warning( "Failed to fetch: {0}".format(fetchurl) )
			else:
				logging.debug( "Duplicate found: {0}".format(fetchurl) )
				duplicated += 1

def main():
	try:
		fetch_all_recipes("recipes.txt")
	except KeyboardInterrupt, e:
		logging.info("Seems like you want to exit")
	finally:
		# report before finishing
		logging.info("Recipes fetched: {0}, saved: {1}, duplicated: {2}.".format(fetched, saved, duplicated))
		logging.info("Finished. Goodbye!")
	# c = chef.Chef()
	# res = c.store.find(Webpage, Webpage.source == u"invalid.tld").one()
	# if res:
	# 	print("Record already exists!")
	# 	print res
	# else:
	# 	print("Adding record...")
	# 	wp = Webpage()
	# 	wp.title = page['title']
	# 	wp.url = page['url']
	# 	wp.source = page['source']
	# 	wp.html = page['html']
	# 	c.store.add(wp)
	# 	c.store.commit()

## entry point
## #################################################################
if __name__ == '__main__':
	#logging.basicConfig(filename="importer.bbcfood.log")
	logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s %(message)s")
	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)
	# add the handler to the root logger
	logging.getLogger('').addHandler(console)
	main()
