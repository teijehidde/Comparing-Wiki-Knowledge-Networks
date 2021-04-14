#!/usr/bin/python3

"""
    app.py

    creates network graphs in flask app. 
    Data is saved in json file create in fetch_data.py. 
    To do 1: draw some graphs. // DONE. 
    To do 2: Create class of node and network (cosisting of nodes) 
    To do 3: Build flask app.    
    Q: use numpy? 
"""
# Setup 
from flask import Flask, render_template, request
import os
import pygraphviz as pgv
import networkx as nx
import requests
import json

PATH = "/home/teijehidde/Documents/Git Blog and Coding/Project one (wikipedia SNA)/Code/"
DATA_FILE = 'networkdata.json'

# load data file. 
def WikiNetworkDrawingMAIN():
    
    os.system('clear')

    try:
        with open(PATH + DATA_FILE) as json_file:
            global network_data
            network_data = json.load(json_file)
    except IOError:
        print("Error: Could not find " + DATA_FILE + ". Please check if file is present in directory, or change DATA_FILE value.")
    else: 
        print("The file " + DATA_FILE + " found, succesfully loaded.")

# initiate class nodes. Attributes: title, edges. Methods: ??   
class Node:
    def __init__(self,title,edges):
        self.title = title
        self.nodes = network_data[title]['edges']
        self.edges = {title: network_data[title]['edges']}


# initiate class network. -- 


# Quick first use of pygraphviz to build a graph. 
d = {"1": {"2": None}, "2": {"1": None, "3": None}, "3": {"2": None}}

G = pgv.AGraph(d)
s = G.string()
G.write(PATH + "test.dot") 
G.layout(prog="dot") 
G.draw(PATH + "test.png")

# RUNTIME 
WikiNetworkDrawingMAIN()

