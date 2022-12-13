import json

def load_sites() -> dict:
    """load pt sites

    Returns:
        dict: site name -> site rss pattern
    """
    return json.load(open('config/sites.json', 'r'))
