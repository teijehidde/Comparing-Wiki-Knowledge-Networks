#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 16 15:16:15 2020

Aim of the script is to create Python classes that can be used for text 
analysis of contributions to a wikipedia page. 

2 - List and meta data of contributors per page.
3 - Meta data and content of revisions of each contributor. 

Contains three classes: 
1 - WikiPage: 
    - contains Meta data wikipage, and list of revisions. 
2 - WikiContributor: 
    - contains Meta data contributors, and each revision done per page. 
3 - WikiRevision: 
    - Contains meta data and content revision. Raw and edited. 
    
Contains one function: 
3 - wiki_page_revision_data: 
    .init (input = page title, output = WikiPage instance, and list of 
           WikiContributor instances, list of WikiRevision instances, but 
           absent of content revisions.)
    .update (input = WikiPage instance; list of WikiContributor instances, 
             list of WikiRevision instances, output = update on WikiPage 
             instance, and update list of WikiContributor instances, appending 
             list WikiRevision instances, but no added content.)
    .data_fetch (input = list WikiRevision instances; throttle, 
                 output = content of WikiRevision instances. Throttle 
                 necessary to not overwhelm Wikipedia API.)
    .save? (input = list of WikiPage instances; list of WikiContributor 
            instances; list of WikiRevision instances. Saves these to a 
            JSON/ Panda file.) 
    .load? (input = JSON/ Panda file. Speaks for itself.)
    
Next steps, after this script works. 
1 - Do actual data analysis.  

@author: teijehidde
"""

# SETUP 
import os 
os.chdir('/home/teijehidde/Documents/Git/core')

import pywikibot
# import requests
# import bs4
# import difflib

# SETUP CLASS - WikiPage
class WikiPage: 
    def __init__(self, title, id_page, text, WikiContributors, WikiRevisions):
        self.title = title # NB needs check for legit title. 
        self.id = id_page 
        self.text = text 
        
        self.WikiContributors = WikiContributors # NB needs check for legit list of WikiContributor instances. 
        self.WikiRevisions = WikiRevisions # NB needs check for legit list of WikiRevision instances. 
     
    def fetch_content_page(self):
        # todo. Call function wiki_page_revision_data
        pass 

# SETUP CLASS - WikiContributor 
class WikiContributor: 
    def __init__(self, name, WikiPages, WikiRevisions):
        self.name = name # NB needs check for legit title. 
        self.bot = False         
        
        self.WikiPages = WikiPages.title # NB needs check for legit list of WikiContributor instances. 
        self.WikiRevisions = WikiRevisions # NB needs check for legit list of WikiRevision instances. 
        
    def fetch_bio_contributor(self):
        # todo. Call function wiki_page_revision_data
        pass 

# SETUP CLASS - WikiRevision  
class WikiRevision: 
    def __init__(self, item, WikiPage, WikiContributor):
        self.item = item # NB needs check for legit item number. 
        # self.id = id_revision 
        # self.parentid = parent_id 
        # self.timestamp = timestamp
        # self.note = revision_note 
        
        self.WikiPages = WikiPage.title # NB needs check for legit list of WikiContributor instances. 
        self.WikiContributor = WikiContributor.name # NB needs check for legit list of WikiRevision instances. 
        self.Data = None 
        self.Text = None 
     
    def fetch_content_revision(self):
        # todo. -- should be specific to this object. 
        pass 

# SETUP FUNCTION - wiki_page_revision_data 
# input should be title page and, optional, dictionary of WikiPages, WikiContributors, WikiRevisions
# output should be tuple of three lists: 
    # 1 - (Appended) Dictionary of WikiPages
    # 2 - (Appended) Dictionary of WikiContributors
    # 3 - (Appended) Dictionary of WikiRevisions 

def wiki_fetch_metadata(wiki_title, wiki_pages = None, wiki_contributors = None, wiki_revisions = None): 
    
    # Setting updictionaries of class instances. 
    if wiki_pages == None: wiki_pages = {}
    if wiki_contributors == None: wiki_contributors = {}
    if wiki_revisions == None: wiki_revisions = {}
    
    # Fetching metadata site, contributors and revisions. 
    site = pywikibot.Site()
    page = pywikibot.Page(site, wiki_title)
    
    contributors = page.contributors()
    
    revisions = []
    for revision in page.revisions(): 
        revisions.append(revision)
    
    # Creating class instances: WikiPage, WikiContributor, WikiRevision  
    WikiPages[wiki_title] = WikiPage(title = wiki_title, id_page = None, text = page.text, WikiContributors=contributors.keys(), WikiRevisions=None)
    WikiPage[wiki_title].id = page._pageid 
    
    for key in contributors.keys(): 
        WikiContributor(name = key, wiki_pages = 'TODO', wiki_revisions = )
    
    return WikiPage_temp
