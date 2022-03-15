import multiprocessing
from multiprocessing.pool import ThreadPool

import re
from collections import Counter

from nltk.corpus import wordnet
from nltk.corpus.reader.wordnet import WordNetError
next(wordnet.words()) # ! Helps prevent AttributeError: 'WordNetCorpusReader' object has no attribute '_LazyCorpusLoader__args'

import spacy
import numpy as np
from numba import jit # using Numba to speed up cosine similarity calculation
nlp = spacy.load('en_core_web_lg')

from memory_profiler import profile

# ! <= LEVENSHTEIN DISTANCE SET GENERATION
# http://norvig.com/spell-correct.html

# @profile
def levenshtein_level_1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

# @profile
def levenshtein_level_2(word): 
    "All edits that are two edits away from `word`."
    return set(e2 for e1 in levenshtein_level_1(word) for e2 in levenshtein_level_1(e1))

    # for e1 in edits1(word):
        # for e2 in edits1(e1):
            # e2_list.append(e2)
    # return e2_list


# ! SYNONYM SET GENERATION
# https://www.holisticseo.digital/python-seo/nltk/wordnet

def synonyms_generator(word):
    synonyms = []

    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())
    
    synonyms = set(synonyms)
    
    return synonyms
# print(synonyms_generator('dog'))





def dom_relevant_words_generator(tag):    
    # ! USING SETS FOR EVERYTHING SO DUPLICATES ARE AUTO-AVOIDED
    
    # ignores funky characters and heiphens to avoid errors when generating similar words
    word_for_generation_comparison = re.sub(r'[^a-zA-Z ]', '', tag)
    
    dom_words_set = set()
    
    # ! SET OF WORDS WITHIN *2* EDITS OF THE WORD_FOR_GENERATION_COMPARISON
    levenshtein_set = levenshtein_level_2(word_for_generation_comparison)
    dom_words_set.update(levenshtein_set)
    
    synonyms_set = synonyms_generator(word_for_generation_comparison)
    dom_words_set.update(synonyms_set)
    
    # spacy_most_similar_words_set = spacy_most_similar_words_generator(word_for_generation_comparison)
    # dom_words_set.update(spacy_most_similar_words_set)
    
    return dom_words_set

# if __name__ == '__main__':
#     import time
#     start_time = time.time()
    
#     dom_words_set = dom_relevant_words_generator("correct")
#     print("BOOB") if "wrong" in dom_words_set else print("NOPE")
    
#     print("Process finished --- %s seconds ---" % (time.time() - start_time))




# ! SPACY MOST SIMILAR WORDS GENERATION (closest thing to finding semantically similar words and not just computing semantic similarity)
# https://towardsdatascience.com/how-to-build-a-fast-most-similar-words-method-in-spacy-32ed104fe498

# # # # @jit(nopython=True)
# # # # def cosine_similarity_numba(u:np.ndarray, v:np.ndarray):
# # # #     assert(u.shape[0] == v.shape[0])
# # # #     uv = 0
# # # #     uu = 0
# # # #     vv = 0
# # # #     for i in range(u.shape[0]):
# # # #         uv += u[i]*v[i]
# # # #         uu += u[i]*u[i]
# # # #         vv += v[i]*v[i]
# # # #     cos_theta = 1
# # # #     if uu != 0 and vv != 0:
# # # #         cos_theta = uv/np.sqrt(uu*vv)
# # # #     print("cos_theta: ", cos_theta)
# # # #     return cos_theta

# # # # def spacy_most_similar_words_generator(word, topn=5):
# # # #     word = nlp.vocab[str(word)]
# # # #     print(word)
# # # #     # queries = [
# # # #     #     w for w in word.vocab 
# # # #     #     if w.is_lower == word.is_lower and w.prob >= -15 and np.count_nonzero(w.vector)
# # # #     # ]
    
# # # #     queries = []
# # # #     max_wprob = -10000
# # # #     for w in word.vocab:
# # # #         # print("w: ", w)
# # # #         # print("w.lower: ", w.lower())
# # # #         # print("w.prob: ", w.prob)
# # # #         # print("w.vector: ", w.vector)
# # # #         if ((w.is_lower == word.is_lower) and (w.prob >= -15) and (np.count_nonzero(w.vector))):
# # # #         # if ((w.is_lower == word.is_lower) and (w.prob >= -20) and (np.count_nonzero(w.vector))):
# # # #             queries.append(w)
# # # #         # if (w.is_lower == word.is_lower):
# # # #         #     print("is_lower")
# # # #         if (w.prob >= -15):
# # # #             print("prob")
# # # #         if (w.prob > max_wprob):
# # # #             max_wprob = w.prob
# # # #         if (w.prob == -20):
# # # #             print(w)
# # # #     print("max_wprob: ", max_wprob)
# # # #     print(queries)
# # # #     by_similarity = sorted(queries, key=lambda w: cosine_similarity_numba(w.vector, word.vector), reverse=True)
    
# # # #     spacy_most_similar_words_set = set()
    
# # # #     for w in by_similarity[:topn+1]:
# # # #         if (w.lower_ != word.lower_):
# # # #             print((w.lower_,w.similarity(word)))
    
# # # #     # return [(w.lower_,w.similarity(word)) for w in by_similarity[:topn+1] if w.lower_ != word.lower_]
# # # # print(spacy_most_similar_words_generator('dog'))

# def most_similar(word, topn=5):
#   word = nlp.vocab[str(word)]
#   queries = [
#       w for w in word.vocab 
#       if w.is_lower == word.is_lower and w.prob >= -15 and np.count_nonzero(w.vector)
#   ]

#   by_similarity = sorted(queries, key=lambda w: word.similarity(w), reverse=True)
#   return [(w.lower_,w.similarity(word)) for w in by_similarity[:topn+1] if w.lower_ != word.lower_]

# print(most_similar("dog", topn=3))