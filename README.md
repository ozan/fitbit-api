# Unofficial JSON data API for http://fitbit.com

Fitbit doesn't provide an API at this stage, so I'm throwing one together for your convenience (well, mostly my convenience). It runs at http://fitbitapi.appspot.com, which you should feel free to make queries to... the code is up here mostly to show you that I'm not storing your credentials. You can also clone this repo and run on your appengine instance if you so choose.

To be clear, this is an API, not a client. You do not need to be using Python, simply make a query using your HTTP client of choice, and expect JSON in response. Behind the scenes, it uses Python mechanize to log in on your behalf and store fitbit cookies, then accesses the xml data feeds that the fitbit front end uses for its graphs.

## Example usage:

    curl -u your_email:your_password http://fitbitapi.appspot.com/weight
    
## Example response:

    {
      "results": [
        {
          "date": "Tue Dec 14 00:00:00 2010", 
          "value": 175.0
        }, 
        {
          "date": "Wed Dec 15 00:00:00 2010", 
          "value": 176.0
        }, 
        {
          "date": "Thu Dec 16 00:00:00 2010", 
          "value": 174.0
        }
        
        ...
        
      ]
    }
    
## Endpoints currently supported:

- /weight
- /mood
- /sleep

You can also use the following GET parameters for any endpoint:

- `period` (default '3m'): the period of time, looking backwards, to retrieve data for, with options being '7d', '1m', '3m', '6m', '1y' and 'max'. Please note that shorter periods consistently return daily data, but longer periods may return data of lower resolution (for instance one datapoint per month)
- `dateTo` (defaults to today's date): the date, in `%Y-%m-%d` form, to seek back from

## Stability and comprehensiveness:

I'm going to develop on the assumption that I'm the only person using this, so I'll likely only add functionality as I need it, and make backwards-incompatible changes at will. If you decide to use this API for an application, please let me know and I'll start releasing discrete numbered versions.

