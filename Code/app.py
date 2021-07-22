# Setup packages (might be able to remove a few of these.)
# packages needed for downloading, saving and loading data 
import os
from collections import Counter
import collections 
import requests
import json

# packages for creation classes and network analysis 
import networkx as nx
from itertools import chain
import communities
from networkx.algorithms import approximation
from networkx.algorithms import community
from networkx.algorithms.community import k_clique_communities
from networkx.algorithms.community import greedy_modularity_communities
from pyvis.network import Network

# Dash packages for presentation analysis  
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd

# setup layout and paths
path = "/home/teijehidde/Documents/Git Blog and Coding/Comparing Wikipedia Knowledge Networks (Network Analysis Page links)/Code/"
data_file = "DATA_THD.json" 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

global network_data # TEMP - NOT SAFE!! ## 

with open(path + data_file) as json_file:
    network_data = json.load(json_file)

# Setting functions
# function: provide titles of networks that are saved in the JSON file. Also provides the language they were saved in. 
def getDownloadedNetworks():

    with open(path + data_file) as json_file:
        network_data = json.load(json_file)

    # create set of ego network names.  
    downloaded_networks = [(v['ego']) for (k,v) in network_data.items()]
    downloaded_networks = set(list(chain(*downloaded_networks)))
    downloaded_networks = [v for v in network_data.values() if v['title'] in downloaded_networks]

    # print names of ego networks and language that they have been downloaded in. 
    items = {}  
    for network in downloaded_networks: 
        items[network['title'] + ' (' + network['language'] + ')'] = {'lang':  network['language'], '*': network['title']}    
    return(items)

# Initiate class Node. 
class WikiNode:
    def __init__(self, node_title, lang):
        
       # with open(path + data_file) as json_file:
       #     network_data = json.load(json_file)

        # Select node in JSON file (by title and language). 
        node_data = [v for (k,v) in network_data.items() if v['title'] == node_title if v['language'] == lang][0]
        
        # Extract data and place in instance of Wikinode class. 
        self.node_title = node_data['title']
        self.node_ID = node_data['node_ID']
        self.node_links = node_data['links']
        self.node_lang = node_data['language']

# Initiate class WikiNetwork
class WikiNetwork(WikiNode):
   
    def __init__(self,node_title, lang):
        
        # initiate the central node of the network as class WikiNode, add additional attributes for class WikiNetwork 
        WikiNode.__init__(self, node_title, lang)
        self.network_nodes = {}
        self.network_links = []
        self.network_edges = [] 
        self.network_status = []
        
        # Go through node_links of the central node (node_title) to build network.
        try: 
            for link in self.node_links:
                Node2 = WikiNode(link, lang)
                purged_links = [x for x in Node2.node_links if x in self.node_links]
                purged_edges = []
                for purged_link in purged_links:
                    purged_edges.append((link,purged_link))  
                self.network_nodes[Node2.node_ID] = Node2
                self.network_links = self.network_links + purged_links
                self.network_edges = self.network_edges + purged_edges
        except: 
            pass
        self.nodes_count = Counter(self.network_nodes)              
                
    def getNodes(self,threshold=0):
        selected_nodes = [k for k,v in self.nodes_count.items() if float(v) >= threshold]
        nodes_network = []

        for node in selected_nodes:
            node_tuple = (node, {"name": node})
            nodes_network.append(node_tuple)

        return nodes_network

    def getEdges(self,threshold=0):
        selected_nodes = [k for k,v in self.nodes_count.items() if float(v) >= threshold]
        edges_network = [(a,b) for a,b in self.network_edges if a in selected_nodes and b in selected_nodes]

        return edges_network

    def getStatsNetwork(self): 
        # TODO: return a dictionary with stats on network: 
        # - triangles
        # - degree_centrality 
        # - ... 

        print('WIP')

    def getStatsNodes(self, nodes):
        # TODO: return an numpy array with stats per node: 
        # - triangles
        # - degree_centrality 
        # - ... 
        # if nodes == None: 
          #  node = self.node_links

        print('WIP')
    
    def getNetworkCommunities(self,threshold=0):
        # TODO: return an numpy array with stats per community. Add in an overall library.  
        G = nx.Graph()
        G.add_edges_from(self.getEdges(threshold))
        
        return greedy_modularity_communities(G)
    
    def drawGraph(self,threshold=0,name='no_name'):
        G = nx.Graph()
        G.add_edges_from(self.getEdges(threshold))

        netdraw = Network('2000px', '2000px')
        netdraw.from_nx(G)
        netdraw.barnes_hut()

        title = name + ".html"
        netdraw.show(title) 

all_networks = getDownloadedNetworks()

app.layout = html.Div([
    dcc.Store(id='memory-output'), 
    html.Div([
        dcc.Dropdown(
        id='selected-network',
        options=
            [{'label': k, 'value': k} for k in all_networks.keys()]
        ),
    ], style={'width': '25%', 'float': 'left', 'padding': 10, 'display': 'inline-block'}), 
    html.Div([
        dcc.Dropdown(
        id='language-options',
            multi=True
        ),
    ], style={'width': '60%', 'float': 'middle', 'padding': 10, 'display': 'inline-block'}),
    #html.Div([
        #html.Button(
        #children='Submit',
        #id='submit-val', 
        #n_clicks = 0)
    #], style={'width': '10%', 'float': 'right', 'padding': 10, 'display': 'inline-block'}), 
    dcc.Tabs(id='tabs-list', value = None),
    html.Div(id='tabs-example-content'),
    html.Div(id='tabs-content'), 
    html.Div(className='row', children=[ 
        html.Div(
        children='Enter a value and press submit',
        id='container-basic')
    ])
])
    
@app.callback(
    Output('language-options', 'options'),
    Input('selected-network', 'value'))
def set_network_options(selected_network):
    wiki_page_options = [v['AvailableLanguages'] for v in network_data.values() if v['title'] == all_networks[selected_network]['*'] if v['language'] == all_networks[selected_network]['lang']]
    language_options = [selected_network] + [k for k,v in all_networks.items() if {'lang': v['lang'], '*': v['*']} in wiki_page_options[0]]
    return [{'label': i, 'value': i} for i in language_options] 

@app.callback(Output('tabs-list', 'children'),
              Input('language-options', 'value'))
def render_tabs(value):
    return [dcc.Tab(label = i, value = i) for i in value] 

@app.callback(Output('tabs-content', 'children'),
              Input('tabs-list', 'value'))
def render_content_tabs(value):
    if value == None: 
        return "Please select an option and tab from above."
    else:
        object_test = WikiNetwork(node_title=all_networks[value]['*'], lang=all_networks[value]['lang'] )

        return "This is a second test: {}".format(
            object_test.nodes_count
    )

if __name__ == '__main__':
    app.run_server(debug=True)
