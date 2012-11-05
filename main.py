#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import sys
sys.path.insert(0, 'tweepy.zip')
import tweepy
import settings

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.ext.webapp import util

from BeautifulSoup import BeautifulSoup
from model import *

from datetime import *
from dateutil.tz import *
from dateutil.relativedelta import *
import dateutil.parser as dparser
import calendar

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        ACCOUNT = self.request.get('location')

        if ACCOUNT:

            accounts = settings.ACCOUNTS
            account_info = accounts[self.request.get('location')]
        
            ZIPCODE = account_info['zipcode']
            RADIUS = account_info['radius']
            FEED_URL = settings.BASE_URL + '&zip=' + ZIPCODE + '&radius=' + RADIUS 
            CONSUMER_KEY = account_info['consumer_key']
            CONSUMER_SECRET = account_info['consumer_secret']
            TOKEN_KEY = account_info['token_key']
            TOKEN_SECRET = account_info['token_secret']

            self.response.out.write(ACCOUNT)
            self.response.out.write(' ----------- ')

            # Load the data feed in Beautiful Soup.
            result = urlfetch.fetch(FEED_URL)
            soup = BeautifulSoup(result.content)

            # Start scraping. This is pretty ugly.
            name = soup.findAll("td", { "class" : "td2" })
            brand = soup.findAll("td", { "class" : "td3" })
            address = soup.findAll("td", { "class" : "td4" })
            phone = soup.findAll("td", { "class" : "td5" })
            price = soup.findAll("td", { "class" : "td6" })
            time = soup.findAll("td", { "class" : "td7" })

            # Loop through the data. This is really inefficient.
            for i in range(len(name)):

                # Clean up data, again pretty ugly.
                c_name=str(name[i].find(text=True))
                c_brand=str(brand[i].find(text=True))
                c_address=str(address[i]).replace('<br />', ' ').replace('<td class="td4">','').replace('</td>', '').strip()            
                c_phone=str(phone[i].find(text=True)).replace(')', ') ')
                c_price=str(price[i].find(text=True)).replace('&nbsp;', '')
                c_time=str(time[i].find(text=True))

                # Determine threshold. Only iterate for updates in the last 7 minutes.
                # hours is a complete hack because I couldn't figure out the timezone madness.
                threshold = datetime.now()-relativedelta(hours=5, minutes=7)

                if threshold <= dparser.parse(c_time):
                    # Check to see if the latest update has already been logged.
                    stationObj = Station.all().filter("account =", ACCOUNT).filter("time =", c_time).order('-date').fetch(1)

                    # If not, log it and then tweet it.
                    if not stationObj:
                        station = Station(account=ACCOUNT, name=c_name, brand=c_brand, address=c_address, phone=c_phone, price=c_price, time=c_time)
                        station.put()
                        message_body = str(c_time) + ": " + str(c_name) + " (" + str(c_brand) + ") " + str(c_address) + ", " + str(c_phone) + " - " + str(c_price) + " per gallon"

                        # Authenticate this app's credentials via OAuth.
                        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)

                        # Set the credentials that we just verified and passed in.
                        auth.set_access_token(TOKEN_KEY, TOKEN_SECRET)

                        # Authorize with the Twitter API via OAuth.
                        twitterapi = tweepy.API(auth)

                        # Update the user's twitter timeline with the tweeted text.
                        # Limit the length to 140 characters
                        twitterapi.update_status(message_body[:140])
                        self.response.out.write(message_body[:140])
                        self.response.out.write(', ')

                    else:
                        # Wah. No new update.
                        self.response.out.write('update already added, ')

                else: 
                    break

def main():
    application = webapp.WSGIApplication(
                                         [('/', MainPage)],
                                          debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()