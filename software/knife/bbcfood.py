import random, string, time
from pprint import pprint
from lxml import html
import requests

__doc__ = """ Rip the whole BBC Food recipes website """

letters = "abcdefghijklamnoprstuvwyz"
INDEX_URL = "http://www.bbc.co.uk/food/ingredients/by/letter/"

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
				name = name.strip().encode("latin-1")
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

def find_all_recipe_urls():
	with open("ingredients.txt", "r") as f:
		for line in f:
			pass

if __name__ == '__main__':
	print("Trying to find all ingredients in the BBC Food website...")
	find_all_ingredients()

