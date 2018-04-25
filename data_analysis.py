from pymongo import MongoClient

from utils.mongo_data import MONGO_HOST

client = MongoClient(MONGO_HOST)
db = client.myDigitalFootprints

for doc in db.fbUSers.find({}):
    print(doc)