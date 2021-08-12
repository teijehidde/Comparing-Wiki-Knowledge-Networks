# Setup packages 
from collections import Counter
from dash_bootstrap_components._components.Row import Row
import pandas as pd
import numpy as np
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
import networkx.algorithms
import networkx.utils # (algorithms to check out: "approximation", "eccentricity", "diameter", "radius", "periphery", "center", "barycenter", "Community" "degree_centrality", "constraint", "local_constraint", "effective_size") 

# Dash packages needed for building dash app 

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_cytoscape as cyto
import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# setup layout and paths
path = "/home/teijehidde/Documents/Git Blog and Coding/"
data_file = "data_dump/data_new2.json" 
external_stylesheets = path + 'Comparing Wikipedia Knowledge Networks (Network Analysis Page links)/Code/stylesheet.css' # downloaded from: https://codepen.io/chriddyp/pen/bWLwgP.css. Should appear in credits! 
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}
colors = {
    'background': 'white', # use color coding later. 
    'text': 'gray'
}
list_colours = ['red', 'blue', 'purple','orange','green','olive', 'maroon', 'brown','lime','teal' ]

# loading data. 
network_data_df = pd.read_json((path + data_file), orient='split')
all_networks = network_data_df.loc[network_data_df['langlinks'].notnull()].loc[network_data_df['lang'] == 'en']['title'].values.tolist()
# new version: all_networks = network_data_df.loc[network_data_df['ego'] == True].loc[network_data_df['lang'] == 'en']['title'].values.tolist()

# setting up classes WikiNode and WikiNetwork. 
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
        degree_centrality_nodes = networkx.algorithms.centrality.degree_centrality(G)
        eccentricity_nodes = networkx.algorithms.distance_measures.eccentricity(G)
        dict_communities = {key:value for value in range(len(communities)) for key in communities[value] }

        df = pd.DataFrame({'degree_centrality':pd.Series(degree_centrality_nodes), 'eccentricity':pd.Series(eccentricity_nodes), 'community':pd.Series(dict_communities)}) 

        val_max = max(df['degree_centrality'])
        val_min = min(df['degree_centrality'])
        df[['normalized_centrality']] = df[['degree_centrality']].apply(lambda x: (x - val_min) / (val_max - val_min), result_type = 'expand')
        df[['degree_centrality']] = df[['degree_centrality']].apply(lambda x: round(x, 2))

        return df

