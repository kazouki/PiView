import os

import requests
from bs4 import BeautifulSoup

import re
import spacy
import en_core_web_sm
from spacy.tokens import Token
from math import isclose
from enum import Enum

from typing import List, Tuple  # for fancy type hints
from spacy.symbols import ADJ, NOUN, VERB
from spacy.symbols import NAMES
from spacy.symbols import IDS

feedback_simple = "The schnitzel tasted good. The soup was too hot. The waiter was quick and polite so i will come back to that restaurant."
feedback_rude = '''The waiter was very rude, 
e.g. when I accidentally opened the wrong door
he screamed "Private!".'''

nlp = spacy.load("en_core_web_sm")

os.system('clear')

print("")
print("-basic sentences parsed-")
document = nlp(u"{}".format(feedback_simple))
for sentence in document.sents:
    print(sentence)

print("")
print("-Abbreviations and indirect speech galore-")
document_rude = nlp(u"{}".format(feedback_rude))
for sentence in document_rude.sents:
    print(sentence)

print("")
print("-separate words/tokens of first sentence of document-")
first_sent = next(document.sents)
for word in first_sent:
    print(word)

print("")
print("-Tokens (first_sent[2] in this case)-")
tastes_token = first_sent[2]
print(tastes_token)
print("-Token.lemma_ ('basic form of word')(first_sent[2] in this case)-")
print(tastes_token.lemma_)
print("-Token.pos_ ('part of speech, role of word in sentence')(first_sent[2] in this case)-")
print(tastes_token.pos_)

# Token attributes
# Full list: https://spacy.io/api/token#attributes
print("")
print("-Many attributes have two variants with or without underscore at the end of the name, for example lemma and lemma_. The first are integer codes that are compact to store and quick to compare while the latter are easier to read.-")
print("pos     :", tastes_token.pos)
print("pos_    :", tastes_token.pos_)

# Import what you need from spacy.symbols:
print("")
print("-Converting between spaCy names and IDs-")
print("VERB    :", VERB)
print("NAMES[99] (100 = VERB)  :", NAMES[100])  # 100 = VERB
print("IDS['VERB']      :", IDS['VERB'])

# Topics and ratings
# Actual topics for our example
#
#     ambience: decoration, space, light, music, temperature, ...
#     food and beverages: eating, drinking, taste, menu, selection
#     hygiene: toilett, smell, ...
#     service: waiters, reaction times, courtesy, competence, availability, ...
#     value: price, size of portions, ...

class Topic(Enum):
    AMBIENCE = 1
    FOOD = 2
    HYGIENE = 3
    SERVICE = 4
    VALUE = 5


# Rating (sentiment)
# There are several ways to represent a rating, for example:
#
#     Two distinct values "positive" and "negative"
#     Same as above but with more distinct values, e.g. 1 to 5 stars
#     use a float between e.g. 0 and 1.0

class Rating(Enum):
    VERY_BAD = -3
    BAD = -2
    SOMEWHAT_BAD = -1
    SOMEWHAT_GOOD = 1
    GOOD = 2
    VERY_GOOD = 3

# The lexicon
# Contents of the lexicon
# words can be regular expression
# for example: .*schnitzel

# Examples:
#
# Lemma        Topic      Rating
# ------------ ---------- ------
# waiter       service
# waitress     service
# wait                    bad
# quick                   good
# .*schnitzel  food
# music        ambience
# loud                    bad


# How to collect words for lexicon?
#
#     Add words that are obvious and easy to find, for example collect food term from menu
#     Find the most common words in raw data and examine them
#     Analyse data early version and check sentences with no topic or rating for interesting words --> iterative improvement
#
# Lexicon entries in Python
#
#     mostly a data container
#     but we also want to be able to compare if it matches a spaCy Token --> we need a matching() function.
#     tokens can match exactly or only after transformations (for example upper/lower case) --> score between 0 (no match) and 1 (perfect match)
#
# And as we want to be able to use regular expressions and spaCy Token we need to import them now:


class LexiconEntry:
    _IS_REGEX_REGEX = re.compile(r'.*[.+*\[$^\\]')

    def __init__(self, lemma: str, topic: Topic, rating: Rating):
        assert lemma is not None
        self.lemma = lemma
        self._lower_lemma = lemma.lower()
        self.topic = topic
        self.rating = rating
        self.is_regex = bool(LexiconEntry._IS_REGEX_REGEX.match(self.lemma))
        self._regex = re.compile(lemma, re.IGNORECASE) if self.is_regex else None

    def matching(self, token: Token) -> float:
        """
        A weight between 0.0 and 1.0 on how much ``token`` matches this entry.
        """
        assert token is not None
        result = 0.0
        if self.is_regex:
            if self._regex.match(token.text):
                result = 0.6
            elif self._regex.match(token.lemma_):
                result = 0.5
        else:
            if token.text == self.lemma:
                result = 1.0
            elif token.text.lower() == self.lemma:
                result = 0.9
            elif token.lemma_ == self.lemma:
                result = 0.8
            elif token.lemma_.lower() == self.lemma:
                result = 0.7
        return result

    def __str__(self) -> str:
        result = 'LexiconEntry(%s' % self.lemma
        if self.topic is not None:
            result += ', topic=%s' % self.topic.name
        if self.rating is not None:
            result += ', rating=%s' % self.rating.name
        if self.is_regex:
            result += ', is_regex=%s' % self.is_regex
        result += ')'
        return result

    def __repr__(self) -> str:
        return self.__str__()


