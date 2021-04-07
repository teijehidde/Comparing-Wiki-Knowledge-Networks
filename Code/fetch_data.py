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
DATA_FILE = 'networkdata3.json'

# Check if json file "DATA_FILE" is present in folder. 
def WikiNetworkDataMAIN():
    
    os.system('clear')

    try:
        with open('/home/teijehidde/Documents/Git Blog and Coding/Project one (wikipedia SNA)/Code/' + DATA_FILE) as json_file:
            global network_data
            network_data = json.load(json_file)
    except IOError:
        print("Error: Could not find " + DATA_FILE + ". Please check if file is present in directory, or change DATA_FILE value.")
    else: 
        print("The file " + DATA_FILE + " found, succesfully loaded.")
        print("Network data accessed through " + API_ENDPOINT + ".")
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

    print("Current networks in " + DATA_FILE + ":")
    print("  ")
    for item in network_data.keys():
        print(item)

    sleep(1)
    SelectMenu()
    
# Function 2: Get summary of available data on one network. WIP!!  
def CheckStatusNetwork():
    os.system('clear')

    pagetitle = input("Please provide a title included in " + DATA_FILE + ": ")
    
    print('Number of nodes in level:')
    for item in network_data[pagetitle][1]['nodes']: 
        if len(item) > 0: 
            print(len(item))
    # ... make a print list! Only print nodes that are actually present! -- this avoids an error... and is cleaner.  
    # print("1: " + str(len(network_data[pagetitle][1]['nodes']['1'])))
    # print("2: " + str(len(network_data[pagetitle][1]['nodes']['2'])))
    # print("3: " + str(len(network_data[pagetitle][1]['nodes']['3'])))
    print(network_data[pagetitle][1]['nodes'])

    sleep(1)
    SelectMenu()


# Function 3: Build new network - first layer only. WORKS! (but very prelim, no checks, error handling etc what so ever. WIP.)
def BuildNetwork():

    # setup 
    nodes = []
    edges = []
    
    # resquesting wiki page to initiate.
    pagetitle = input("Please provide a title of a Wikipedia page: ")

    # requesting data via wikimedia API.  
    S = requests.Session()
    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": pagetitle,
        "prop": "links",
        "plnamespace": 0, # only load wikipedia main/articles. 
        "pllimit": 100 # can go up to 500. Go for max? 
    }
    response = S.get(url=API_ENDPOINT, params=PARAMS)
    
    # Transforming response to network data format.  
    data_wiki = response.json()
    page = next(iter(data_wiki['query']['pages']))
        
    for x in data_wiki['query']['pages'][page]['links']:
        nodes.append(x['title'])
        edges.append((pagetitle, x['title']))
        
    data_page = page, {'date': 'TODO', 'nodes': {1: nodes, 2: " " , 3:  " ", 4: " " }, 'edges': {1: edges, 2: " ", 3: " ", 4: " "} }
    network_data[pagetitle] = data_page
    
    # Dumping data into file and saving. 
    with open('/home/teijehidde/Documents/Git Blog and Coding/Project one (wikipedia SNA)/Code/' + DATA_FILE, 'w') as outfile:
        json.dump(network_data, outfile)
        print("Data succesfully loaded and saved. Returning to main menu.")
        sleep(1)

# Function 4: Append one level (or remainder of one level) to existing network. Includes a throttle.  TODO
def AppendNetwork():
    os.system('clear')
    print("AppendNetwork is not implemented yet. Returning to main menu.")
    sleep(1)
    SelectMenu()

# Function 5: Checks for changes since last action on network and updates. TODO
def UpdateNetwork():
    os.system('clear')
    print("UpdateNetwork is not implemented yet. Returning to main menu.")
    sleep(1)
    SelectMenu()

# Function 6: Creates a revision history of complete network. Enables changing network over time. Includes a throttle. TODO
def UpdateRevisionsNetwork():
    os.system('clear')
    print("UpdateRevisionsNetwork is not implemented yet. Returning to main menu.")
    sleep(1)
    SelectMenu()
    
# NB: RUNTIME
WikiNetworkDataMAIN()

# END 