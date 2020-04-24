from flask import Flask, request, render_template, render_template_string
from flask_socketio import SocketIO, emit
from tinydb import TinyDB
from event_db import event_db 
from random_username import get_random_username
import json
import os
import urlparse
"""
Main server file
"""

db = event_db(TinyDB("db/event_db.json"))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'not_on_github_no_you_dont'
socketio = SocketIO(app)

######################
# Main Server Functs #
######################

@app.route('/')
def landing():
    twines = [fname.split(".")[0] for fname in filter(lambda x: x[0]!=".", os.listdir("twines"))]
    with open("templates/landing.html") as landing_loc:
        landing = landing_loc.read()

    print(twines)
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

@app.route('/admin')
def admin():
    return "ohoho it's an admin route. will get here eventually ;)"


#######################
# Async Functions     #
#######################

@socketio.on("connected")
def connect_socket(connect_event):
    print("connect_event")
    username = get_random_username()
    client_doc = {"client_id":connect_event["client_id"], "username":username}
    db.add_client(client_doc)
    emit("client_connect_ok", client_doc)

@socketio.on("nav_event")
def nav_event(log_data):
    print("nav event")
    print(log_data)
    db.insert(log_data)
    client_locations = db.get_all_current_client_location_events()
    print(client_locations)
    emit("clients_present", client_locations, broadcast="true")

@app.route("/log", methods=["POST"])
def exit_event():
    print("exit event")
    request.get_data()
    log_data = json.loads(request.data)
    db.insert(log_data)
    return {"Status":"OK"}

#######################

if __name__ == '__main__':
    socketio.run(app)