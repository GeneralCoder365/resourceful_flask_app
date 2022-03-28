import re
import sys
import time
import json
# import builtins as __builtin__
import multiprocessing
# from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
# import threading
# from pathos.multiprocessing import ProcessingPool as Pool
# import dill
# import multiprocessing_on_dill as multiprocessing
# from xml import dom

import lxml
import cchardet # lxml and cchardet speed up requests data processing
from bs4 import BeautifulSoup as bs
import requests

# from memory_profiler import profile # used for detailed breakdown of memory usage


# import resource_finder
# import web_crawler_multiprocess
# import relevance_analyzer

summary_list = ["about", "summary", "mission", "overview", "about this course", "about this professional certificate", "about this opportunity", "about this specialization", "purpose", "our purpose", "description"]


# url = "https://www.coursera.org/learn/machine-learning"

def relevant_words_dict_generator(tags, dom_queue):
    import relevant_words_generator
    relevant_words_generator.master_relevant_words_generator(tags, dom_queue)

def master_query_maker(tags, relevant_words_dict, dom_queue):
    import resource_finder
    resource_finder.query_maker(tags, relevant_words_dict, dom_queue)

def master_web_crawler(search_queries, dom_queue):
    import web_crawler_multiprocess
    web_crawler_multiprocess.master_urls_to_search(search_queries, dom_queue)

def overview_finder(bottom_session, url):
    text_list = []
    
    k = 1
    try:
        # request = requests.get(url)
        request = bottom_session.get(url)
    except Exception as e:
        return False
        
 
    # Soup = bs(request.text, 'html.parser')
    Soup = bs(request.text, 'lxml')
 
    # creating a list of all common heading tags
    wanted_tags = ["h1", "h2", "h3", "h4", "h5", "p"]
    for tags in Soup.find_all(wanted_tags):
        text_list.append(tags.text.strip())
            
    # print("text_list: ", text_list)
    for i in text_list:
        # for j in range(len(summary_list)):
        #     if i.lower() in summary_list[j]:
        if i.lower() in summary_list:
            # print("Header: " + i)
            # print("k: " + str(k)) 
            break
        k += 1
        
            
    # print(text_list)
    # print(text_list[-1])
    # print(len(text_list))
    # print(k)
    # print(text_list[k])
    try:
        if text_list[k].lower() == "applied learning project":
            # print(text_list[k + 1])
            return(text_list[k + 1])
        else:                  
            # print(text_list[k])
            return(text_list[k])
    except IndexError:
        return False

def other_info_finder(url): # for Coursera only
    t_list = []

    r_list = []
    
    s = 1
    u = 0
    request = requests.get(url)
 
    Soup = bs(request.text, 'html.parser')
    
    w_tags = ["h1", "h2", "h3", "span"]
    for tags in Soup.find_all(w_tags):
        t_list.append(tags.text.strip())
    
    for l in t_list:
        if "approx" in l.lower():
            t = l.split(" ")
            r_list.append(t[1])
            
    for x in t_list:
        if x.lower() == "offered by":
            break
        
        s += 1
    r_list.append(t_list[s])
    
    r = list(dict.fromkeys(r_list))
    
    # print(r)
    return r

# other_info_finder(url) 
# print(overview_finder("https://www.coursera.org/specializations/data-structures-algorithms"))

def tags_to_dict(str_tags):
    tags = dict(json.loads(str_tags))
    
    return tags

# ! used to solve AttributeError: Can't pickle local object 'master_results.<locals>.description_relevance_calculator'
# global description_relevance_calculator
def description_relevance_calculator(hashmap_description_relevance, relevance_calculator, bottom_session, tags_to_compare_to, url):
    bottom_time = time.time()
    print("HELLOOOOOO")
    print("CURRENT TAGS TO COMPARE TO: ", tags_to_compare_to)
    print("CURRENT URL: ", url)
    print("HASHMAP CURRENT: ", hashmap_description_relevance)
    if (url in hashmap_description_relevance.keys()):
        print("URL FOUND IN HASHMAP")
        data = hashmap_description_relevance[url]
        if (data == False):
            return (url, False)
        print("Description relevance process finished --- %s seconds ---" % (time.time() - bottom_time))
        return (url, data[0], data[1], data[2]) # (url, description, relevance, tags_frequency)
    
    else:
        # description = str(overview_finder(url))
        description = str(overview_finder(bottom_session, url))
        # print("DESCRIPTION: ", description)

        if (description != "False"): # only include urls that we can pull descriptions from
            relevance_data = relevance_calculator(tags_to_compare_to, description)
            relevance = relevance_data[0]
            tags_frequency = relevance_data[1] # {'exam': 3, 'boobs': 2, 'favourite': 1}
            # tags_frequency_dict[urls_to_search[j]] = tags_frequency
            # print("current relevance: ", relevance)
            if (relevance == False):
                relevance = 0
            
            # print("RELEVANCE: ", relevance)
            print("Description relevance process finished --- %s seconds ---" % (time.time() - bottom_time))
            return (url, description, relevance, tags_frequency)
        print("Description relevance process finished --- %s seconds ---" % (time.time() - bottom_time))
        return (url, False)
        # else:

