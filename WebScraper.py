# In[]
# ----------------------------------------------------------
# Import libraries
import csv
from smart_open import open
from bs4 import BeautifulSoup
import url_parser
import requests
from IPython.display import clear_output, display, Markdown
import ipywidgets as widgets
from google_trans_new import google_translator
import json
import pandas as pd
import re
import os
import boto3
from io import StringIO
import time

translator = google_translator()

# ----------------------------------------------------------
# In[15]


def readCSV(csvFile):

    # ----------------------------------------------------------
    # Select excel sheet as input
    df = pd.read_csv(csvFile)
    # ----------------------------------------------------------
    for site in df.iloc[:, 0]:
        website = ''
        temp_dict = {}

        # while (website != 'exit') and (website != 'translate'):
        try:
            # user_input = input(
            #     "Please ensure that your link has \033[1m https:// \033[0m \n\n")
            website = str(site)  # str(user_input)
            html_text = requests.get(website, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            }).text
            # clear_output(wait=True)
        except:
            pass  # continue

        try:
            soup = BeautifulSoup(html_text, 'lxml')
            meta_tags = soup.find_all('meta')
        except:
            continue

        # ----------------------------------------------------------
        # Pre-fill path with NIL string in the event there is no directory
        temp_dict['topDomain'] = "NIL"
        # ----------------------------------------------------------

        try:
            # ----------------------------------------------------------
            # Get the top domain from the URL
            first_index = site.find('/', 8)
            second_index = site.find('/', first_index + 1)
            temp_dict['topDomain'] = site[8:second_index]
            # ----------------------------------------------------------

        except:
            pass

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

        categories = categories.encode("ascii", "ignore")
        categories = categories.decode("utf-8")
        categories_array = categories.split()
        #categories_array = re.split(', ', categories)
        categories_array = list(dict.fromkeys(categories_array))
        temp_dict['Categories'] = categories_array
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
        keywords = keywords.replace(",", " ")
        keywords = keywords.encode("ascii", "ignore")
        keywords = keywords.decode("utf-8")
        keywords_array = keywords.split()
        #keywords_array = re.split(', ', keywords)
        keywords_array = list(dict.fromkeys(keywords_array))
        temp_dict['Keywords'] = keywords_array
        # ----------------------------------------------------------

        # ----------------------------------------------------------
        # Search for the first "title" metatag and add it into the output
        title = "NIL"
        for tag in meta_tags:
            try:
                if ("title" in tag['property'].lower()):
                    title = tag['content']
                    title = ' '.join(title.split())
                    title = title.encode("ascii", "ignore")
                    title = title.decode("utf-8")
                    break
            except:
                pass
        temp_dict['Title'] = title
        # ----------------------------------------------------------

        # ----------------------------------------------------------
        # Search for the first "description" metatag and add it into the output
        description = "NIL"
        for tag in meta_tags:
            try:
                if ("description" in tag['property'].lower()):
                    description = tag['content']
                    description = ' '.join(description.split())
                    description = description.encode("ascii", "ignore")
                    description = description.decode("utf-8")
                    break
                if ("description" in tag['name'].lower()):
                    description = tag['content']
                    description = ' '.join(description.split())
                    description = description.encode("ascii", "ignore")
                    description = description.decode("utf-8")
                    break
            except:
                pass

        temp_dict['Description'] = description
        # ----------------------------------------------------------

        temp_dict['URL'] = "NIL"
        try:
            # ----------------------------------------------------------
            # Get the full URL
            temp_dict['URL'] = website
            # ----------------------------------------------------------
        except:
            pass

        gt_title = "NIL"
        temp_dict['gt_Title'] = gt_title

        gt_description = "NIL"
        temp_dict['gt_Description'] = gt_description

        try:
            # ----------------------------------------------------------
            # Translate Title & Description
            gt_title = translator.translate(title, lang_tgt='en')
            temp_dict['gt_Title'] = gt_title

            gt_description = translator.translate(description, lang_tgt='en')
            temp_dict['gt_Description'] = gt_description
            # ----------------------------------------------------------
        except:
            pass

        # ----------------------------------------------------------
        # Write data into JSON file
        with open('QA_test.json', 'a') as outfile:
            json.dump(temp_dict, outfile)
            outfile.write('\n')
        # ----------------------------------------------------------


# ----------------------------------------------------------
# Read and combine all CSVs in a bucket
client = boto3.client('s3')
s3_bucket = 'shaohang-development'

'''for key in client.list_objects(Bucket=s3_bucket, Prefix='dmp2')['Contents']:
    value = key['Key']
    try:
        with open(f's3://{s3_bucket}/{value}', 'r') as f:
            readCSV(f)
    except:
        pass'''


start_time = time.time()
with open('QA_test_7.csv') as csvfile:
    readCSV(csvfile)
print("--- %s seconds ---" % (time.time() - start_time))
# ----------------------------------------------------------

# %%
