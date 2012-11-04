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

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.api import mail

from BeautifulSoup import BeautifulSoup
from model import *

class MainPage(webapp.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'

        url = 'http://rrtexternalweb.wrightexpress.com/neo_ww/site_locator/list.action?sortByValue=LAST_TRAN_TIME&sortDirection=DESCENDING&latitude=40.6945036&longitude=-73.9565551&mapType=Hybrid&mapZoom=12&sorting=true&address=&city=&state=&zip=11205&fuelType=Unleaded+Regular&radius=5'
        result = urlfetch.fetch(url)
        soup = BeautifulSoup(result.content)

        name = soup.find("td", { "class" : "td2" })
        brand = soup.find("td", { "class" : "td3" })
        address = soup.find("td", { "class" : "td4" })
        phone = soup.find("td", { "class" : "td5" })
        price = soup.find("td", { "class" : "td6" })
        time = soup.find("td", { "class" : "td7" })

        c_name=str(name.find(text=True))
        c_brand=str(brand.find(text=True))
        c_address=str(address).replace('<br />', ' ').replace('<td class="td4">','').replace('</td>', '').strip()            
        c_phone=str(phone.find(text=True))
        c_price=str(price.find(text=True))
        c_time=str(time.find(text=True))

        stationObj = Station.all().filter("time =", c_time).order('-date').fetch(1)
        if not stationObj:
            station = Station(name=c_name, brand=c_brand, address=c_address, phone=c_phone, price=c_price, time=c_time)
            station.put()
            message_body = str(c_time) + ": " + str(c_name) + " (" + str(c_brand) + ") " + str(c_address) + ", " + str(c_phone)

            # these tokens are necessary for user authentication
            # (created within the twitter developer API pages)
            consumer_key = "xxxxx"
            consumer_secret = "xxxxx"
            token_key = "xxxxx"
            token_secret = "xxxxx"

            # Here we authenticate this app's credentials via OAuth
            auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

            # Here we set the credentials that we just verified and passed in.
            auth.set_access_token(token_key, token_secret)

            # Here we authorize with the Twitter API via OAuth
            twitterapi = tweepy.API(auth)

            # Here we update the user's twitter timeline with the tweeted text.
            twitterapi.update_status(message_body)

            # post a new status
            # twitter API docs: https://dev.twitter.com/docs/api/1/post/statuses/update
            print "updated status: %s" % message_body
            
            # Now we fetch the user information and redirect the user to their twitter
            # username page so that they can see their tweet worked.
            user = twitterapi.me()
            self.redirect('http://www.twitter.com/%s' % user.screen_name)
        else:
           self.response.out.write('nothing new')

application = webapp.WSGIApplication([('/', MainPage)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()