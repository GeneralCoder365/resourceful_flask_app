import sys
import time
import logging

import multiprocessing



from flask import Flask, render_template
from flask import request
from flask_restful import Resource, Api, reqparse

# import web_scraper
import web_scraper_multiprocess_copy_5 as ws_m_v5


app = Flask(__name__)
api = Api(app)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

# import json
@app.route('/search', methods=["GET"])
# @profile # marks function to be tracked for memory usage
def search():
    import os
    print("CURRENT WORKING DIRECTORY: ", os.path.abspath(os.getcwd()))
    # tags = request.args.get('tags')
    # print("tags: ", tags)
    # tags = json.dumps(dict(json.loads(tags)))
    # data = web_scraper.master_output(tags)
    # print(data)
    # return {'data':data}, 200
    
    skills = str(request.args.get('skills')).strip().lower().split(',')
    print("SKILLS: ", skills)
    interests = str(request.args.get('interests')).strip().lower().split(',')
    print("INTERESTS: ", interests)
    type_of_opportunity = str(request.args.get('type_of_opportunity')).strip().lower().split(',')
    print("TYPE_OF_OPPORTUNITY: ", type_of_opportunity)
    in_person_online = str(request.args.get('in_person_online')).strip().lower()
    print("IN_PERSON_ONLINE: ", in_person_online)
    try:
        location = str(request.args.get('location')).strip().lower()
        if (location == "none"):
            location = None
        print("LOCATION: ", location)
    except Exception as e:
        if (in_person_online == 'online'):
            location = None
        else:
            location = ""
    
    tags = '{"skills": ['
    if (len(skills) == 1):
        tags += skills[0] + '"], "interests": ["'
    else:
        for skill in skills[:-1]:
            tags += '"' + skill + '", '
        tags += '"' + skills[-1] + '"], "interests": ["'
    
    if (len(interests) == 1):
        tags += interests[0] + '"], "type_of_opportunity": ["'
    else:
        for interest in interests[:-1]:
            tags += '"' + interest + '", '
        tags += '"' + interests[-1] + '"], "type_of_opportunity": ["'
    
    tags += type_of_opportunity[0] + '"], "in_person_online": "' + in_person_online + '"'
    
    if (location != None):
        tags += ', "location": ' + location + '"}'
    else:
        tags += '}'

    tags = str(tags).strip().lower()
    print(tags)
    
    master_output = {}
    # if __name__ == '__main__':
    start_time = time.time()
    print("TIT 1")
    multiprocessing.set_start_method('spawn', True)
    master_queue = multiprocessing.Queue()
    master_process = multiprocessing.Process(target=ws_m_v5.master_scraper, args=(tags, master_queue))
    master_process.start()
    # master_process.join()
    while master_queue.qsize() == 0:
        pass
    print("TIT 2")
    master_output = master_queue.get()
    # pickled_master_output = master_queue.get()
    # master_output = dill.loads(pickled_master_output)
    master_process.terminate()
    master_queue.close()
    print("TIT 3")
    
    # master_output = master_scraper(tags)
    print("MASTER OUTPUT: ", master_output)
    # print(len(master_output))
    print("Process finished --- %s seconds ---" % (time.time() - start_time))


    # data = {"tags": tags}
    data = master_output
    
    return data, 200

app.debug = True

if __name__ == '__main__':
    app.run()