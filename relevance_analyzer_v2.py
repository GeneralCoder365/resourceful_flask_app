from multiprocessing.pool import ThreadPool
import multiprocessing

import numpy as np

import re
from collections import Counter

from nltk import regexp_tokenize
# from stop_words import get_stop_words
from nltk.corpus import stopwords

# stop_words = list(get_stop_words('en'))
nltk_stopwords = list(stopwords.words('english'))

import spacy
nlp = spacy.load('en_core_web_lg')


def text_cleaner(description):
    description = str(description).lower()
    description = re.sub(r'[^a-zA-Z0-9 ]', '', description)
    # print(description)
    # print(type(description))
    description = description.split(" ")
    
    description = [word for word in description if not word in nltk_stopwords]
    
    return description



# ! RELEVANT WORDS SCORER
def relevant_words_checker(tags_to_compare_relevant_words_dict, description_array):
    # print("LENGTH: ", len(tags_to_compare_relevant_words_dict))
    # check if each description word exists in the relevant_words_dict
    
    tags_frequency = {}
    relevant_words_score = 0

    # for tag in relevance_words_dict.keys():
    # tags_frequency[tag] = 0

    for word in description_array:
        # print("tags_frequency: ", tags_frequency)
        for tag, related_words in tags_to_compare_relevant_words_dict.items():
            if (word in related_words):
                relevant_words_score += 1
                if (tag in tags_frequency.keys()):
                    tags_frequency[tag] += 1
                else:
                    tags_frequency[tag] = 1
    
    # relevant_words_score = round((relevant_words_score/len(tags_to_compare_relevant_words_dict)), 2) # ! MIGHT NEED TO CHANGE!!!
   
    
    return [relevant_words_score, tags_frequency]

# ! COSINE SIMILARITY (cos of angle between vectors u & v) <-- cos theta = (u . v)/(|u||v|)
def squared_sum(x):
    """ return 3 rounded square rooted value """

    return round(np.sqrt(sum([a*a for a in x])),3)

def cosine_similarity(x,y):
    """ return cosine similarity between two lists """

    numerator = sum(a*b for a,b in zip(x,y))
    denominator = squared_sum(x)*squared_sum(y)
    return round(numerator/float(denominator),3)

def master_cosine_similarity(tags, sentence_2):
    tag_sentence = " ".join(tags)
    embeddings = [nlp(sentence).vector for sentence in [tag_sentence, sentence_2]]
    return cosine_similarity(embeddings[0], embeddings[1]) # max = 1, min = 0

# def result_relevance_calculator(tags, tags_to_compare_relevant_words_dict, url_dict, top_queue):
def result_relevance_calculator(tags, tags_to_compare_relevant_words_dict, url_dict):
    print("RESULT RELEVANCE CALCULATOR STARTING")
    txt_description = url_dict["description"]
    description = url_dict["description"]
    
    # ! AAU CASE
    if ("aau" in url_dict["url"].lower()):
        url_dict["composite_relevance_score"] = 100000
        url_dict["tags_frequency"] = {}
	
        # top_queue.put(url_dict)
        # return url_dict
	
    # ! NO DESCRIPTION CASE
    elif (description == "False"):
        url_dict["composite_relevance_score"] = 0
        url_dict["tags_frequency"] = {}

        # top_queue.put(url_dict)
        # return url_dict
        
    else:
        description = text_cleaner(description)
    
        tags = [tag.lower().strip() for tag in tags]

        # tags_to_compare_relevant_words_dict = {}
        # for tag in tags:
        #     tags_to_compare_relevant_words_dict[tag] = relevant_words_dict[tag]
        #     sub_tags = tag.split()
        #     if (len(sub_tags) > 1):
        #         for sub_tag in sub_tags:
        #             tags_to_compare_relevant_words_dict[sub_tag] = relevant_words_dict[sub_tag]


        # print(tags)
        # print(description)

        relevant_words_data = relevant_words_checker(tags_to_compare_relevant_words_dict, description)
        relevant_words_score = relevant_words_data[0]
        tags_frequency = relevant_words_data[1]

        cosine_similarity_score = master_cosine_similarity(tags, txt_description)
        # print("Cosine similarity score: ", cosine_similarity_score)

        composite_relevance_score = round((cosine_similarity_score*(relevant_words_score/len(description))), 2)

        url_dict["composite_relevance_score"] = composite_relevance_score
        url_dict["tags_frequency"] = tags_frequency

        # relevance_rating_data = relevance_rater(tags, description) # returns relevance rating and dictionary of prominent tags as keys and frequency as values
        # return OF THE FORM: [description_fuzzy_hmni_synonym_rating, tags_frequency_dict]

        # return [composite_relevance_score, tags_frequency]
        # top_queue.put([composite_relevance_score, tags_frequency])
        # top_queue.put(url_dict)
    
    # top_queue.put(url_dict)
    print("RESULT RELEVANCE CALCULATOR FINISHING")
    return url_dict