# The lexicon in Python
#
#     Contains a list of LexiconEntry
#     Can find the best matching entry for a Token (or None)
#     In the beginning entries have to be added
#     manually for our example, in practice from e.g .CSV
#

class Lexicon:
    def __init__(self):
        self.entries: List[LexiconEntry] = []

    def append(self, lemma: str, topic: Topic, rating: Rating):
        lexicon_entry = LexiconEntry(lemma, topic, rating)
        self.entries.append(lexicon_entry)

    def lexicon_entry_for(self, token: Token) -> LexiconEntry:
        """
        Entry in lexicon that best matches ``token``.
        """
        result = None
        lexicon_size = len(self.entries)
        lexicon_entry_index = 0
        best_matching = 0.0
        while lexicon_entry_index < lexicon_size and not isclose(best_matching, 1.0):
            lexicon_entry = self.entries[lexicon_entry_index]
            matching = lexicon_entry.matching(token)
            if matching > best_matching:
                result = lexicon_entry
                best_matching = matching
            lexicon_entry_index += 1
        return result

# Let's build a small lexicon
lexicon = Lexicon()
lexicon.append('waiter'     , Topic.SERVICE , None) #Gensim Topic analysis
lexicon.append('waitress'   , Topic.SERVICE , None)
lexicon.append('wait'       , None          , Rating.BAD)
lexicon.append('quick'      , None          , Rating.GOOD) #pos wordlist
lexicon.append('.*schnitzel', Topic.FOOD    , None)
lexicon.append('music'      , Topic.AMBIENCE, None)
lexicon.append('loud'       , None          , Rating.BAD)  #neg wordlist
lexicon.append('tasty'      , Topic.FOOD    , Rating.GOOD)
lexicon.append('polite'     , Topic.SERVICE , Rating.GOOD)

print("")
print("-Matching tokens in a sentence to a lexicon entry-")
feedback_text = 'The music was very loud.'
feedback = nlp(u"{}".format(feedback_text))
for token in next(feedback.sents):
    lexicon_entry = lexicon.lexicon_entry_for(token)
    print(f'{token!s:10} {lexicon_entry}')

# Just add some filters and format the output:
print("")
print("-formatted output-")
for sent in feedback.sents:
    print(sent)
    for token in sent:
        lexicon_entry = lexicon.lexicon_entry_for(token)
        if lexicon_entry is not None:
            if lexicon_entry.topic is not None:
                print('    ', lexicon_entry.topic)
            if lexicon_entry.rating is not None:
                print('    ', lexicon_entry.rating)


# Intensifiers, diminishers, negations
#
#     increase or decrease the rating of sentiment words
#     examples:
#         diminishers: barely, slightly, somewhat, ...
#         intensifiers: really, terribly, very, ...
#
# Impact on "loud":
#
#     "loud": Rating.BAD
#     "very loud": Rating.VERY_BAD

# Intensifiers and diminishers in python:
# Use sets:
INTENSIFIERS = {
    'really',
    'terribly',
    'very',
    'extremely',
    'overly',
}

def is_intensifier(token: Token) -> bool:
    return token.lemma_.lower() in INTENSIFIERS

DIMINISHERS = {
    'barely',
    'slightly',
    'somewhat',
    'hardly',
}

def is_diminisher(token: Token) -> bool:
    return token.lemma_.lower() in DIMINISHERS

print("")
print("-Find out if a token is an intensifier-")
print('-For a little test, get the 4th token in 1st sentence, which is "very"-')
very_token = next(nlp(feedback_text).sents)[3]
print(very_token)
print("is_intensifier(very_token)   boolean  :")
print(is_intensifier(very_token))

# Intensify or diminish a Rating:
def signum(value) -> int:
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0

_MIN_RATING_VALUE = Rating.VERY_BAD.value
_MAX_RATING_VALUE = Rating.VERY_GOOD.value


def _ranged_rating(rating_value: int) -> Rating:
    return Rating(min(_MAX_RATING_VALUE, max(_MIN_RATING_VALUE, rating_value)))

