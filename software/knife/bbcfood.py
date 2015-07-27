import random, string, time
import logging
from pprint import pprint
from lxml import html
import requests
import urllib
import csv
import isodate

from storm.locals import *
from chef.models import *
from knife import FoodImporter
from chef import Chef
import cookbook


def example():
    page = requests.get('http://www.bbc.co.uk/food/ingredients/by/letter/a')
    # page
    # <Response [200]>
    tree = html.fromstring(page.text)
    ingredients = tree.xpath('//li[@class="resource food"]/a/text()')

class BBCFood(FoodImporter):
    """ Rip from BBC Food recipes website """
    __source__ = "BBC Food (http://www.bbc.co.uk/food/)"

    alphabet = "abcdefghijklamnoprstuvwyz"
    INDEX_URL = "http://www.bbc.co.uk/food/ingredients/by/letter/{0}"
    SEARCH_URL = "http://www.bbc.co.uk/food/recipes/search?{0}"
    BASE_URL = "http://www.bbc.co.uk{0}"

    ENCODING = "latin-1"

    def rip(self, fetchurl):
        """ fetch and store a single url """
        book = Store( cookbook.open() )
        res = book.find(Webpage, Webpage.url == unicode(fetchurl, 'utf-8')).any()

        wp = None
        if not res:
            logging.debug( "Fetching recipe at {0}".format(fetchurl) )
            page = requests.get(fetchurl)
            if (page.status_code == 200):
                # get title
                title = "Untitled"
                tree = html.fromstring(page.text)
                tnode = tree.xpath('//h1[@class="fn "]')  # violates hRecipe in that it has a space
                if tnode:
                    title = tnode[0].text_content().encode(BBCFood.ENCODING)

                # store in db
                logging.debug("Saving webpage...")
                wp = Webpage()
                wp.title = unicode(title, 'utf-8')
                wp.url = unicode(fetchurl, 'utf-8')
                wp.source = unicode(BBCFood.__source__, 'utf-8')
                wp.html = page.text  # should be unicode too?
                book.add(wp)
                book.commit()
                book.close()
            else:
                logging.warning( "Failed to fetch: {0}".format(fetchurl) )
        else:
            logging.debug( "Duplicate found: {0}".format(fetchurl) )
            del res

        del book
        return wp


    def find_all_ingredients(self):
        """ return a list of tuples containing (ingredient, url) """
        total = 0
        with open("ingredients.txt", "a+") as f:
            for a in BBCFood.alphabet:
                found = 0
                page = requests.get(BBCFood.INDEX_URL.format(a))
                tree = html.fromstring(page.text)
                ingredients = tree.xpath('//li[@class="resource food"]/a')
                for i in ingredients:
                    # if it's a "related" link instead of an actual ingredient skip
                    if 'related-foods ingredient' in i.attrib.values():
                        continue
                    name = i.text_content()
                    name = name.strip().encode(BBCFood.ENCODING)
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

    def find_recipe_urls(self, etree):
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
                name = lnk[0].text_content().encode(BBCFood.ENCODING)
                print url, name
                recipes.append((url, name))

        return recipes

    def search_recipes_per_ingredient(self, ingredient, page=1):
        # build the query string for a given ingredient
        qstring = urllib.urlencode({'keywords': ingredient, 'page' : page})
        searchurl = BBCFood.SEARCH_URL.format(qstring)
        logging.debug( "Requesting {0}".format(searchurl) )
        page = requests.get(searchurl)

        # quit the parsing if http response isn't what we are after
        if not (page.status_code == 200):
            return None

        # parse content of response
        tree = html.fromstring(page.text)

        # fetch description
        """
        loop increasing page number untill this is found:
        <meta name="description" content="No results" />
        """
        desc = tree.xpath('//head/meta[@name="description"]')
        pprint(desc)
        if len(desc)>0:
            desctxt = desc[0].attrib['content'].encode(BBCFood.ENCODING)
            logging.debug( desctxt )
            # when this string is found we know that the are no more result pages
            if "No results" in desctxt:
                logging.debug("No recipes were found on this page")
                return None
            elif "Recipe search results for" in desctxt:
                """
                Check that this header is there:
                <meta name="description" content="Recipe search results for cherry tomatoes " />

                Get total results from:
                <div id="queryBox">
                    <h2>Recipes with keyword cherry tomatoes.</h2>
                    <p>401 results found</p>
                </div>
                """
                found = tree.xpath('//div[@id="queryBox"]/p')
                qty = found[0].text_content().encode(BBCFood.ENCODING)
                logging.info(qty)
                logging.debug("Page contains: {0}".format(qty))
                urls = self.find_recipe_urls(tree)
                return urls
            else:
                logging.warning("Search result returned unknown header, format might have changed.")

    def save_recipe_urls(self, urls):
        total = 0
        with open("recipes.txt", "a+") as fout:
            for url, title in urls:
                fout.write("{0}, \"{1}\"\n".format(url, title))

    def find_all_recipe_urls(self):
        with open("ingredients.txt", "r") as fin:
            for line in fin:
                ingredient, uri = line.split(',')
                logging.debug( "#### Searching for recipes containing ingredient {0}".format(ingredient) )

                # for each ingredient parse all search pages
                ingredient = ingredient.strip()
                page = 1
                allrecipes = []
                while True:
                    res = self.search_recipes_per_ingredient(ingredient, page)
                    if res:
                        allrecipes.extend(res)
                        page += 1
                        # do not hammer the server, do a little random waiting
                        nap = 4.0 / random.randrange(1, 8)
                        time.sleep(nap)
                    else:
                        break # out of the while

                self.save_recipe_urls(allrecipes)

    def fetch_recipe(self, url, title):
        pass

    def fetch_all_recipes(self):
        with open("recipes.txt", "r") as fin:
            reader = csv.reader(csvfile, delimiter=', ', quotechar='"')
            for line in reader:
                from chef import models
                Webpage
                fetchurl = BBCFood.BASE_URL.format(qstring)
                logging.debug( "Fetching recipe at {0}".format(fetchurl) )
                page = requests.get(fetchurl)

                # quit the parsing if http response isn't what we are after
                if not (page.status_code == 200):
                    return None

        # parse content of response
        tree = html.fromstring(page.text)

    def scrape_site(self):
        logging.info("Trying to find all ingredients in the BBC Food website...")
        bbc.find_all_ingredients()
        logging.info("Getting urls for all recipes...")
        bbc.find_all_recipe_urls()


