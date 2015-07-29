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
from knife.bbcfood import BBCFood
from lxml import html

duplicated = 0
found = 0

def fetch_all_pictures(filein):
    global duplicated, found

    book = Store( cookbook.open() )
    with open(filein, "r") as fin:
        reader = csv.reader(fin, delimiter=',', skipinitialspace=True)
        for line in reader:
            fsname = line[0]
            uri = line[1]
            fetchurl = BBCFood.BASE_URL.format(uri)

            # see if we find a corresponding foodstuff
            fsname = fsname.strip()
            print ">>> foodstuff:", fsname
            res = book.find(Foodstuff, Foodstuff.name.like( unicode(fsname, 'utf-8')) ).any()
            print res

            if res:
                logging.warning("Ingredient found, will update...")
                must_update = True
            else:
                must_update = False

            # sleep for a bit between requests
            nap = 2.0 / random.randrange(1, 8)
            time.sleep( nap )
            # do the actual fetching
            #logging.debug( "Fetching foodstuff at {0}".format(fetchurl) )
            page = requests.get(fetchurl)

            if (page.status_code == 200):
                markup = page.text
                tree = html.fromstring(markup)

                # picture of foodstuff
                picnode = tree.xpath('//img[@id="food-image"]')
                img = None
                if picnode:
                    imgurl = picnode[0].attrib['src']
                    existing = book.find(Image, Image.url == imgurl).any()
                    if not existing:
                        img = Image()
                        img.url = imgurl
                        img.description = unicode(picnode[0].attrib['alt'].encode(BBCFood.ENCODING), 'utf-8')
                        img.width = int(picnode[0].attrib['width'])
                        img.height = int(picnode[0].attrib['height'])
                        logging.info("Image found: {0}, ({1}x{2}), {3}".format(img.url,img.width, img.height, repr(img.description) ))
                        found += 1

                        book.add(img)
                        book.commit()

                        if must_update:
                            res.photo_id = img.id
                            book.commit()
                        logging.debug("Added image") # id: ", res.photo_id)
                    else:
                        if must_update:
                            res.photo_id = existing.id
                            book.commit()
                        duplicated += 1
                        logging.debug("Assigned image") # id {0} to foodstuff {1}".format(res.photo_id, res.name))


def main():
    try:
        fetch_all_pictures("ingredients-original.txt")
    except KeyboardInterrupt, e:
        logging.info("Seems like you want to exit")
    finally:
        # report before finishing
        logging.info("Pictures found: {0}, duplicated: {1}.".format(found, duplicated))
        logging.info("Finished. Goodbye!")

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