def top_results(i, bottom_session, hashmap_description_relevance, relevance_calculator, all_urls_to_search):
    i_urls_to_search = all_urls_to_search[i]
    print("I URLS TO SEARCH: ", i_urls_to_search)
    # relevance_calculator = dill.loads(pickled_relevance_calculator)
    
    # i_urls_to_search = all_urls_to_search[i]
    if "type_of_opportunity" in i_urls_to_search:
        type_of_opportunity = i_urls_to_search["type_of_opportunity"]
    if "skill_interest" in i_urls_to_search:
        skill_interest = i_urls_to_search["skill_interest"]
    if "in_person_online" in i_urls_to_search:
        in_person_online = i_urls_to_search["in_person_online"]
    if "location" in i_urls_to_search:
        location = i_urls_to_search["location"]
        print("HAGOBA")
    urls_to_search = i_urls_to_search["urls_to_search"]
    
    # tags_to_compare_to = [skill_interest, type_of_opportunity, in_person_online]
    if (in_person_online == "online"):
        tags_to_compare_to = [skill_interest, type_of_opportunity, in_person_online]
    else:
        tags_to_compare_to = [skill_interest, type_of_opportunity, location]
        
    relevance_ratings_dict = {}
    tags_frequency_dict = {}
    all_description_dict = {}
    
    # top_threads = []
    
    # for j in range(len(urls_to_search)):
    #     description_relevance_thread = threading.Thread(target=description_relevance_calculator, args=(relevance_analyzer.result_relevance_calculator, tags_to_compare_to, urls_to_search[j], top_queue))
    #     top_threads.append(description_relevance_thread)
    dom_time = time.time()
    with ThreadPool() as bottom_pool: # not specifying Pool(processes=__) so using max number of cores on computer
        # bottom_pool = bottom_pool.starmap_async(description_relevance_calculator, [(relevance_analyzer.result_relevance_calculator, tags_to_compare_to, urls_to_search[j]) for j in range(len(urls_to_search))]).get()
        bottom_pool_starmap = bottom_pool.starmap_async(description_relevance_calculator, [(hashmap_description_relevance, relevance_calculator, bottom_session, tags_to_compare_to, urls_to_search[j]) for j in range(len(urls_to_search))]).get()
        # ! hashmap_description_relevance may have memory sharing error
        # ! line 200, in master_results
        # ! IndexError: list index out of range
        # top_results = bottom_pool.get()
        bottom_pool.terminate()
    # print("POOL ", i, " RESULTS: ", bottom_pool)
    print("POOL ", i, " RESULTS: ", bottom_pool_starmap)
    # # print("TOP_THREADS: ", top_threads)
    print("Pool process finished --- %s seconds ---" % (time.time() - dom_time))
    # for t_thread in top_threads:
    #     t_thread.start()
    # print("FINISHED STARTING TOP_THREADS")
    # for t_thread in top_threads:
    #     print("FINISHING TOP_THREAD")
    #     t_thread.join()
    #     print("FINISHED TOP_THREAD")
    
    # if (len(urls_to_search) == top_queue.qsize()):
    #     print("GOOODDDDD!!!")
    
    # for k in range(top_queue.qsize()):
    #     description_relevance_data = top_queue.get()
        # (url, description, relevance, tags_frequency)
    
    top_hashmap_description_relevance = {}
    
    print("BOTTOM POOL STARMAP: ", bottom_pool_starmap)
    
    for description_relevance_data in bottom_pool_starmap:
        print("DESCRIPTION RELEVANCE DATA: ", description_relevance_data)
        try:
            if (description_relevance_data[1] == None):
                print("WEIRD SHIT IS HAPPENING!!!")
                print("WEIRD SHIT URL IS: ", description_relevance_data[0])
                print("WEIRD SHIT LENGTH IS: ", len(description_relevance_data))
            if (description_relevance_data[1] != False): # (url, False)
                url = description_relevance_data[0]
                description = description_relevance_data[1]
                relevance = description_relevance_data[2]
                tags_frequency = description_relevance_data[3]
                
                all_description_dict[url] = description
                tags_frequency_dict[url] = tags_frequency
                relevance_ratings_dict[url] = relevance
                
                top_hashmap_description_relevance[url] = [description, relevance, tags_frequency] # hdr[url] = [description, relevance, tags_frequency]  # (url, description, relevance, tags_frequency)
            else:
                url = description_relevance_data[0]
                # top_hashmap_description_relevance[url] = [False] # hdr[url] = [False]
                top_hashmap_description_relevance[url] = False
        except TypeError:
            print("WEIRD FUCKSHIT HAPPENED DESCRIPTION RELEVANCE DATA IS NONETYPE FOR SOME REASON")
    
    print("TOP_HASHMAP_DESCRIPTION_RELEVANCE: ", top_hashmap_description_relevance)
    # need to call .close() before using .join()
    # bottom_pool.close()
    # bottom_pool.join()

    # sorts in descending order
    relevance_ratings_dict = dict(sorted(relevance_ratings_dict.items(), key=lambda x:x[1], reverse=True))
    print("RELEVANCE_RATINGS_DICT: ", relevance_ratings_dict)
    
    # print("sorted relevance_ratings_dict: ", relevance_ratings_dict)
    
    relevance_ratings_dict = dict(list(relevance_ratings_dict.items())[0: 5])
    
    print("processed relevance_ratings_dict: ", relevance_ratings_dict)
    
    resource_data_dict = {}
    for a in relevance_ratings_dict.keys():
        description =  re.sub(r'[^a-zA-Z0-9.!? ]', '', all_description_dict[a])
        resource_data_dict[a] = [description, tags_frequency_dict[a]]
    print("resource_data_dict: ", resource_data_dict)
    # hashmap_description_relevance.update(resource_data_dict) # !!!!
    
    url_dict = {}
    if (type_of_opportunity == "sports"):
        url_dict["sport"] = i_urls_to_search["sport"]
        url_dict["type_of_opportunity"] = i_urls_to_search["type_of_opportunity"]
    else:
        url_dict["skill_interest"] = skill_interest
        url_dict["type_of_opportunity"] = type_of_opportunity
        url_dict["in_person_online"] = in_person_online
        if ("location" in url_dict.keys()):
            url_dict["location"] = location
    url_dict["resource_data_dict"] = resource_data_dict
    
    print("url_dict: ", url_dict)
    
    hashmap_description_relevance.update(top_hashmap_description_relevance)
    
    # top_queue.put(url_dict)
    return url_dict


# global master_results
# @profile
def master_results(all_urls_to_search, dom_queue):
    import relevance_analyzer_multiprocess
    
    # top_queue = multiprocessing.Queue()
    
    
    # https://towardsdatascience.com/parallelism-with-python-part-1-196f0458ca14
    search_results = {}
    
    print("NUMBER OF POOLS TO CREATE: ", len(all_urls_to_search))
    
    bottom_session = requests.Session()
    
    top_manager = multiprocessing.Manager()
    hashmap_description_relevance = top_manager.dict()
    
    with ThreadPool() as top_pool:
        # top_pool_starmap = top_pool.starmap_async(top_results, [(i, bottom_session, hashmap_description_relevance, relevance_analyzer.relevance_calculator) for i in range(len(all_urls_to_search))]).get()
        top_pool_starmap = top_pool.starmap_async(top_results, [(i, bottom_session, hashmap_description_relevance, relevance_analyzer_multiprocess.result_relevance_calculator, all_urls_to_search) for i in range(len(all_urls_to_search))]).get()

        top_pool.terminate()
    
    for i in range(len(top_pool_starmap)):
        search_results[i] = top_pool_starmap[i]
    
    search_results = json.dumps(search_results)
    print("SEARCH RESULTS: ", search_results)
    # pickled_search_results = dill.dumps(search_results)
    # print("PICKLED SEARCH RESULTS: ", pickled_search_results)
    print("PRE DOM QUEUE SIZE: ", dom_queue.qsize())
    dom_queue.put(search_results)
    print("POST DOM QUEUE SIZE: ", dom_queue.qsize())
    print("MASTER RESULTS DONE")
    
    # return None


