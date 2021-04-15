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
from datetime import date

translator = google_translator()

# ----------------------------------------------------------
# In[15]

# ----------------------------------------------------------


def ddb_upload(table_name, record):
    # DynamoDB
    dynamodb_client.put_item(TableName=table_name, Item=record)
# ----------------------------------------------------------


def exists(site):
    try:
        response = table.get_item(Key={'url': site})
        item = response['Item']
        return item
    except:
        item = None
        return item


def readCSV(csvFile):

    # ----------------------------------------------------------
    # Select excel sheet as input
    df = pd.read_csv(csvFile)
    # ----------------------------------------------------------
    for site in df.iloc[:, 0]:
        website = ''
        temp_dict = {}

        try:
            website = str(site)  # str(user_input)
            html_text = requests.get(website, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            }).text
        except:
            pass

        try:
            soup = BeautifulSoup(html_text, 'lxml')
            meta_tags = soup.find_all('meta')
        except:
            continue

        if exists(website):
            ddb_dict = exists(website)

            temp_dict['0_top_domain'] = {"S": ddb_dict['0_top_domain']}

            temp_categories = []
            for category in ddb_dict['1_categories']:
                temp_categories.append(category)
            temp_dict['1_categories'] = {"SS": temp_categories}

            temp_keywords = []
            for keyword in ddb_dict['2_keywords']:
                temp_keywords.append(keyword)
            temp_dict['2_keywords'] = {"SS": temp_keywords}

            temp_dict['3_title'] = {"S": ddb_dict['3_title']}
            temp_dict['4_description'] = {"S": ddb_dict['4_description']}
            temp_dict['url'] = {"S": ddb_dict['url']}
            temp_dict['5_gt_title'] = {"S": ddb_dict['5_gt_title']}
            temp_dict['6_gt_description'] = {"S": ddb_dict['6_gt_description']}
            temp_dict['7_date'] = {"S": str(date.today())}

            # ----------------------------------------------------------
            # Write data into JSON file
            # with open('QA_test.json', 'a') as outfile:
            #     json.dump(temp_dict, outfile)
            #     outfile.write('\n')
            # ----------------------------------------------------------
            continue
        else:
            pass

        # ----------------------------------------------------------
        # Pre-fill path with NIL string in the event there is no directory
        temp_dict['0_top_domain'] = "NIL"
        # ----------------------------------------------------------

        try:
            # ----------------------------------------------------------
            # Get the top domain from the URL
            first_index = site.find('/', 8)
            second_index = site.find('/', first_index + 1)
            temp_dict['0_top_domain'] = {"S": site[8:second_index]}
            # ----------------------------------------------------------

        except:
            pass

        # ----------------------------------------------------------
        # Search for the "categories" metatag and add it into the output (In array structure)
        categories = "NIL"
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
        # categories_array = re.split(', ', categories)
        categories_array = list(dict.fromkeys(categories_array))
        temp_dict['1_categories'] = {"SS": categories_array}
        # ----------------------------------------------------------

        # ----------------------------------------------------------
        # Search for the "keywords" metatag and add it into the output (In array structure)
        keywords = "NIL"
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
        # keywords_array = re.split(', ', keywords)
        keywords_array = list(dict.fromkeys(keywords_array))
        temp_dict['2_keywords'] = {"SS": keywords_array}
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
        temp_dict['3_title'] = {"S": title}
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

        temp_dict['4_description'] = {"S": description}
        # ----------------------------------------------------------

        temp_dict['url'] = {"S": "NIL"}
        try:
            # ----------------------------------------------------------
            # Get the full URL
            temp_dict['url'] = {"S": website}
            # ----------------------------------------------------------
        except:
            pass

        gt_title = "NIL"
        temp_dict['5_gt_title'] = {"S": gt_title}

        gt_description = "NIL"
        temp_dict['6_gt_description'] = {"S": gt_description}

        try:
            # ----------------------------------------------------------
            # Translate Title & Description
            gt_title = translator.translate(title, lang_tgt='en')
            temp_dict['5_gt_title'] = {"S": gt_title}

            gt_description = translator.translate(description, lang_tgt='en')
            temp_dict['6_gt_description'] = {"S": gt_description}
            # ----------------------------------------------------------
        except:
            pass

        # ----------------------------------------------------------
        # Date of scraping website
        temp_dict['7_date'] = {"S": str(date.today())}
        # ----------------------------------------------------------

        # ----------------------------------------------------------
        # Write data into JSON file
        # with open('QA_test.json', 'a') as outfile:
        #     json.dump(temp_dict, outfile)
        #     outfile.write('\n')
        # ----------------------------------------------------------

        # ----------------------------------------------------------
        ddb_upload(table_name, temp_dict)
        # ----------------------------------------------------------


if __name__ == "__main__":
    start_time = time.time()

    # ----------------------------------------------------------
    # DynamoDB
    # Client
    dynamodb_client = boto3.client("dynamodb")

    # Table Name
    table_name = 'scrapy'

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Read and combine all CSVs in a bucket & output in a JSON file
    s3_client = boto3.client('s3')
    s3_bucket = 'shaohang-development'

    for key in s3_client.list_objects(Bucket=s3_bucket, Prefix='dmp2')['Contents']:
        value = key['Key']
        try:
            with open(f's3://{s3_bucket}/{value}', 'r') as f:
                readCSV(f)
            s3_client.delete_object(Bucket=s3_bucket, Key=value)
        except:
            pass
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Testing for single CSV file
    # with open('QA_test_7.csv') as csvfile:
    #     readCSV(csvfile)
    # ----------------------------------------------------------
    print("--- %s seconds ---" % (time.time() - start_time))

# %%
