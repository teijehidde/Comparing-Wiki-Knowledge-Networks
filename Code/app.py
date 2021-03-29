#!/usr/bin/python3

"""
    app.py

    MediaWiki API Demos

    User contributions feed app: Demp app that uses `list=usercontribs` module
    to fetch the top 50 edits made by a user

    MIT license
"""

from flask import Flask, render_template, request
import networkx as nx
import requests
import json

WIKI_URL = "https://en.wikipedia.org"
API_ENDPOINT = WIKI_URL + "/w/api.php"

"""
# App config.
DEBUG = True
APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'enter_your_secret_key'


@APP.route("/", methods=['GET'])
def index():
    pagename = request.args.get('pagename')

    if pagename is not None:
        data = get_user_contribs(pagename)
    else:
        data = None

    return render_template('page_links.html', data=data, \
        pagename=pagename, wikiurl=WIKI_URL)
"""

def get_ego_network(pagetitle):
    """ Fetch links via MediaWiki API's links module """
    nodes = set()
    edges = []
    params = {
        "action": "query",
        "format": "json",
        "titles": pagetitle,
        "prop": "links"
    }

    response = requests.get(url=API_ENDPOINT, params=params)
    
    data = response.json()
    page = next(iter(data['query']['pages']))
    
    for x in data['query']['pages'][page]['links']: 
        nodes.add(x['title'])
        edges.append((pagetitle, x['title']))
    
    return{'ego': [pagetitle], 'nodes': nodes, 'edges': edges}

# NB: Have to create links of links - to a certain depth... 

def get_edges_of_edges(egonetwork):

    for x in egonetwork['nodes']: 
        
        data = get_ego_network(x)
        egonetwork['ego'].append(x) 
        # NB: concatenating two sets... 
        egonetwork['nodes'] =  egonetwork['nodes'] | data['nodes']
        # NB: and concatenating two lists... 
        egonetwork['edges'].append(data['edges'])
        
    
    return(egonetwork)


""" DOWNLOAD DATA ONE LEVEL DEEP """ 

data = get_ego_network("Bergen")
# data = get_edges_of_edges(data)

json.dump(data, f, ensure_ascii=False, indent=4)



# draw the graph using PyGraphviz, analysis can be done through networkx package.  



# print(result)


"""
   for employee,hours in work_hours:
        if hours > current_max:
            current_max = hours
            employee_of_month = employee
        else:
            pass
"""

# def create_graph_list(pagelinks): 
#     """construct list of edges that can be used in networkx""" 





# print(type(result['prop']))

# print(data['links'])
"""
if __name__ == '__main__':
    APP.run()
"""