def url_grouper(url_dicts_array):
    print("URL DICTS ARRAY: ", url_dicts_array)
    # url_dict = {
        # "url": url -> str
        # "type_of_opportunity": type_of_opportunity -> str
        # "skill_interest": skill_interest -> str
        # "in_person_online": in_person_online -> str
        # "location": location # ! OPTIONAL -> str
        # "composite_relevance_score": composite_relevance_score -> float
        # "tags_frequency": tags_frequency -> dict
    # }

    url_groups = {} # dict containing arrays by groups of form
                                    # {url: [composite_relevance_score, description, tags_frequency]}, ...
    # FRAME BY: keys: "type_of_opportunity, skill_interest, in_person_online, location"
    # SAME type_of_opportunity, skill_interest, in_person_online, location

    for url_dict in url_dicts_array:
        # has_location = False
        key_to_search = ""
        if "url" in url_dict.keys():
            url = url_dict["url"]
        if "description" in url_dict.keys():
            description = url_dict["description"]

        if "type_of_opportunity" in url_dict.keys():
            key_to_search += url_dict["type_of_opportunity"]  + " "
        if "skill_interest" in url_dict.keys():
            key_to_search += url_dict["skill_interest"] + " "
        if "in_person_online" in url_dict.keys():
            key_to_search += url_dict["in_person_online"] + " "
        if "location" in url_dict.keys():
            key_to_search += url_dict["location"] + " "
            # has_location = True

        if "composite_relevance_score" in url_dict.keys():
            composite_relevance_score = url_dict["composite_relevance_score"]
        if "tags_frequency" in url_dict.keys():
            tags_frequency = url_dict["tags_frequency"]


        if key_to_search in url_groups.keys():
            entry = url_groups[key_to_search]
            entry.append({
                url: [composite_relevance_score, description, tags_frequency]
            })
            url_groups[key_to_search] = entry
        else:
            url_groups[key_to_search] = [{
                url: [composite_relevance_score, description, tags_frequency]
            }]

    return url_groups

def results_formatter(url_groups):
    print("URL GROUPS: ", url_groups)
    results_dict = {}
    for url_group_key, url_group in url_groups:
        sorted_url_group = dict(sorted(url_group.items(), key=lambda item: item[1][0], reverse=True))
        if (len(sorted_url_group) > 5):
            top_five_sorted_url_group = {k: sorted_url_group[k] for k in sorted_url_group.keys()[:5]}
        else:
            top_five_sorted_url_group = sorted_url_group
        
        # removes relevance score since it is no no longer needed
        for url, url_data in top_five_sorted_url_group.items():
            data = url_data
            removed_relevance_score = data.pop(0)
            top_five_sorted_url_group[url] = data

    results_dict[url_group_key] = top_five_sorted_url_group

    return results_dict


# tags, description, relevant_words_dict
def master_relevance_analyzer(all_urls_to_search, relevant_words_dict): # ! just return normally no need to make this a separate process
    # ! NEED TO ADD BACK HASHMAP IF NOT FAST ENOUGH!!!
    pre_top_time = time.time()
    spacy_time = time.time()
    import relevance_analyzer_v2
    relevance_calculator = relevance_analyzer_v2.result_relevance_calculator
    print("SPACY IMPORT FINISHED --- %s seconds ---" % (time.time() - spacy_time))
    # ! SPACY IMPORT FINISHED --- 31.02342939376831 seconds ---
    
    # top_queue = multiprocessing.Queue()
    # relevance_processes = []
    relevance_threads_parameters = []
    
    top_session = requests.Session()
    
    # print("RELEVANCE WORDS DICT: ", relevant_words_dict)
    
    for group_of_urls_to_search in all_urls_to_search:
        url_dict = {}
        try:
            if "type_of_opportunity" in group_of_urls_to_search:
                type_of_opportunity = group_of_urls_to_search["type_of_opportunity"]
                url_dict["type_of_opportunity"] = type_of_opportunity
            if "skill_interest" in group_of_urls_to_search:
                skill_interest = group_of_urls_to_search["skill_interest"]
                url_dict["skill_interest"] = skill_interest
            if "in_person_online" in group_of_urls_to_search:
                in_person_online = group_of_urls_to_search["in_person_online"]
                url_dict["in_person_online"] = in_person_online
            if "location" in group_of_urls_to_search:
                location = group_of_urls_to_search["location"]
                url_dict["location"] = location
                print("HAGOBA")
            urls_to_search = group_of_urls_to_search["urls_to_search"]
            
            # tags_to_compare_to = [skill_interest, type_of_opportunity, in_person_online]
            if (in_person_online == "online"):
                tags_to_compare_to = [skill_interest, type_of_opportunity, in_person_online]
            else:
                tags_to_compare_to = [skill_interest, type_of_opportunity, location]
            
            tags_to_compare_relevant_words_dict = {}

            for tag in tags_to_compare_to:
                tag = tag.lower().strip()
                if (tag not in relevant_words_dict.keys()):
                    print("TAG NOT IN RELEVANT WORDS DICT: ", tag)
                tags_to_compare_relevant_words_dict[tag] = relevant_words_dict[tag]
                sub_tags = tag.split()
                if (len(sub_tags) > 1):
                    for sub_tag in sub_tags:
                        tags_to_compare_relevant_words_dict[sub_tag] = relevant_words_dict[sub_tag]
            
            if (len(urls_to_search) == 0):
                print("WEIRD SHIT IS HAPPENING")
            
            for url in urls_to_search:
                url_dict["url"] = url
                description = str(overview_finder(top_session, url))
                url_dict["description"] = description
                # relevance_process = multiprocessing.Process(target=relevance_calculator, args=(tags_to_compare_to, tags_to_compare_relevant_words_dict, url_dict, top_queue))
                relevance_thread_parameters = (tags_to_compare_to, tags_to_compare_relevant_words_dict, url_dict)
                # relevance_thread_parameters_print = (tags_to_compare_to, url_dict)
                # print("RELEVANCE THREAD PARAMETERS: ", relevance_thread_parameters_print)
                relevance_threads_parameters.append(relevance_thread_parameters)
        except Exception as e:
            print("Error: " + str(e))
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print("Didn't work :(")

            return False
        
    print("RELEVANCE PROCESSES READY FOR EXECUTION")
    print("PRE TOP STUFF finished --- %s seconds ---" % (time.time() - pre_top_time))
    # ! PRE TOP STUFF finished --- 81.4465844631195 seconds ---
    # ! PARAMETERS PREPARATION TIME: PRE TOP TIME - SPACY IMPORT TIME = 
    # ! 81.4465844631195 - 31.02342939376831 
    # ! = 50.421805849609375 seconds
    print("RELEVANCE PARAMETERS: ", relevance_threads_parameters)
    
    # top_time = time.time()
    # with ThreadPool() as top_pool:
    #     top_pool_starmap = top_pool.starmap_async(relevance_calculator, [param for param in relevance_threads_parameters]).get()
    #     top_pool.terminate()
    # # ! WRITE ALGORITHM THAT GROUPS THE RESULTS BY SKILL INTEREST, TYPE OF OPPORTUNITY, IN PERSON ONLINE, LOCATION (IF APPLICABLE)
    #     # ! THEN SORTS THE RESULTS WITHIN EACH GROUP BY RELEVANCE
    # # ! RETURN FORMATTED RESULTS
    # url_dicts_array = top_pool_starmap
    # print("TOP POOL RESULTS: ", url_dicts_array)
    # print("Pool process finished --- %s seconds ---" % (time.time() - top_time))

    # url_groups = url_grouper(url_dicts_array)
    # results_dict = results_formatter(url_groups)
    
    
    # return results_dict

