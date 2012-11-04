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
from google.appengine.api import mail

from BeautifulSoup import BeautifulSoup
from model import *

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        # Load the data feed in Beautiful Soup.
        result = urlfetch.fetch(settings.FEED_URL)
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

            # Check to see if the latest update has already been logged.
            stationObj = Station.all().filter("time =", c_time).order('-date').fetch(1)

            # If not, log it and then tweet it.
            if not stationObj:
                station = Station(name=c_name, brand=c_brand, address=c_address, phone=c_phone, price=c_price, time=c_time)
                station.put()
                message_body = str(c_time) + ": " + str(c_name) + " (" + str(c_brand) + ") " + str(c_address) + ", " + str(c_phone) + " - " + str(c_price) + " per gallon"

                # Authenticate this app's credentials via OAuth.
                auth = tweepy.OAuthHandler(settings.CONSUMER_KEY, settings.CONSUMER_SECRET)

                # Set the credentials that we just verified and passed in.
                auth.set_access_token(settings.TOKEN_KEY, settings.TOKEN_SECRET)

                # Authorize with the Twitter API via OAuth.
                twitterapi = tweepy.API(auth)

                # Update the user's twitter timeline with the tweeted text.
                twitterapi.update_status(message_body)
                self.response.out.write(message_body)

            else:
                # Wah. No new update.
                self.response.out.write(' none ')

application = webapp.WSGIApplication([('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()