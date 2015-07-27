import sys, os
from nltk.stem import WordNetLemmatizer


class PostProcessingTool:
    """Post processing tools are used to massage the imported data into workable formats
    total processed: {0}
    failed to process: {1}
    """
    def __init__(self):
        self.stats['processed'] = 0
        self.stats['failed']    = 0
        self.book = None

    def query(self):
        return None

    def finalize(self):
        t = Trail()
        t.what = self.__doc__.format(self.stats['processed'], self.stats['failed'])
        t.script = os.path.basename(sys.argv[0])
        self.book.add(t)
        self.book.commit()

    def processOne(self):
        pass

    def run(self):
        try:
            self.book = Store( cookbook.open() )
            res = self.query()
            if res:
                for r in res:
                    self.processOne(r)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            logging.error(str(e))
            self.stats['failed'] += 1
            # ad to our list of failures so that we can try some other time
            f = Fail()
            f.reason = str(e)
            self.book.add(f)
            self.book.commit()
        finally:
            if self.book: self.book.close()
            self.finalize()
            logging.info('Finished. Goobye!')


# http://regexr.com/
# (\d+\gr?)|(\d+\ml)|(\d+\s?tsp)|(\d+\s?tbsp)
def match_ingredient_amounts():
    re = r"\d+\g\r"
    pass

def foodstuff_normalize_name(name):
    pass


wnl = WordNetLemmatizer()

def foodstuff_normalize_name(foodstuff):
    """ normalize foodstuff, makes word lowercase and singular """
    lemma = ""
    words = foodstuff.strip().split()
    for w in words:
        lemma += wnl.lemmatize(w.lower(), 'n') + " "
        print "int:", w, lemma

    return lemma.strip()

# nounls = ['geese', 'mice', 'bars', 'foos', 'foo',
#                 'families', 'family', 'dog', 'dogs']

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
