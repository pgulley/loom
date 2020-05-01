from pymongo import MongoClient
c = MongoClient()
c.drop_database("default")