# @profile
def master_scraper(tags, master_queue):
    # if __name__ == '__main__':
    
    try:
        dom_time = time.time()
        dom_queue = multiprocessing.Queue()
        
        tags = tags_to_dict(tags)
        
        print("tags: ", tags)
        
        # tags:  {'skills': ['computer science', 'cs', 'math'], 'interests': ['machine learning', 'probability'], 'type_of_opportunity': ['courses'], 'in_person_online': 'all', 'location': 'Rockville MD USA'}
        tags_array = []
        for category, category_tags in tags.items():
            if ((category == "in_person_online") and (category_tags != "online")):
                pass
            else:
                if (type(category_tags) == list):
                    tags_array += category_tags
                elif (type(category_tags) == str):
                    tags_array.append(category_tags)
        print("tags_array: ", tags_array)
        
        
        relevant_words_process = multiprocessing.Process(target=relevant_words_dict_generator, args=(tags_array, dom_queue))
        relevant_words_process.start()
        while dom_queue.qsize() == 0:
            pass
        # if (dom_queue.qsize() != 0):
        #     print("YEETUS")
        # relevant_words_process.join()
        # print("YEETUS FETUS")
        relevant_words_dict = dom_queue.get()
        relevant_words_process.terminate()
        if (len(relevant_words_dict) > 0):
            print("RELEVANT WORDS DICT NOT EMPTY")
        
        search_queries_process = multiprocessing.Process(target=master_query_maker, args=(tags, relevant_words_dict, dom_queue))
        # search_queries_process = multiprocessing.Process(target=resource_finder.database_lister_query_maker, args=(tags, dom_queue))
        search_queries_process.start()
        search_queries_process.join()
        search_queries = dom_queue.get()
        search_queries_process.terminate()
        print("SEARCH QUERIES PROCESS IS ALIVE: ", search_queries_process.is_alive())
        # search_queries = resource_finder.database_lister_query_maker(tags)
        print("search_queries: ", search_queries)
        print("DOM_QUEUE SIZE = ", dom_queue.qsize())
        
        web_crawler_process = multiprocessing.Process(target=master_web_crawler, args=(search_queries, dom_queue))
        # web_crawler_process = multiprocessing.Process(target=web_crawler_multiprocess.master_urls_to_search, args=(search_queries, dom_queue))
        web_crawler_process.start()
        print("PREBOOB")
        web_crawler_process.join()
        print("BOOB")
        all_urls_to_search = dom_queue.get()
        print("POSTBOOB")
        web_crawler_process.terminate()
        print("WEB CRAWLER PROCESS IS ALIVE: ", web_crawler_process.is_alive())
        print("ENDBOOB")
        
        
