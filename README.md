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
Name the file 'twine.html' and plop that bad boy into the 'twines/' folder and you're golden. 


### How to run

create and enter a virtual environment, install required packages. 
`python loom.py`


### Development Status

- [X] Javascript Injection and Twine Event Binding
- [X] Server-side event-sourced database
- [X] Simple AJAX bodge for client-server interaction 
- [X] SocketIO for better client-server interaction
- [X] better client profile system
- [X] client-side UI for user presense
- [ ] client-side admin ui 
- [ ] flexible configuration and deployment options 
- [ ] choose a better wsgi solution for non-dev deployments
- [ ] ui polish pls and thx

#### Stretch Goals

- [ ] Client-defined names and icons
- [ ] Multi-Story Support
- [ ] Web Interface to load new stories
- [ ] Extended API- ifttt? 