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
from sklearn import preprocessing

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
data_file = "data_new2.json" 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# Setting functions
# function: provide titles of networks that are saved in the JSON file. Also provides the language they were saved in. 
def getDownloadedNetworks():

    network_data_df = pd.read_json((path + data_file), orient='split')
    available_wiki_networks = network_data_df.loc[network_data_df['langlinks'].notnull()].loc[network_data_df['lang'] == 'en']['title'].values.tolist()
    
    return(available_wiki_networks)

def normalizing(val, max, min):
    return (val - min) / (max - min); 

def degreeCentrality(G):
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


all_networks = getDownloadedNetworks()
network_data_df = pd.read_json((path + data_file), orient='split')

class WikiNode:
    def __init__(self, node_title, lang, network_data):

        node_data = network_data.loc[network_data['title'] == node_title].loc[network_data['lang'] == lang]
        
        self.node_title = node_data[['title']].iloc[0,0] # iloc[0,0] needed because there can be two instance of same wikipage in the dataframe: one as centralnode (with langlinks) and one as a normal node of other network (without langlinks).  
        self.node_ID = node_data[['uniqueid']].iloc[0,0]
        self.node_links = node_data[['links']].iloc[0,0]
        self.node_lang = node_data[['lang']].iloc[0,0]

class WikiNetwork(WikiNode):
   
    def __init__(self,node_title, lang, threshold = 0):
        
        WikiNode.__init__(self, node_title, lang, network_data = network_data_df)
        self.threshold = threshold
        self.network_nodes = {}
        self.network_links = [node_title]
        self.network_edges = [] 
        self.network_status = []
        
        # Go through node_links of the central node (node_title) to build network.
        for link in self.node_links + [self.node_title]:
            try: 
                Node2 = WikiNode(link, lang, network_data = network_data_df) # NB: the links are not always in the same language as the network. It throws an error as result. - for now it just skips. 
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

    def getNodes(self, type="cytoscape"):
        selected_nodes = [k for k,v in self.links_count.items() if float(v) >= self.threshold]
        
        if type == 'networkx':
            return [(i, {"name": i}) for i in selected_nodes]
        if type == 'cytoscape':
            return [{'data': {'id': i, "label": i}} for i in selected_nodes]

    def getEdges(self,type="cytoscape"):  
        selected_nodes = [k for k,v in self.links_count.items() if float(v) >= self.threshold]
        edges_network = [(a,b) for a,b in self.network_edges if a in selected_nodes and b in selected_nodes]
        
        if type == 'networkx':
            return edges_network
        if type == 'cytoscape':
            return [{'data': {'source': a, "target": b}} for a,b in edges_network]

    def getCommunities(self):  
        G = nx.Graph()
        G.add_edges_from(self.getEdges(type = 'networkx'))
        communities = greedy_modularity_communities(G)

        result = []
        for number in range(len(communities)): 
            result = result + [{i: number} for i in list(communities[number])] 

        return result

    def getStatsNodes(self):
        
        G = nx.Graph()
        G.add_edges_from(self.getEdges(type = 'networkx'))
        communities = greedy_modularity_communities(G)
        degree_centrality_nodes = degreeCentrality(G)
        eccentricity_nodes = eccentricity(G)
        dict_communities = {key:value for value in range(len(communities)) for key in communities[value] }

        return pd.DataFrame({'degree_centrality':pd.Series(degree_centrality_nodes), 'eccentricity':pd.Series(eccentricity_nodes), 'community':pd.Series(dict_communities)}) 

