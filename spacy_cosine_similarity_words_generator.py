import numpy as np
# https://pypi.org/project/spacy-lookups-data/
import spacy
from spacy.lookups import load_lookups
from spacy.vocab import Vocab

nlp = spacy.load('en_core_web_lg')
# lexemes = [nlp.vocab[orth] for orth in nlp.vocab.vectors]
lookups = load_lookups("en", ["lexeme_prob"])
nlp.vocab.lookups.add_table("lexeme_prob", lookups.get_table("lexeme_prob"))

from numba import jit

@jit(nopython=True)
def cosine_similarity_numba(u:np.ndarray, v:np.ndarray):
    assert(u.shape[0] == v.shape[0])
    uv = 0
    uu = 0
    vv = 0
    for i in range(u.shape[0]):
        uv += u[i]*v[i]
        uu += u[i]*u[i]
        vv += v[i]*v[i]
    cos_theta = 1
    if uu != 0 and vv != 0:
        cos_theta = uv/np.sqrt(uu*vv)
    return cos_theta

def most_similar(word, topn=5):
    word_index = nlp.vocab.strings[str(word)]
    print(word_index)
    # assert nlp.vocab[word_index] == nlp.vocab[str(word)]
    # word = nlp.vocab[word_index]
    # word = [nlp.vocab[orth] for orth in nlp.vocab.vectors]
    # word = nlp.vocab[word_index]
    word = nlp.vocab[200]
    print(word)
    print(word.vector)
    # print("word.vocab: ", word.vocab)
    # print(word.vocab.strings)
    # lexemes = [nlp.vocab[orth] for orth in nlp.vocab.vectors]
    
    queries = [
        # w for w in word.vocab
        w for w in nlp.vocab
        if w.is_lower == word.is_lower and w.prob >= -15 and np.count_nonzero(w.vector)
    ]
    # print(queries)
    
    # max_wprob = -100
    # for w in word.vocab:
    #     if (w.prob > max_wprob):
    #         max_wprob = w.prob
    # print("max_wprob:", max_wprob)
    # for i in queries:
        # print(i.lower_)
    by_similarity = sorted(queries, key=lambda w: cosine_similarity_numba(w.vector, word.vector), reverse=True)
    # by_similarity = sorted(queries, key=lambda w: word.similarity(w), reverse=True)
    return [(w.lower_,w.similarity(word)) for w in by_similarity[:topn+1] if w.lower_ != word.lower_]

import time
start_time = time.time()
print(most_similar("accurate", topn=15))
# print(most_similar("character", topn=3))
print("Process finished --- %s seconds ---" % (time.time() - start_time))
# lexemes = [nlp.vocab[orth] for orth in nlp.vocab.vectors]
# print(lexemes[15].vocab.prob)
# words = list(nlp.vocab.strings)
# print(words)