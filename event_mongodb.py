#A rewrite of the database interfaces using mongodb
from pymongo import MongoClient

def clean_mongo_doc(doc):
	#the mongo-internal object id is irrelevant
	del doc["_id"]
	return doc

class RootCollection():
	def __init__(self, db):
		self.db = db
		self.stories = db.stories

	def add_story(self, story_doc):
		self.stories.insert_one(story_doc)

	def get_story(self, story_id):
		return clean_mongo_doc(self.stories.find_one({"story_id":story_id}))

	def get_all(self):
		return [clean_mongo_doc(item) for item in self.stories.find()]


class StoryCollection():
	def __init__(self, db, story_id):
		self.story_id = story_id
		self.db = db
		self.events = db.events
		self.clients = db.clients
		self.passages = db.passages

	def add_client(self, client_doc):
		client_doc["story_id"] = self.story_id
		self.clients.insert_one(client_doc)

	def update_client(self, client_doc):
		self.clients.replace_one({"story_id":self.story_id, "client_id":client_doc["client_id"]}, client_doc)

	def add_passage(self, passage_doc):
		passage_doc["story_id"] = self.story_id
		self.passages.insert_one(passage_doc)

	def add_event(self, event_doc):
		#print("adding event")
		event_doc["story_id"] = self.story_id
		#print(event_doc)
		self.events.insert_one(event_doc)

	def get_all_events(self):
		return [clean_mongo_doc(item) for item in self.events.find({"story_id":self.story_id})]

	def get_all_clients(self):
		as_list =  [clean_mongo_doc(item) for item in self.clients.find({"story_id":self.story_id})]
		#print("all clients: ", as_list)
		return as_list

	def get_all_passages(self):
		return [clean_mongo_doc(item) for item in self.passages.find({"story_id":self.story_id})]

	def get_client(self, client_id):
		return clean_mongo_doc(self.clients.find_one({"story_id":self.story_id, "client_id":client_id}))

	def get_all_client_events(self, client_id):
		all_client_events = self.events.find({"story_id": self.story_id, "client_id":client_id})
		as_list = [clean_mongo_doc(item) for item in all_client_events]
		#print("all client events: ", client_id, all_client_events)
		return as_list

	def get_current_client_location_event(self, client_id):
		client_events = self.get_all_client_events(client_id)
		if len(client_events) != 0:
			return max(client_events, key=lambda x: x["time"])
		else:
			return None

	def get_all_current_client_location_events(self):
		all_current_events = [{"event": self.get_current_client_location_event(client["client_id"]), "client":client} 
								for client in self.get_all_clients()]

		all_current_events = [event for event in all_current_events if event["event"] is not None]
		#don't return exit events
		return list(filter(lambda x: (x["event"]["passage_id"] != "event:exit"), all_current_events))