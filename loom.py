from flask import Flask, request, render_template, render_template_string
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
# Main Server Functs #
######################

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

    with open("loom.js", "r") as loom_js_file:
        loom_js = loom_js_file.read()

    with open("loom.css") as css:
        loom_css = css.read()

    with open("socketio.js", "r") as socket_io:
        socket = socket_io.read()
        socket_inject = "<script type='text/javascript'>{}</script>".format(socket)
    
    loomed = twine.replace("{LOOM_JS}", loom_js)
    loomed = loomed.replace("{LOOM_CSS}", loom_css)
    loomed = socket_inject+loomed
    return loomed

@app.route('/twine/<twine_name>/admin')
def admin():
    return "ohoho it's an admin route for {}. will get here eventually ;)".format(twine_name)


#######################
# Async Functions     #
#######################

@socketio.on("connected")
def connect_socket(connect_event):
    print(connect_event)
    story = connect_event["story_id"]
    del connect_event["story_id"]
    username = get_random_username()
    client_doc = {"client_id":connect_event["client_id"], "username":username}
    event_dbs[story].add_client(client_doc)
    if story_db_.get_story(story)["setup"] == True:
        emit("client_connect_ok", client_doc)
    else: 
        emit("get_story_structure", story)

@socketio.on("send_story_structure")
def process_story_structure(structure):
    print structure
    #run once per story- populates the story's eventdb with story passages
    #and updates the storydb entry to prevent this being re-run
    story = structure["story"]
    for passage in structure["passages"]:
        event_dbs[story].add_passage({"passage_id":passage})
    story_db_.mark_story_setup(story)




@socketio.on("nav_event")
def nav_event(nav_event):
    print("NAV EVENT: ",nav_event)
    story = nav_event["story_id"]
    del nav_event["story_id"]
    event_dbs[story].insert(nav_event)
    time.sleep(0.01)
    client_locations = event_dbs[story].get_all_current_client_location_events()
    emit("clients_present", client_locations, broadcast="true")

@app.route("/log", methods=["POST"])
def exit_event():
    request.get_data()
    log_data = json.loads(request.data)
    story = log_data["story_id"]
    del log_data["story_id"]
    event_dbs[story].insert(log_data)
    return {"Status":"OK"}

#######################

def setup():
    twines = [fname.split(".")[0] for fname in filter(lambda x: x[0]!=".", os.listdir("twines"))]
    already_twines = story_db_.get_all()
    for twine in twines:
        event_dbs[twine] = event_db(TinyDB("db/{}_event_db.json".format(twine)))
        if twine not in already_twines:
            story_db_.insert({"story_id":twine, "setup":False})

if __name__ == '__main__':
    setup()
    socketio.run(app)