import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open('scrapy').sheet1

# scrapy = sheet.get_all_records()

# pp = pprint.PrettyPrinter()
# pp.pprint(scrapy)


row = ["I'm", "inserting", "a", "row", "into",
       "a,", "Spreadsheet", "with", "Python"]
index = 1
sheet.insert_row(row, index)
