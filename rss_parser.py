import feedparser
import requests
import logging

def parse_rss_feed(feed_url):
    """Parse the RSS feed and return the parsed feed"""
    
    try:
        response = requests.get(feed_url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        content = response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the feed: {e}")
        content = None
    if content:
        return feedparser.parse(content)
    else:
        return None  