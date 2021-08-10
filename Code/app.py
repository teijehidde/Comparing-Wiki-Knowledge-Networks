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

class WikiNode:
    def __init__(self, node_title, lang, network_data):

        node_data = network_data.loc[network_data['title'] == node_title].loc[network_data['lang'] == lang]
        
        self.node_title = node_data[['title']].iloc[0,0] # iloc[0,0] needed because there can be two instance of same wikipage in the dataframe: one as centralnode (with langlinks) and one as a normal node of other network (without langlinks).  
        self.node_ID = node_data[['uniqueid']].iloc[0,0]
        self.node_links = node_data[['links']].iloc[0,0]
        self.node_lang = node_data[['lang']].iloc[0,0]

class WikiNetwork(WikiNode):
   
    def __init__(self,node_title, lang):
        
        saved_network_data = pd.read_json((path + data_file), orient='split')
        
        WikiNode.__init__(self, node_title, lang, network_data = saved_network_data)
        self.network_nodes = {}
        self.network_links = []
        self.network_edges = [] 
        self.network_status = []
        
        # Go through node_links of the central node (node_title) to build network.
        try: 
            for link in self.node_links + [self.node_title]:
                Node2 = WikiNode(link, lang, network_data = saved_network_data) # NB: the links are not always in the same language as the network. It throws an error as result. - for now it just skips. 
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
        # I think this will work much better with pandas... For next sprint. (see: https://stackoverflow.com/questions/46711557/calculating-min-and-max-over-a-list-of-dictionaries-for-normalizing-dictionary-v)
        G = nx.Graph()
        G.add_edges_from(self.getEdges(type = 'networkx', threshold= threshold))

        data = {}
        degree_centrality_nodes = degreeCentrality(G)
        eccentricity_nodes = eccentricity(G) 

        for item in G.nodes: 
            data[item] = {'Centrality': round(degree_centrality_nodes[item], 4), 'Eccentricity': eccentricity_nodes[item]} 

        return(data)

all_networks = getDownloadedNetworks()

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
    network_data_df = pd.read_json((path + data_file), orient='split')
    
    all_networks_keys = network_data_df.loc[network_data_df['langlinks'].notnull()]['title'].values.tolist()
    all_networks_values = network_data_df.loc[network_data_df['langlinks'].notnull()]['lang'].values.tolist()
    all_networks = dict(zip(all_networks_keys, all_networks_values))

    node_title_langlinks = network_data_df.loc[network_data_df['langlinks'].notnull()].loc[network_data_df['title'] == selected_network].loc[network_data_df['lang'] == 'en']['langlinks'].values.tolist()[0]
    node_title_langlinks = [i['*'] for i in node_title_langlinks]

    language_options = [{k,v} for k,v in all_networks.items() if k in node_title_langlinks]
    language_options = ["{} ({})".format(v,k) for k,v in language_options] 

    return [{'label': i, 'value': i} for i in language_options] 

@app.callback(Output('tabs-list', 'children'),
              Input('language-options', 'value'))
def render_tabs(value):
    return [dcc.Tab(label = i, value = i) for i in value] 

@app.callback(Output('tabs-content', 'children'),
            [Input('memory-selected-networks', 'data'),
            Input('tabs-list', 'value')])  #, 
            # [State('tabs-content', 'children')])
def render_content_tabs(data, value):

        wiki_page = WikiNetwork(node_title=all_networks[value]['*'], lang=all_networks[value]['lang'] )
        graph_node_threshold = 0 
        list_colours = ['red', 'blue', 'purple','orange','green','olive', 'maroon', 'brown','lime','teal' ]

        nodes = wiki_page.getNodes(type='cytoscape', threshold=graph_node_threshold)
        edges = wiki_page.getEdges(type='cytoscape', threshold=graph_node_threshold)
        stats_nodes = wiki_page.getStatsNodes(threshold=graph_node_threshold)
        communities = wiki_page.getCommunities(threshold=graph_node_threshold)

        centrality_max = max([v['Centrality'] for v in stats_nodes.values()])
        centrality_min = min([v['Centrality'] for v in stats_nodes.values()])
        for node in stats_nodes.keys():
            stats_nodes[node]['centrality_normed'] = normalizing(val= stats_nodes[node]['Centrality'], max= centrality_max, min = centrality_min)

        list_selectors = ['[label = "{}"]'.format(i) for i in stats_nodes.keys()]
        list_styles = []
        for node in stats_nodes.keys(): 
            selected_community = [node in i for i in communities].index(True)
            list_styles.append({'background-color': list_colours[selected_community], 
                                'background-opacity': stats_nodes[node]['centrality_normed'] + .2, 
                                'shape': 'ellipse',
                                'width': (stats_nodes[node]['centrality_normed'] * 5) + 1, 
                                'height': (stats_nodes[node]['centrality_normed'] * 5) + 1,
                                }) 
        d = {'selector': list_selectors,
            'style':   list_styles } 
        pd_stylesheet = pd.DataFrame(d)

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
                                                    id='NetworkData-json',
                                                        columns=[{"name": 'Network', "id": 'network'}, {"name": 'Nodes', "id": 'nodes'}, {"name": 'Edges', "id": 'edges'}, {"name": 'Communities', "id": 'communities'}, {"name": 'Center', "id": 'center'}, {"name": 'Clustering', "id": 'clustering'} ], 
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
                                                html.H6("Data on selected node:"),
                                                dash_table.DataTable(
                                                    id='tapNodeData-json',
                                                    columns=[{"name": 'Title', "id": 'title'}, {"name": 'Centrality', "id": 'Centrality'} ], # {"name": 'RAAC', "id": 'C'}],
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
                                                        columns=[{"name": 'Title', "id": 'title'}, {"name": 'Centrality', "id": 'Centrality'} ], 
                                                        data = data, 
                                                        editable=True,
                                                        row_deletable=False,
                                                        style_table={'height': '300px', 'overflowY': 'auto'}
                                                )
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

@app.callback(Output('NetworkData-json', 'data'),
              Input('tabs-list', 'value')) 
def displaytapNetworkData(value):
    wiki_page = WikiNetwork(node_title=all_networks[value]['*'], lang=all_networks[value]['lang'] )
    df_dict = [ 
        {'network': value,
        'nodes':len(wiki_page.getNodes()), # 
        'edges':len(wiki_page.getEdges()), # 
        'communities': len(wiki_page.getCommunities()), #  
        'center': 'TODO', 
        'clustering': 'TODO', 
        'dominating set': 'TODO'} 
    ]
    return df_dict

@app.callback(Output('tapNodeData-json', 'data'),
            Input('tabs-list', 'value'), 
            Input('cytoscape-graph', 'tapNodeData')) 
def displayTapNodeData(value, tapNodeData):
    s = str(value)
    lang = s.split('(', 1)[1].split(')')[0]
    node_title = tapNodeData['id']
    wiki_page = WikiNetwork(node_title=all_networks[value]['*'], lang=all_networks[value]['lang'] )
    stats_nodes = wiki_page.getStatsNodes(threshold=0)
    
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
    stats_nodes = wiki_page.getStatsNodes(threshold=0)
    selected_stats_nodes = list([i for i in communities if node_title in i][0])

    df_dict = [v for (k,v) in network_data.items() if v['title'] in selected_community if v['language'] == lang]
    for item in df_dict: 
        try: 
            item.update( {'Centrality': stats_nodes[item['title']]['Centrality'] })
        except: 
            pass

    return sorted(df_dict, key=lambda k: k['Centrality'], reverse=True)

if __name__ == '__main__':
    app.run_server(debug=True)