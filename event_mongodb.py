#A rewrite of the database interfaces using mongodb
from pymongo import MongoClient

def clean_mongo_doc(doc):
	#the mongo-internal object id is irrelevant
	del doc["_id"]
	return doc

class RootCollection():
	def __init__(self, collection):
		self.db = collection
		self.stories = collection.stories

	def add_story(self, story_doc):
		self.stories.insert_one(story_doc)

	def get_story(self, story_id):
		return clean_mongo_doc(self.stories.find_one({"story_id":story_id}))

	def get_all(self):
		return [clean_mongo_doc(item) for item in self.stories.find()]


class StoryCollection():
	def __init__(self, collection):
		self.db = collection
		self.events = collection.events
		self.clients = collection.clients
		self.passages = collection.passages

	def add_client(self, client_doc):
		self.clients.insert_one(client_doc)

	def add_passage(self, passage_doc):
		self.passages.insert_one(passage_doc)

	def add_event(self, event_doc):
		self.events.insert_one(event_doc)

	def get_all_events(self):
		return [clean_mongo_doc(item) for item in self.events.find()]

	def get_all_clients(self):
		return [clean_mongo_doc(item) for item in self.clients.find()]

	def get_all_passages(self):
		return [clean_mongo_doc(item) for item in self.passages.find()]

	def get_client(self, client_id):
		return clean_mongo_doc(self.clients.find_one({"client_id":client_id}))

	def get_all_client_events(self, client_id):
		all_client_events = self.events.find({"client_id":client_id})
		return [clean_mongo_doc(item) for item in all_client_events]

	def get_current_client_location_event(self, client_id):
		return max(self.get_all_client_events(client_id), key=lambda x: x["time"])

	def get_all_current_client_location_events(self):
		all_current_events = [{"event": self.get_current_client_location_event(client["client_id"]), "client":client} 
								for client in self.get_all_clients()]
		#don't return exit events
		return filter(lambda x: (x["event"]["passage_id"] != "event:exit"), all_current_events)