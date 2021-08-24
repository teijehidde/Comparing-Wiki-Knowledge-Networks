"""
CWKN is an application that can be used to compare networks of Wikipedia page links about one topic across multiple languages. 
Variations in network structure reflect different understandings of social concepts - such as 'secularism', 'gender' or 'terrorism' - between language groups.

The app consists of two parts: 
- The current file is fetch_data.py: a simple command line app to call the Wikimedia API. The app comes with a preloaded data set, but fetch_data.py can be used to add additional topics to this data set. 
- The second part is app.py: a Dash powered app to visualise and compare Wikipedia page links networks. 

The app is under active development. 
Please note that this is my first python script. Comments, feature suggestions or bug reports are welcome.
"""

#-------- loading packages --------#
import time 
import pandas as pd
import init_wiki_api as iwa

#-------- config --------#
languages = ["ar", "ja", "es", "zh", "fr", "ru"]
path = "/home/teijehidde/Documents/Git Blog and Coding/data/"
data_file = "network_data.json"

#-------- function to download wikinetwork in multple languages. Call functions in init_wiki_api --------#
def downloadMultiLangWikiNetwork(node_title, original_lang = 'en', additional_langs = languages): # or: 'available_langs'
    network_data_df = iwa.downloadWikiNetwork(node_title=node_title, lang=original_lang)
    available_langs = network_data_df.loc[network_data_df['ego'] == True]['langlinks'].values.tolist()[0]

    if additional_langs == []:
        print('The wikipedia page is available in the following languages:')         
        print(available_langs)
    
    else:
        for item in available_langs: 
            if item['lang'] in additional_langs:
                network_data_df_additional = iwa.downloadWikiNetwork(node_title = item['*'], lang = item['lang'])
                network_data_df = pd.concat([network_data_df, network_data_df_additional], ignore_index=True, sort=False)
                
    try: 
        network_data_saved = pd.read_json((path + data_file), orient='split')
    except:
        network_data_saved = None
    network_data_df = pd.concat([network_data_df, network_data_saved], ignore_index=True, sort=False)
    network_data_df = network_data_df.loc[network_data_df.astype(str).drop_duplicates(subset=['title', 'lang', 'ego'], keep = 'first').index].reset_index(drop=True)
    network_data_df.to_json((path + data_file), orient='split')
    print("Download of network and additional languages finished. Returning to main menu...") 
    time.sleep(5) 

#-------- Runtime --------#
if __name__ == '__main__':
    while True: 
        print ('This command line tool downloads pagelink data from the chosen topic in English, Arabic, Japanese, Spanish, Chinese, French and Russian - if available.')
        input_var = input("Please type a topic to download (or Q to quit): ")
        print ("You entered " + input_var)
        if input_var.lower() != 'q':
            try: 
                downloadMultiLangWikiNetwork(input_var[0].upper() + input_var[1:])
            except: 
                print ('Soemthing went wrong. Please try again.')
        else: 
            break

#-------- End --------#