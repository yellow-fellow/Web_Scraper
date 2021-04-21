import gspread
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import urlparse

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope)
client = gspread.authorize(creds)

sheet = client.open('scrapy').sheet1

# scrapy = sheet.get_all_records()

print(sheet.find('https://20.detik.com/detikflash/20210401-210401033/pria-yang-tendang-injak-wanita-keturunan-asia-di-as-ditangkap%3Ftag_from%3Dwp_belt_videoTerpopuler').col)

temp_list = ['female', 'celebrity']

counter = 11

# for segment in temp_list:
#     if segment in temp_list:
#         sheet.update_cell(2, counter, True)
#         counter += 1
