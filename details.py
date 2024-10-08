import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

"""Email service details"""

email_sender = "update.stock.news.pp@gmail.com"
password_email_sender = os.getenv('EMAIL_SENDER_PASSWORD')

"""MongoDB connection details"""

mongo_uri = "mongodb://localhost:27017/"
mongo_database = "STOCK_TRACKER"

"""Keyword check fuzzy logic"""

keywords = ["mutual funds", "ETF", "MF", "FTP","Declaration of NAV"]
threshold = 80 

"""Feed URLs being tracked"""

feed_urls = {
    "NSE_Company_Announcements": {
        "url": "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml",
        "collection": "NSE_Company_Announcements"
    },
     "NSE_Financial_Results": {
        "url": "https://nsearchives.nseindia.com/content/RSS/Financial_Results.xml",
        "collection": "NSE_Financial_Results"
    },
    "NSE_Board_Mettings": {
        "url": "https://nsearchives.nseindia.com/content/RSS/Board_Meetings.xml",
        "collection": "NSE_Board_Meetings"
    },
    "NSE_Corporate_Actions": {
        "url": "https://nsearchives.nseindia.com/content/RSS/Corporate_action.xml",
        "collection": "NSE_Corporate_Actions"
    }
}

