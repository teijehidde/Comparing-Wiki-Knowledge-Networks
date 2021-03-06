"""
This is a function that calls the wikipedia API to download links and language links form selected pages. 
See app.py and fetch_data.py for more information. 
"""

#-------- loading packages --------#
import requests
import pandas as pd


#-------- function to call wikimedia API --------#
def downloadWikiNetwork(node_title, lang = "en"):
    api_endpoint = "https://" + lang + ".wikipedia.org/w/api.php" # fr.wikipedia.org; https://en.wikipedia.org
    wiki_data = []
    print("Starting download of network " + node_title + " in language " + lang + ".")
    
    # step 1a: download data on the node_title wikipage. First call
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
    
    # step 1b: Subsequent calls remaining data chunks
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

    # step 2a: download data on the links of node_title wikipage.
    # Generator to get data of pages linked to selected node. The link to the english version of the page is downloaded as well
    S = requests.Session()
    params_network_title = {
        "action": "query",
        "generator": "links",
        "titles": node_title,
        "gplnamespace": 0, 
        "gpllimit": 500, 
        "prop": "info|links|langlinks", 
        "plnamespace": 0,
        "pllimit": 500,
        "lllang": "en", 
        "lllimit":500,
        "format": "json"
    }
    response = S.get(url=api_endpoint, params=params_network_title)
    wiki_data.append(response.json())

    # step 2b: Subsequent calls remaining data chunks of each page. 
    while 'continue' in wiki_data[-1].keys():
        params_cont = params_network_title
        if 'plcontinue' in wiki_data[-1]['continue']:
            params_cont["plcontinue"] = wiki_data[-1]['continue']['plcontinue'] 
            print('plcontinue: ' + params_cont["plcontinue"])

        elif 'llcontinue' in wiki_data[-1]['continue']:
            params_cont["llcontinue"] = wiki_data[-1]['continue']['llcontinue'] 
            print('llcontinue: ' + params_cont["llcontinue"])

        elif 'gplcontinue' in wiki_data[-1]['continue']: 
            params_cont["gplcontinue"] = wiki_data[-1]['continue']['gplcontinue']
            print('gplcontinue: ' + params_cont["gplcontinue"])

        response = S.get(url=api_endpoint, params = params_cont)
        wiki_data.append(response.json())

    # step 3: creating a list of all nodes present in downloaded data. 
    all_nodes = []

    for item in wiki_data:
        all_nodes = all_nodes + list(item['query']['pages'].keys())
    all_nodes = list(set(all_nodes))
    all_nodes = [int(i) for i in all_nodes if int(i) > 0]
    all_nodes = [str(i) for i in all_nodes]

    # step 4: Using list of all nodes to go through data, building a panda dataframe from scratch. 
    network_data_df = pd.DataFrame(
        columns = ['title', 'lang', 'pageid', 'uniqueid', 'lastrevid', 'links', 'langlinks', 'ego'], # complete list: ['ns', 'title', 'missing', 'contentmodel', 'pagelanguage', 'pagelanguagehtmlcode', 'pageid', 'lastrevid', 'length', 'links', 'langlinks']
        index = all_nodes)

    for node in all_nodes:
        network_data_df.at[node,'links'] = []
        network_data_df.at[node,'langlinks'] = []
        for item in wiki_data:
            if node in item['query']['pages'].keys(): # possibility:  df_new_wiki_data.update(item) #, errors = 'raise') 
                network_data_df.at[node, 'title'] = item['query']['pages'][node]['title']
                network_data_df.at[node,'lang'] = item['query']['pages'][node]['pagelanguage']
                network_data_df.at[node,'pageid'] = item['query']['pages'][node]['pageid']
                network_data_df.at[node,'uniqueid'] = network_data_df.at[node,'lang'] + str(network_data_df.at[node,'pageid'])
                network_data_df.at[node,'lastrevid'] = item['query']['pages'][node]['lastrevid']
                if network_data_df.at[node,'title'] == node_title.replace('_', ' '): network_data_df.at[node,'ego'] = True

                if 'links' in item['query']['pages'][node].keys():
                    for link in item['query']['pages'][node]['links']:
                        network_data_df.at[node,'links'].append(link['title'])

                if 'langlinks' in item['query']['pages'][node].keys(): 
                    network_data_df.at[node,'langlinks'] = network_data_df.at[node,'langlinks'] + item['query']['pages'][node]['langlinks']

    # step 5: returns panda with all data from network. 
    return network_data_df

#-------- End --------#