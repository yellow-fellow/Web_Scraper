# Web_Scraper

This is a web scraper script that scrapes content from all the meta tags in a given URL. It takes in a CSV of URLs from a designated S3 bucket, and outputs the relevant content on a public Google Spreadsheet, as well as DynamoDB tables. The purpose of this script is to hasten the process of conducting Quality Assurance (QA).

## Packages
- pip install python-csv
- pip install smart-open
- pip install bs4
- pip install urllib3
- pip install requests
- pip install google-trans-new
- pip install jsonlib
- pip install pandas
- pip install boto3
- pip install times
- pip install DateTime
- pip install gspread
- pip install oauth2client

## Required Keys
- Google Spreadsheet authentication
- AWS authentication

## Operating Instructions
Firstly, please ensure that the URLs in CSVs are contained in the first column ONLY. 
Secondly, upload the CSVs into the designated S3 bucket directory. Please note that after reading through the CSVs, they will automatically be removed from the S3 bucket directory in order to not re-read the same CSV files. On this note, ALL CSVs uploaded inside the directory will be read through, as long as it is a file with .csv extension.
Lastly, please ensure all rows except the header row on the Google Spreadsheet are cleared, in order for the script to append the scraped records nicely onto the sheet.

