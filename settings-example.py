# Rename to settings.py

# Data source is wrightexpress.com
BASE_URL = 'http://rrtexternalweb.wrightexpress.com/neo_ww/site_locator/list.action?sortByValue=LAST_TRAN_TIME&sortDirection=DESCENDING&mapType=Hybrid&mapZoom=12&sorting=true&fuelType=Unleaded+Regular&'

# Takes zipcode as input as well a radius in miles
# Twitter API / Auth
# these tokens are necessary for user authentication
# (created within the twitter developer API pages)

ACCOUNTS = {
  'nycgasfinder': {
    'zipcode': '11201',
    'radius': '10',
    'consumer_key': 'xxxxxxxxxxxxxxxx',
    'consumer_secret': 'xxxxxxxxxxxxxxxx',
    'token_key': 'xxxxxxxxxxxxxxxx',
    'token_secret': 'xxxxxxxxxxxxxxxx',
  },
}