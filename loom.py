from flask import Flask, escape, request
from tinydb import TinyDB
from event_db import event_db 
import json
import urlparse
"""
Main server file
"""

db = event_db(TinyDB("db/event_db.json"))
app = Flask(__name__)

@app.route('/')
def default():
    with open("twines/test_twine.html", "r") as twine_file:
        twine = twine_file.read()

    with open("loom_inject.js", "r") as loom_js_file:
        loom_js = loom_js_file.read()
    
    loomed = twine.replace("{LOOM}", loom_js)
    return loomed


@app.route("/log", methods=["POST"])
def get_state():
    request.get_data()
    print request.data
    log_data = json.loads(request.data)
    print(log_data)
    db.insert(log_data)
    current_passage_visitor_events = db.get_current_passage_visitor_events(log_data["passage_id"])
    return {"Status":"OK", "data":json.dumps(current_passage_visitor_events)}