def diminished(rating: Rating) -> Rating:
    if abs(rating.value) > 1:
        return _ranged_rating(rating.value - signum(rating.value))
    else:
        return rating

def intensified(rating: Rating) -> Rating:
    if abs(rating.value) > 1:
        return _ranged_rating(rating.value + signum(rating.value))
    else:
        return rating

print("")
print("-diminished/intensified ratings-")
print(diminished(Rating.BAD))
print(diminished(Rating.SOMEWHAT_BAD))
print(intensified(Rating.BAD))


# Negations
#
#     turn a sentiment to the opposit
#     example: "not"
#         "tasty" = Rating.GOOD
#         "not tasty" = Rating.BAD
#     can be combined with intensifiers and diminishers
#     example:
#         "very good" = Rating.VERY_GOOD
#         "not very good" = Rating.SOMEWHAT_BAD
#     negation also swaps intensifier and diminisher


# Negations in Python
# Detection is similar to intensifiers and diminishers:
NEGATIONS = {
    'no',
    'not',
    'none',
}

def is_negation(token: Token) -> bool:
    return token.lemma_.lower() in NEGATIONS


# Negation of a Rating
# Negating a Rating is classic mapping issue:
_RATING_TO_NEGATED_RATING_MAP = {
    Rating.VERY_BAD     : Rating.SOMEWHAT_GOOD,
    Rating.BAD          : Rating.GOOD,
    Rating.SOMEWHAT_BAD : Rating.GOOD,  # hypothetical? #ik denk SOMEWHAT_GOOD
    Rating.SOMEWHAT_GOOD: Rating.BAD,  # hypothetical? #ik denk SOMEWHAT_BAD
    Rating.GOOD         : Rating.BAD,
    Rating.VERY_GOOD    : Rating.SOMEWHAT_BAD,
}

def negated_rating(rating: Rating) -> Rating:
    assert rating is not None
    return _RATING_TO_NEGATED_RATING_MAP[rating]

print("")
print("-Negated ratings, 'very good' -> 'not very good'-")
print(Rating.GOOD, ' -> ', negated_rating(Rating.GOOD))
print(Rating.VERY_BAD, ' -> ', negated_rating(Rating.VERY_BAD))

# Based on a simple lexicon and a few Python sets we can now assign sentiment information to single tokens concerning:
#     Topic
#     Rating
#     intensifiers / diminishers
#     nagations
# However, we still need to combine multiple tokens in our analysis. We could of course start messing with lists of tokens. However, spaCy offers nice possibilities for such situations.


# Extending spaCy's pipeline
# What's this pipleline thingy?
#
#     When you pass a text to spaCy's nlp() it performs multiple separate steps until it ends up with tokens and all their attributes
#     Nice and clean "separation of concerns" (basic software principle)
#     Token can get additional attributes (same goes for documents (Doc) and sents (Span), but we don't need this right now)
#     Steps can be added or removed from the pipeline
#
# Recommended reading: https://explosion.ai/blog/spacy-v2-pipelines-extensions
# Extending Token
#

# We can add new attributes for sentiment relevant information to the extensible "underscore" attribute:
Token.set_extension('topic', default=None)
Token.set_extension('rating', default=None)
Token.set_extension('is_negation', default=False)
Token.set_extension('is_intensifier', default=False)
Token.set_extension('is_diminisher', default=False)

# Now we can set and examine these attributes
print("")
print("-Add sentiment relevant attributes to token with 'underscore' extensible-")
token = next(nlp('schnitzel').sents)[0]
print(token.lemma_)
token._.topic = Topic.FOOD
print("token._.topic    :", token._.topic)


# Intermission: a small debugging function
# In order to print tokens including the new attributes here's a little helper:
def debugged_token(token: Token) -> str:
    result = 'Token(%s, lemma=%s' % (token.text, token.lemma_)
    if token._.topic is not None:
        result += ', topic=' + token._.topic.name
    if token._.rating is not None:
        result += ', rating=' + token._.rating.name
    if token._.is_diminisher:
        result += ', diminisher'
    if token._.is_intensifier:
        result += ', intensifier'
    if token._.is_negation:
        result += ', negation'
    result += ')'
    return result

print("")
print(debugged_token(token))


# Extending the pipeline
# First we need a function to add to the pipeline that sets our new Token attributes:
def opinion_matcher(doc):
    for sentence in doc.sents:
        for token in sentence:
            if is_intensifier(token):
                token._.is_intensifier = True
            elif is_diminisher(token):
                token._.is_diminisher = True
            elif is_negation(token):
                token._.is_negation = True
            else:
                lexicon_entry = lexicon.lexicon_entry_for(token)
                if lexicon_entry is not None:
                    token._.rating = lexicon_entry.rating
                    token._.topic = lexicon_entry.topic
    return doc


