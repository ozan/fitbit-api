"""
Authorization logic and decorator

"""

import cookielib
from functools import wraps
import logging
from md5 import md5
import re

from google.appengine.api import memcache

from flask import request, Response
import mechanize


class FitbitAuthorization(object):
    """
    Simple utility for proxying authentication to http://fitbit.com
    """
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    @property
    def user_id(self):
        data = self._get_data()
        return data and data['user_id'] or None
        
    @property
    def cookies(self):
        data = self._get_data()
        return data and data['cookies'] or None
        
    def is_valid(self):
        """
        Check to see if the username and password provided is valid. We
        consider the pair to be valid if we have cookies for the pair.
        """
        return bool(self.cookies)
        
    def _get_data(self):
        """
        Attempt to retrieve auth data from cache, otherwise fetch from fitbit
        """
        data = memcache.get(self._get_cache_key())
        if data is not None:
            return data
        
        # Cache miss, so fetch auth data from fitbit
        data = self._fetch_data_from_fitbit()
        if data is None:
            return None
            
        if not memcache.add(self._get_cache_key(), data, 60 * 60 * 24):
            logging.error("Memcache set failed.")
            
        return data
        
    def _fetch_data_from_fitbit(self):
        """
        Fetch useful authentication data from fitbit.
        
        Using mechanize, we log in to http://fitbit.com, stashing any cookies
        we are sent. We then also extract the user's id.
        """
        br = mechanize.Browser()

        br.open("http://www.fitbit.com/login")
        br.select_form(name="login")
        br['email'] = self.username
        br['password'] = self.password
        br['rememberMe'] = ['true']
        response = br.submit()
        
        cj = br._ua_handlers['_cookies'].cookiejar
        # If the 'u' cookie is not set, login was invalid
        if 'u' not in map(lambda c: c.name, cj):
            return None
        
        # Manually set the 'uid' cookie based on information available in 
        # the 'u' cookie. Appengine strips some headers from our request 
        # (such as 'Host') which results in fitbit not sending this 
        # particular cookie, for some reason.
        cookie_values = dict(map(lambda c: (c.name, c.value), cj))
        uid = cookie_values['u'].split('|')[1]    
        cj.set_cookie(self._create_cookie('uid', uid))
        
        # We will also need the fitbit user id, which is unfortunately not 
        # set in a cookie, so extract it from the logged-in user's homepage.
        doc = br.open("http://www.fitbit.com").get_data()
        res = re.search('\/user\/(\w+)', doc)
        user_id = res.groups()[0]

        return {'cookies': cj, 'user_id': user_id}
        
    def _get_cache_key(self):
        return md5("%s:%s" % (self.username, self.password)).hexdigest()
        
    def _create_cookie(self, name, value):
        return cookielib.Cookie(version=0, name=name, value=value, 
            port=None, port_specified=False, domain='www.fitbit.com', 
            domain_specified=False, domain_initial_dot=False, path='/', 
            path_specified=True, secure=False, expires=None, discard=True, 
            comment=None, comment_url=None, rest={'HttpOnly': None}, 
            rfc2109=False)
            
        
class Http401(Response):
    def __init__(self, msg, *args, **kwargs):
        return super(Http401, self).__init__(msg, 401, *args, **kwargs)


def requires_auth(func):
    """
    A simple decorator for requiring the user's fitbit username and password.
    This should be used on any function which acts as an API method.
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return Http401('You must provide your fitbit username '
                            'and password')      
                                  
        fitbit_auth = FitbitAuthorization(auth.username, auth.password)
        if not fitbit_auth.is_valid():
            return Http401('The username and password you provided '
                           'were not valid')
                           
        return func(fitbit_auth, *args, **kwargs)
    return decorated
