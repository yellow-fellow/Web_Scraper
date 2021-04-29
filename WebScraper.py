# In[]
# ----------------------------------------------------------
# Import libraries
import csv
from smart_open import open
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
from google_trans_new import google_translator
import json
import pandas as pd
import boto3
import time
from datetime import date
import gspread
from oauth2client.service_account import ServiceAccountCredentials

translator = google_translator()
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope)
client = gspread.authorize(creds)
sheet = client.open('scrapy').sheet1

segments_list = ['female', 'avid-news-readers', 'celebrity', 'avid-political-news-readers', 'auto-enthusiasts', 'motocycle-enthusiasts', 'sports-fans', 'football-enthusiasts',
                 'family', 'parenting', 'mobile-enthusiasts', 'consumer-electronics', 'business-professionals', 'beauty', 'fashion', 'movie', 'kids', 'education', 'shoppers']

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


def ct_exists(temp_dict):
    try:
        response = ct_table.get_item(
            Key={'domain': temp_dict['0_domain']['S'], 'path': temp_dict['1_path']['S']})
        ct_item = response['Item']
        return (ct_item['segments'])
    except:
        ct_item = None


def excel_upload(temp_dict):
    excel_array = []

    for value in temp_dict.values():
        try:
            excel_array.append(value['S'])
        except:
            temp_str = ""
            for item in value['SS']:
                temp_str += item
                temp_str += ', '
            excel_array.append(temp_str)

    sheet.append_row(excel_array)
    excel_row = sheet.find(temp_dict['url']['S']).row
    try:
        existing_segments = ct_exists(temp_dict)
        for segment in existing_segments:
            positional_index = segments_list.index(segment)
            sheet.update_cell(excel_row, 11 + positional_index, True)
    except:
        pass


def readCSV(csvFile, user_input):

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

            response = requests.get(website, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
            }).status_code

            if (response == 404):
                print(f'This <{website}> is invalid! ')
                continue
        except:
            pass

        try:
            soup = BeautifulSoup(html_text, 'lxml')
            meta_tags = soup.find_all('meta')
        except:
            continue

        if exists(website):
            ddb_dict = exists(website)

            temp_dict['0_domain'] = {"S": ddb_dict['0_domain']}
            temp_dict['1_path'] = {"S": ddb_dict['1_path']}

            temp_categories = []
            for category in ddb_dict['2_categories']:
                temp_categories.append(category)
            temp_dict['2_categories'] = {"SS": temp_categories}

            temp_keywords = []
            for keyword in ddb_dict['3_keywords']:
                temp_keywords.append(keyword)
            temp_dict['3_keywords'] = {"SS": temp_keywords}

            temp_dict['4_title'] = {"S": ddb_dict['4_title']}
            temp_dict['5_description'] = {"S": ddb_dict['5_description']}
            temp_dict['url'] = {"S": ddb_dict['url']}
            temp_dict['6_gt_title'] = {"S": ddb_dict['6_gt_title']}
            temp_dict['7_gt_description'] = {"S": ddb_dict['7_gt_description']}
            temp_dict['8_date'] = {"S": str(date.today())}

            if (user_input == "1"):
                # ----------------------------------------------------------
                # Write data into an array to push to google sheets
                excel_upload(temp_dict)
                # ----------------------------------------------------------
            else:
                print(json.dumps(temp_dict, sort_keys=True, indent=4))
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
        # Pre-fill domain with NIL string in the event there is no directory
        temp_dict['0_domain'] = "NIL"
        # ----------------------------------------------------------

        try:
            # ----------------------------------------------------------
            # Get the domain from the URL
            domain = urlparse(site)[1]
            temp_dict['0_domain'] = {"S": domain}
            # ----------------------------------------------------------

        except:
            pass

        # ----------------------------------------------------------

        # ----------------------------------------------------------
        # Pre-fill path with NIL string in the event there is no directory
        temp_dict['1_path'] = "NIL"
        # ----------------------------------------------------------

        try:
            # ----------------------------------------------------------
            # Get the domain from the URL
            path = urlparse(site)[2][0: urlparse(site)[2].find('/', 1)]
            temp_dict['1_path'] = {"S": path}
            # ----------------------------------------------------------

        except:
            pass

        # ----------------------------------------------------------

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
        temp_dict['2_categories'] = {"SS": categories_array}
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
        temp_dict['3_keywords'] = {"SS": keywords_array}
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
        temp_dict['4_title'] = {"S": title}
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

        temp_dict['5_description'] = {"S": description}
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
        temp_dict['6_gt_title'] = {"S": gt_title}

        gt_description = "NIL"
        temp_dict['7_gt_description'] = {"S": gt_description}

        try:
            # ----------------------------------------------------------
            # Translate Title & Description
            gt_title = translator.translate(title, lang_tgt='en')
            temp_dict['6_gt_title'] = {"S": gt_title}

            gt_description = translator.translate(description, lang_tgt='en')
            temp_dict['7_gt_description'] = {"S": gt_description}
            # ----------------------------------------------------------
        except:
            pass

        # ----------------------------------------------------------
        # Date of scraping website
        temp_dict['8_date'] = {"S": str(date.today())}
        # ----------------------------------------------------------

        if (user_input == "1"):
            # ----------------------------------------------------------
            # Write data into an array to push to google sheets
            excel_upload(temp_dict)
            # ----------------------------------------------------------
            # ----------------------------------------------------------
            ddb_upload(table_name, temp_dict)
            # ----------------------------------------------------------
        else:
            print(json.dumps(temp_dict, sort_keys=True, indent=4))

        # ----------------------------------------------------------
        # Write data into JSON file
        # with open('QA_test.json', 'a') as outfile:
        #     json.dump(temp_dict, outfile)
        #     outfile.write('\n')
        # ----------------------------------------------------------


if __name__ == "__main__":
    user_input = input(
        "Select 1 to upload data onto Google Spreadsheet. Select 2 to print out in console. \n")
    start_time = time.time()

    # ----------------------------------------------------------
    # DynamoDB (Scrapy Table)
    # Client
    dynamodb_client = boto3.client("dynamodb")

    # Table Name
    table_name = 'scrapy'
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # DynamoDB (Contextual Targeting Table)
    # Client

    # Table Name
    ct_table_name = 'contextual-targeting'
    ct_table = dynamodb.Table(ct_table_name)
    # ----------------------------------------------------------

    # ----------------------------------------------------------
    # Read and combine all CSVs in a bucket & output in a JSON file
    s3_client = boto3.client('s3')
    s3_bucket = 'shaohang-development'

    for key in s3_client.list_objects(Bucket=s3_bucket, Prefix='dmp2')['Contents']:
        value = key['Key']
        try:
            with open(f's3://{s3_bucket}/{value}', 'r') as f:
                readCSV(f, user_input)
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
