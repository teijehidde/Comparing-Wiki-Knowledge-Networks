# Setup 
from flask import Flask, render_template, request
import os
import pygraphviz as pgv
from pyvis.network import Network
import networkx as nx
import requests
import json

PATH = "/home/teijehidde/Documents/Git Blog and Coding/Project one (wikipedia SNA)/Code/"
DATA_FILE = "networkdata3.json"
WIKI_URL = "https://en.wikipedia.org"
API_ENDPOINT = WIKI_URL + "/w/api.php"
LIMIT_LINKS_PER_NODE = 500
LIMIT_API_REQUESTS = 100

# Function A: load data node_title from data file. 
def loadNode(node_title):

    try:
        with open(PATH + DATA_FILE) as json_file:
            global network_data 
            network_data = json.load(json_file)
            return network_data[node_title]
    except IOError:
        print("Error: Could not find " + DATA_FILE + ". Please check if file is present in directory, or change DATA_FILE value.")
    else: 
        print("The file " + DATA_FILE + " found, succesfully loaded.")

# Function B: download data node_title from Wikimedia API
def downloadNode(node_title):

    # setup 
    links_wiki = []

    # requesting data via wikimedia API.  
    S = requests.Session()
    PARAMS = {
        "action": "query",
        "format": "json",
        "titles": node_title,
        "prop": "links",
        # "plcontinue": ,
        "plnamespace": 0, # only load wikipedia main/articles. 
        "pllimit": 'max' # can go up to 500. Go for max? 
    }
    response = S.get(url=API_ENDPOINT, params=PARAMS)

    # Transforming response to network data format + error handling.  
    data_wiki = response.json()
    node = next(iter(data_wiki['query']['pages']))
    
    try: 
        for x in data_wiki['query']['pages'][node]['links']:
            links_wiki.append(x['title'])
                
        node_data = {'status': 'alive', 'node_ID': node, 'links': links_wiki, 'timestamp': 'TODO', 'ego': 0, 'revisions': 'TODO'}
        network_data[node_title] = node_data
        return network_data[node_title]
        
    except:
        node_data = {'status': 'dead', 'timestamp': 'TODO'}
        network_data[node_title] = node_data
        return network_data[node_title]
    
    finally:   
        with open(PATH + DATA_FILE, 'w') as outfile:
            json.dump(network_data, outfile)
            print("Data succesfully saved. Wikipage name: " + node_title + ". Status: " + network_data[node_title]['status'] + ".")

# initiate class Node. 
class WikiNode:
    def __init__(self,node_title):
        self.title = node_title
        self.status = 'empty'
        self.links = []

        try:
            self.status = loadNode(node_title)['status']
            if self.status == 'alive':
                self.links = loadNode(node_title)['links']
        except: 
            self.status = 'empty'


    def downloadData(self):

        if self.status == 'dead':
            print("This title does not seem to exist on " + WIKI_URL + ".")
        else:
            downloadNode(self.title)
            self.__init__(self.title)

class WikiNetwork(WikiNode):
    
    def __init__(self,node_title):
        WikiNode.__init__(self, node_title)
        self.network_nodes = {}
        self.network_nodes_count = {}
        
        if self.status == 'alive':
            self.links.append(self.title)

            for link in self.links:
                self.network_nodes[link] = WikiNode(link)
                self.network_nodes_count[link] = 1

                if self.network_nodes[link].status == 'alive':
                    for link2 in self.network_nodes[link].links:
                        if link2 in self.links:
                            self.network_nodes_count[link] = self.network_nodes_count[link] + 1


    def statusNetwork(self): 
        total = len(self.network_nodes)
        alive = 0
        dead = 0
        empty = 0
        
        for network_node in self.network_nodes:
            if self.network_nodes[network_node].status == 'alive': 
                alive = alive + 1
            if self.network_nodes[network_node].status == 'dead': 
                dead = dead + 1
            if self.network_nodes[network_node].status == 'empty': 
                empty = empty + 1        

        print("Total number of nodes is " + str(total) + ".")
        print("The number of alive nodes is " + str(alive) + ".")
        print("The number of dead nodes is " + str(dead) + ".")
        print("The number of empty nodes is " + str(empty) + ".")
        print("(sum is " + str(alive + dead + empty) + ").")


    def downloadNetwork(self,callLimit): 
        if self.status != 'alive': 
            self.downloadData() 

        call = 0
        for link in self.network_nodes:

            if self.network_nodes[link].status == 'empty':
                self.network_nodes[link].downloadData()
                call = call + 1
                if call >= callLimit: break 


    def getNodesEdges(self,threshold):
        selected_nodes = [k for k,v in self.network_nodes_count.items() if float(v) >= threshold]

        nodes_network = []
        edges_network = []

        for node in selected_nodes:
            node_tuple = (node, {"name": node})
            nodes_network.append(node_tuple)
        
        for node in selected_nodes:
            x = WikiNode(node)
            for link in x.links:
                    if link in selected_nodes:
                        edge_tuple = (node, link)
                        edges_network.append(edge_tuple)

        return (nodes_network,edges_network)

def drawGraph(WikiNodesEdges):
    
    Graph = nx.Graph()

    Graph.add_nodes_from(WikiNodesEdges[0])
    Graph.add_edges_from(WikiNodesEdges[1])

    netdraw = Network('2000px', '2000px')
    netdraw.from_nx(Graph)
    netdraw.barnes_hut()

    netdraw.show("wikinetworkgraph.html")