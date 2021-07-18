# Comparing Networks of Knowledge
Application that uses [prop=links] in the Wikipedia API module to compare networks of Wikipedia pages on one topic between multiple languages.
App is under active development. WIP.

Regarding API, see Wikipedia API websites:
- https://www.mediawiki.org/wiki/API:Etiquette
- https://www.mediawiki.org/wiki/API:Query#Generators


## Requested features for app.
-------
1. Compare Network graphs of one page in two (or more) language side by side.
2. Compare data on network structure side by side. For instance data clusters in each network.
3. An accessible way to see and choose between available networks and languages (that are all saved in a .JSON file).  
4. An accessible way to initiate the Wikipedia API to download new networks and to chose in what languages a network should be downloaded.


## TODOs:
-------
1. Create a Wiki-graph class, based on networkx nx.Graph instance. It should have method to call status graph (no. of nodes, edges, etc; analysis on individual nodes and clusters in the graph) and include visualisation of graph. All this should be build using networkx, pyvis and numpy.
2. [DONE] Revise API call to act at network (not node) level, and based completely on generators. -- see website from wikipedia. Also consider implementing zipping.
3. [DONE] API should check what language a topic is available in.
4. [DONE] Write function to download network in specific additional language.
4. [DONE] Restructure (again) how data is saved. a) The 'plcontinue value' should NOT be linked to node (similar to how wikimedia treats it). b) Implement timestamp c) save the Wikipedia version (english, french, arabic) that data is from.
5. [WIP] Start playing around with comparing knowledge networks around topics _in different languages_. Cross case comparison on same topic.
6. [ASK Neci] Start playing with Django for building interacting website to visualize descriptive analysis. On the face of it Django seems more straighforward than Flask.
7. -- later -- incorporate 'revision' in data that is downloaded.

## Install
-------

```


```

## Screenshot
----------

<table><tr><td>
<img src="screenshot.png" width="300" style="border 5px solid black">
</td></tr></table>