# Then we can actually add it to the pipeline (and remove it first if it already was part of the pipeline):
if nlp.has_pipe('opinion_matcher'):
    nlp.remove_pipe('opinion_matcher')
nlp.add_pipe(opinion_matcher)


# Extracting token relevant for the opinion
# With all the information attached to the token it is simple to reduce a sentence to its essential information:
def is_essential(token: Token) -> bool:
    return token._.topic is not None \
           or token._.rating is not None \
           or token._.is_diminisher \
           or token._.is_intensifier \
           or token._.is_negation


def essential_tokens(tokens):
    return [token for token in tokens if is_essential(token)]


# For example:
print("")
print("-Extracted essential tokens from input-")
document = nlp('The schnitzel is not very tasty.')

print("for     :   document = nlp('The schnitzelz are not very tasty.')")
opinion_essence = essential_tokens(document)
for token in opinion_essence:
    print(debugged_token(token))


# Apply on Rating
# Now we have all the building blocks to apply intensifiers, diminishers and nagations on the rating. The basic idea is
# that when we encounter a token with a rating and modifiers to the left of it than we can combine them until we don't find any more.
# To keep things tidy, here's a another little helper:

def is_rating_modifier(token: Token):
    return token._.is_diminisher \
        or token._.is_intensifier \
        or token._.is_negation


# Example
#
# The previous sentence yielded the tokens:
#
# Token(schnitzel, lemma=schnitzel, topic=FOOD)
# Token(not, lemma=not, negation)
# Token(very, lemma=very, intensifier)
# Token(tasty, lemma=tasty, topic=FOOD, rating=GOOD)
#
# We want to perform the following steps:
#
#     Find the first rating from the left -> tasty(GOOD)
#     Check if the token to the left is a modifer -> yes: very(intensifier)
#     Combine them -> (very) tasty(VERY_GOOD) and remove the left token
#     Check if the token to the left is a modifer -> yes: not(negation)
#     Combine them -> (not very) tasty(BAD) and remove the left token
#     End result: not very tasty(GOOD) -> tasty(BAD)
def combine_ratings(tokens):
    # Find the first rating (if any).
    rating_token_index = next(
        (
            token_index for token_index in range(len(tokens))
            if tokens[token_index]._.rating is not None
        ),
        None  # Default if no rating token can be found

    )

    if rating_token_index is not None:
        # Apply modifiers to the left on the rating.
        original_rating_token = tokens[rating_token_index]
        combined_rating = original_rating_token._.rating
        modifier_token_index = rating_token_index - 1
        modified = True  # Did the last iteration modify anything?
        while modified and modifier_token_index >= 0:
            modifier_token = tokens[modifier_token_index]
            if is_intensifier(modifier_token):
                combined_rating = intensified(combined_rating)
            elif is_diminisher(modifier_token):
                combined_rating = diminished(combined_rating)
            elif is_negation(modifier_token):
                combined_rating = negated_rating(combined_rating)
            else:
                # We are done, no more modifiers
                # to the left of this rating.
                modified = False
            if modified:
                # Discord the current modifier
                # and move on to the token on the left.
                del tokens[modifier_token_index]
                modifier_token_index -= 1
        original_rating_token._.rating = combined_rating


# Example for a combined rating:
print("")
document = nlp('The schnitzel is not very tasty.')

opinion_essence = essential_tokens(document)
print("")
print('essential token ratings:')
for token in opinion_essence:
    print('  ', debugged_token(token))

combine_ratings(opinion_essence)
print("")
print('combined token ratings:')
for token in opinion_essence:
    print('  ', debugged_token(token))


# A function to extract topic and rating of a sentence


def topic_and_rating_of(tokens: List[Token]) -> Tuple[Topic, Rating]:
    result_topic = None
    result_rating = None
    opinion_essence = essential_tokens(tokens)
    # print('  1: ', opinion_essence)
    combine_ratings(opinion_essence)
    # print('  2: ', opinion_essence)
    for token in opinion_essence:
        # print(debugged_token(token))
        if (token._.topic is not None) and (result_topic is None):
            result_topic = token._.topic
        if (token._.rating is not None) and (result_rating is None):
            result_rating = token._.rating
        if (result_topic is not None) and (result_rating is not None):
            break
    return result_topic, result_rating

sentence = next(nlp("The schnitzel wasn't very tasty.").sents)
print("")
print(sentence)
print(topic_and_rating_of(sentence))


# A function to extract opinions from feedback:
def opinions(feedback_text: str):
    feedback = nlp(feedback_text)
    for tokens in feedback.sents:
        yield(topic_and_rating_of(tokens))


feedback_text = """
The schnitzel was not very tasty. 
The waiter was polite.
The music was loud."""
print("")
print("-for input: ", feedback_text, "-")
print("")
for topic, rating in opinions(feedback_text):
    print(topic, rating)