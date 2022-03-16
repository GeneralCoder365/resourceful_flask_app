import nltk
import pandas as pd
import re
from collections import Counter
import time
import numpy as np
# import PyDictionary
import json
import itertools
import warnings
warnings.filterwarnings("ignore")

import requests
from bs4 import BeautifulSoup
import lxml
import cchardet # lxml and cchardet speed up requests data processing
import json


# ! The below Code Finds the Synonyms1 for one word, For that synonyms1 next synonyms2 will be searched 
# ! This way the process will be continued to Fetch all the relative words of mentioned word. 
# ! The stages of word synonyms will be given with the score for each stage to point how relative the word is.
# Dictionary =  PyDictionary.PyDictionary()

def synonyms(word):
    response = requests.get('https://www.thesaurus.com/browse/{}'.format(word))
    soup = BeautifulSoup(response.text, 'lxml')
    soup.find('div', {'class': 'css-ixatld e15rdun50'})
    synonyms = [span.text for span in soup.findAll('a', {'class': 'css-1kg1yv8 eh475bn0'})]
    less_relevant_synonyms = [span.text for span in soup.findAll('a', {'class': 'css-1gyuw4i eh475bn0'})]
    synonyms = [word] + synonyms + less_relevant_synonyms # includes word as a synonym of itself!
    return synonyms 

# word = "character"
# print(synonyms(word))

def extended_synonyms(word, base_syns):
    word = word.lower()
    temp_df = pd.DataFrame(columns= [word,'word'])
    syns = synonyms(word)
        
    temp_list1 = syns
    temp_list2 = []
    words = []
    score = []
    words.extend(syns)
    score.extend(np.repeat(1,len(syns)))
    print('stage -1')
    print(temp_list1)

    # Looping the dataframe to 
    for i in range(1):
        print('loop',i)
        
        for j in temp_list1:
            
            if j not in words:
                print('inner')
                word_in = j.split(' ')[0]
                print("word_in",word_in)
                new_syns = synonyms(word_in)
                count = 0
                if syns is not None:
                    temp_list2.extend(new_syns)

        words.extend(temp_list2)
        score.extend(np.repeat(1-0.005*i,len(temp_list2)))
        temp_list1 = temp_list2

    print(temp_list1)
    
word = 'apathy'
print(extended_synonyms(word, synonyms(word)))



def Json_data(x,word_feature):
    '''
    Function to extract the different types of information from Json data of word`
    
    '''
    if word_feature == 'synonyms':
        j_val = 'swds'
    elif word_feature =='meaning':
        j_val = 'sdsc'
    else:
        return 'Not Found'
    
    sub_means= x[1:][:-1].split('},')
    if len(sub_means)>1:
        json_data = [json.loads(sub_means[word]+'}')[j_val] for word in range(len(sub_means)-1)]
        return np.unique([word.replace(' ','') for word in ','.join(json_data).split(',')])
    else:
        return np.unique([word.replace(' ','') for word in json.loads(sub_means[0])[j_val].split(',')])
    

import sys 
import math
BETA = 0.45
ALPHA = 0.2

def get_best_synset_pair(word_1, word_2):
    """ 
    Choose the pair with highest path similarity among all pairs. 
    Mimics pattern-seeking behavior of humans.
    """
    syns1 = nltk.corpus.wordnet.synsets(word_1)
    syns2 = nltk.corpus.wordnet.synsets(word_2)
    a =  np.array([nltk.corpus.wordnet.path_similarity(i,j) for i,j in itertools.product(syns1,syns2)])
    a = np.array(list(map(lambda x: x if x != None else 0,list(a))))
    best_pair = list(itertools.product(syns1,syns2))[np.argmax(a)]
    return best_pair

def length_dist(synset_1, synset_2):
    """
    Return a measure of the length of the shortest path in the semantic 
    ontology (Wordnet in our case as well as the paper's) between two 
    synsets.
    """
    l_dist = sys.maxsize
    if synset_1 is None or synset_2 is None: 
        return 0.0
    if synset_1 == synset_2:
        # if synset_1 and synset_2 are the same synset return 0
        l_dist = 0.0
    else:
        wset_1 = set([str(x.name()) for x in synset_1.lemmas()])        
        wset_2 = set([str(x.name()) for x in synset_2.lemmas()])
        if len(wset_1.intersection(wset_2)) > 0:
            # if synset_1 != synset_2 but there is word overlap, return 1.0
            l_dist = 1.0
        else:
            # just compute the shortest path between the two
            l_dist = synset_1.shortest_path_distance(synset_2)
            if l_dist is None:
                l_dist = 0.0
    # normalize path length to the range [0,1]
    return math.exp(-ALPHA * l_dist)

