from flask import Flask, request, render_template, render_template_string, send_from_directory, redirect
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from urllib.parse import parse_qs
from pymongo import MongoClient
import json
import os
import sys
from event_mongodb import RootCollection, StoryCollection
from random_utils import get_random_username, get_invite_code
import process_twine

import pprint
pp = pprint.PrettyPrinter(indent=4)

#####################
# environment setup #
#####################

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

###################################
# prepare a story for the browser #
###################################

def get_loomed_twine(twine_name):
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

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@app.route('/')
@login_required
def landing():
    with open("templates/landing.html") as landing_loc:
        landing = landing_loc.read()

    all_twines = root_db.get_all_stories()
    view_twines = []

    for story in all_twines:
        user_story_client = current_user.get_client(story["story_id"])
        if current_user.admin:
            view_twines.append( {"story":story, "admin":True} )
        elif story["auth_scheme"] != "invite":
            if user_story_client is not None:
                view_twines.append( {"story": story, "admin":user_story_client["admin"]} )
            else:
                view_twines.append( {"story": story, "admin":False} )
        else:
            if user_story_client != None:
                view_twines.append( {"story": story, "admin":user_story_client["admin"]} )

    if current_user.admin:
        users = root_db.get_all_users()
    else:
        users = None

    return render_template_string(landing, twines=view_twines, users = users)

#Blunt but effective
@app.route('/twine/<twine_name>')
def serve_twine(twine_name):
    if(twine_name.split(".")[-1]=="map"):
        return "no", 404
    story = root_db.get_story(twine_name)
    if story["auth_scheme"]=="login":
        if current_user.is_authenticated:
            return get_loomed_twine(twine_name)
    if story["auth_scheme"]=="none":
        return get_loomed_twine(twine_name)
    if story["auth_scheme"]=="invite":
        if current_user.is_authenticated and current_user.get_client(twine_name) is not None:
            return get_loomed_twine(twine_name)
    return redirect("/")

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
@login_required
def admin(twine_id):
    user_story_doc = current_user.story_dict[twine_id]
    if user_story_doc is not None and user_story_doc["admin"]:
        with open('templates/admin.html') as admin_loc:
            admin = admin_loc.read()
        twine = root_db.get_story(twine_id)
        return render_template_string(admin, twine=twine)
    else:
        return redirect("/")



#######################
# socketio functions  #
#######################

####################
## site-wide sockets

@socketio.on("create_user")
def create_user(user_create_doc):
    all_users = [u.to_json() for u in root_db.get_all_users()]
    if user_create_doc["uname"] in [doc["username"] for doc in all_users]:
        emit("create_user_response", {"status":"ERROR", "error":"User already exists with that username"})
    else:
        root_db.new_user(user_create_doc["uname"], user_create_doc["pass"])
        emit("create_user_response",{
            "status":"OK", 
            "users":[u.to_json() for u in root_db.get_all_users()]
        })

@socketio.on("user_admin_toggle")
def user_admin_toggle(event):
    user = root_db.get_user(event["user"])
    user.admin = event["admin"]
    root_db.save_user(user)
    emit("user_admin_toggle_response")



######################
## story-bound sockets


