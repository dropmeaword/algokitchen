#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from storm.locals import *
from chef.models import *
from pprint import pprint
import random
import cookbook

PARAF = u"""Heat half the butter butters butter and half the oil in a large, deep, ovenproof frying pan. Season the chicken breasts with salt and pepper and fry, in batches if necessary, for 2 minutes on each side until golden-brown. Remove from the pan and set aside."""
STUFFS = [u"butter",
u"oil",
u"chicken breasts",
u"shallots",
u"plain flour",
u"chicken stock",
u"lemon",
u"asparagus",
u"crème fraîche",
u"parsley",
u"salt",
u"black pepper"]

FOODSTUFFS = [u"spirulina", u"tomato", u"egg", u"bulgur", u"white rice", u"milk"]

logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s %(message)s")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# add the handler to the root logger
logging.getLogger('').addHandler(console)

## ##############################
book = Store( cookbook.open() )

rez = Recipe()
rez.description = u"Some eggs, some rice and some tomato, a classic"
rez.name = u"Arroz a la cubana"
rez.serves = 5
rez.serves_txt = "Serves five"
rez.time_cooking = "DT2H"
rez.time_prep = "DT1H"

book.add(rez)
book.commit()

## ##############################
foodstuff = random.choice(FOODSTUFFS)

fs = book.find(Foodstuff, Foodstuff.name == foodstuff).any()
if not fs:
    fs = Foodstuff()
    fs.name = foodstuff
    fs.normalized = foodstuff
    book.add(fs)
    book.commit()
else:
    print("Foodstuff already exists!")

print fs.id

## ##############################

INGREDIENTS = [u"200 ml tomato sauce", u"1L soya milk", u"300gr steak", u"3 egg yolks"]
ingredient = random.choice(INGREDIENTS)

ing = book.find(RecipeIngredient, RecipeIngredient.name == ingredient).any()
if not ing:
    ing = Ingredient()
    ing.name = ingredient
    ing.recipe_id = rez.id
    ing.foodstuffs.add(fs)
    book.add(ing)
    book.commit()
else:
    print("Ingredient already exists!")

book.close()

print ing
print ing.foodstuffs

print "combination was", foodstuff, "and", ingredient

# METHOD 1: finding foodstuffs in preparation
# FINDINGS: will not match if normalized is singular and prep is plural and fails to match two-word ingredients like 'chicken breasts'
print
print "="*80
print

paraf_set = set(PARAF.split())
stuffs_set = set(STUFFS)

matches = paraf_set & stuffs_set
print matches

# METHOD 2: finding foodstuffs in preparation
print
print "="*80
print
#matches = [word in PARAF for word in STUFFS]
matches = [s for s in STUFFS if s in PARAF]
print matches