#         all_urls_to_search = [{'skill_interest': 'cs', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.montgomerycollege.edu/academics/departments/engineering-physical-computer-sciences-rockville/index.html', 'https://coursebulletin.montgomeryschoolsmd.org/CourseLists/Index/163', 'https://www.coursera.org/learn/introcss', 'https://www.coursera.org/learn/duke-programming-web', 'https://www.oercommons.org/courses/cs-fundamentals-4-5-events-in-bounce/view#summary-tab', 'https://www.coursera.org/learn/introduction-to-web-development-with-html-css-javacript', 'https://www.montgomeryschoolsmd.org/curriculum/computer-science/index.aspx', 'https://www.computerscience.org/online-degrees/maryland/', 'https://www.coursera.org/learn/html-css-javascript-for-web-developers', 'https://www.coursera.org/projects/design-and-develop-website-using-figma-and-css', 'https://www.montgomerycollege.edu/academics/programs/computer-science-and-technologies/index.html', 'https://www.oercommons.org/courses/cs-discoveries-2019-2020-web-development-lesson-2-2-websites-for-expression/view#summary-tab', 'https://www.oercommons.org/courses/cs-for-oregon-plan-version-1-0/view#summary-tab', 'https://www.oercommons.org/courses/cs-fundamentals-7-1-learn-to-drag-and-drop/view#summary-tab', 'https://www.oercommons.org/courses/cs-fundamentals-2-10-the-right-app/view#summary-tab']}, {'skill_interest': 'probability', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.oercommons.org/courseware/lesson/4140/view#summary-tab', 'https://www.coursera.org/learn/stanford-statistics', 'https://www.wyzant.com/Rockville_MD_statistics_tutors.aspx', 'https://www.coursera.org/specializations/advanced-statistics-data-science', 'https://www.coursera.org/learn/introductiontoprobability', 'https://www.oercommons.org/courseware/lesson/4158/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/53607/view#summary-tab', 'https://www.montgomerycollege.edu/academics/stem/mathematics-statistics-data-science/index.html', 'https://www.oercommons.org/courseware/lesson/4104/view#summary-tab', 'https://www.montgomerycollege.edu/academics/support/learning-centers/math-course-resources/math-132.html', 'https://www.montgomeryschoolsmd.org/departments/onlinelearning/courses/ap.aspx', 'https://www.coursera.org/specializations/probabilistic-graphical-models', 'https://www.oercommons.org/courseware/lesson/14210/view#summary-tab', 'https://www.coursera.org/learn/probability-theory-foundation-for-data-science', 'https://coursebulletin.montgomeryschoolsmd.org/CourseDetails/Index/MAT2039']}, {'skill_interest': 'math', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.oercommons.org/courseware/lesson/86384/view#summary-tab', 'https://www.montgomeryschoolsmd.org/curriculum/math/hs.aspx', 'https://www.montgomeryschoolsmd.org/curriculum/math/', 'https://www.coursera.org/specializations/mathematics-machine-learning', 'https://www.montgomerycollege.edu/academics/stem/mathematics-statistics-data-science/index.html', 'https://www.coursera.org/learn/tsi-math-prep', 'https://www.mathnasium.com/rockville', 'https://www.montgomerycollege.edu/academics/programs/mathematics/index.html', 
# 'https://www.oercommons.org/courseware/lesson/86570/view#summary-tab', 'https://www.oercommons.org/authoring/29013-math-routines/view#summary-tab', 'https://www.coursera.org/specializations/algebra-elementary-to-advanced', 'https://www.oercommons.org/courseware/lesson/65288/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/1321/view#summary-tab', 'https://www.coursera.org/learn/mathematical-thinking', 'https://www.coursera.org/learn/introduction-to-calculus']}, {'skill_interest': 'computer science', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.coursera.org/learn/cs-programming-java', 'https://www.oercommons.org/courses/computers-all-around/view#summary-tab', 'https://www.oercommons.org/courses/free-online-computer-science-books/view#summary-tab', 'https://www.montgomerycollege.edu/academics/departments/engineering-physical-computer-sciences-rockville/index.html', 'https://webcache.googleusercontent.com/search?q=cache:AGU8c4phrTgJ:https://www.computerscience.org/online-degrees/maryland/+&cd=4&hl=en&ct=clnk&gl=us', 'https://www.oercommons.org/courseware/lesson/71695/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/84461/view#summary-tab', 'https://www.coursera.org/professional-certificates/google-it-support', 'https://www.coursera.org/degrees/bachelor-of-science-computer-science-london', 'https://www.montgomerycollege.edu/academics/programs/computer-science-and-technologies/index.html', 'https://www.oercommons.org/courses/computation-and-visualization-in-the-earth-sciences/view#summary-tab', 'https://www.google.com/search?q=computer+science++courses+all+Rockville+MD+USA+&source=hp&ei=K18pYrDfFbuuytMPl6yx4A4&iflsig=AHkkrS4AAAAAYiltO0gmOVJ1FnccG2wP_S-qdIA11at6&ved=0ahUKEwjwoK3DvLr2AhU7l3IEHRdWDOwQ4dUDCAk&uact=5&oq=computer+science++courses+all+Rockville+MD+USA+&gs_lcp=Cgdnd3Mtd2l6EAMyBQghEKABOhEILhCABBCxAxCDARDHARDRAzoICAAQgAQQsQM6DgguEIAEELEDEMcBEKMCOgUIABCABDoOCC4QgAQQsQMQxwEQ0QM6BQguEIAEOhEILhCABBCxAxDHARCjAhDUAjoOCC4QgAQQxwEQrwEQ1AI6CwgAEIAEELEDEIMBOggIABCABBDJAzoFCAAQkgM6CwguEIAEEMcBENEDOgUIABCxAzoLCC4QgAQQxwEQrwE6BggAEBYQHjoICAAQFhAKEB46BQgAEIYDOggIIRAWEB0QHjoFCCEQqwJQAFioKWDOLWgAcAB4AYAB6wGIAYEckgEGNDAuNi4xmAEAoAEB&sclient=gws-wiz#', 'https://www.coursera.org/specializations/introduction-computer-science-programming', 'https://www.coursera.org/specializations/python', 'https://www.computerscience.org/online-degrees/maryland/']}, {'skill_interest': 'machine learning', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.oercommons.org/authoring/27895-artificial-intelligence-and-machine-learning/view#summary-tab', 'https://www.coursera.org/learn/machine-learning', 'https://www.coursera.org/specializations/deep-learning', 'https://www.coursera.org/specializations/machine-learning', 'https://www.onlc.com/training/python/rockville-md.htm', 'https://www.oercommons.org/courses/machine-learning-module-by-hunter-r-johnson/view#summary-tab', 'https://www.indeed.com/q-Machine-Learning-l-Rockville,-MD-jobs.html', 'https://www.oercommons.org/courses/flashcard-machine/view#summary-tab', 'https://asmed.com/information-technology-it/', 'https://professionalprograms.umbc.edu/data-science/post-baccalaureate-certificate-in-professional-studies-data-science/', 'https://www.coursera.org/professional-certificates/ibm-machine-learning', 'https://asmed.com/course/aws-certified-machine-learning-specialty/', 'https://www.oercommons.org/authoring/56645-machine-learning/view#summary-tab', 'https://www.oercommons.org/courses/gitbook-machine-learning-in-action/view#summary-tab', 'https://www.coursera.org/specializations/mathematics-machine-learning']}]



        print("all_urls_to_search: ", all_urls_to_search)
        print("DOM_QUEUE SIZE = ", dom_queue.qsize())
        print("PRE RELEVANCE STUFF finished --- %s seconds ---" % (time.time() - dom_time))
        # ! PRE RELEVANCE STUFF finished --- 34.89859437942505 seconds ---
        
        # relevance_optimization_process = multiprocessing.Process(target=master_results, args=(all_urls_to_search, dom_queue))
        # relevance_optimization_process.start()
        # print("ZEBOOBOO")
        # while dom_queue.qsize() == 0:
        #     pass
        # print("DOM_QUEUE SIZE AFTER FINISHING MASTER_RESULTS = ", dom_queue.qsize())
        # dom_results = dom_queue.get()
        # # dom_results = dill.loads(dom_results)
        # print("GEEBOOBOO")
        # relevance_optimization_process.terminate()
        # print("RELEVANCE OPTIMIZATION PROCESS IS ALIVE: ", relevance_optimization_process.is_alive())
        # print("DOM_RESULTS: ", dom_results)
        # print("DOM_QUEUE SIZE = ", dom_queue.qsize())
        
        print("STARTING RELEVANCE OPTIMIZATION PROCESS")
        dom_results = master_relevance_analyzer(all_urls_to_search, relevant_words_dict)
        print("FINISHED RELEVANCE OPTIMIZATION PROCESS")
        print("RESULTS DICT: ", dom_results)
        
        dom_queue.close()
        
        # return dom_results
        master_queue.put(dom_results)
        
    
    except Exception as e:
        print("Error: " + str(e))
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print("Didn't work :(")

        return False

