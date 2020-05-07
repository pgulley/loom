from pymongo import MongoClient
import os

if "localhost" in os.environ["MONGODB_URI"]:
    db_name = "default"
else:
    db_name = os.environ["MONGODB_URI"].split("/")[-1]

c = MongoClient(os.environ["MONGODB_URI"])
c.drop_database(db_name)