#this particular function is due for a ol refactor sometime. 
def connect_socket(connect_event):
    story_id = connect_event["story_id"]
    story = root_db.get_story(story_id)
    all_clients = story_dbs[story_id].get_all_clients()
    
    if story["auth_scheme"] == "login":
        if(current_user.is_authenticated): #this should be a redundant clause but just in case...
            
            user_story_doc = current_user.get_client(story_id)

            #if this user already has an entry for this story and this client, just grab it and send it
            if user_story_doc is not None and user_story_doc["client_id"] is not None:
                connect_event["client_id"] = user_story_doc["client_id"]
                client_doc = story_dbs[story_id].get_client(user_story_doc["client_id"])
                emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))
            #otherwise: create one, add it to the userdoc, and send it
            else: 
                if user_story_doc is not None:
                    admin_val = user_story_doc['admin']
                else:
                    admin_val = False

                user_twine_doc = {
                                    "story_id":story_id, 
                                    "client_id":connect_event["client_id"], 
                                    "admin":admin_val
                }

                current_user.story_dict[story_id] = user_twine_doc
                root_db.save_user(current_user)

                username = get_random_username()
                client_doc = {"client_id":connect_event["client_id"], "username":username, "user_id":current_user.user_id}
                story_dbs[story_id].add_client(client_doc)
                del client_doc["_id"]
                emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))
                    
    #none auth should still associate the client to a user if there is a user...
    elif story["auth_scheme"] == "none":
        if(current_user.is_authenticated): #this should be a redundant clause but just in case...
            
            
            user_story_doc = current_user.get_client(story_id)

            #if this user already has an entry for this story and this client, just grab it and send it
            if user_story_doc is not None and user_story_doc["client_id"] is not None:
                connect_event["client_id"] = user_story_doc["client_id"]
                client_doc = story_dbs[story_id].get_client(user_story_doc["client_id"])
                emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))
            else: 
                if user_story_doc is not None:
                    admin_val = user_story_doc['admin']
                else:
                    admin_val = False

                user_twine_doc = {
                                    "story_id":story_id, 
                                    "client_id":connect_event["client_id"], 
                                    "admin":admin_val
                }
                current_user.story_dict[story_id] = user_twine_doc
                root_db.save_user(current_user)

                username = get_random_username()
                client_doc = {"client_id":connect_event["client_id"], "username":username, "user_id":current_user.user_id}
                story_dbs[story_id].add_client(client_doc)
                del client_doc["_id"]
                emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))
        else:
            if connect_event["client_id"] in [c["client_id"] for c in all_clients]:
                client_doc = story_dbs[story_id].get_client(connect_event["client_id"])
                emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))
            else:
                username = get_random_username()
                client_doc = {"client_id":connect_event["client_id"], "username":username}
                story_dbs[story_id].add_client(client_doc)
                del client_doc["_id"]
                emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))

    if story["auth_scheme"] == "invite":
        if(current_user.is_authenticated): #this should be a redundant clause but just in case...
            user_story_doc = current_user.get_client(story_id)
            if user_story_doc is not None and user_story_doc["client_id"] is not None:
                connect_event["client_id"] = user_story_doc["client_id"]
                client_doc = story_dbs[story_id].get_client(user_story_doc["client_id"])
                emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))
            #otherwise: create one, add it to the userdoc, and send it
            elif user_story_doc is not None: 
                user_twine_doc = {
                                    "story_id":story_id, 
                                    "client_id":connect_event["client_id"], 
                                    "admin":user_story_doc['admin']
                }

                current_user.story_dict[story_id] = user_twine_doc
                root_db.save_user(current_user)

                username = get_random_username()
                client_doc = {"client_id":connect_event["client_id"], "username":username, "user_id":current_user.user_id}
                story_dbs[story_id].add_client(client_doc)
                del client_doc["_id"]
                emit("client_connect_ok", client_doc, namespace="/{}".format(story_id))

    story_dbs[story_id].add_event(connect_event)
    client_locations = story_dbs[story_id].get_all_current_client_location_events()
    emit("clients_present", client_locations, namespace="/{}".format(story_id), broadcast="true")


def nav_event(nav_event):
    story_id = nav_event["story_id"]
    story_dbs[story_id].add_event(nav_event)
    client_locations = story_dbs[story_id].get_all_current_client_location_events()
    emit("clients_present", client_locations, namespace="/{}".format(story_id), broadcast="true")

def get_story_structure(story_id):
    story = root_db.get_story(story_id)
    passages = story_dbs[story_id].get_all_passages()
    emit("story_structure", {"structure":passages, "story":story, "current_user":current_user.username}, namespace="/{}".format(story_id))

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

def update_story(story_update_doc):
    root_db.update_story(story_update_doc)
    emit("story_updated")

