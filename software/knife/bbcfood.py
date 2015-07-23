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
    def __init__(self, markup):
        tree = html.fromstring(markup)
        tnode = tree.xpath('//h1[@class="fn "]')  # title of recipe
        self.title = tnode[0].text_content().encode(BBCFood.ENCODING)
        print("Title: {0}".format(self.title))

        # picture of dish
        picnode = tree.xpath('//img[@id="food-image"]')
        if picnode:
            imgurl = picnode[0].attrib['src'].encode(BBCFood.ENCODING)
            imgdesc = picnode[0].attrib['alt'].encode(BBCFood.ENCODING)
            imgw = picnode[0].attrib['width'].encode(BBCFood.ENCODING)
            imgh = picnode[0].attrib['height'].encode(BBCFood.ENCODING)
            print("Image found: {0}, ({1}x{2}), {3}".format(imgurl,imgw, imgh, imgdesc))

        # description of dish
        dnode = tree.xpath('//div[@id="description"]//span[@class="summary"]')
        if dnode:
            desc = dnode[0].text_content().encode(BBCFood.ENCODING)
            print "Description: ", desc

        # preparation time
        node = tree.xpath('//span[@class="prepTime"]/span[@class="value-title"]')
        if node:
            tprep = node[0].attrib['title'].encode(BBCFood.ENCODING)
            td = isodate.parse_duration(tprep)
            print "Prep time: ", td

        # cooking time
        node = tree.xpath('//span[@class="cookTime"]/span[@class="value-title"]')
        if node:
            tcook = node[0].attrib['title'].encode(BBCFood.ENCODING)
            td = isodate.parse_duration(tcook)
            print "Cook time: ", td

        # yield
        node = tree.xpath('//h3[@class="yield"]')
        if node:
            yld = node[0].text_content().encode(BBCFood.ENCODING)
            print "Yield: ", yld

        self.ingredients = []
        self.foodstuffs  = []
        nodes = tree.xpath('//dt[@class="stage-title"]')
        # is it a recipe with multiple stages?
        if len(nodes) > 0:
            for st in nodes:
                stage = st.text_content().encode('utf-8')
                #print "STAGE ", stage
                inglst = st.getnext() # get sibling
                lst = inglst.xpath('.//li/p[@class="ingredient"]')
                #pprint(lst)
                ings = self.parse_ingredients(lst, stage)
                #pprint(ings)
                self.ingredients.extend(ings['ingredients'])
                self.foodstuffs.extend(ings['foodstuffs'])
        else:
            # description of ingredients and normalized names
            nodes = tree.xpath('//div[@id="ingredients"]')
            inodes = nodes[0].xpath('//ul/li/p[@class="ingredient"]')
            self.ingredients = []
            ings = self.parse_ingredients(inodes)
            self.ingredients.extend(ings['ingredients'])
            self.foodstuffs.extend(ings['foodstuffs'])

        self.preparations = []
        nodes = tree.xpath('//ol[@class="instructions"]/li[@class="instruction"]')
        self.parse_preparations(nodes)

    def parse_ingredients(self, nodes, stage=''):
        """
            Parse ingredients specified as:
            <p class="ingredient">1 <a href="/food/shallot" class="name food">shallot</a>, peeled, finely sliced</p>
        """
        # description of ingredients and normalized names
        if len(nodes) > 0:
            ingredients = []
            foodstuffs = []
            for i in nodes:
                ing = i.text_content().encode("utf-8") # ingredient description
                #print "ing: ", ing, " || stage: ", stage
                ingredients.append(ing)
                norms = i.xpath('a[@class="name food"]')  # ingredients, normalized names
                if norms:
                    for n in norms:
                        norm = n.text_content().encode(BBCFood.ENCODING)
                        #print "norm: ", norm
                        foodstuffs.append(norm)

        return {'ingredients' : ingredients, 'foodstuffs': foodstuffs}

    def parse_preparations(self, nodes):
        if len(nodes) > 0:
            ordinal = 1
            preparations = []
            for pnode in nodes:
                parafs = pnode.xpath('.//p')
                for p in parafs:
                    print ordinal, ". prep:", p.text_content().encode("utf-8")

                ordinal += 1
