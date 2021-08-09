# Setup packages and file paths 
import os
from itertools import chain
from collections import Counter
import collections 
import requests
import json
import pandas as pd
import numpy as np 
import zipfile
from io import BytesIO

path = "/home/teijehidde/Documents/Git Blog and Coding/data_dump/"
data_file = "data_new2.json"

# Check if json file "DATA_FILE" is present in folder. 
def WikiNetworkDataMAIN():
    os.system('clear')

    try:
        pd.read_json((path + data_file), orient='split')
        print("The file " + data_file + " found.")
        SelectMenu()
    except IOError:
        print("Error: Could not find " + data_file + ". Please check if file is present in directory, or change data_file value.")

# Function A: the actual function that calls the wikipedia API and outputs a panda table with curated date. 
def downloadWikiNetwork(node_title, lang = "en"):

    api_endpoint = "https://" + lang + ".wikipedia.org/w/api.php" # fr.wikipedia.org; https://en.wikipedia.org
    wiki_data = []
    print("Starting download of network " + node_title + " in language " + lang + ".")
    
    # 1: download data on the node_title wikipage.
    S = requests.Session()
    params_node_title = {
        "action": "query",
        "titles": node_title,
        "prop": "info|links|langlinks", 
        "plnamespace": 0, 
        "pllimit": 500,
        "lllimit": 500, 
        "format": "json"
    }
    response = S.get(url=api_endpoint, params=params_node_title)
    wiki_data.append(response.json())
    
    while 'continue' in wiki_data[-1].keys():
        params_cont = params_node_title
        if 'plcontinue' in wiki_data[-1]['continue']:
            params_cont["plcontinue"] = wiki_data[-1]['continue']['plcontinue'] 
            print('plcontinue: ' + params_cont["plcontinue"])

        elif 'llcontinue' in wiki_data[-1]['continue']:
            params_cont["llcontinue"] = wiki_data[-1]['continue']['llcontinue'] 
            print('llcontinue: ' + params_cont["llcontinue"])

        response = S.get(url=api_endpoint, params=params_cont)
        wiki_data.append(response.json())

    # 2: download data on the links of node_title wikipage.
    S = requests.Session()
    params_network_title = {
        "action": "query",
        "generator": "links",
        "titles": node_title,
        "gplnamespace": 0, 
        "gpllimit": 500, 
        "plnamespace": 0,
        "pllimit": 500, 
        "prop": "info|links", 
        "format": "json"
    }
    response = S.get(url=api_endpoint, params=params_network_title)
    wiki_data.append(response.json())

    while 'continue' in wiki_data[-1].keys():
        params_cont = params_network_title
        if 'plcontinue' in wiki_data[-1]['continue']:
            params_cont["plcontinue"] = wiki_data[-1]['continue']['plcontinue'] 
            print('plcontinue: ' + params_cont["plcontinue"])

        elif 'gplcontinue' in wiki_data[-1]['continue']: 
            params_cont["gplcontinue"] = wiki_data[-1]['continue']['gplcontinue']
            print('gplcontinue: ' + params_cont["gplcontinue"])

        response = S.get(url=api_endpoint, params = params_cont)
        wiki_data.append(response.json())

    # 3: creating list of available nodes in wiki_data. 
    all_nodes = []

    for item in wiki_data:
        all_nodes = all_nodes + list(item['query']['pages'].keys())
    all_nodes = list(set(all_nodes))
    all_nodes = [int(i) for i in all_nodes if int(i) > 0]
    all_nodes = [str(i) for i in all_nodes]
    
    network_data_df = pd.DataFrame(
        columns = ['title', 'lang', 'pageid', 'uniqueid', 'lastrevid', 'links', 'langlinks'], # complete list: ['ns', 'title', 'missing', 'contentmodel', 'pagelanguage', 'pagelanguagehtmlcode', 'pageid', 'lastrevid', 'length', 'links', 'langlinks']
        index = all_nodes)

    # 4: Using all_nodes to go through list of raw data from API. 
    for node in all_nodes:
                
        for item in wiki_data:
            if node in item['query']['pages'].keys(): # possibility:  df_new_wiki_data.update(item) #, errors = 'raise') 
                network_data_df.at[node, 'title'] = item['query']['pages'][node]['title']
                network_data_df.at[node,'lang'] = item['query']['pages'][node]['pagelanguage']
                network_data_df.at[node,'pageid'] = item['query']['pages'][node]['pageid']
                network_data_df.at[node,'uniqueid'] = network_data_df.at[node,'lang'] + str(network_data_df.at[node,'pageid'])
                network_data_df.at[node,'lastrevid'] = item['query']['pages'][node]['lastrevid']

                if 'links' in item['query']['pages'][node].keys():
                    links_temp = []
                    for link in item['query']['pages'][node]['links']:
                        links_temp.append(link['title'])
                    network_data_df.at[node,'links'] = links_temp

                if 'langlinks' in item['query']['pages'][node].keys():
                    network_data_df.at[node,'langlinks'] = item['query']['pages'][node]['langlinks']

    # returns panda with all data from network. 
    return network_data_df

