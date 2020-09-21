
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

import os
import tempfile
TEMP_FOLDER = tempfile.gettempdir()
print('Folder "{}" will be used to save temporary dictionary and corpus.'.format(TEMP_FOLDER))


from pprint import pprint  # pretty-printer
from collections import defaultdict

from gensim import corpora
from smart_open import smart_open


os.system('clear')
# from gensim import corpora
documents = ["Human machine interface for lab abc computer applications",
             "A survey of user opinion of computer system response time",
             "The EPS user interface management system",
             "System and human system engineering testing of EPS",
             "Relation of user perceived response time to error measurement",
             "The generation of random binary unordered trees",
             "The intersection graph of paths in trees",
             "Graph minors IV Widths of trees and well quasi ordering",
             "Graph minors A survey"]

######### remove common words and tokenize #########
# from collections import defaultdict
stoplist = set('is for a of the and to in on at'.split())
texts = [[word for word in document.lower().split() if word not in stoplist]
         for document in documents]

# remove words that appear only once
from collections import defaultdict
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1

texts = [[token for token in text if frequency[token] > 1] for text in texts]
#from pprint import pprint  # pretty-printer
pprint(texts)


######### create dictionary on disk #########
dictionary = corpora.Dictionary(texts)
dictionary.save(os.path.join(TEMP_FOLDER, 'deerwester.dict'))  # store the dictionary, for future reference
print("")
print(dictionary)
# We assigned a unique integer ID to all words appearing in the processed corpus with the gensim.corpora.dictionary.Dictionary class.
print(dictionary.token2id)

###### To actually convert tokenized documents to vectors: #######
new_doc = "Human computer interface interface"
new_vec = dictionary.doc2bow(new_doc.lower().split())
print("")
print("bag of words for input 'new_doc': '",new_doc,"', words index coincide with input text indices")
print(new_vec)  # the word "interaction" does not appear in the dictionary and is ignored

###### convert texts to bag-of-words vectors ######
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize(os.path.join(TEMP_FOLDER, 'deerwester.mm'), corpus)  # store to disk, for later use
print("")
for c in corpus:
    print(c)

###### memory friendly local corpus txt opener ######
# from smart_open import smart_open
class MyCorpus(object):
    def __iter__(self):
        for line in smart_open('datasets/mycorpus.txt', 'rb'):
            # assume there's one document per line, tokens separated by whitespace
            yield dictionary.doc2bow(line.lower().split())

corpus_memory_friendly = MyCorpus() # doesn't load the corpus into memory!
print("")
print("corpus_memory_friendly: ", corpus_memory_friendly)

###### load vectors from corpus object one at a time ######
print("")
for vector in corpus_memory_friendly:  # load one vector into memory at a time
    print(vector)


# We are going to create the dictionary from the mycorpus.txt file without loading the entire file into memory.
# Then, we will generate the list of token ids to remove from this dictionary by querying the dictionary for the token ids of the stop words,
# and by querying the document frequencies dictionary (dictionary.dfs) for token ids that only appear once. Finally,
# we will filter these token ids out of our dictionary. Keep in mind that dictionary.filter_tokens (and some other
# functions such as dictionary.add_document) will call dictionary.compactify() to remove the gaps in the token id
# series thus enumeration of remaining tokens can be changed.
from six import iteritems
from smart_open import smart_open

# collect statistics about all tokens
dictionary = corpora.Dictionary(line.lower().split() for line in smart_open('datasets/mycorpus.txt', 'rb'))

# remove stop words and words that appear only once
stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
            if stopword in dictionary.token2id]
once_ids = [tokenid for tokenid, docfreq in iteritems(dictionary.dfs) if docfreq == 1]

# remove stop words and words that appear only once
dictionary.filter_tokens(stop_ids + once_ids)
print("")
print("New dictionary from filtered mycorpus.txt : ")
print(dictionary)

######-------------------------gensim tutorial part 2 -------------------------#######



