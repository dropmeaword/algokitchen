import random, string, time
import logging
from pprint import pprint
from lxml import html
import requests
import urllib

__doc__ = """ Rip the whole BBC Food recipes website """

letters = "abcdefghijklamnoprstuvwyz"
INDEX_URL = "http://www.bbc.co.uk/food/ingredients/by/letter/"
SEARCH_URL = "http://www.bbc.co.uk/food/recipes/search?{0}" 

ENCODING = "latin-1"

def example():
	page = requests.get('http://www.bbc.co.uk/food/ingredients/by/letter/a')
	# page
	# <Response [200]>
	tree = html.fromstring(page.text) 
	ingredients = tree.xpath('//li[@class="resource food"]/a/text()')

def find_all_ingredients():
	""" return a list of tuples containing (ingredient, url) """
	total = 0
	with open("ingredients.txt", "a+") as f:
		for a in letters:
			found = 0
			page = requests.get("http://www.bbc.co.uk/food/ingredients/by/letter/{0}".format(a))
			tree = html.fromstring(page.text) 
			ingredients = tree.xpath('//li[@class="resource food"]/a')
			for i in ingredients:
				# if it's a "related" link instead of an actual ingredient skip
				if 'related-foods ingredient' in i.attrib.values():
					continue
				name = i.text_content()
				name = name.strip().encode(ENCODING)
				url  = i.attrib['href']
				f.write("{0}, {1}\n".format(name, url))
				found = found + 1

			# keep count
			total = total + found
			# random delay to prevent hammering the server
			nap = 4.0 / random.randrange(1, 8)
			print("{0} ingredients starting with letter '{1}' were found out of {2} total found so far.".format(found, a, total))
			print("Sleeping for {0} before continuing...".format(nap))
			time.sleep( nap )

def find_recipe_urls(etree):
	"""
	in <div id="article-list">
	find all:
	<li class="article no-image"><div class="left"><h3><a href="/food/recipes/vodkasoakedcherrytom_70018">Vodka-soaked cherry tomatoes</a></h3>

	or:
	"""
	#print etree
	recipes = []
	# get address and name of recipe
	entries = etree.xpath('//div[@id="article-list"]/ul/li')
	#pprint(entries)
	for li in entries:
		lnk = li.xpath('div/h3/a')
		if len(lnk)>0:
			#pprint(lnk[0])
			url  = lnk[0].attrib['href']
			name = lnk[0].text_content().encode(ENCODING)
			print url, name
			recipes.append((url, name))

	return recipes

def search_recipes_per_ingredient(ingredient, page=1):
	# build the query string for a given ingredient
	qstring = urllib.urlencode({'keywords': ingredient, 'page' : page})
	searchurl = SEARCH_URL.format(qstring)
	logging.debug( "Requesting {0}".format(searchurl) )
	page = requests.get(searchurl)
	# parse content of response
	tree = html.fromstring(page.text) 

	# fetch description
	"""
	loop increasing page number untill:
	<meta name="description" content="No results" />
	"""
	desc = tree.xpath('//head/meta[@name="description"]')
	pprint(desc)
	if len(desc)>0:
		desctxt = desc[0].attrib['content'].encode(ENCODING)
		logging.debug( desctxt )
		# when this string is found we know that the are no more result pages
		if "No results" in desctxt:
			logging.debug("No recipes were found on this page")
			return None
		elif "Recipe search results for" in desctxt:
			"""
			Check that this heade ris there: 
			<meta name="description" content="Recipe search results for cherry tomatoes " />
			
			Get total results from:
			<div id="queryBox">
				<h2>Recipes with keyword cherry tomatoes.</h2>
				<p>401 results found</p>
			</div>
			"""
			found = tree.xpath('//div[@id="queryBox"]/p')
			qty = found[0].text_content().encode(ENCODING)
			logging.info(qty)
			logging.debug("Page contains: {0}".format(qty))
			urls = find_recipe_urls(tree)
			return urls
		else:
			logging.warning("Search result returned unknown header, format might have changed.")

def find_all_recipe_urls():
	with open("ingredients.txt", "r") as fin:
		for line in fin:
			ingredient, uri = line.split(',')
			logging.debug( "Searching for recipes containing ingredient {0}".format(ingredient) )
			#search_recipes_per_ingredient( line.strip() )

def main():
	logging.info("Trying to find all ingredients in the BBC Food website...")
	#find_all_ingredients()
#	find_all_recipe_urls()
	page = 1
	allrecipes = []
	while True:
		res = search_recipes_per_ingredient("caviar", page)
		if res:
			allrecipes.extend(res)
			page += 1
		else:
			break

	# pprint(allrecipes)

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
