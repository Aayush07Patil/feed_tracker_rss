import logging
from pymongo import MongoClient
import gridfs
import utility

"""Configure logging"""

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log"),
                              logging.StreamHandler()])

def connect_to_mongodb(uri, database_name):
    """Connect to MongoDB and return the database"""
    
    try:
        client = MongoClient(uri)
        db = client[database_name]
        return db
    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")
        raise

def save_attachment(db, attachment_data, title, file_extension):
    """Save attachment data using GridFS and return the file ID"""
    try:
        fs = gridfs.GridFS(db)
        filename = f"{title}.{file_extension}"
        file_id = fs.put(attachment_data, filename=filename)
        logging.info(f"Attachment {filename} saved in GridFS with ID: {file_id}")
        return file_id
    except Exception as e:
        logging.error(f"Error saving attachment: {e}")
        raise

def extract_entry_data(collection_name, entry):
    """Extract relevant data from the RSS feed entry based on collection"""
    
    try:
        summary = entry.get('summary', '')
        entry_data = {
            "Title": entry.get('title', 'No Title'),
            "Published": entry.get('published', 'Unknown Date'),
            "Link": entry.get('link', '')
        }
        
        if collection_name == "NSE_Company_Announcements":
            entry_data.update({
                "Category": utility.extract_field_after(summary, "SUBJECT:", "|"),
                "Summary": utility.extract_field_before(summary, "|SUBJECT:")
            })

        elif collection_name == "NSE_Board_Meetings":
            entry_data.update({
                "Purpose": utility.extract_field_before(summary, "|Meeting Date:"),
                "Meeting date": utility.extract_field_after(summary, "Meeting Date:", "|")
            })

        elif collection_name == "NSE_Corporate_Actions":
            entry_data.update({
                "Series": utility.extract_field_after(summary, "SERIES:", "|"),
                "Purpose": utility.extract_field_between(summary, "PURPOSE:", " -"),
                "Face value": utility.extract_field_after(summary, "FACE VALUE:", "|"),
                "Record date": utility.extract_field_after(summary, "RECORD DATE:", "|"),
                "Book closure start date": utility.extract_field_after(summary, "BOOK CLOSURE START DATE:", "|"),
                "Book closure end date": utility.extract_field_after(summary, "BOOK CLOSURE END DATE:", "|")
            })

        elif collection_name == "NSE_Financial_Results":
            entry_data.update({
                "Relating to": utility.extract_field_after(summary, "RELATING TO:", "|"),
                "Audit Status": utility.extract_field_after(summary, "AUDITED/UNAUDITED:", "|"),
                "Cumulative Or Not": utility.extract_field_after(summary, "CUMULATIVE/NON-CUMULATIVE:", "|"),
                "Consolidated Or Not": utility.extract_field_after(summary, "CONSOLIDATED/NON-CONSOLIDATED:", "|"),
                "IND AS Or Not": utility.extract_field_after(summary, "IND AS/ NON IND AS:", "|"),
                "Period": utility.extract_field_after(summary, "PERIOD:", "|"),
                "Period Ended": utility.extract_field_after(summary, "PERIOD ENDED:", "|")
            })

        return entry_data

    except Exception as e:
        logging.error(f"Error extracting entry data: {e}")
        raise


def insert_entry_mongodb(db, collection_name, entry, attachment_data=None, file_extension=None):
    """Insert an RSS feed entry into the specified MongoDB collection"""
    
    try:
        collection = db[collection_name]
        entry_data = extract_entry_data(collection_name, entry)

        # Handle attachment if provided
        if attachment_data and file_extension:
            file_id = save_attachment(db, attachment_data, entry_data["Title"], file_extension)
            entry_data["Attachment_file_id"] = file_id
        
        collection.insert_one(entry_data)
        logging.info(f"Inserted entry into {collection_name}: {entry_data['Title']}")
        return entry_data

    except Exception as e:
        logging.error(f"Failed to insert entry into {collection_name}: {e}")
        raise


def entry_exists_mongodb(db, collection_name, entry):
    """Check if an entry with the given title, published date, and link already exists in the collection"""
    
    try:
        collection = db[collection_name]
        query = {
            "Title": entry.get('title', ''),
            "Published": entry.get('published', ''),
            "Link": entry.get('link', '')
        }

        exists = collection.count_documents(query) > 0
        return exists
    except Exception as e:
        logging.error(f"Error checking entry existence in {collection_name}: {e}")
        raise