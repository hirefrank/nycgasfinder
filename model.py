from google.appengine.api import users
from google.appengine.ext import db

class Station(db.Model):
    account = db.StringProperty(default="nycgasfinder")
    name = db.StringProperty()
    brand = db.StringProperty()
    address = db.StringProperty()
    phone = db.StringProperty(default="No phone")
    price = db.StringProperty()
    time = db.StringProperty()
    date = db.DateTimeProperty(auto_now_add=True)