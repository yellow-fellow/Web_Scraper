import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from urllib.parse import urlparse

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open('scrapy').sheet1

# scrapy = sheet.get_all_records()

pp = pprint.PrettyPrinter(indent=4)
# pp.pprint(scrapy)

test = "https://20.detik.com/detikflash/20210401-210401033/pria-yang-tendang-injak-wanita-keturunan-asia-di-as-ditangkap%3Ftag_from%3Dwp_belt_videoTerpopuler"

print(urlparse(test)[1])
print(urlparse(test)[2])
