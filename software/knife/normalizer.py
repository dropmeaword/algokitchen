import sys, os
import random, string, time
import logging
import chef
from chef.models import *
from storm.locals import *
from knife import *
import cookbook
from knife import bbcfood

from nltk.stem import WordNetLemmatizer


# http://regexr.com/
# (\d+\gr?)|(\d+\ml)|(\d+\s?tsp)|(\d+\s?tbsp)
def match_ingredient_amounts():
    re = r"\d+\g\r"
    pass

wnl = WordNetLemmatizer()
def foodstuff_normalize_name(foodstuff):
    """ normalize foodstuff, makes word lowercase and singular """
    lemma = ""
    words = foodstuff.strip().split()
    for w in words:
        lemma += wnl.lemmatize(w.lower(), 'n') + " "
        #print "int:", w, lemma

    return lemma.strip()

# nounls = ['geese', 'mice', 'bars', 'foos', 'foo',
#                 'families', 'family', 'dog', 'dogs']

def test_normalizer():
    nounls = [u"hot cross buns",
    u"papayas",
    u"Turkish delights",
    u"pulled pork",
    u"Mozzarella",
    u"Naan breads",
    u"Seasoning",
    u"Rocket",
    u"tamarillo",
    u"saucisson",
    u"forced rhubarb",
    u"Chicken Stock",
    u"pandan leaves",
    u"winkles",
    u"Cream",
    u"passion fruit juice",
    u"kiwi fruits",
    u"chocolate brownies",
    u"red leicester",
    u"grey mullets",
    u"teriyaki",
    u"butters",
    u"Christmas cake",
    u"whisky liqueur",
    u"soya oil",
    u"ouzo"]

    for nn in nounls:
        norm = foodstuff_normalize_name(nn)
        print ">>", nn, "|",norm


## ###################################################################
class NormalizeFoodstuffs(PostProcessingTool):
    """ Normalized foodstuffs names. Normalization consists on making names lowercase and singular.
    total: {0}
    skipped: {1}
    """
    def query(self):
        return self.book.find(Foodstuff) #, Foodstuff.name == u'papayas')

    def finalize(self):
        logging.info(self.__doc__.format(self.stats['processed'], self.stats['failed']))
        t = Trail()
        t.what = self.__doc__.format(self.stats['processed'], self.stats['failed'])
        t.script = os.path.basename(sys.argv[0])
        self.book.add(t)
        self.book.commit()

    def processOne(self, item):
        try:
            norm = foodstuff_normalize_name(item.name)
            # make change in db
            item.normalized = norm
            self.book.commit()
            # print to screen
            if norm is not item.name:
                print item.name, " -> ", norm
            self.stats['processed'] += 1
        except KeyboardInterrupt as e:
            raise
        except Exception as e:
            self.stats['failed'] += 1


if __name__ == '__main__':
    #logging.basicConfig(filename="importer.bbcfood.log")
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s %(message)s")
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    fn = NormalizeFoodstuffs()
    fn.run()
