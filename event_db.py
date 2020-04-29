from tinydb import TinyDB, Query
"""
Handles the database concerns: event-sourcing transformations and common queries. 
A lot of these seem redundant rn, but I'm hoping to switch out to a better fit database eventually
And building the db wrapper this way will reduce refactor complexity later on. 
"""

class event_db():
    def __init__(self, collection):
        self.db = collection
        self.events = db.table("events")
        self.clients = db.table("clients")
        self.passages = db.table("passages")

    def get_all_events(self):
        return self.events.all()

    def get_all_clients(self):
        return self.clients.all()

    def get_all_passages(self):
        return self.passages.all()

    def add_client(self, client_doc):
        self.clients.insert(client_doc)

    def add_passage(self, passage_doc):
        self.passages.insert(passage_doc)

    def get_client(self, client_id):
        Client = Query()
        return self.clients.search(Client.client_id==client_id)

    def insert(self, event):
        self.events.insert(event)

    def get_all_client_events(self, client_id):
        Event = Query()
        return self.events.search(Event.client_id==client_id)

    def get_current_client_location_event(self, client_id):
        return max(self.get_all_client_events(client_id), key=lambda x: x["time"])

    def get_all_current_client_location_events(self):
        all_current_events = [{"event": self.get_current_client_location_event(client["client_id"]), "client":client} 
                                for client in self.get_all_clients()]

        return filter(lambda x: (x["event"]["passage_id"] != "event:exit"), all_current_events) #never send exited clients

    