# if __name__ == '__main__':
#     import time
#     start_time = time.time()
#     # ! TEMPORARY CODE
#     import relevant_words_generator
#     relevant_words_dict = relevant_words_generator.master_relevant_words_generator(['math'])
#     print("GENERATED RELEVANT WORDS DICTIONARY")
    
    
#     print(result_relevance_calculator(["math"], '''Students enter our math classrooms with anxiety about performance, misconceptions about what math is, and a lack of confidence that can limit their ability to have meaningful learning experiences. In response to this challenge, Stanford researcher Jo Boaler has focused on 
#     some key tenants to help students transform their mindset to find more success with math teaching and learning. Some of these mindset shifts include recognizing that: (1) anyone can learn math, (2) making mistakes is essential to learning, (3) math is about fluency and not speed, (4) math is visual, (5) being successful in math requires creativity, flexibility, problem solving, and number sense.\r\n\r\nIn order to start building these mindsets, Boaler advocates, among other strategies, that students build a habit of being mathematical through common routines, tasks, and puzzles.\r\n\r\nThis guide will introduce 3 of those routines/puzzles including tips on how to successfully implement these tasks in a face to face, blended, or distance learning setting.\r\n\r\nThe Need\r\nMany adult education students had difficult (and often negative) experiences with math teaching and learning during their time in the K-12 system. Without addressing their math trauma and helping them to build a mathematical mindset, our students may continue to struggle and be limited in their ability to succeed in math class, on the equivalency exam, and in college and 
#     career settings. So our program views math mindsets as the greatest challenge and largest opportunity for transforming the experience our students have when returning to school. Without this shift, we could share the best lesson plans, the most engaging OERs, and the most transformative teachers, and students will continue to be held back by self-limiting perceptions about math and about their ability to succeed.''',
#     relevant_words_dict))
#     # print(master_cosine_similarity("my cat wears a hat", "my cat is wearing a hat"))
#     # print(master_cosine_similarity("my cat wears a hat", "my cat wears a hat"))
#     print("Process finished --- %s seconds ---" % (time.time() - start_time))


# # # ! EUCLIDEAN DISTANCE (most commonly used form of Minkowski Distance) -> WORSE THAN COSINE AT DEALING WITH DIFFERENT LENGTHS
# # # uses Pythagorean Theorem to calculate the distance between two points (the two sentences)
# # # as the difference increases, so does the distance
# # def euclidean_distance(x,y):
# # 	""" return euclidean distance between two lists """

# # 	return np.sqrt(sum(pow(a-b,2) for a, b in zip(x, y)))

# # def distance_to_similarity(distance): # ! normalizes distance from 0 to 1
# #   return 1/np.exp(distance) # computes 1/e^distance

# # def master_euclidean_distance_to_similarity(sentence_1, sentence_2):
# #     embeddings = [nlp(sentence).vector for sentence in [sentence_1, sentence_2]]
# #     return distance_to_similarity(euclidean_distance(embeddings[0], embeddings[1]))

# # # print(master_euclidean_distance_to_similarity("my cat wears a hat", "my cat is wearing a hat"))