#the complexity of this function could be obliterated by a more model oriented storage system
def get_admin_clients(story_id):
    final_table = {} #this will be client_id :: client+user doc 
    anon_count = 0 #count up an identifier for 

    #we'll iterate over the users and transform them into one of three forms 
    #(and add them to a final table, indexed by client id (or other!)) 
    for user in root_db.get_all_users():
        user_story_client = user.get_client(story_id)
        if user_story_client is not None:
            if user_story_client["client_id"] is not None:
                client_key = user_story_client["client_id"]
                doc = {
                    "user_id":user.user_id, 
                    "username":user.username,
                    "added_to_story":True,
                    "loom_admin":user.admin,
                    "client_id":client_key,
                    "story_admin":user_story_client["admin"]
                    }
            else:
                client_key = anon_count
                anon_count += 1
                doc = {
                    "user_id":user.user_id, 
                    "username":user.username,
                    "added_to_story":True,
                    "client_id":None,
                    "story_admin":False,
                    "client_name":None,
                    "location":None
                    }
        else:
            client_key = anon_count
            anon_count += 1
            doc = {
                "user_id":user.user_id, 
                "username":user.username,
                "loom_admin":user.admin,
                "added_to_story":False,
                "client_id":None,
                "story_admin":False,
                "client_name":None,
                "location":None
                }
        final_table[client_key] = doc

    #Then, get all of the clients in the database for this story
    #and, if there is already an entry matching that client_id, fill out the appropreate information 
    #otherwise, just add a new doc to the final table

    clients = [{"client":doc["client"], "loc":doc["event"]["passage_id"]} for doc in 
                story_dbs[story_id].get_all_current_client_location_events(get_exited=True)]
    for doc in clients:
        client_id = doc["client"]["client_id"]
        if client_id in final_table.keys():
            existing_doc = final_table[client_id]
            existing_doc["client_name"] = doc["client"]["username"]
            existing_doc["location"] = doc["loc"]
            final_table[client_id] = existing_doc
        else:
            doc = {
                "user_id":None, 
                "username":None,
                "added_to_story":True,
                "loom_admin":False,
                "client_id":client_id,
                "story_admin":False,
                "client_name":doc["client"]["username"],
                "location":doc["loc"]
                }
            final_table[client_id] = doc
    emit("admin_clients", [doc for doc in final_table.values()])

def client_admin_toggle(event):
    client = story_dbs[event["story_id"]].get_client(event["client_id"])
    user = root_db.get_user_by_id(client["user_id"])
    user_story_doc = user.get_client(event["story_id"])
    user_story_doc["admin"] = event["admin"]
    user.story_dict[event["story_id"]] = user_story_doc
    root_db.save_user(user)
    emit("client_admin_toggle_response")

def client_added_toggle(event):
    #get the user in the event
    user = root_db.get_user_by_id(event["user_id"])
    if event["added"]:
        story_doc = {"story_id":event["story_id"], "client_id":None, "admin":None}
        user.story_dict[event["story_id"]] = story_doc
        root_db.save_user(user)
    else:
        user.story_dict[event["story_id"]] = None
        root_db.save_user(user)
    emit("client_added_toggle_response")

def generate_codes(event):
    codes = [get_invite_code() for i in range(int(event["number"]))]
    for code in codes:
        root_db.add_code(code, event["story_id"])
    all_story_codes = root_db.get_story_codes(event["story_id"])
    emit("invite_codes", all_story_codes)

def get_codes(story_id):
    all_story_codes = root_db.get_story_codes(story_id)
    emit("invite_codes", all_story_codes)

##user story toggle
all_socket_handlers = {
    "confirm_connected": connect_socket,
    "nav_event": nav_event,
    "get_story_structure": get_story_structure,
    "get_client_locations": get_client_locations,
    "get_admin_clients":get_admin_clients,
    "update_client":update_client,
    "update_story":update_story,
    "client_admin_toggle":client_admin_toggle,
    "client_added_toggle":client_added_toggle,
    "generate_codes":generate_codes,
    "get_codes":get_codes
}

##############
# data setup #
##############

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
            story_doc = {"story_id":twine_structure["story_id"],"title":twine_structure["title"], "auth_scheme":"none"}
            root_db.add_story(story_doc)
            for passage in twine_structure["passages"]:
                story_dbs[story_id].add_passage(passage)
    print("finished story setup")
    new, admin_user = root_db.new_user("admin", os.environ["ADMIN_PASS"], admin=True)
    if new:
        for story_id in twines:
            admin_user.story_dict[story_id] = {"story_id":story_id, "client_id":None, "admin":True}
        root_db.save_user(admin_user)
    new, test_user = root_db.new_user("test", "test")

setup()