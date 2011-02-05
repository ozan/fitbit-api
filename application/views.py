"""
URL handlers

"""

import datetime
import re
import urllib2

from flask import request, jsonify
from BeautifulSoup import BeautifulStoneSoup

from auth import requires_auth
from utils import parse_date_from_url


@requires_auth
def weight(auth):
    """A history of the user's daily weight"""
    return _historic_graph_data(auth, 'weight')
    
    
@requires_auth
def sleep(auth):
    """A history of the user's daily length of sleep"""
    return _historic_graph_data(auth, 'timeAsleep')
    
    
@requires_auth
def awoken(auth):
    """A history of the number of times awoken each night"""
    return _historic_graph_data(auth, 'timesWokenUp')
    
    
@requires_auth
def mood(auth):
    """A history of the user's daily mood"""
    return _historic_graph_data(auth, 'mood')
    
    
def _historic_graph_data(auth, graph_type):
    """
    Get fitbit data from a historic graph, being a common fitbit graph
    where one datapoint represents data for a single day in the past.
    """
    url = ''.join(["https://www.fitbit.com/graph/getGraphData",
                   "?userId=%(user_id)s",
                   "&type=%(graph_type)s",
                   "&period=%(period)s",
                   "&dateTo=%(date_to)s",
                   "&version=amchart"])

    valid_periods = ['7d', '1m', '3m', '6m', '1y', 'max']
    period = request.args.get('period', '1m')
    if period not in valid_periods:
        return "Valid periods are: %s" % ', '.join(valid_periods)
          
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    paramatized_url = url % {
        'graph_type': graph_type,
        'user_id': auth.user_id,
        'period': period,
        'date_to': request.args.get('dateTo', today)
    }
    
    processor = urllib2.HTTPCookieProcessor(auth.cookies)
    opener = urllib2.build_opener(processor)
    result = opener.open(paramatized_url)
    
    soup = BeautifulStoneSoup(result.read())

    data = [
        {'date': parse_date_from_url(m['url']).ctime(), 
         'value': float(m.text)}
        for m in soup.data.chart.graphs.graph.findChildren()
    ]
    
    return jsonify(results=data)  

