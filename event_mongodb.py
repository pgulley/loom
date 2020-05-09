#A rewrite of the database interfaces using mongodb
from pymongo import MongoClient
from passlib.hash import sha256_crypt
import uuid

class User():
	def __init__(self, mongo_doc):
		self.user_id = mongo_doc["user_id"]
		self.pass_hash = mongo_doc["pass_hash"]
		self.username = mongo_doc["username"]
		self.admin = mongo_doc["admin"]
		#[{twine_story_id:str, client_id:str, admin:bool},...]
		self.twines = mongo_doc["twines"] 

		self.is_authenticated = mongo_doc["is_authenticated"]
		self.is_active = True #unnessecary for loom
		self.is_anonymous = False #unessecary for loom

	def get_id(self):
		return self.user_id

	def validate_pass(self, password):
		self.is_authenticated = sha256_crypt.verify(password, self.pass_hash)
		return self.is_authenticated

	def change_pass(self, new_pass): 
		self.pass_hash = sha256_crypt.encrypt(new_pass)
		return True

	def to_doc(self):
		return {
			"username":self.username,
			"pass_hash":self.pass_hash,
			"user_id":self.user_id,
			"twines":self.twines,
			"admin":self.admin,
			"is_authenticated":self.is_authenticated,
		}

	#only returns information of interest to the browser
	def to_json(self):
		return {
			"username":self.username,
			"user_id":self.user_id,
			"twines":self.twines,
			"admin":self.admin,
		}

	def __repr__(self):
		return str(self.to_doc())


def clean_mongo_doc(doc):
	#the mongo-internal object id is irrelevant
	if doc is None:
		return doc
	else:
		del doc["_id"]
		return doc

class RootCollection():
	def __init__(self, db):
		self.db = db
		self.stories = db.stories
		self.users = db.users

	def add_story(self, story_doc):
		self.stories.insert_one(story_doc)

	def get_story(self, story_id):
		return clean_mongo_doc(self.stories.find_one({"story_id":story_id}))

	def update_story(self, story_doc):
		self.stories.replace_one({"story_id":story_doc["story_id"]}, story_doc)

	def get_all_stories(self):
		return [clean_mongo_doc(item) for item in self.stories.find()]

	def new_user(self, username, password, admin=False):
		doc = {
			"username":username,
			"pass_hash":sha256_crypt.encrypt(password),
			"user_id":str(uuid.uuid4()),
			"twines":[],
			"admin":admin,
			"is_authenticated":False
		}
		#check if username exists in db yet
		if self.users.find({"username":username}).count() == 0:
			self.users.insert_one(doc)
			user = User(doc)
			return True, user
		else:
			return False, self.get_user(username)

	def get_user(self, username):
		got = self.users.find_one({"username":username})
		if got is not None:
			return User(got)
		else:
			return None

	def get_user_by_id(self, user_id):
		#this is just for the flask-login mixin
		got = self.users.find_one({"user_id":user_id})
		if got is not None:
			return User(got)
		else:
			return None

	def get_all_users(self):
		return [User(doc) for doc in self.users.find()]

	def save_user(self, User):
		self.users.replace_one({"user_id":User.user_id}, User.to_doc())
		return User


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
		event_doc["story_id"] = self.story_id
		self.events.insert_one(event_doc)

	def get_all_events(self):
		return [clean_mongo_doc(item) for item in self.events.find({"story_id":self.story_id})]

	def get_all_clients(self):
		as_list =  [clean_mongo_doc(item) for item in self.clients.find({"story_id":self.story_id})]
		return as_list

	def get_all_passages(self):
		return [clean_mongo_doc(item) for item in self.passages.find({"story_id":self.story_id})]

	def get_client(self, client_id):
		return clean_mongo_doc(self.clients.find_one({"story_id":self.story_id, "client_id":client_id}))

	def get_all_client_events(self, client_id):
		all_client_events = self.events.find({"story_id": self.story_id, "client_id":client_id})
		as_list = [clean_mongo_doc(item) for item in all_client_events]
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