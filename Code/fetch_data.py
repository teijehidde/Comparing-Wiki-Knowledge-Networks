#!/usr/bin/python3

"""
    MediaWiki API Demos

    This application fetches data from Wikimedia API and saves json files that are directly usable in drawing networks using PyGraphviz and networkx packages.
    Actual drawing is done in app.py (that draws purely on json file) 

    MIT license
"""

import requests
import json
from datetime import date

WIKI_URL = "https://en.wikipedia.org"
API_ENDPOINT = WIKI_URL + "/w/api.php"

def get_network_level_zero(pagetitle):
    """ Fetch links via MediaWiki API's links module """
    nodes = []
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
        nodes.append(x['title'])
        edges.append((pagetitle, x['title']))
    
    return{'pages': [{'pageID': page, 'date': 'TODO', 'nodes': {'level0': pagetitle, 'level1': nodes}, 'edges': {'level1': edges}} ] }


data1 = get_network_level_zero("Duiven")
data['pages'].append(data2)
test = json.dumps(data, indent=2, sort_keys=True)

# NB: Have to create links of links - to a certain depth... 
"""
def get_network_level_one(networkzero):

    for x in networkzero['nodes']: 
        
        data = get_ego_network(x)
        egonetwork['ego'].append(x) 
        # NB: concatenating two sets... 
        egonetwork['nodes'] =  egonetwork['nodes'] | data['nodes']
        # NB: and concatenating two lists... 
        egonetwork['edges'].append(data['edges'])
        
    
    return(egonetwork)
"""

""" DOWNLOAD DATA ONE LEVEL DEEP """ 

data = get_network_level_zero("Bergen")


# data = get_edges_of_edges(data)

# json.dump(data, f, ensure_ascii=False, indent=4)



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