# Function B: Downloading multiple languages and saving them to json/panda file. 
def downloadMultiLangWikiNetwork(node_title, original_lang = 'en', additional_langs = ["ar", "de", "fr", "nl"]): # or: 'available_langs'
    network_data_df = downloadWikiNetwork(node_title=node_title, lang=original_lang)
    available_langs = network_data_df.loc[network_data_df['title'] == node_title].loc[network_data_df['lang'] == original_lang]['langlinks'].values.tolist()[0]

    if additional_langs == []:
        print('The wikipedia page is available in the following languages:')         
        print(available_langs)
    
    else:
        for item in available_langs: 
            if item['lang'] in additional_langs:
                network_data_df_additional = downloadWikiNetwork(node_title = item['*'], lang = item['lang'])
                network_data_df = pd.concat([network_data_df, network_data_df_additional], ignore_index=True, sort=False)
                
    network_data_saved = pd.read_json((path + data_file), orient='split')
    network_data_df = pd.concat([network_data_df, network_data_saved], ignore_index=True, sort=False)
    network_data_df = network_data_df.loc[network_data_df.astype(str).drop_duplicates(keep = 'last').index].reset_index(drop=True)
    network_data_df.to_json((path + data_file), orient='split')
    print("Download of network and additional languages finished.") 


# Function 0: Select function to be run on json file.  
def SelectMenu():

    print("   ")
    print("---")
    print("   ")
    print("This is a command line tool to build, append and update " + data_file + ". Please select one of the following options:")
    print("   ")
    print("1 = Overview available networks in " + data_file + ".") # should output panda datframe: index = topics; columns = languages available; cells = number of nodes. 
    print("2 = Download and save new network.")

    choice_int = int(input("Please type a number between 1 and 2 to select one of the above options:" ))
    
    if choice_int == 1: overviewNetworks()
    if choice_int == 2: downloadNetworks()
    else: 
        # os.system('clear')
        print("Please type a number.")
        print("   ")
        SelectMenu()

# Function 1: provide overview of available networks. 
def overviewNetworks():
    network_data_df = pd.read_json((path + data_file), orient='split')
    available_wiki_networks = network_data_df.loc[network_data_df['langlinks'].notnull()]
    available_wiki_networks['number_of_links'] = available_wiki_networks['links'].apply(lambda x: len(x)) # here it throws an error. FIX. 

    print(available_wiki_networks[['title', 'lang', 'pageid', 'number_of_links']])

# Function 2: request name of network + languages and download networks in these languages .  
def downloadNetworks():
    print('to be implemnted')

# NB: RUNTIME -- this should be written differently.
if __name__ == '__main__':
    WikiNetworkDataMAIN()

# END 