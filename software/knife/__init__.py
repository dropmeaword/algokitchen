import os, sys
import logging

import cookbook
from chef.models import *
from storm.locals import *

class FoodImporter:
	__source__ = "Undefined"

class PostProcessingTool:
    """Post processing tools are used to massage the imported data into workable formats
    total processed: {0}
    failed to process: {1}
    """
    def __init__(self):
        logging.debug('Init...')
        self.stats = {}
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
            print "res:", res
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
            self.finalize()
            if self.book: self.book.close()
            logging.info('Finished. Goobye!')
