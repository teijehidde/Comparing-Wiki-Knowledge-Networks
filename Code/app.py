# Setup packages (might be able to remove a few of these.)
# packages needed for downloading, saving and loading data 
import os
from collections import Counter
import collections
from dash_bootstrap_components._components.Col import Col 
import json
from networkx.algorithms.traversal.depth_first_search import dfs_labeled_edges
import pandas as pd
import numpy as np

# packages for creation classes and network analysis 
import networkx as nx
from itertools import chain
# import communities
# from networkx.algorithms import approximation
# from networkx.algorithms import community
from networkx.algorithms.community import greedy_modularity_communities
from networkx.utils import not_implemented_for 
__all__ = [
    "eccentricity",
    "diameter",
    "radius",
    "periphery",
    "center",
    "barycenter",
    "degree_centrality",
    "constraint", 
    "local_constraint", 
    "effective_size"
]

# Dash packages for presentation analysis  
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px


# setup layout and paths
path = "/home/teijehidde/Documents/Git Blog and Coding/data_dump/"
data_file = "DATA.json" 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
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

    # create set of ego network names.  
    downloaded_networks = [(v['ego']) for (k,v) in network_data.items()]
    downloaded_networks = set(list(chain(*downloaded_networks)))
    downloaded_networks = [v for v in network_data.values() if v['title'] in downloaded_networks]

    # print names of ego networks and language that they have been downloaded in. 
    items = {}  
    for network in downloaded_networks: 
        items[network['title'] + ' (' + network['language'] + ')'] = {'lang':  network['language'], '*': network['title']}    
    return(items)

def degree_centrality(G):
# function copy-pasted from: https://networkx.org/documentation/stable/_modules/networkx/algorithms/centrality/degree_alg.html#degree_centrality
    
    if len(G) <= 1:
        return {n: 1 for n in G}

    s = 1.0 / (len(G) - 1.0)
    centrality = {n: d * s for n, d in G.degree()}
    return centrality

def eccentricity(G, v=None, sp=None):
# function copy-pasted from: https://networkx.org/documentation/stable/_modules/networkx/algorithms/distance_measures.html#eccentricity

    order = G.order()

    e = {}
    for n in G.nbunch_iter(v):
        if sp is None:
            length = nx.single_source_shortest_path_length(G, n)
            L = len(length)
        else:
            try:
                length = sp[n]
                L = len(length)
            except TypeError as e:
                raise nx.NetworkXError('Format of "sp" is invalid.') from e
        if L != order:
            if G.is_directed():
                msg = (
                    "Found infinite path length because the digraph is not"
                    " strongly connected"
                )
            else:
                msg = "Found infinite path length because the graph is not" " connected"
            raise nx.NetworkXError(msg)

        e[n] = max(length.values())

    if v in G:
        return e[v]  # return single value
    else:
        return e

# Initiate class Node. 
class WikiNode:
    def __init__(self, node_title, lang):

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
        self.links_count = Counter(self.network_links)

    def getNodes(self, type="cytoscape", threshold=0):
        selected_nodes = [k for k,v in self.links_count.items() if float(v) >= threshold]
        
        if type == 'networkx':
            return [(i, {"name": i}) for i in selected_nodes]
        if type == 'cytoscape':
            return [{'data': {'id': i, "label": i}} for i in selected_nodes]

    def getEdges(self,type="cytoscape", threshold=0):  
        selected_nodes = [k for k,v in self.links_count.items() if float(v) >= threshold]
        edges_network = [(a,b) for a,b in self.network_edges if a in selected_nodes and b in selected_nodes]
        
        if type == 'networkx':
            return edges_network
        if type == 'cytoscape':
            return [{'data': {'source': a, "target": b}} for a,b in edges_network]

    def getCommunities(self,threshold=0):  
        G = nx.Graph()
        G.add_edges_from(self.getEdges(type = 'networkx', threshold= threshold))
        return greedy_modularity_communities(G)

    def getStatsNodes(self, threshold = 0):
        G = nx.Graph()
        G.add_edges_from(self.getEdges(type = 'networkx', threshold= threshold))

        data = {}
        degree_centrality_nodes = degree_centrality(G)
        eccentricity_nodes = eccentricity(G)

        for item in G.nodes: 
            data[item] = {'Centrality': degree_centrality_nodes[item], 'Eccentricity': eccentricity_nodes[item]} 

        return(data)
    
    def getStatsCommunities(self, node):
        # TODO: return an numpy array with stats per node: 
        # - triangles
        # - degree_centrality 
        # - ... 
        # if nodes == None: 
          #  node = self.node_links

        print('WIP')
    
    def getStatsNetwork(self): 
        return(
            pd.DataFrame(
                {
                    "A": self.node_ID,
                    "B": pd.Timestamp("20200102"),
                    "C": pd.Series(1, index=list(range(4)), dtype="float32"),
                    "D": np.array([3] * 4, dtype="int32"),
                    "E": pd.Categorical(["test", "train", "test", "train"]),
                    "F": self.node_title,
                }
                )
            )   
        # TODO: return a dictionary with stats on network: 
        # - triangles
        # - degree_centrality 
        # - ...

