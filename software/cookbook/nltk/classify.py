import nltk
import pickle
from nltk.classify import MaxentClassifier

# Set up our training material in a nice dictionary.
training = {
    'ingredients': [
        'Pastry for 9-inch tart pan',
        'Apple cider vinegar',
        '3 eggs',
        '1/4 cup sugar',
    ],
    'steps': [
        'Sift the powdered sugar and cocoa powder together.',
        'Coarsely crush the peppercorns using a mortar and pestle.',
        'While the vegetables are cooking, scrub the pig ears clean and cut away any knobby bits of cartilage so they will lie flat.',
        'Heat the oven to 375 degrees.',
    ]
}

# Set up a list that will contain all of our tagged examples,
# which we will pass into the classifier at the end.
training_set = []
for key, val in training.items():
    for i in val:
        # Set up a list we can use for all of our features,
        # which are just individual words in this case.
        feats = []
        # Before we can tokenize words, we need to break the
        # text out into sentences.
        sentences = nltk.sent_tokenize(i)
        for sentence in sentences:
            feats = feats + nltk.word_tokenize(sentence)

        # For this example, it's a good idea to normalize for case.
        # You may or may not need to do this.
        feats = [i.lower() for i in feats]
        # Each feature needs a value. A typical use for a case like this
        # is to use True or 1, though you can use almost any value for
        # a more complicated application or analysis.
        feats = dict([(i, True) for i in feats])
        # NLTK expects you to feed a classifier a list of tuples
        # where each tuple is (features, tag).
        training_set.append((feats, key))

# Train up our classifier
classifier = MaxentClassifier.train(training_set)

# # Test it out!
# # You need to feed the classifier your data in the same format you used
# # to train it, in this case individual lowercase words.
res = classifier.classify({'apple': True, 'cider': True, 'vinegar': True})
print res
# >>> 'ingredients'
#
# # Save it to disk, if you want, because these can take a long time to train.
# outfile = open('my_pickle.pickle', 'wb')
# pickle.dump(classifier, outfile)
# outfile.close()