navbar = html.Div(
    [
        dbc.Card(
            dbc.Row(
                [
                    dbc.Col(html.Div([dcc.Dropdown(
                        id='selected-network',
                        options= [{'label': k, 'value': k} for k in all_networks]
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
                                html.Div(id='memory-tabs'),
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
    dcc.Store(id='memory-network'),
    dcc.Store(id='memory-tab'),
    dcc.Store(id='memory-node-table'),  #storage_type='local'), # Can potentially be used to save graphs of tabs so they do not need to reload. 
    navbar,
    tabs,
    overview
])

@app.callback(
    Output('language-options', 'options'),
    Input('selected-network', 'value'))
def set_network_options(selected_network):
    
    all_networks_keys = network_data_df.loc[network_data_df['langlinks'].notnull()]['title'].values.tolist()
    all_networks_values = network_data_df.loc[network_data_df['langlinks'].notnull()]['lang'].values.tolist()
    all_networks = dict(zip(all_networks_keys, all_networks_values))

    node_title_langlinks = network_data_df.loc[network_data_df['langlinks'].notnull()].loc[network_data_df['title'] == selected_network].loc[network_data_df['lang'] == 'en']['langlinks'].values.tolist()[0]
    node_title_langlinks = [i['*'] for i in node_title_langlinks]
    language_options = [("{}: {}".format(v,k), v)  for k,v in all_networks.items() if k in node_title_langlinks]

    return [{'label': a, 'value': a} for a,b in language_options]

@app.callback(Output('tabs-list', 'children'),
              Input('language-options', 'value'))
def render_tabs(value):
    return [dcc.Tab(label = i, value = i) for i in value] 

@app.callback(Output('memory-network', 'data'),
              Input('tabs-list', 'value'),
              # State('memory-selected-networks', 'data')
              ) 
def createNetworkDataframe(value):
    if value is None:
        raise PreventUpdate

    lang, node_title = str(value).split(': ', 1)
    wiki_page = WikiNetwork(node_title=node_title, lang=lang)
    stats_nodes = wiki_page.getStatsNodes()
    nodes = wiki_page.getNodes(type='cytoscape')
    edges = wiki_page.getEdges(type='cytoscape')

    pd_nodes = pd.DataFrame([{'page_ID': v.node_ID, 'title': v.node_title} for v in wiki_page.network_nodes.values()])
    pd_nodes = pd_nodes.set_index('title', drop = False)
    pd_nodes = pd.concat([pd_nodes, stats_nodes], axis = 1)

    return {'nodes_network': nodes, 'edges_network': edges, 'nodes_stats': pd_nodes.to_dict('records')} 

@app.callback(Output('network-graph', 'children'),
              Input('memory-network', 'data')) 
def displayGraph(data):
    list_colours = ['red', 'blue', 'purple','orange','green','olive', 'maroon', 'brown','lime','teal' ]
    nodes = data['nodes_network'] 
    edges = data['edges_network']
    stats_nodes = pd.DataFrame.from_dict(data['nodes_stats']) 
    stats_nodes = stats_nodes.set_index('title', drop = False)

    # dynamic styling for network graph.
    list_selectors = ['[label = "{}"]'.format(i) for i in stats_nodes.index]
    list_styles = []
    for node in stats_nodes.index:
        try: 
            list_styles.append({'background-color': list_colours[int(stats_nodes.loc[node]['community'])], #  'blue', # list_colours[stats_nodes.loc[node]['community']], 
                                'background-opacity': stats_nodes.loc[node]['degree_centrality'] + .2, 
                                'shape': 'ellipse',
                                'width':  (stats_nodes.loc[node]['degree_centrality']* 5) + 1, 
                                'height': (stats_nodes.loc[node]['degree_centrality']* 5) + 1,
                                })
        except:
            list_styles.append({'background-color': 'black', #  'blue', # list_colours[stats_nodes.loc[node]['community']], 
                'background-opacity': 1, 
                'shape': 'ellipse',
                'width': 10, 
                'height': 10,
                })
    d = {'selector': list_selectors,
        'style':   list_styles } 
    pd_stylesheet = pd.DataFrame(d)

    return cyto.Cytoscape(
                    id='cytoscape-graph',
                    layout={'name': 'cose',
                    'animate': True,
                    'randomize': True, 
                    'gravity': 1
                }, 
                style={'width': '100%', 'height': '650px'},
                elements=nodes+edges,
                stylesheet= 
                    [
                        {'selector': 'edge',
                            'style': {
                                'curve-style': 'haystack', # bezier
                                'width': .03
                        }}, 
                        {'selector': 'node',
                            'style': {
                                'width': .01, 
                                'height': .01
                        }}, 
                    ] + 
                    pd_stylesheet.to_dict('records')  
                )

    

@app.callback(Output('memory-tabs', 'children'),
              Input('memory-network', 'data'))
def render_content_tabs(data): 
        stats_nodes = pd.DataFrame.from_dict(data['nodes_stats']) 
        stats_nodes = stats_nodes.set_index('title', drop = False)

        network_table_data = [ 
            {'nodes':len(stats_nodes.index), # 
            'communities': len(stats_nodes['community'].unique()), #  
            'center': 'TODO', 
            'clustering': 'TODO', 
            'dominating set': 'TODO'} 
        ]

        return (
            dbc.Row([
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.Div(id='network-graph')
                        ]
                    ), style={"width": "45%"},
                ),
                dbc.Card(
                    dbc.CardBody(
                            [dbc.Col(
                                [dbc.Card(
                                    dbc.CardBody(
                                            [
                                                html.H6("Data on network:"),
                                                dash_table.DataTable(
                                                    columns=[{"name": 'Nodes', "id": 'nodes'}, {"name": 'Edges', "id": 'edges'}, {"name": 'Communities', "id": 'communities'}, {"name": 'Center', "id": 'center'}, {"name": 'Clustering', "id": 'clustering'} ], 
                                                    data = network_table_data, 
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
                                                html.H6("Data on selected node:"),
                                                html.Div(id='node-table')
                                            ]
                                        ), 
                                ),
                                dbc.Card(
                                    dbc.CardBody(
                                            [
                                                html.H6("Data on nodes in selected community:"),
                                                html.Div(id='community-table')
                                            ]
                                        ), 
                                ),
                                ]
                            ),
                            ]
                    ), style={"width": "55%"},
                    )
        ])
    )

@app.callback(Output('node-table', 'children'),
             Input('memory-network', 'data'),
             Input('cytoscape-graph', 'tapNodeData')) 
def displayTapNodeData(data, tapNodeData):  
    stats_nodes = pd.DataFrame.from_dict(data['nodes_stats']) 
    stats_nodes = stats_nodes.loc[stats_nodes['title'] == str(tapNodeData['id'])]

    return dash_table.DataTable(
        columns=[{"name": 'Title', "id": 'title'}, {"name": 'Centrality', "id": 'degree_centrality'}, {"name": 'Community', "id": 'community'} ], 
        data = stats_nodes.to_dict('records'),
        style_table={'height': '75px', 'overflowY': 'auto'})

@app.callback(Output('community-table', 'children'),
             Input('memory-network', 'data'),
             Input('cytoscape-graph', 'tapNodeData')) 
def displayTapCommunityData(data, tapNodeData):
    stats_nodes = pd.DataFrame.from_dict(data['nodes_stats'])
    community = stats_nodes.loc[stats_nodes['title'] == str(tapNodeData['id'])]['community']
    stats_nodes = stats_nodes.loc[stats_nodes['community'] == int(community)].sort_values(by=['degree_centrality'], ascending=False)

    return dash_table.DataTable(
        columns=[{"name": 'Title', "id": 'title'}, {"name": 'Centrality', "id": 'degree_centrality'} ], 
        data = stats_nodes.to_dict('records'),
        style_table={'height': '300px', 'overflowY': 'auto'})

if __name__ == '__main__':
    app.run_server(debug=True)