def hierarchy_dist(synset_1, synset_2):
    """
    Return a measure of depth in the ontology to model the fact that 
    nodes closer to the root are broader and have less semantic similarity
    than nodes further away from the root.
    """
    h_dist = sys.maxsize
    if synset_1 is None or synset_2 is None: 
        return h_dist
    if synset_1 == synset_2:
        # return the depth of one of synset_1 or synset_2
        h_dist = max([x[1] for x in synset_1.hypernym_distances()])
    else:
        # find the max depth of least common subsumer
        hypernyms_1 = {x[0]:x[1] for x in synset_1.hypernym_distances()}
        hypernyms_2 = {x[0]:x[1] for x in synset_2.hypernym_distances()}
        lcs_candidates = set(hypernyms_1.keys()).intersection(
            set(hypernyms_2.keys()))
        if len(lcs_candidates) > 0:
            lcs_dists = []
            for lcs_candidate in lcs_candidates:
                lcs_d1 = 0
                if lcs_candidate in hypernyms_1:
                    lcs_d1 = hypernyms_1[lcs_candidate]
                lcs_d2 = 0
                if lcs_candidate in hypernyms_2:
                    lcs_d2 = hypernyms_2[lcs_candidate]
                lcs_dists.append(max([lcs_d1, lcs_d2]))
            h_dist = max(lcs_dists)
        else:
            h_dist = 0
    return ((math.exp(BETA * h_dist) - math.exp(-BETA * h_dist)) / 
        (math.exp(BETA * h_dist) + math.exp(-BETA * h_dist)))
    
def word_similarity(word_1, word_2):
    '''
    Function to Calculate the Similarity between two words based on the Lexical word synonyms in NLTK library
    with the use of Natural language toolkit library synonyms similariy
    
    '''
    
    try:
        synset_pair = get_best_synset_pair(word_1, word_2)
    except:
        return 0
    return (length_dist(synset_pair[0], synset_pair[1]) * 
        hierarchy_dist(synset_pair[0], synset_pair[1]))


def Synonyms_threshold_setting(word,threshold):
    '''
    Function to Calculate the Float value Similarity between feature word and Netword of words
    
    Similarity Between words  = Weight of level(W) * Wordnet Similarity (S)
    
    '''
    
    if word not in word_synonyms.keys():
        return [word],[0]
    
    syns = list(word_synonyms[word])
    scores = list(map(lambda x: (word_similarity('apathy',x)+threshold)/2,syns))

    return syns,scores


def Threshold_tree(word,threshold):
    '''
    Threshold tree function will fix the Threshold of weights to multiply to words level by level
    
    weight will get reduced by 2% for each time it progressed to inner level
    
    '''
    syn_scores = Synonyms_threshold_setting(word,threshold)
    word_dict = dict(zip(syn_scores[0],syn_scores[1]))
    temp_dict1 = word_dict

    for deep in range(1):
        print ('loop 1',i)
        temp_dict2 = {}
        for syn in temp_dict1.keys():
            syn_scores = Synonyms_threshold_setting(syn,temp_dict1[syn])
            syn_scores = dict(zip(syn_scores[0],syn_scores[1]))
            temp_dict2.update(syn_scores)
        
        temp_dict1 = temp_dict2
        temp_dict2.update(word_dict)
        word_dict = temp_dict2
    return word_dict

# # Creating the Dictionary of Word Synonyms and Word Meanings for all words in a dictionary
# word_dict['Synonyms'] = word_dict.meanings.apply(lambda x: Json_data(x,'synonyms'))
# word_dict['word_mean'] =  word_dict.meanings.apply(lambda x: Json_data(x,'meaning'))
# word_synonyms = dict([(i,j) for i,j in zip(word_dict.word,word_dict.Synonyms)])