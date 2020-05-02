Loom! 
=====

Imagined here is a simple multi-user networking add-on for Twine stories.
It will give real-time monitoring of users progress through a story to a story moderator,
and allow users to see the status of other users in the space with them.

### Whats its for
covid-inspired telepresence weirdness 

### How it works
It' a simple python server which injects a socket.io client into a twine story. 
The only requirement placed upon the twine story is that it is written in the SugarCube engine. 
The only modification needed is to add a tag: `{LOOM_JS}` to the user javascript of a twine story and `{LOOM_CSS}` to the user stylesheet.
Name the file anything unique and plop that bad boy into the 'twines/' folder and you're golden. 


### How to run

Right now there is only a development server- it's packaged as a default python package, so 
slap this thing in a virtual environment and run `python loom.py` and you're golden. 

As of recently, we're using mongodb for database stuff. 
I may switch this over eventually for easier deployments by hobbyists, but for now it solves a lot of concurrency issues to use mongo.
All this to say, make sure you have a mongodb instance running or it won't work. 

### It's Deployed!
Find a live version [here](https://twine-loom-test.herokuapp.com/twine/twine) if you please. 

### Development Status

#### MVP checklist

- [X] Javascript Injection and Twine Event Binding
- [X] Server-side event-sourced database
- [X] Simple AJAX bodge for client-server interaction 
- [X] SocketIO for better client-server interaction
- [X] better client profile system
- [X] client-side UI for user presense
- [X] Multi-Story Support
- [X] client-side admin ui 
- [X] store story graph stucture
- [X] Load story structure on server-side
- [X] Client-defined names and icons
- [X] flexible configuration and deployment options 
- [X] choose a better wsgi solution for non-dev deployments: using eventlet
- [ ] ui polish pls and thx

#### Down the road options

- [ ] Authentication / User Sessions 
- [ ] Web Interface to load new stories
- [ ] Client to client chatting
- [ ] More Admin interaction options
- [ ] More Sugarcube Engine interactions (variables etc)
- [ ] Extended API- ifttt? 

#### Bugs

None (that I know of) right now