tags = '{"skills": ["computer science", "cs", "math"], "interests": ["machine learning", "probability"], "type_of_opportunity": ["courses"], "in_person_online": "all", "location": "Rockville MD USA"}'

# ! total runtime without multiprocessing/multithreading: 4 minutes and 25 seconds
# ! TOTAL RUNTIME WITH MULTIPROCESSING/MULTITHREADING: 1 minute and 58 seconds
if __name__ == '__main__':
    multiprocessing.set_start_method('spawn', True)
    start_time = time.time()
    master_queue = multiprocessing.Queue()
    master_process = multiprocessing.Process(target=master_scraper, args=(tags, master_queue))
    master_process.start()
    # master_process.join()
    while True:
        if (master_queue.qsize() != 0):
            master_output = master_queue.get()
            break
    # master_output = master_queue.get()
    master_process.terminate()
    master_queue.close()

    print("MASTER OUTPUT: ", master_output)
    print("Process finished --- %s seconds ---" % (time.time() - start_time))

# if __name__ == '__main__':
#     dom_queue = multiprocessing.Queue()
        
#     tags = tags_to_dict(tags)
    
#     print("tags: ", tags)
    
#     search_queries_process = multiprocessing.Process(target=master_query_maker, args=(tags, dom_queue))
#     # search_queries_process = multiprocessing.Process(target=resource_finder.query_maker, args=(tags, dom_queue))
#     search_queries_process.start()
#     search_queries_process.join()
#     search_queries = dom_queue.get()
#     search_queries_process.terminate()
#     print("SEARCH QUERIES PROCESS IS ALIVE: ", search_queries_process.is_alive())
#     # search_queries = resource_finder.database_lister_query_maker(tags)
#     print("search_queries: ", search_queries)
#     print("DOM_QUEUE SIZE = ", dom_queue.qsize())
#     # print(dom_queue.get())
    
#     # search_queries = [{'search_query': 'computer science ', 'skill_interest': 'computer science', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'location': 'Rockville MD USA'}, 
#     # {'search_query': 'cs ', 'skill_interest': 'cs', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'location': 'Rockville MD USA'}, 
#     # {'search_query': 'math ', 'skill_interest': 'math', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'location': 'Rockville MD USA'}, 
#     # {'search_query': 'machine learning ', 'skill_interest': 'machine learning', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'location': 'Rockville MD USA'}, 
#     # {'search_query': 'probability ', 'skill_interest': 'probability', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'location': 'Rockville MD USA'}]
    
#     web_crawler_process = multiprocessing.Process(target=master_web_crawler, args=(search_queries, dom_queue))
#     # web_crawler_process = multiprocessing.Process(target=web_crawler_multiprocess.master_urls_to_search, args=(search_queries, dom_queue))
#     web_crawler_process.start()
#     print("PREBOOB")
#     web_crawler_process.join()
#     print("BOOB")
#     print("DOM_QUEUE SIZE = ", dom_queue.qsize())
#     all_urls_to_search = dom_queue.get()
#     print("POSTBOOB")
#     web_crawler_process.terminate()
#     print("WEB CRAWLER PROCESS IS ALIVE: ", web_crawler_process.is_alive())
#     print("ENDBOOB")
#     # all_urls_to_search = web_crawler_multiprocess.master_urls_to_search(search_queries, dom_queue)
#     print("all_urls_to_search: ", all_urls_to_search)
    
#     dom_queue.close()

# master_urls_to_search:  [{'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.montgomerycollege.edu/academics/programs/computer-science-and-technologies/index.html', 'https://www.montgomeryschoolsmd.org/curriculum/computer-science/index.aspx', 'https://www.montgomeryschoolsmd.org/departments/onlinelearning/courses/computerscience.aspx', 'https://www.computerscience.org/online-degrees/maryland/', 'https://www.franklin.edu/colleges-near/bachelors-programs/maryland/rockville/computer-science-bachelors-degrees', 'https://www.coursera.org/learn/cs-programming-java', 'https://www.coursera.org/specializations/introduction-computer-science-programming', 'https://www.coursera.org/specializations/python', 'https://www.coursera.org/professional-certificates/google-it-support', 'https://www.coursera.org/specializations/data-structures-algorithms', 'https://www.oercommons.org/courseware/lesson/84461/view#summary-tab', 'https://www.oercommons.org/courses/computers-all-around/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/71695/view#summary-tab', 'https://www.oercommons.org/courses/free-online-computer-science-books/view#summary-tab', 'https://www.oercommons.org/courses/computation-and-visualization-in-the-earth-sciences/view#summary-tab']}, {'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.montgomerycollege.edu/academics/programs/computer-science-and-technologies/index.html', 'https://www.montgomeryschoolsmd.org/curriculum/computer-science/index.aspx', 'https://coursebulletin.montgomeryschoolsmd.org/CourseLists/Index/163', 'https://www.computerscience.org/online-degrees/maryland/', 'https://www.franklin.edu/colleges-near/bachelors-programs/maryland/rockville/computer-science-bachelors-degrees', 'https://www.coursera.org/learn/html-css-javascript-for-web-developers', 'https://www.coursera.org/learn/duke-programming-web', 'https://www.coursera.org/learn/introduction-to-web-development-with-html-css-javacript', 'https://www.coursera.org/learn/introcss', 'https://www.coursera.org/learn/website-coding', 
# 'https://www.oercommons.org/courses/cs-for-oregon-plan-version-1-0/view#summary-tab', 'https://www.oercommons.org/courses/cs-fundamentals-4-5-events-in-bounce/view#summary-tab', 'https://www.oercommons.org/courses/cs-fundamentals-1-2-learn-to-drag-and-drop/view#summary-tab', 'https://www.oercommons.org/courses/cs-fundamentals-2-10-the-right-app/view#summary-tab', 'https://www.oercommons.org/courses/cs-discoveries-2019-2020-web-development-lesson-2-2-websites-for-expression/view#summary-tab']}, {'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': 
# ['https://www.montgomeryschoolsmd.org/curriculum/math/', 'https://www.montgomeryschoolsmd.org/curriculum/math/hs.aspx', 'https://www.mathnasium.com/rockville', 'https://www.montgomerycollege.edu/academics/stem/mathematics-statistics-data-science/index.html', 'https://www.montgomerycollege.edu/academics/programs/mathematics/index.html', 'https://www.coursera.org/specializations/algebra-elementary-to-advanced', 'https://www.coursera.org/learn/mathematical-thinking', 'https://www.coursera.org/specializations/mathematics-machine-learning', 'https://www.coursera.org/learn/introduction-to-calculus', 'https://www.coursera.org/learn/tsi-math-prep', 'https://www.oercommons.org/courseware/lesson/86384/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/65288/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/86570/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/1321/view#summary-tab', 'https://www.oercommons.org/authoring/29013-math-routines/view#summary-tab']}, {'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.montgomerycollege.edu/academics/programs/data-science/index.html', 'https://www.icertglobal.com/course/Artificial-Intelligence-and-Deep-Learning-Certification-Training-Baltimore-MD/Classroom/82/178', 'https://www.glassdoor.com/Job/rockville-machine-learning-jobs-SRCH_IL.0,9_IC1153899_KO10,26.htm', 'https://www.onlc.com/training/python/rockville-md.htm', 'https://www.indeed.com/q-Machine-Learning-l-Rockville,-MD-jobs.html', 'https://www.coursera.org/learn/machine-learning', 'https://www.coursera.org/professional-certificates/ibm-machine-learning', 'https://www.coursera.org/specializations/deep-learning-healthcare', 'https://www.coursera.org/specializations/machine-learning', 'https://www.coursera.org/specializations/deep-learning', 'https://www.oercommons.org/authoring/56645-machine-learning/view#summary-tab', 'https://www.oercommons.org/courses/flashcard-machine/view#summary-tab', 'https://www.oercommons.org/courses/gitbook-machine-learning-in-action/view#summary-tab', 'https://www.oercommons.org/authoring/27895-artificial-intelligence-and-machine-learning/view#summary-tab', 'https://www.oercommons.org/courses/machine-learning-module-by-hunter-r-johnson/view#summary-tab']}, {'type_of_opportunity': 'courses', 'in_person_online': 'all', 'urls_to_search': ['https://www.montgomerycollege.edu/academics/stem/mathematics-statistics-data-science/index.html', 'https://www.montgomeryschoolsmd.org/departments/onlinelearning/courses/ap.aspx', 'https://coursebulletin.montgomeryschoolsmd.org/CourseDetails/Index/MAT2039', 'https://www.wyzant.com/Rockville_MD_statistics_tutors.aspx', 'https://academiccatalog.umd.edu/undergraduate/approved-courses/stat/', 'https://www.coursera.org/learn/introductiontoprobability', 'https://www.coursera.org/learn/probability-theory-foundation-for-data-science', 'https://www.coursera.org/learn/stanford-statistics', 'https://www.coursera.org/specializations/statistical-inference-for-data-science-applications', 'https://www.coursera.org/specializations/probabilistic-graphical-models', 'https://www.oercommons.org/courseware/lesson/53607/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/4104/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/14210/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/4140/view#summary-tab', 'https://www.oercommons.org/courseware/lesson/4158/view#summary-tab']}]