# # # def sub_relevance_rater(relevant_words_dict, description_array):
# # #     relevance_rating = 0
# # #     for word in description_array:
# # #         if word in relevant_words_dict:
# # #             relevance_rating += relevant_words_dict[word]
# # #     return relevance_rating

# # # def relevance_rater(tags, description):
# # #     tags_frequency = []
# # #     tags_prominence_iterator = 0
    
# # #     # word_relevance_ratings = [0] * len(description)
    
# # #     word_relevance_manager = multiprocessing.Manager()
# # #     word_relevance_ratings = [0] * len(description)
# # #     word_relevance_ratings = word_relevance_manager.list(word_relevance_ratings)
    
# # #     tags_frequency_manager = multiprocessing.Manager()
# # #     tags_frequency = tags_frequency_manager.list()
# # #     tags_prominence_iterator = multiprocessing.Value('i', 0)
    
# # #     for i in range(len(description)):
# # #     with ThreadPool() as relevance_rater_pool:
# # #         relevance_rater_starmap = relevance_rater_pool.starmap_async(relevance_rater_worker, [(tags, description, i, word_relevance_ratings, tags_frequency, tags_prominence_iterator)])
    
# # #     # ! ADD THREADPOOL FOR EACH i
# # #     for i in range(len(tags)):
        
# # #         tag = tags[i].strip()
        
# # #         with ThreadPool() as relevance_rater_pool:
# # #             relevance_rater_starmap = relevance_rater_pool.starmap_async(sub_relevance_rater, [(j, tag, description[j].strip(), tags, word_relevance_ratings, tags_frequency, tags_prominence_iterator) for j in range(len(description))]).get()
            
# # #             relevance_rater_pool.terminate()
    
# # #     divider = (len(description)**2)/len(tags) #["exam", "sits", "C"]: 0.36; ["exam", "boobs", "favourite"]: 0.54 for "This is_. a test. What if tits are the best things in the world?
# # #         # "This is_. a test. What if tits are the best things in the world?" has significant words: ['test', 'tits', 'best', 'things', 'world']
    
# # #     # NOTE: The Wu-Palmer Similarity measures "boobs" and "tits" to have a 1.0 similarity score!
    
# # #     # ! TRYING JUST SUM BECAUSE A WEBSITE SHOULDN'T BE PENALIZED FOR HAVING A LONG DESCRIPTION
# # #     description_fuzzy_hmni_synonym_rating = round(sum(word_relevance_ratings), 2)
# # #     # description_fuzzy_hmni_synonym_rating = round((sum(word_relevance_ratings) / divider), 2)
    
# # #     tags_frequency_dict = dict(Counter(tags_frequency))
    
# # #     # print(word_relevance_ratings)
# # #     return [description_fuzzy_hmni_synonym_rating, tags_frequency_dict]


# https://newscatcherapi.com/blog/ultimate-guide-to-text-similarity-with-python
# ! JACCARD SIMILARITY -> WORSE THAN COSINE AND EUCLIDEAN, DON'T USE!!!
# number of shared words/total number of unique words between two arrays
# # # def jaccard_similarity(x, y):
# # #     # formats the text properly
# # #     if (type(x) != list):
# # #         x = [word.lower() for word in x.split()]
# # #     if (type(y) != list):
# # #         y = [word.lower() for word in y.split()]
# # #     x = [word.strip(' ') for word in x]
# # #     y = [word.strip(' ') for word in y]
    
# # #     """ returns the jaccard similarity between two lists """
# # #     intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
# # #     union_cardinality = len(set.union(*[set(x), set(y)]))
    
# # #     jaccard_similarity = intersection_cardinality/float(union_cardinality)
# # #     print("Jaccard similarity: ", jaccard_similarity)
    
# # #     normalized_jaccard_similarity = jaccard_similarity/float(min(len(x), len(y))) # ! normalizes similarity from 0 to 
# # #     # ! max = 1/float(min(len(x), len(y)))
# # #     # ! min = 0
# # #     return normalized_jaccard_similarity
# # # # print(jaccard_similarity('below bob','below bob cat hat'))
