# In[]
# ----------------------------------------------------------
# Import libraries

from bs4 import BeautifulSoup
import url_parser
import requests
from IPython.display import clear_output, display, Markdown
import ipywidgets as widgets
from google_trans_new import google_translator
import json
import pandas as pd

translator = google_translator()

# ----------------------------------------------------------
# In[15]

# ----------------------------------------------------------
# Select excel sheet as input
df = pd.read_excel('QA_test.xlsx')
# ----------------------------------------------------------
for site in df.iloc[:, 0]:
    website = ''
    stored_text = ''
    user_input = ''
    temp_dict = {}
    tags_dict = {}
    tags_array = []

    # while (website != 'exit') and (website != 'translate'):
    try:
        # user_input = input(
        #     "Please ensure that your link has \033[1m https:// \033[0m \n\n")
        website = str(site)  # str(user_input)
        temp_dict['domain'] = url_parser.parse_url(site)['domain']
        temp_dict['URL'] = website
        html_text = requests.get(website, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
        }).text
        clear_output(wait=True)
    except:
        pass  # continue

    try:
        soup = BeautifulSoup(html_text, 'lxml')
        meta_tags = soup.find_all('meta')
    except:
        continue

    #exclusion_list = ['https://','width','charset','image','jpeg','index','@detikcom','max-snippet','wordpress','chrome=1','ie=edge','2021','rgb','2020','singlepage','app-id','desktop','article','.org']

    # <meta property="og:title" content="The faces of the #SAF44">
    # Targetting meta-property tags
    property_list = ['description', 'title', 'keyword',
                     'categories', 'category', 'article:section']

    # ----------------------------------------------------------
    # Pre-fill path with NIL string in the event there is no directory
    temp_dict['Full-URL-Path'] = "NIL"
    temp_dict['First-URL-Directory'] = "NIL"
    temp_dict['Second-URL-Directory'] = "NIL"
    # ----------------------------------------------------------

    try:
        # ----------------------------------------------------------
        # Get the full-URL path from the URL
        print('\n\033[1mFULL-URL-DIRECTORY\033[0m')
        print(url_parser.parse_url(site)['path'])
        temp_dict['Full-URL-Path'] = url_parser.parse_url(site)['path']
        # ----------------------------------------------------------

        # ----------------------------------------------------------
        # Get first directory from URL
        print('\n\033[1mFIRST-URL-DIRECTORY\033[0m')
        category = url_parser.parse_url(site)['dir']
        category = category[1:-1]
        first_directory = category.split('/')[0]
        print(first_directory)
        temp_dict['First-URL-Directory'] = first_directory
        # ----------------------------------------------------------

        # ----------------------------------------------------------
        # Get second directory from URL
        print('\n\033[1mSECOND-URL-DIRECTORY\033[0m')
        second_directory = category.split('/')[1]
        print(second_directory)
        temp_dict['Second-URL-Directory'] = second_directory
        # ----------------------------------------------------------

    except:
        pass

    # ----------------------------------------------------------
    # Search for the first "title" metatag and add it into the output
    title = "NIL"
    for tag in meta_tags:
        try:
            if ("title" in tag['property'].lower()):
                title = tag['content']
                break
        except:
            pass
    temp_dict['Title'] = title
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Search for the "keywords" metatag and add it into the output (In array structure)
    keywords = ""
    for tag in meta_tags:
        try:
            if ("keyword" in tag['property'].lower()):
                keywords += " " + tag['content']
        except:
            pass
        try:
            if ("keyword" in tag['name'].lower()):
                keywords += " " + tag['content']
        except:
            pass

    # See if can use css-selector instead.
    # a_tags = soup.find_all("div > a")
    # may be lazy loading
    div_tags = soup.find_all("div")
    for div_tag in div_tags:
        try:
            a_tags = div_tag.find_all("a", {"class": "tag-detail"})
            for a in a_tags:
                keywords += " " + a.text
        except:
            pass
    keywords_array = keywords.split()
    temp_dict['Keywords'] = keywords_array
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Search for the "categories" metatag and add it into the output (In array structure)
    categories = ""
    for tag in meta_tags:
        try:
            if ("category" in tag['property'].lower()):
                categories += " " + tag['content']
        except:
            pass
        try:
            if ("categories" in tag['property'].lower()):
                categories += " " + tag['content']
        except:
            pass
        try:
            if ("article:section" in tag['property'].lower()):
                categories += " " + tag['content']
        except:
            pass
        try:
            if ("category" in tag['name'].lower()):
                categories += " " + tag['content']
        except:
            pass
        try:
            if ("categories" in tag['name'].lower()):
                categories += " " + tag['content']
        except:
            pass
    categories_array = categories.split()
    temp_dict['Categories'] = categories_array
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Search for the first "description" metatag and add it into the output
    description = "NIL"
    for tag in meta_tags:
        try:
            if ("description" in tag['property'].lower()):
                description = tag['content']
                break
            if ("description" in tag['name'].lower()):
                description = tag['content']
                break
        except:
            pass
    temp_dict['Description'] = description
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Write data into JSON file
    with open('QA_test.json', 'a') as outfile:
        json.dump(temp_dict, outfile)
        outfile.write('\n')
    # ----------------------------------------------------------

    if (website == 'translate'):
        print("\n\033[1mTRANSLATED-TEXT\033[0m")
        translate_text = translator.translate(stored_text, lang_tgt='en')
        print('\n' + translate_text)

# %%
requests.get("https://bolastylo.bolasport.com/read", headers={
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
})
# %%
