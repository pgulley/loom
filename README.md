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
If you are logged in with admin permissions, you will be able to upload your story to the server on the landing page. 


### How to run

The devlopment server is run via `gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 loom:app`
Make sure you have `ADMIN_PASS`, `MONGODB_URI` and `SOCKET_SECRET` defined in your environment.
Make sure you have a mongodb instance available.

`python reset_db.py` reverts the database to its empty state. 

### It's Deployed!
Find a live version [here](https://twine-loom-test.herokuapp.com) if you please. 
[Looming](https://twine-loom-test.herokuapp.com/twine/looming) is a short story showcasing some of the capabilities of the platform

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
- [X] Web Interface to load new stories

MVP is done and deployed!

#### 0.2 checklist

- [X] Authentication / User Sessions 
	- [X] basic universal login loop
	- [X] new user creation
	- [X] Story-scope permissions
		- [X] 3 Auth Schemes:
			- [X] None Scheme (default)
			- [X] Login Required scheme
				- [X] associate clients with users
			- [X] Invitation scheme

 - [ ] POLISH TIL IT SHINES

#### Down the road features

- [ ] Chat features
	- [X] None Scheme 
	- [ ] Jitsi Scheme
	- [ ] Echo Scheme
	- [ ] Tweet Scheme

- [ ] More Elaborate Sugarcube Engine Interaction
	- [ ] Share Story Variables with Server
		- [ ] Mark editable/sharable/viewable etc 

- [ ] More Admin interaction options 
	- [ ] Boot User
	- [ ] @ User
	- [ ] Edit Story Variables

- [ ] Extended API- ifttt or RSS?


