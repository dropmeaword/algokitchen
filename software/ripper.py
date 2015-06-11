import logging
import knife
from knife import bbcfood

def main():
	bbc = bbcfood.BBCFood()
	# logging.info("Trying to find all ingredients in the BBC Food website...")
	# bbc.find_all_ingredients()

	logging.info("Getting urls for all recipes...")
	bbc.find_all_recipe_urls()
	# page = 1
	# allrecipes = []
	# while True:
	# 	res = bbc.search_recipes_per_ingredient("caviar", page)
	# 	if res:
	# 		allrecipes.extend(res)
	# 		page += 1
	# 		# do not hammer the server, do a little random waiting
	# 		nap = 4.0 / random.randrange(1, 8)
	# 		time.sleep(nap)
	# 	else:
	# 		break

	# # pprint(allrecipes)

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