# Basic layout app 
navbar = html.Div(
    [
        dbc.Card(
            dbc.Row(
                [
                    dbc.Col(html.Div([dcc.Dropdown(
                        id='selected-network',
                        options= [{'label': k, 'value': k} for k in all_networks],
                        placeholder='Step 1: Select a topic'
                        ),
                        ]), width = 3
                    ),
                    dbc.Col(html.Div([dcc.Dropdown(
                        id='language-options',
                        multi=True, 
                        placeholder='Step 2: Select languages'
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
    [dbc.Card([
                dbc.CardHeader(html.H4("Introduction", style = {"align": "center"})),
                    dbc.Row([
                        dbc.Card([
                            dbc.CardBody(
                                [
                                    html.H6("What does this app do?", className="card-subtitle"),
                                        dcc.Markdown('''
                                                    This app shows a network of pagelinks from a _single_ wikipedia page across _multiple_ languages. 
                                                    The app makes it possible to easily compare pagelinks networks for the same topic between languages.  

                                                    Variations between these networks reflect different ways in which topics such as _secularism_, _religion_, _terrorism_ are linked to other topics on wikipedia.
                                                    These differences are not due to language: the app only considers pagelinks, not text.
                                                    Instead, they reflect the development of wikipedia, and popular understandings of these concepts, in each language. 

                                                    '''),
                                    html.H6("How does it work?", className="card-subtitle"),
                                        dcc.Markdown('''
                                                    * Step 1: Select a topic. 
                                                    * Step 2: Select multiple languages to compare. A tab will appear per chosen language. 
                                                    * Step 3: Select a tab, which contains a network graph and analysis. 

                                                    Also see the clip to the right.
                                                    '''),
                                    html.H6("Credits", className="card-subtitle"),
                                        dcc.Markdown('''
                                                    All data used in this app was downloaded freely via the Wikimedia API.
                                                    [Please consider donating to Wikimedia.](https://donate.wikimedia.org/wiki/Ways_to_Give)
                                                    '''),
                                ], 
                            )], style={"width": "40%", "padding-left":"1%", "padding-right":"2%"}, 
                            ), 
                        dbc.Card([
                            dbc.CardBody(
                                [
                                    html.Iframe(
                                        width="100%", 
                                        height="500", 
                                        src=f'https://www.youtube.com/embed/_jWbqhP5eJI'
                                    )
                                ]
                            )], style={"width": "60%", "padding-left":"1%", "padding-right":"2%"},
                            ),
                    ]),
                dbc.CardFooter('This app has been build using Dash.') # 
                ], 
            ),
        ])

app.layout = html.Div([
    dcc.Store(id='memory-network'),
    # dcc.Store(id='memory-tab'),
    # dcc.Store(id='memory-node-table'),  #storage_type='local'), # Can potentially be used to save graphs of tabs so they do not need to reload. 
    navbar,
    tabs,
    overview
])

# Callbacks for functioning app. 
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
              ) 
def createNetworkDataframe(value):
    if value is None:
        raise PreventUpdate

    lang, node_title = str(value).split(': ', 1)
    wiki_page = WikiNetwork(node_title=node_title, lang=lang)
    stats_nodes = wiki_page.getStatsNodes()
    nodes = wiki_page.getNodes(type='cytoscape')
    edges = wiki_page.getEdges(type='cytoscape')

    pd_nodes = pd.DataFrame([{'page_ID': v.node_ID, 'title': v.node_title} for v in wiki_page.network_nodes.values()]).set_index('title', drop = False)
    pd_nodes = pd.concat([pd_nodes, stats_nodes], axis = 1)

    return {'node_title': node_title, 'lang': lang, 'nodes_network': nodes, 'edges_network': edges, 'nodes_stats': pd_nodes.to_dict('records')} 

@app.callback(Output('network-graph', 'children'),
              Input('memory-network', 'data')) 
def displayGraph(data):
    nodes = data['nodes_network'] 
    edges = data['edges_network']
    stats_nodes = pd.DataFrame.from_dict(data['nodes_stats']) 
    stats_nodes = stats_nodes.set_index('title', drop = False)

    # dynamic styling for network graph.
    list_selectors = ['[label = "{}"]'.format(i) for i in stats_nodes.index]
    list_styles = []
    for node in stats_nodes.index:
        list_styles.append({'background-color': list_colours[int(stats_nodes.loc[node]['community'])], #  'blue', # list_colours[stats_nodes.loc[node]['community']], 
                            'background-opacity': stats_nodes.loc[node]['normalized_centrality'] + .2, 
                            'shape': 'ellipse',
                            'width':  (stats_nodes.loc[node]['normalized_centrality']* 5) + 1, 
                            'height': (stats_nodes.loc[node]['normalized_centrality']* 5) + 1,
                            })
    pd_stylesheet = pd.DataFrame({'selector': list_selectors, 'style': list_styles } )

    return cyto.Cytoscape(
                    id='cytoscape-graph',
                    layout={'name': 'cose',
                    'animate': True,
                    'randomize': True, 
                    'gravity': 1
                }, 
                style={'width': '100%', 'height': '900px'},
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
                                                html.H6("Network:"),
                                                dash_table.DataTable(
                                                    columns=[{"name": 'Nodes', "id": 'nodes'}, {"name": 'Edges', "id": 'edges'}, {"name": 'Communities', "id": 'communities'}, {"name": 'Clustering', "id": 'clustering'}], 
                                                    data = network_table_data, 
                                                    editable=True,
                                                    row_deletable=False,
                                                    style_table={'height': '60px', 'overflowY': 'auto'}, 
                                                    style_cell={'textAlign': 'left'},                                                
                                                ), 
                                                dash_table.DataTable(
                                                    columns=[{"name": 'Title', "id": 'title'}, {"name": 'Translation', "id": 'translation'}, {"name": 'Centrality', "id": 'degree_centrality'}], 
                                                    data = stats_nodes.sort_values(by=['degree_centrality'], ascending=False).to_dict('records'),
                                                    editable=True,
                                                    row_deletable=False,
                                                    style_table={'height': '100px', 'overflowY': 'auto'}, 
                                                    style_cell={'textAlign': 'left'},
                                                )
                                            ]
                                        ), 
                                ),
                                dbc.Card(
                                    dbc.CardBody(
                                            [
                                                html.H6("Data on communities:"),
                                                dbc.Col([ 
                                                dcc.Tabs(id='community-tabs-list', value = None), 
                                                html.Div(id='community-table')
                                                ]),
                                            ], 
                                        ), 
                                ),
                                dbc.Card(
                                    dbc.CardBody(
                                            [
                                                html.H6("Data on selected nodes:"),
                                                html.Div(id='node-table')
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

@app.callback(Output('community-tabs-list', 'children'),
             Input('memory-network', 'data')) 
def displayCommunityTabs(data):
    stats_nodes = pd.DataFrame.from_dict(data['nodes_stats'])
    number_community = set(stats_nodes['community'].tolist())
    return [dcc.Tab(label = 'Community {}'.format(n), value = n, style={'height': '60px', 'color': list_colours[n]}) for n in number_community]

@app.callback(Output('community-table', 'children'),
              Input('community-tabs-list', 'value'),
              Input('memory-network', 'data')) 
def displayCommunityData(value, data):
    stats_nodes = pd.DataFrame.from_dict(data['nodes_stats'])
    stats_nodes = stats_nodes.loc[stats_nodes['community'] == int(value)]

    return dash_table.DataTable(
        columns=[{"name": 'Title', "id": 'title'}, {"name": 'Centrality', "id": 'degree_centrality'} ], 
        data = stats_nodes.sort_values(by=['degree_centrality'], ascending=False).to_dict('records'),
        style_table={'height': '200px', 'overflowY': 'auto'})

@app.callback(Output('node-table', 'children'),
             Input('memory-network', 'data'),
             Input('cytoscape-graph', 'tapNodeData')) 
def displayTapNodeData(data, tapNodeData):  
    stats_nodes = pd.DataFrame.from_dict(data['nodes_stats']) 
    stats_nodes = stats_nodes.loc[stats_nodes['title'] == str(tapNodeData['id'])]
    return dbc.Col(
                    [
                        dash_table.DataTable(
                            columns=[{"name": 'Title', "id": 'title'}, {"name": 'Centrality', "id": 'degree_centrality'}, {"name": 'Community', "id": 'community'} ], 
                            data = stats_nodes.to_dict('records'),
                            style_table={'height': '75px', 'overflowY': 'auto'},
                            style_cell={'textAlign': 'left'}),                        
                        html.Iframe(
                            width="100%", 
                            height="400", 
                            src=f'https://{data["lang"]}.wikipedia.org/wiki/{tapNodeData["id"]}')
                    ], 
    )

if __name__ == '__main__':
    app.run_server(debug=True)