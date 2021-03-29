#!/usr/bin/python3

"""
    app.py

    MediaWiki API Demos

    User contributions feed app: Demp app that uses `list=usercontribs` module
    to fetch the top 50 edits made by a user

    MIT license
"""

from flask import Flask, render_template, request
import requests

WIKI_URL = "https://en.wikipedia.org"
API_ENDPOINT = WIKI_URL + "/w/api.php"
# pagename = "Albert Einstein"

"""
# App config.
DEBUG = True
APP = Flask(__name__)
APP.config['SECRET_KEY'] = 'enter_your_secret_key'


@APP.route("/", methods=['GET'])
def index():
    pagename = request.args.get('pagename')

    if pagename is not None:
        data = get_user_contribs(pagename)
    else:
        data = None

    return render_template('page_links.html', data=data, \
        pagename=pagename, wikiurl=WIKI_URL)
"""

def get_page_links(pagetitle):
    """ Fetch links via MediaWiki API's links module """
    params = {
        "action": "query",
        "format": "json",
        "titles": pagetitle,
        "prop": "links"
    }

    response = requests.get(url=API_ENDPOINT, params=params)
    data = response.json()
    page = next(iter(data['query']['pages']))
    return data['query']['pages'][page]


result = get_page_links("Alexander Friedmann")
print(result['links'])
# print(type(result['prop']))

# print(data['links'])
"""
if __name__ == '__main__':
    APP.run()
"""