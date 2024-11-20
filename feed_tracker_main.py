import time
import pandas as pd
import requests
import utility
import rss_parser
import mongo_db_connections
import email_notification
import details

def get_categories():
    """Get the categories and keywords we want to ignore from datasheet"""
    
    data = pd.read_excel("Datasheet.xlsx",sheet_name="Categories",engine='openpyxl')
    return data["Categories_to_avoid"].tolist()

def main():
    db_mongodb = mongo_db_connections.connect_to_mongodb(details.mongo_uri, details.mongo_database)

    for feed_name, feed_info in details.feed_urls.items():
        news_feed = rss_parser.parse_rss_feed(feed_info['url'])

        if news_feed is None:
            utility.logging.error(f"Failed to parse RSS Feed for {feed_name}")
            continue  

        
        reversed_entries = reversed(news_feed.entries)

        for entry in reversed_entries:
            title = entry.get('title', 'No Title')
            summary = entry.get('summary', '')
            link = entry.get('link', '')
            
            categories_to_ignore = get_categories()

            match_found = (utility.contains_fuzzy_match(title, categories_to_ignore, 80) or
                           utility.contains_fuzzy_match(summary, categories_to_ignore, 80))
            
            if not match_found:

                if not mongo_db_connections.entry_exists_mongodb(db_mongodb, feed_info['collection'], entry):  # Check if the entry does not exist in MongoDB
                    attachment_data = None
                    attachment_filename = None
                    file_extension = None
                    is_xml = False

                    if feed_info['collection'] != "NSE_Corporate_Actions" and link:
                        
                        try:
                            response = requests.get(link, stream=True, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                            if response.status_code == 200:
                                attachment_data = response.content

                                if link.endswith('.pdf'):
                                    attachment_filename = title + ".pdf"
                                    file_extension = "pdf"
                                elif link.endswith('.xml'):
                                    attachment_filename = title + ".xml"
                                    file_extension = "xml"
                                    is_xml = True 
                                else:
                                    utility.logging.warning(f"Unsupported file format for {link}")
                                    attachment_data = None
                                    attachment_filename = None
                                    file_extension = None

                                utility.logging.info(f"Downloaded {feed_info['collection']} attachment from {link}")
                            else:
                                utility.logging.error(f"Failed to download attachment after retries. URL: {link}")
                                attachment_data = None
                                attachment_filename = None
                        except requests.exceptions.RequestException as e:
                            utility.logging.error(f"Exception occurred while downloading file: {e}. URL: {link}")

                    # Insert into the appropriate MongoDB collection
                    entry_data = mongo_db_connections.insert_entry_mongodb(db_mongodb, feed_info['collection'], entry, attachment_data, file_extension)
                    # Send an email update if the entry is about a tracked stock
                    email_notification.send_all_updates(entry, feed_info['collection'], entry_data, is_xml, attachment_data, attachment_filename, not match_found)

    utility.logging.info('RSS feed entries have been inserted into MongoDB.')


def run_periodically():
    while True:
        # Capture the start time
        start_time = time.time()

        # Run the main function
        main()

        # Calculate the time taken for the function to execute
        elapsed_time = time.time() - start_time

        # Calculate the remaining time until the next minute
        time_to_wait = max(0, 60 - elapsed_time)
        
        #Log waiting time
        utility.logging.info(f"Waiting for {time_to_wait} secs")
        
        # Wait for the remaining time to complete the 1-minute interval
        time.sleep(time_to_wait)
     

if __name__ == "__main__":
  run_periodically()