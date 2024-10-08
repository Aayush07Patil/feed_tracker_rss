import logging
import pandas as pd
from pymongo import MongoClient
import details

"""Configure logging"""

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("db_cleanup.log"),
                              logging.StreamHandler()])

def collections_list():
    """Get list of collection names to get from datasheet"""
    
    data = pd.read_excel("Datasheet.xlsx",sheet_name="Collections_To_Clear",engine='openpyxl')
    return data["Collection_Name"].tolist()

def drop_collections():
    """Drops specified collections from the MongoDB database"""
    
    collections_to_drop = collections_list()

    try:
        with MongoClient(details.mongo_uri) as client:
            db = client[details.mongo_database]

            for collection_name in collections_to_drop:
                try:
                    db.drop_collection(collection_name)
                    logging.info(f"Collection '{collection_name}' dropped successfully.")
                except Exception as e:
                    logging.error(f"Failed to drop collection '{collection_name}': {e}")
        
    except Exception as e:
        logging.critical(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    drop_collections()