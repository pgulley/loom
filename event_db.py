from tinydb import TinyDB, Query
"""
Handles the database concerns: event-sourcing transformations and common queries. 

"""

class event_db():
    def __init__(self, db):
        self.db = db
        self.events = db.table("events")
        self.clients = db.table("clients")
        self.passages = db.table("passages")

    def get_all_events(self):
        return self.events.all()

    def get_all_clients(self):
        return [c["client_id"] for c in self.clients.all()]

    def get_all_passages(self):
        return [p["passage_id"] for p in self.passages.all()]

    def insert(self, event):
        if event["client_id"] not in self.get_all_clients():
            self.clients.insert({"client_id":event["client_id"]})
        if event["passage_id"] not in self.get_all_passages():
            self.passages.insert({"passage_id":event["passage_id"]})
        self.events.insert(event)

    def get_all_client_events(self, client_id):
        Event = Query()
        return self.events.search(Event.client_id==client_id)

    def get_current_client_location_event(self, client_id):
        return max(self.get_all_client_events(client_id), key=lambda x: x["time"])

    def get_all_current_client_location_events(self):
        return [self.get_current_client_location_event(client_id) for client_id in self.get_all_clients()]

    def get_current_passage_visitor_events(self, passage_id):
        return filter(lambda x: (x["passage_id"] == passage_id), self.get_all_current_client_location_events())
             