class RecipeParser:
    """ The BBCFood website presents the data in hRecipe format
    http://microformats.org/wiki/hrecipe
    """
    def __init__(self, url, markup, db):
        self.db = db #Store( cookbook.open() )

        self.ingredient_ordinal = 1

        self.stats = {}
        self.stats['ingredients'] = 0
        self.stats['ingredients_added'] = 0
        self.stats['foodstuffs'] = 0
        self.stats['foodstuffs_added'] = 0
        self.stats['images'] = 0
        self.stats['images_added'] = 0
        self.stats['preparations'] = 0
        self.stats['skipped'] = 0

        rez = self.db.find(Recipe, Recipe.url == url).any()
        if rez:
            logging.debug('Skipping.')
            self.stats['skipped'] += 1
            return

        recipe = Recipe()
        tree = html.fromstring(markup)
        tnode = tree.xpath('//h1[@class="fn "]')  # title of recipe
        #self.title = tnode[0].text_content().encode(BBCFood.ENCODING)
        recipe.url = url
        recipe.name = unicode(tnode[0].text_content().encode(BBCFood.ENCODING), 'utf-8') #.encode(BBCFood.ENCODING) #unicode(self.title, BBCFood.ENCODING)
        logging.info("Title: {0}".format(repr(recipe.name)))

        # picture of dish
        picnode = tree.xpath('//img[@id="food-image"]')
        img = None
        if picnode:
            self.stats['images'] += 1
            img = Image()
            img.url = picnode[0].attrib['src']
            img.description = unicode(picnode[0].attrib['alt'].encode(BBCFood.ENCODING), 'utf-8')
            img.width = int(picnode[0].attrib['width'])
            img.height = int(picnode[0].attrib['height'])
            #print("Image found: {0}, ({1}x{2}), {3}".format(img.url,img.width, img.height, repr(img.description) ))
            existing = self.db.find(Image, Image.url == img.url).any()
            if not existing:
                self.db.add(img)
                self.db.commit()
                recipe.photo_id = img.id
                #print "recipe photo id: ", recipe.photo_id
                self.stats['images_added'] += 1
            else:
                recipe.photo_id = existing.id

        # description of dish
        dnode = tree.xpath('//div[@id="description"]//span[@class="summary"]')
        if dnode:
            recipe.description = unicode(dnode[0].text_content().encode(BBCFood.ENCODING), 'utf-8')
            #print "Description: ", repr(recipe.description)

        # preparation time
        node = tree.xpath('//span[@class="prepTime"]/span[@class="value-title"]')
        if node:
            recipe.time_prep = node[0].attrib['title']
            td = isodate.parse_duration(recipe.time_prep)
            #print "Prep time: ", td

        # cooking time
        node = tree.xpath('//span[@class="cookTime"]/span[@class="value-title"]')
        if node:
            recipe.time_cook = node[0].attrib['title']
            td = isodate.parse_duration(recipe.time_cook)
            #print "Cook time: ", td

        # yield
        node = tree.xpath('//h3[@class="yield"]')
        if node:
            recipe.serves_txt = node[0].text_content().encode(BBCFood.ENCODING)
            #print "Yield: ", recipe.serves_txt

        self.db.add(recipe)
        self.db.commit()

        self.ingredients = []
        self.foodstuffs  = []
        nodes = tree.xpath('//dt[@class="stage-title"]')
        # is it a recipe with multiple stages?
        if len(nodes) > 0:
            for st in nodes:
                stage = st.text_content().encode(BBCFood.ENCODING)
                #print "STAGE ", stage
                inglst = st.getnext() # get sibling
                lst = inglst.xpath('.//li/p[@class="ingredient"]')
                #pprint(lst)
                ings = self.parse_ingredients(lst, recipe.id, stage)
                #pprint(ings)
                self.ingredients.extend(ings['ingredients'])
        else:
            # description of ingredients and normalized names
            nodes = tree.xpath('//div[@id="ingredients"]')
            inodes = nodes[0].xpath('//ul/li/p[@class="ingredient"]')
            self.ingredients = []
            ings = self.parse_ingredients(inodes, recipe.id)
            self.ingredients.extend(ings['ingredients'])

        if len(self.ingredients) < 1:
            f = Fail()
            f.url = url
            f.reason = "Didn't find any ingredients"
            self.db.add(f)
            self.db.commit()

        # print "+"*60
        # for fs in self.foodstuffs:
        #     print("foodstuff:", fs.name, fs)
        # print "+"*60

        self.preparations = []
        nodes = tree.xpath('//ol[@class="instructions"]/li[@class="instruction"]')
        self.parse_preparations(nodes, recipe.id)

        #self.db.close()

    def parse_ingredients(self, nodes, rid, stage=''):
        """
            Parse ingredients specified as:
            <p class="ingredient">1 <a href="/food/shallot" class="name food">shallot</a>, peeled, finely sliced</p>
        """
        #self.db = Store( cookbook.open() )
        # description of ingredients and normalized names
        ingredients = []
        if len(nodes) > 0:
            for i in nodes:
                # get ingredient name
                ingname = i.text_content().encode(BBCFood.ENCODING) # ingredient description
                # find the foodstuffs in this ingredient
                norms = i.xpath('a[@class="name food"]')  # ingredients, normalized names
                #print "ing: ", ing, " || stage: ", stage
                ing = self.db.find(Ingredient, Ingredient.name == unicode(ingname, 'utf-8')).any()
                self.stats['ingredients'] += 1
                if not ing:
                    ing = Ingredient()
                    ing.name = unicode(ingname, 'utf-8')
                    #ing.stage = unicode(stage, 'utf-8')
                    #ing.recipe_id = rid
                    self.stats['ingredients_added'] += 1

                    tmpfs = [] # temp array for foodstuffs
                    if norms:
                        for n in norms:
                            self.stats['foodstuffs'] += 1
                            norm = n.text_content().encode(BBCFood.ENCODING)
                            fs = self.db.find(Foodstuff, Foodstuff.name == unicode(norm, 'utf-8')).any()
                            if not fs:
                                #print("{0} NOT found in db".format(repr(name)))
                                fs = Foodstuff()
                                fs.name = unicode(norm, 'utf-8')
                                fs.normalized = unicode(norm, 'utf-8')
                                self.db.add(fs)
                                self.db.commit()
                                self.stats['foodstuffs_added'] += 1
                            # else:
                            #     print("{0} found in db".format(repr(name) ))

                            if not fs in self.foodstuffs:
                                #print("adding fs:", fs)
                                ing.foodstuffs.add(fs)
                                self.foodstuffs.append(fs)

                    self.db.add(ing)
                    self.db.commit()
                # else:
                #     logging.debug("already existing: {0}".format(repr(ing.name)))

                # add m2m ingredient-2-recipe
                i2r = RecipeIngredients()
                i2r.ordinal = self.ingredient_ordinal
                i2r.stage = unicode(stage, 'utf-8')
                i2r.recipe_id = rid
                i2r.ingredient_id = ing.id
                #print("adding {0} to {1} with ordinal {2}".format(ing.id, rid, self.ingredient_ordinal))
                self.db.add(i2r)
                self.db.commit()

                self.ingredient_ordinal += 1
                ingredients.append(ing)

        #self.db.close()
        return {'ingredients' : ingredients}

    def parse_preparations(self, nodes, rid):
        if len(nodes) > 0:
            ordinal = 1
            preparations = []
            for pnode in nodes:
                parafs = pnode.xpath('.//p')
                for p in parafs:
                    prep = Preparation()
                    prep.ordinal = ordinal
                    prep.recipe_id = rid
                    prep.description = unicode(p.text_content().encode(BBCFood.ENCODING), 'utf-8')
                    #print ordinal, ". prep:", p.text_content().encode(BBCFood.ENCODING)
                    # what foodstuffs are mentioned in this preparation step?
                    matches = [s for s in self.foodstuffs if s.name in prep.description]
                    #print("desc: ", prep.description)
                    for m in matches:
                        #print("found", m.name)
                        prep.foodstuffs.add(m)

                    self.db.add(prep)
                    self.db.commit()

                ordinal += 1
