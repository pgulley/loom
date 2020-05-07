from flask import Flask, request, render_template, render_template_string, send_from_directory, redirect
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_required, login_user, current_user
from urllib.parse import parse_qs
from pymongo import MongoClient
import json
import os
import sys
from event_mongodb import RootCollection, StoryCollection
from random_username import get_random_username
import process_twine

app = Flask("LOOM")
app.config['SECRET_KEY'] = os.environ["SOCKET_SECRET"]
socketio = SocketIO(app, cors_allowed_origins="*")
client = MongoClient(os.environ["MONGODB_URI"],retryWrites=False) 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

#to handle dev environ
if "localhost" in os.environ["MONGODB_URI"]:
    db_name = "default"
else:
    db_name = os.environ["MONGODB_URI"].split("/")[-1]

db = client[db_name]
root_db = RootCollection(db)
story_dbs = {}


@login_manager.user_loader
def load_user(user_id):
    user = root_db.get_user_by_id(user_id)
    return user

######################
# main server functs #
######################


@app.route('/static/<path>')
def send_static(path):
    return send_from_directory("static",path)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        with open("templates/login.html") as login_loc:
            login = login_loc.read()
        return render_template_string(login)

    elif request.method == "POST":
        request.get_data()
        data = parse_qs(request.data.decode("utf-8"))
        user = root_db.get_user(data["user"][0])
        if user is None:
            return {"Status":"NOT OK"} 
        else:
            if user.validate_pass(data["pass"][0]):
                root_db.save_user(user)
                login_user(user)
                return {"Status":"OK"}
            else:
                return {"Status":"NOT OK"}      



@app.route('/')
@login_required
def landing():
    with open("templates/landing.html") as landing_loc:
        landing = landing_loc.read()
    return render_template_string(landing, twines=root_db.get_all_stories())

#Blunt but effective
@app.route('/twine/<twine_name>')
def serve_twine(twine_name):
    with open("twines/{}.html".format(twine_name), "r") as twine_file:
        twine = twine_file.read()

    with open("static/loom.js", "r") as loom_js_file:
        loom_js = loom_js_file.read()

    with open("static/loom.css") as css:
        loom_css = css.read()


    socket_inject = "<script type='text/javascript' src='/static/socketio.js'></script>"
    iro_inject = "<script type='text/javascript' src='/static/iro.js'></script>"
    bootjs_inject = "<script type='text/javascript' src='/static/bootstrap.bundle.min.js'></script>"
    bootcss_inject = "<link rel='stylesheet' type='text/css' href='/static/bootstrap.min.css'>"
        
    
    loomed = twine.replace("{LOOM_JS}", loom_js)
    loomed = loomed.replace("{LOOM_CSS}", loom_css)
    loomed = bootcss_inject+loomed
    loomed = socket_inject+loomed
    loomed = iro_inject+loomed
    loomed = loomed+bootjs_inject

    return loomed

@app.route("/log", methods=["POST"])
def exit_event():
    request.get_data()
    log_data = json.loads(request.data)
    story_id = log_data["story_id"]    
    story_dbs[story_id].add_event(log_data)
    client_locations = story_dbs[story_id].get_all_current_client_location_events()
    emit("clients_present", client_locations, namespace="/{}".format(story_id), broadcast="true")
    return "OK"

@app.route('/twine/<twine_id>/admin')
def admin(twine_id):
    with open('templates/admin.html') as admin_loc:
        admin = admin_loc.read()
    twine = root_db.get_story(twine_id)
    return render_template_string(admin, twine=twine)


#######################
# socket functions    #
#######################


def connect_socket(connect_event):
    story_id = connect_event["story_id"]
    del connect_event["story_id"]
    all_clients = story_dbs[story_id].get_all_clients()
    if connect_event["client_id"] in [c["client_id"] for c in all_clients]:
        client_doc = story_dbs[story_id].get_client(connect_event["client_id"])
        emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))
    else:
        username = get_random_username()
        client_doc = {"client_id":connect_event["client_id"], "username":username}
        story_dbs[story_id].add_client(client_doc)
        del client_doc["_id"]
        emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))

def nav_event(nav_event):
    story_id = nav_event["story_id"]
    story_dbs[story_id].add_event(nav_event)
    client_locations = story_dbs[story_id].get_all_current_client_location_events()
    emit("clients_present", client_locations, namespace="/{}".format(story_id), broadcast="true")

def get_story_structure(story_id):
    passages = story_dbs[story_id].get_all_passages()
    emit("story_structure", passages, namespace="/{}".format(story_id))

def get_client_locations(story_id):
    client_locations = story_dbs[story_id].get_all_current_client_location_events()
    emit("clients_present", client_locations, namespace="/{}".format(story_id) )

def update_client(client_update_doc):
    story_id = client_update_doc["story_id"]
    client_doc = client_update_doc["client"]
    story_dbs[story_id].update_client(client_doc)
    emit("did_client_update", client_doc)
    
    client_locations = story_dbs[story_id].get_all_current_client_location_events()
    emit("clients_present", client_locations, namespace="/{}".format(story_id), broadcast="true")

all_socket_handlers = {
    "confirm_connected": connect_socket,
    "nav_event": nav_event,
    "get_story_structure": get_story_structure,
    "get_client_locations": get_client_locations,
    "update_client":update_client
}

#######################

def setup():
    print("Setting up")
    twines = [fname.split(".")[0] for fname in filter(lambda x: x[0]!=".", os.listdir("twines"))]
    already_twines = [story['story_id'] for story in root_db.get_all_stories()]
    for story_id in twines:
        print("setup {}".format(story_id))
        story_dbs[story_id] = StoryCollection(db, story_id)

        for name, function in all_socket_handlers.items():
            socketio.on_event(name, function, namespace="/{}".format(story_id))

        #this setup should only happen once per twine per database instantiation 
        if story_id not in already_twines:
            twine_structure = process_twine.process("twines/{}.html", story_id)
            story_doc = {"story_id":twine_structure["story_id"],"title":twine_structure["title"]}
            root_db.add_story(story_doc)
            for passage in twine_structure["passages"]:
                story_dbs[story_id].add_passage(passage)
    print("finished story setup")
    new, admin_user = root_db.new_user("admin", os.environ["ADMIN_PASS"])
    if new:
        for story_id in twines:
            admin_user.twines.append({"story_id":story_id, "client_id":None, "admin":True})
        root_db.save_user(admin_user)

setup()