all_networks = getDownloadedNetworks()

navbar = html.Div(
    [
        dbc.Card(
            dbc.Row(
                [
                    dbc.Col(html.Div([dcc.Dropdown(
                        id='selected-network',
                        options= [{'label': k, 'value': k} for k in all_networks.keys()]
                        ),
                        ]), width = 3
                    ),
                    dbc.Col(html.Div([dcc.Dropdown(
                        id='language-options',
                        multi=True
                        ),
                        ]), width= 6
                    ),
                ], justify="center", 
        ), body = True
        ), 
    ]
)

tabs = html.Div(
    dbc.Card(
        dbc.CardBody(    
                    [
                        dcc.Tabs(id='tabs-list', value = None),
                        dbc.Card(
                            dbc.CardBody( 
                                [
                                html.Div(id='tabs-content'),
                            ] )), 
                    ]
            )
        )  
)

overview = html.Div(
    [
        dbc.Card(
                    [
                        dbc.CardHeader("Introduction to the app."),
                        dbc.CardBody(
                            [
                                html.H4("Introduction", className="card-title"),
                                html.H6("How does this app work?", className="card-subtitle"),
                                html.P(
                                "Here is a brief one, two, three steps explaining how the app works.",
                                className="card-text",
                                ),
                                dbc.CardLink("Card link", href="#"),
                                dbc.CardLink("External link", href="https://google.com"),
                            ]
                        ),
                    dbc.CardFooter("Consider donating to WIkipedia. See here: LINK HERE.")
                ], style={"width": "100%"},
            )
    ]
    )

app.layout = html.Div([
    dcc.Store(id='memory-selected-networks'), # Can potentially be used to save graphs of tabs so they do not need to reload. 
    navbar,
    tabs,
    overview
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

# NB! 
@app.callback(Output('memory-selected-networks', 'data'),
              Input('tabs-list', 'value'))     
def create_wiki_network(value):         
    return WikiNetwork(node_title=all_networks[value]['*'], lang=all_networks[value]['lang'] )

@app.callback(Output('tabs-content', 'children'),
            [Input('memory-selected-networks', 'data'),
            Input('tabs-list', 'value')])  #, 
            # [State('tabs-content', 'children')])
def render_content_tabs(data, value):
        
        wiki_page = WikiNetwork(node_title=all_networks[value]['*'], lang=all_networks[value]['lang'] )

        nodes = wiki_page.getNodes(type='cytoscape', threshold=4)
        edges = wiki_page.getEdges(type='cytoscape', threshold=4)
        communities = wiki_page.getCommunities()

        stats_nodes = wiki_page.getStatsNodes(threshold=4)
        network_stats_df = wiki_page.getStatsNetwork()

        def get_selectors_centrality(number):
            tuple_node_centrality = {(k,v['Centrality']) for k, v in stats_nodes.items() } 
            tuple_node_centrality = sorted(tuple_node_centrality, key= lambda node: node[1])
            tuple_node_centrality_split = np.array_split(tuple_node_centrality, 5)

            list_selectors = ''.join([('[label = "{}"],'.format(i[0])) for i in tuple_node_centrality_split[number]])
            return(list_selectors.rstrip(list_selectors[-1]))

        def get_selectors_communities(number):
            try: 
                list_selectors = ''.join([('[label = "{}"],'.format(i)) for i in communities[number]])
                return (list_selectors.rstrip(list_selectors[-1]))
            except: 
                return ('[label = " "]') 

        return (
            dbc.Row([
                dbc.Card(
                    dbc.CardBody(
                        [
                            cyto.Cytoscape(
                            id='cytoscape-graph',
                            layout={'name': 'cose',
                            'animate': True,
                            'randomize': True, 
                            'gravity': 1
                            }, # cose, ... 
                            style={'width': '100%', 'height': '600px'},
                            elements=nodes+edges,
                            stylesheet=[{
                            'selector': 'node',
                            'style': {
                                'content': '',
                                'shape': 'ellipse',
                                'width': .5,    
                                'height': .5,
                                'background-color': 'black',
                                'padding': '50%'
                            }},
                            {'selector': get_selectors_communities(0),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'red',
                             }},
                            {'selector': get_selectors_communities(1),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'blue',
                             }},
                            {'selector': get_selectors_communities(2),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'orange',
                             }},
                            {'selector': get_selectors_communities(3),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'green',
                             }},
                            {'selector': get_selectors_communities(4),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'purple',
                             }},
                            {'selector': get_selectors_communities(5),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'olive',
                             }},
                            {'selector': get_selectors_communities(6),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'brown',
                             }},
                            {'selector': get_selectors_communities(7),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'maroon',
                             }},
                            {'selector': get_selectors_communities(8),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'lime',
                             }},
                            {'selector': get_selectors_communities(9),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-color': 'teal',
                             }},
                            {'selector': get_selectors_centrality(0),
                            'style': {
                                'width': .2,
                                'height': .2,
                                'background-opacity': .2,
                             }},
                            {'selector': get_selectors_centrality(1),
                            'style': {
                                'width': .4,
                                'height': .4,
                                'background-opacity': .4,
                             }},
                            {'selector': get_selectors_centrality(2),
                            'style': {
                                'width': .6,
                                'height': .6,
                                'background-opacity': .6,
                             }},
                            {'selector': get_selectors_centrality(3),
                            'style': {
                                'width': .8,
                                'height': .8,
                                'background-opacity': .8,
                             }},
                            {'selector': get_selectors_centrality(4),
                            'style': {
                                'width': 1,
                                'height': 1,
                                'background-opacity': 1,
                             }},
                            {'selector': 'edge',
                            'style': {
                                'curve-style': 'haystack', # bezier
                                'width': .03
                                #'height': .1
                            }}
                        ]),
                            html.Div(
                                [
                                    dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dcc.RangeSlider(
                                                    min=0,
                                                    max=100,
                                                    step=5,
                                                    marks={
                                                        0: '0%',
                                                        25: '25%',
                                                        50: '50%',
                                                        75: '75%',
                                                        100: '100%'
                                                    },
                                                    value=[20, 100],
                                                ),
                                            ], width = 9, 
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button("Update", outline=True, color="primary", className="mr-1"), 
                                            ], width = 3, 
                                        )
                                    ]
                                )
                                ], style={"width": "100%"}
