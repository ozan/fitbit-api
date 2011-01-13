"""
Utility functions

"""

import datetime


def parse_date_from_url(url):
    """
    Parse the date from a fitbit url.
    
    eg. /sleep/2010/01/03
    """
    parts = [int(p) for p in url.split('/')[2:]]
    return datetime.date(*parts)
