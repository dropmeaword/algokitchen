import sys, os
import random, string, time
import logging
import chef
from chef.models import *
from storm.locals import *
from storm.expr import And
from knife import *
import cookbook
from pprint import pprint

## ###################################################################
class MappingFoodstuffs(PostProcessingTool):
    """ Mapping of foodstuffs relative frequencies.
    total: {0}
    skipped: {1}
    """
    def query(self):
        # sql = SQL("""SELECT r.id FROM recipes r
        # JOIN recipes_ingredients r2i
        # ON r2i.recipe_id = r.id
        # WHERE r2i.ingredient_id IN (
        #     SELECT i.id
        #     FROM ingredients i, foodstuffs fs
        #     JOIN ingredients_foodstuffs i2f
        #     ON (i2f.ingredient_id = i.id AND i2f.foodstuff_id = fs.id)
        #     WHERE fs.name LIKE ? LIMIT 1)""", ('apricot%',) )

        #sql = SQL("""SELECT * FROM foodstuffs fs WHERE fs.name LIKE ?""", ('apricot%',))
        return self.book.execute("""SELECT r.* FROM recipes r
        JOIN recipes_ingredients r2i
        ON r2i.recipe_id = r.id
        WHERE r2i.ingredient_id IN (
            SELECT i.id
            FROM ingredients i, foodstuffs fs
            JOIN ingredients_foodstuffs i2f
            ON (i2f.ingredient_id = i.id AND i2f.foodstuff_id = fs.id)
            WHERE fs.name LIKE ?)""", ('apricot',) ) #find(Foodstuff, sql)

        # return self.book.find(Recipe, sql)

    def finalize(self):
        logging.info(self.__doc__.format(self.stats['processed'], self.stats['failed']))
        # t = Trail()
        # t.what = self.__doc__.format(self.stats['processed'], self.stats['failed'])
        # t.script = os.path.basename(sys.argv[0])
        # self.book.add(t)
        # self.book.commit()

    def processOne(self, item):
        try:
            pprint(item) #"id:", item.id, "name:", item.name
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
    fn = MappingFoodstuffs()
    fn.run()
