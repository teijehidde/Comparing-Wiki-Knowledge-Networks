# Setup packages and file paths 
import requests
import time 
import pandas as pd
import init_wiki_api as iwa

# Config
path = "/home/teijehidde/Documents/Git Blog and Coding/data/"
data_file = "network_data.json"

# Function B: Downloading multiple languages of one topic and saving them to json/panda file. 
def downloadMultiLangWikiNetwork(node_title, original_lang = 'en', additional_langs = ["ar", "ja", "es", "zh", "fr", "ru"]): # or: 'available_langs'
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

# NB: RUNTIME 
if __name__ == '__main__':
    input_var = input("Please type a topic to download: ")
    print ("you entered " + input_var) 
    downloadMultiLangWikiNetwork(input_var[0].upper() + input_var[1:])
    ## write a small func to check if a str has char like "" ' / | 
# END 