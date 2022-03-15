import nltk
import pandas as pd
import re
from collections import Counter
import time
import numpy as np
import PyDictionary
import json
import itertools
import warnings
warnings.filterwarnings("ignore")

import requests
import json


t1 = time.time()
Dictionary =  PyDictionary.PyDictionary()
word = 'Apathy'
temp_df = pd.DataFrame(columns= [word,'word'])
syns = Dictionary.synonym(word)
while syns is None:
    syns = Dictionary.synonym(word)
    
temp_list1 = syns
temp_list2 = []
words = []
score = []
words.extend(syns)
score.extend(np.repeat(1,len(syns)))
print('stage -1')
print(temp_list1)
    
for i in range(1):
    print('loop',i)
    for j in temp_list1:        
        if j not in words:
            print('inner')
            word_in = j.split(' ')[0]
            syns = Dictionary.synonym(word_in)
            count = 0
            while syns is None:
                syns = Dictionary.synonym(word_in)
            if syns is not None:
                temp_list2.extend(syns)

    words.extend(temp_list2)
    score.extend(np.repeat(1-0.005*i,len(temp_list2)))
    temp_list1 = temp_list2

    
    
#     syns = Dictionary.synonym(word)
#     while temp is None:
#         syns = Dictionary.synonym(word)
print(time.time()-t1)