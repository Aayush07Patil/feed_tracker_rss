import logging
import xml.etree.ElementTree as ET
from rapidfuzz import fuzz

"""Logging configuration"""

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("app.log"),
                              logging.StreamHandler()])

def extract_field_after(text, keyword, separator):
    """Extract the text after the keyword until the next separator"""
    
    try:
        if keyword in text:
            return text.split(keyword, 1)[1].split(separator)[0].strip() or None
    except Exception as e:
        logging.error(f"Error extracting field after {keyword}: {e}")
    return None

def extract_field_before(text, keyword):
    """Extract the text before the keyword"""
    
    try:
        if keyword in text:
            return text.split(keyword, 1)[0].strip() or None
    except Exception as e:
        logging.error(f"Error extracting field before {keyword}: {e}")
    return None

def extract_field_between(text, keyword1, keyword2):
    """Extract the text between two keywords"""
    
    try:
        if keyword1 in text:
            split_text = text.split(keyword1, 1)[1]
            separator = keyword2 if keyword2 in split_text else '|'
            return split_text.split(separator, 1)[0].strip() or None
    except Exception as e:
        logging.error(f"Error extracting field between {keyword1} and {keyword2}: {e}")
    return None

def contains_fuzzy_match(text, keywords, threshold):
    """Check if the text contains any of the keywords using fuzzy matching. Returns True if a match exceeds the threshold."""
    
    if not text:
        return False
    try:
        return any(fuzz.partial_ratio(text.lower(), keyword.lower()) >= threshold for keyword in keywords)
    except Exception as e:
        logging.error(f"Error performing fuzzy match: {e}")
        return False


def extract_fields_from_xml_content(xml_content):
    """Extract fields from XML content and return as a formatted string"""
    
    try:
        root = ET.fromstring(xml_content)
        fields = {}
        for elem in root.iter():
            tag = elem.tag.split('}', 1)[-1]  
            if tag:
                fields[tag] = elem.text.strip() if elem.text else ''
        
        if not fields:
            logging.warning("No fields were extracted from the XML content.")
            return None
        
        output = "Extracted fields:\n" + "\n".join(f"{field} : {value}" for field, value in fields.items())
        return output
    except ET.ParseError as e:
        logging.error(f"XML parsing failed: {e}")
        return None
    except Exception as e:
        logging.error(f"Error extracting fields from XML: {e}")
        return None