# [{'skill_interest': 'computer science', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'resource_data_dict': {'https://www.coursera.org/specializations/python': ['No prior experience required.', {'courses': 1}], 'https://www.coursera.org/professional-certificates/google-it-support': ['This program includes over 100 hours of instruction and hundreds of practice-based assessments, which will help you simulate real-world IT support scenarios that are critical for success in the workplace.', {'courses': 8}], 'https://www.coursera.org/specializations/introduction-computer-science-programming': ['There are a range of activities included in this specialization that will enable learners to apply and develop their programming skills in a fun and engaging way. Learners will master the fundamentals of computer science by solving mathematical puzzles using interactive techniques, becoming a detective and solving crimes in an interactive sleuth application and apply computer science concepts to solve problems found in daily computer use.', {'courses': 20, 'computer science': 6}], 'https://www.coursera.org/specializations/data-structures-algorithms': ['The specialization contains two real-world projects: Big Networks and Genome Assembly. You will analyze both road networks and social networks and will learn how to compute the shortest route between New York and San Francisco 1000 times faster than the shortest path algorithms you learn in the standard Algorithms 101 course! Afterwards, you will learn how to assemble genomes from millions of short fragments of DNA and how assembly algorithms fuel recent developments in personalized medicine.', {'courses': 24, 'computer science': 4}], 'https://www.coursera.org/learn/cs-programming-java': ['The basis for education in the last millennium was â\x80\x9creading, writing, and arithmetic;â\x80\x9d now it is reading, writing, and computing. Learning to program is an essential part of the education of every student, not just in the sciences and engineering, but in the arts, social sciences, and humanities, as well. Beyond direct applications, it is the first step in understanding the nature of computer scienceâ\x80\x99s undeniable impact on the modern world.  This course covers the first half of our book Computer Science: An Interdisciplinary Approach (the second half is covered in our Coursera course Computer Science: Algorithms, Theory, and Machines). Our intent is to teach programming to those who need or want to learn it, in a scientific context.', {'courses': 38, 'computer science': 10}]}}, {'skill_interest': 'cs', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'resource_data_dict': {'https://www.coursera.org/learn/introduction-to-web-development-with-html-css-javacript': ['Want to take the first steps to become a Cloud Application Developer? This course will lead you through the languages and tools you will need to develop your own Cloud Apps.', {'courses': 7, 'cs': 6}], 'https://www.coursera.org/learn/website-coding': ['In this course you will learn three key website programming and design languages: HTML, CSS and JavaScript. You will create a web page using basic elements to control layout and style.  Additionally, your web page will support interactivity.', {'cs': 11, 'courses': 10}], 'https://www.coursera.org/learn/html-css-javascript-for-web-developers': ['Do you realize that the only functionality of a web application that the user directly interacts with is through the web page? Implement it poorly and, to the user, the server-side becomes irrelevant! Todayâ\x80\x99s user expects a lot out of the web page: it has to load fast, expose 
# the desired service, and be comfortable to view on all devices: from a desktop computers to tablets and mobile phones.', {'courses': 18, 'cs': 6}], 'https://www.coursera.org/learn/duke-programming-web': ['Learn foundational programming concepts (e.g., functions, for loops, conditional statements) and how to solve problems like a programmer. In addition, learn basic web development as you build web pages using HTML, CSS, JavaScript. By the end of the course, will create a web page where others can upload their images and apply image filters that you create.', {'courses': 15, 'cs': 7}], 'https://www.coursera.org/learn/introcss': ['The web today is almost unrecognizable from the early days of white pages with lists of blue links.  Now, sites are designed with complex layouts, unique fonts, and customized color schemes.   This course will show you the basics of Cascading Style Sheets (CSS3).  The emphasis will be on learning how to write CSS rules, how to test code, and how to establish good programming habits.', {'courses': 14, 'cs': 14}]}}, {'skill_interest': 'math', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'resource_data_dict': {'https://www.coursera.org/learn/mathematical-thinking': ['Learn how to think the way mathematicians do â\x80\x93 a powerful cognitive process developed over thousands of years.', {'math': 2, 'courses': 3}], 'https://www.coursera.org/learn/introduction-to-calculus': ['The focus and themes of the Introduction to Calculus course address the most important foundations for applications of mathematics in science, engineering and commerce. The course emphasises the key ideas and historical motivation for calculus, while at the same time striking a balance between theory and application, leading to a mastery of key threshold concepts in foundational mathematics.', {'courses': 18, 'math': 11}], 'https://www.coursera.org/learn/tsi-math-prep': ['The purpose of this course is to review and practice key concepts in preparation for the math portion of the Texas Success Initiative Assessment 2.0 (TSI2).Â\xa0 The TSI2 is series of placement tests for learners enrolling in public universities in Texas.Â\xa0 This MOOC will cover the four main categories of the Mathematics portion:Â\xa0 Quantitative Reasoning, Algebraic Reasoning, Geometric & Spatial 
# Reasoning, and Probabilistic & Statistical Reasoning.Â', {'math': 7, 'courses': 19}], 'https://www.coursera.org/specializations/algebra-elementary-to-advanced': ['Instead of a single large project, there are many smaller applied and algebra problems throughout the modules of the courses. Practice problems with worked solutions are provided throughout the course to prepare students and allow them to be successful. Problems range in difficulty to allow students to be challenged as they apply the knowledge gained from the course.', {'courses': 11, 'math': 6}], 'https://www.coursera.org/specializations/mathematics-machine-learning': ['Through the assignments of this specialisation you will use the skills you have learned to produce mini-projects with Python on interactive notebooks, an easy to learn tool which will help you apply the knowledge to real world problems. For example, using linear algebra in order to calculate the page rank of a small simulated internet, applying multivariate calculus in order to train your own neural network, performing a non-linear least squares regression to fit a model to a data set, and using principal component analysis to determine the features of the MNIST digits data set.', {'courses': 22, 'math': 17}]}}, {'skill_interest': 'machine learning', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'resource_data_dict': {'https://www.coursera.org/specializations/deep-learning': ['By the end youâ\x80\x99ll be able to', {'courses': 1}], 'https://www.coursera.org/specializations/machine-learning': ['Learners will implement and apply predictive, classification, clustering, and information retrieval machine learning algorithms to real datasets throughout each course in the specialization. They will walk away with applied machine learning and Python programming experience.', {'machine learning': 7, 'courses': 13}], 'https://www.coursera.org/specializations/deep-learning-healthcare': ['Learners will be able to apply the theoretical concepts in autograded programming assignments that use training data we provide for use with different types of neural networking algorithms. The technology used is (among others) Jupyter Notebooks / PyTorch.', {'machine learning': 1, 'courses': 11}], 'https://www.coursera.org/professional-certificates/ibm-machine-learning': ['This Professional Certificate has a strong emphasis on developing the skills that help you advance a career in Machine Learning. All the courses include a series of hands-on labs and final projects that help you focus on a specific project that interests you. Throughout this Professional Certificate, you will gain exposure to a series of tools, libraries, cloud services, 
# datasets, algorithms, assignments and projects that will provide you with practical skills with applicability to Machine Learning jobs. These skills include:', {'courses': 25, 'machine learning': 4}], 'https://www.coursera.org/learn/machine-learning': ["Machine learning is the science of getting computers to act without being explicitly programmed. In the past decade, machine learning has given us self-driving cars, practical speech recognition, effective web search, and a vastly improved understanding of the human genome. Machine learning is so pervasive today that you probably use it dozens of times a day without knowing it. Many researchers also think it is the best way to make progress towards human-level AI. In this class, you will learn about the most effective machine learning techniques, and gain practice implementing them and getting them to work for yourself. More importantly, you'll learn about not only the theoretical underpinnings of learning, but also gain the practical know-how needed to quickly and powerfully apply these techniques to new problems. Finally, you'll learn about some of Silicon Valley's best practices in innovation as it pertains to machine learning and AI.", {'machine learning': 14, 'courses': 28}]}}, {'skill_interest': 'probability', 'type_of_opportunity': 'courses', 'in_person_online': 'all', 'resource_data_dict': {'https://www.coursera.org/specializations/probabilistic-graphical-models': ['Through various lectures, quizzes, programming assignments and exams, learners in this specialization will practice and master the fundamentals of probabilistic graphical models. This specialization has three five-week courses for a total of fifteen weeks.', {'courses': 13, 'probability': 
# 1}], 'https://www.coursera.org/learn/introductiontoprobability': ['This course will provide you with a basic, intuitive and practical introduction into Probability Theory. You will be able to learn how to apply Probability Theory in different scenarios and you will earn a "toolbox" of methods to deal with uncertainty in your daily life.', {'courses': 9, 'probability': 5}], 'https://www.coursera.org/specializations/statistical-inference-for-data-science-applications': ['Learners will practice new probability skills. including fundamental statistical analysis of data sets, by completing exercises in Jupyter Notebooks. In addition, learners will test their knowledge by completing benchmark quizzes throughout the courses.', {'courses': 11, 'probability': 4}], 'https://www.coursera.org/learn/probability-theory-foundation-for-data-science': ['Understand the foundations of probability and its relationship to statistics and data science.Â\xa0 Weâ\x80\x99ll learn what it means to calculate a probability, independent and dependent outcomes, and conditional events.Â\xa0 Weâ\x80\x99ll study discrete and continuous random variables and see how this fits with data collection.Â\xa0 Weâ\x80\x99ll end the course with Gaussian (normal) random variables and the Central Limit Theorem and understand its fundamental importance for all of statistics and data science.', {'courses': 18, 'probability': 7}], 'https://www.coursera.org/learn/stanford-statistics': ['Stanford\'s "Introduction to Statistics" teaches you statistical thinking concepts 
# that are essential for learning from data and communicating insights. By the end of the course,Â\xa0you will be able to perform exploratory data analysis, understand key principles of sampling, and select appropriate tests of significance for multiple contexts. You will gain the foundational skills that prepare you to pursue more advanced topics in statistical thinking and machine learning.', {'courses': 11, 'probability': 3}]}}]