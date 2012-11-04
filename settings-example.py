# Rename to settings.py

# Data source is wrightexpress.com
# Take zipcode as input as well a radius in miles
ZIPCODE = '11201'
RADIUS = '10'
BASE_URL = 'http://rrtexternalweb.wrightexpress.com/neo_ww/site_locator/list.action?sortByValue=LAST_TRAN_TIME&sortDirection=DESCENDING&latitude=40.6945036&longitude=-73.9565551&mapType=Hybrid&mapZoom=12&sorting=true&fuelType=Unleaded+Regular&'
FEED_URL = BASE_URL + '&zip=' + ZIPCODE + '&radius=' + RADIUS 

# Twitter API / Auth
# these tokens are necessary for user authentication
# (created within the twitter developer API pages)
CONSUMER_KEY = "xxxxxxxxxxxxxxxx"
CONSUMER_SECRET = "xxxxxxxxxxxxxxxx"
TOKEN_KEY = "xxxxxxxxxxxxxxxx"
TOKEN_SECRET = "xxxxxxxxxxxxxxxx"