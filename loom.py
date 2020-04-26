
from flask import Flask, request, render_template, render_template_string, send_from_directory
from flask_socketio import SocketIO, emit
from tinydb import TinyDB
from event_db import event_db 
from story_db import story_db
from random_username import get_random_username
import time
import json
import os
import urlparse
"""
Main server file
"""

story_db_ = story_db(TinyDB("db/story_db_.json"))
event_dbs = {}
app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_on_github_no_you_dont'
socketio = SocketIO(app)

######################
# main server functs #
######################

@app.route('/static/<path>')
def send_static(path):
    return send_from_directory("static",path)


@app.route('/')
def landing():
    with open("templates/landing.html") as landing_loc:
        landing = landing_loc.read()
    twines = [t["story_id"] for t in story_db_.get_all()]
    return render_template_string(landing, twines=twines)


@app.route('/twine/<twine_name>')
def serve_twine(twine_name):
    with open("twines/{}.html".format(twine_name), "r") as twine_file:
        twine = twine_file.read()

    with open("static/loom.js", "r") as loom_js_file:
        loom_js = loom_js_file.read()

    with open("static/loom.css") as css:
        loom_css = css.read()

    with open("static/socketio.js", "r") as socket_io:
        socket = socket_io.read()
        socket_inject = "<script type='text/javascript'>{}</script>".format(socket)
    
    loomed = twine.replace("{LOOM_JS}", loom_js)
    loomed = loomed.replace("{LOOM_CSS}", loom_css)
    loomed = socket_inject+loomed
    return loomed

@app.route("/log", methods=["POST"])
def exit_event():
    request.get_data()
    log_data = json.loads(request.data)
    story = log_data["story_id"]
    del log_data["story_id"]
    event_dbs[story].insert(log_data)
    return {"Status":"OK"}

@app.route('/twine/<twine_name>/admin')
def admin(twine_name):
    with open('templates/admin.html') as admin_loc:
        admin = admin_loc.read()
    return render_template_string(admin, twine_name=twine_name)


#######################
# socket functions    #
#######################
def connect_socket(connect_event):
    print(connect_event)
    story_id = connect_event["story_id"]
    del connect_event["story_id"]
    username = get_random_username()
    client_doc = {"client_id":connect_event["client_id"], "username":username}
    event_dbs[story_id].add_client(client_doc)
    if story_db_.get_story(story_id)["setup"] == True:
        emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))
    else: 
        emit("load_story_structure", story_id, namespace="/{}".format(story_id))


def nav_event(nav_event):
    print("NAV EVENT: ",nav_event)
    story_id = nav_event["story_id"]
    del nav_event["story_id"]
    event_dbs[story_id].insert(nav_event)
    client_locations = event_dbs[story_id].get_all_current_client_location_events()
    emit("clients_present", client_locations, namespace="/{}".format(story_id), broadcast="true")


def process_story_structure(structure):
    print structure
    #run once per story- populates the story's eventdb with story passages
    #and updates the storydb entry to prevent this being re-run
    story_id = structure["story"]
    for passage in structure["passages"]:
        event_dbs[story_id].add_passage(passage)
    story_db_.mark_story_setup(story_id)


def get_story_structure(story_id):
    passages = event_dbs[story_id].get_all_passages()
    print passages
    emit("story_structure", passages, namespace="/{}".format(story_id))


def get_client_locations(story_id):
    client_locations = event_dbs[story_id].get_all_current_client_location_events()
    emit("clients_present", client_locations, namespace="/{}".format(story_id) )


all_socket_handlers = {
    "connected": connect_socket,
    "nav_event": nav_event,
    "process_story_structure": process_story_structure,
    "get_story_structure": get_story_structure,
    "get_client_locations": get_client_locations
}

#######################

def setup():
    twines = [fname.split(".")[0] for fname in filter(lambda x: x[0]!=".", os.listdir("twines"))]
    already_twines = story_db_.get_all()
    for story_id in twines:
        event_dbs[story_id] = event_db(TinyDB("db/{}_event_db.json".format(story_id)))
        for name, function in all_socket_handlers.iteritems():
            socketio.on_event(name, function, namespace="/{}".format(story_id))
        if story_id not in already_twines:
            story_db_.insert({"story_id":story_id, "setup":False})

if __name__ == '__main__':
    setup()
    socketio.run(app)