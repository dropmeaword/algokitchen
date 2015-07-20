import nltk
from nltk.tag import pos_tag, map_tag

phrases = [
"Apple cider vinegar",
"And now for something completely different",
"1/4 cup sugar",
"Pastry for 9-inch tart pan"
]

for p in phrases:
    text = nltk.word_tokenize(p)
    posTagged = pos_tag(text)
    simplifiedTags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in posTagged]
    print("="*80)
    print(simplifiedTags)
