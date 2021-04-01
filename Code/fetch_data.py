#!/usr/bin/python3

"""
    MediaWiki API Demos

    This command line tool fetches data from Wikimedia API and saves json files that are directly usable in drawing networks using PyGraphviz and networkx packages.
    Actual drawing is done in app.py (that draws purely on json file) 

    MIT license
"""

#Setup 
import requests
import json
import os
from time import sleep
from datetime import date

WIKI_URL = "https://en.wikipedia.org"
API_ENDPOINT = WIKI_URL + "/w/api.php"
DATA_FILE = 'networkdata.json'

# Check if json file "DATA_FILE" is present in folder. 
def WikiNetworkDataMAIN():
    
    os.system('clear')

    try:
        network_data = open('/home/teijehidde/Documents/Git Blog and Coding/Project one (wikipedia SNA)/Code/' + DATA_FILE)
    except IOError:
        print("Error: Could not find " + DATA_FILE + ". Please check if file is present in directory, or change DATA_FILE value.")
    else: 
        print("The file " + DATA_FILE + " found, succesfully loaded.")
        print("Networks are loaded through " + API_ENDPOINT + ".")
        SelectMenu()

# Select function to be run on json file.  
def SelectMenu():

    print("   ")
    print("---")
    print("   ")
    print("This is a command line tool to build, append and update wikinetworks. Please select one of the following options:")
    print("   ")
    print("1 = List existing networks in " + DATA_FILE + ".")
    print("2 = Check status of an existing network.")
    print("3 = Build a new network.")
    print("4 = Append existing network.")
    print("5 = Update existing network.")
    print("6 = Update revision history of existing network.")
    print("9 = Quit program.")

    choice_int = int(input("Please type a number between 1 and 9 to select one of the above options:" ))
    
    if choice_int == 1: ListNetworks()
    if choice_int == 2: CheckStatusNetwork()
    if choice_int == 3: BuildNetwork()
    if choice_int == 4: AppendNetwork()
    if choice_int == 5: UpdateNetwork()
    if choice_int == 6: UpdateRevisionsNetwork()
    if choice_int == 9: None 
    else: 
        os.system('clear')
        print("Please type a number.")
        print("   ")
        SelectMenu()

# Function 1: List networks in Json file. 
def ListNetworks():
    os.system('clear')
    print("ListNetworks is not implemented yet. Returning to main menu.")
    sleep(1)
    SelectMenu()
    

# Function 2: Get summary of available data on one network. 
def CheckStatusNetwork():
    os.system('clear')
    print("CheckStatusNetwork is not implemented yet. Returning to main menu.")
    sleep(1)
    SelectMenu()


# Function 3: Build new network - first layer only. 
def BuildNetwork():

    network_data = json.load('/home/teijehidde/Documents/Git Blog and Coding/Project one (wikipedia SNA)/Code/' + DATA_FILE)

    pagetitle = input("Please provide a title of a Wikipedia page.")

    nodes = set()
    edges = []
    params = {
        "action": "query",
        "format": "json",
        "titles": pagetitle,
        "prop": "links"
    }

    response = requests.get(url=API_ENDPOINT, params=params)
    
    data_wiki = response.json()
    page = next(iter(data_wiki['query']['pages']))
    
    for x in data_wiki['query']['pages'][page]['links']: 
        nodes.add(x['title'])
        edges.append((pagetitle, x['title']))
    
    data_page = {'pages': [{'pageID': page, 'date': 'TODO', 'nodes': {'level0': pagetitle, 'level1': nodes}, 'edges': {'level1': edges}} ] }
    
    network_data['pages'].append(data_page)

    with open(DATA_FILE, 'x') as outfile:
        json.dump(network_data, outfile)

   # json_object = json.dumps(network_data, indent=2, sort_keys=True)

# Append one level (or remainder of one level) to existing network. Includes a throttle.  TODO
def AppendNetwork():
    os.system('clear')
    print("AppendNetwork is not implemented yet. Returning to main menu.")
    sleep(1)
    SelectMenu()

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

# Checks for changes since last actio non network and updates. TODO
def UpdateNetwork():
    os.system('clear')
    print("UpdateNetwork is not implemented yet. Returning to main menu.")
    sleep(1)
    SelectMenu()

# Creates a revision history of complete network. Enables changing network over time. Includes a throttle. TODO
def UpdateRevisionsNetwork():
    os.system('clear')
    print("UpdateRevisionsNetwork is not implemented yet. Returning to main menu.")
    sleep(1)
    SelectMenu()
    
# NB: RUNTIME 

WikiNetworkDataMAIN()