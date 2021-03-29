"""
    app.py
    Initial code from MediaWiki API Demos (User contributions feed app, https://github.com/wikimedia/mediawiki-api-demos/blob/master/apps/user-contributions-feed/app.py) 
    MIT license
"""

import os as os
os.chdir('/home/teijehidde/Documents/Git Blog and Coding/Project one (wikipedia SNA)/Code')
import pywikibot as pywikibot

site = pywikibot.Site()
page = pywikibot.Page(site, u"War on terror")
text = page.text

print(text)
