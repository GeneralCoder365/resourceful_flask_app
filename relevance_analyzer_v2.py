import multiprocessing
import numpy as np

import spacy
nlp = spacy.load('en_core_web_lg')

# https://newscatcherapi.com/blog/ultimate-guide-to-text-similarity-with-python
# ! JACCARD SIMILARITY
# number of shared words/total number of unique words between two arrays
def jaccard_similarity(x, y):
    # formats the text properly
    if (type(x) != list):
        x = [word.lower() for word in x.split()]
    if (type(y) != list):
        y = [word.lower() for word in y.split()]
    x = [word.strip(' ') for word in x]
    y = [word.strip(' ') for word in y]
    
    """ returns the jaccard similarity between two lists """
    intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    union_cardinality = len(set.union(*[set(x), set(y)]))
    
    jaccard_similarity = intersection_cardinality/float(union_cardinality)
    print("Jaccard similarity: ", jaccard_similarity)
    
    normalized_jaccard_similarity = jaccard_similarity/float(min(len(x), len(y))) # ! normalizes similarity from 0 to 
    # ! max = 1/float(min(len(x), len(y)))
    # ! min = 0
    return normalized_jaccard_similarity
print(jaccard_similarity('below bob','below bob cat hat'))


# ! EUCLIDEAN DISTANCE (most commonly used form of Minkowski Distance)
# uses Pythagorean Theorem to calculate the distance between two points (the two sentences)
# as the difference increases, so does the distance
def squared_sum(x):
	""" return 3 rounded square rooted value """

	return round(np.sqrt(sum([a*a for a in x])),3)
 
def euclidean_distance(x,y):
	""" return euclidean distance between two lists """

	return np.sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))

def distance_to_similarity(distance): # ! normalizes distance from 0 to 1
  return 1/np.exp(distance) # computes 1/e^distance

def master_euclidean_distance_to_similarity(sentence_1, sentence_2):
    embeddings = [nlp(sentence).vector for sentence in [sentence_1, sentence_2]]
    return distance_to_similarity(euclidean_distance(embeddings[0], embeddings[1]))

# print(master_euclidean_distance_to_similarity("my cat wears a hat", "my cat is wearing a hat"))


# ! COSINE SIMILARITY (cos of angle between vectors u & v) <-- cos theta = (u . v)/(|u||v|)
def cosine_similarity(x,y):
	""" return cosine similarity between two lists """

	numerator = sum(a*b for a,b in zip(x,y))
	denominator = squared_sum(x)*squared_sum(y)
	return round(numerator/float(denominator),3)

def master_cosine_similarity(sentence_1, sentence_2):
	embeddings = [nlp(sentence).vector for sentence in [sentence_1, sentence_2]]
	return cosine_similarity(embeddings[0], embeddings[1])

print(master_cosine_similarity("my cat wears a hat", "my cat is wearing a hat"))