, 
                            )
                        ]
                    ), style={"width": "40%"},
                ),
                dbc.Card(
                    dbc.CardBody(
                            [dbc.Col(
                                [dbc.Card(
                                    dbc.CardBody(
                                            [
                                                html.H6("Data on selected node:"),
                                                dash_table.DataTable(
                                                    id='tapNodeData-json',
                                                    columns=[{"name": 'Node ID', "id": 'node_ID'}, {"name": 'Title', "id": 'title'}, {"name": 'Language', "id": 'language'}, {"name": 'Centrality', "id": 'Centrality'} ], # {"name": 'RAAC', "id": 'C'}],
                                                    data = data, 
                                                    editable=True,
                                                    row_deletable=False,
                                                    style_table={'height': '75px', 'overflowY': 'auto'}
                                                )
                                            ]
                                        ), 
                                ),
                                dbc.Card(
                                    dbc.CardBody(
                                            [
                                                html.H6("Data on nodes in selected community:"),
                                                dash_table.DataTable(
                                                    id='tapCommunityData-json',
                                                        columns=[{"name": 'Node ID', "id": 'node_ID'}, {"name": 'Title', "id": 'title'}, {"name": 'Language', "id": 'language'} ], 
                                                        data = data, 
                                                        editable=True,
                                                        row_deletable=False,
                                                        style_table={'height': '300px', 'overflowY': 'auto'}
                                                )
                                            ]
                                        ), 
                                ),
                                dbc.Card(
                                    dbc.CardBody(
                                            [
                                                html.H6("Data on network:"),
                                                dbc.Table.from_dataframe(network_stats_df, striped=True, bordered=True, hover=True), 
                                            ]
                                        ), 
                                )
                                ]
                            ),
                            ]
                    ), style={"width": "60%"},
                    )
        ])
    )

@app.callback(Output('tapNodeData-json', 'data'),
            Input('tabs-list', 'value'), 
            Input('cytoscape-graph', 'tapNodeData')) #               # Input('tabs-list', 'value')
def displayTapNodeData(value, tapNodeData):
    s = str(value)
    lang = s.split('(', 1)[1].split(')')[0]
    node_title = tapNodeData['id']
    wiki_page = WikiNetwork(node_title=all_networks[value]['*'], lang=all_networks[value]['lang'] )
    stats_nodes = wiki_page.getStatsNodes(threshold=4)
    
    df_dict = [v for (k,v) in network_data.items() if v['title'] == node_title if v['language'] == lang]
    df_dict[0]['Centrality'] = stats_nodes[node_title]['Centrality']

    return df_dict

@app.callback(Output('tapCommunityData-json', 'data'),
              Input('tabs-list', 'value'), 
              Input('cytoscape-graph', 'tapNodeData')) 
def displaytapCommunityData(value, tapNodeData):
    s = str(value)
    lang = s.split('(', 1)[1].split(')')[0]
    node_title = tapNodeData['id']
    wiki_page = WikiNetwork(node_title=all_networks[value]['*'], lang=all_networks[value]['lang'] )
    communities = wiki_page.getCommunities()
    selected_community = list([i for i in communities if node_title in i][0])

    df_dict = [v for (k,v) in network_data.items() if v['title'] in selected_community if v['language'] == lang]
    return df_dict

if __name__ == '__main__':
    app.run_server(debug=True)



"""    html.Div(
        [
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
"""
    #html.Div([
        #html.Button(
        #children='Submit',
        #id='submit-val', 
        #n_clicks = 0)
    #], style={'width': '10%', 'float': 'right', 'padding': 10, 'display': 'inline-block'}), 