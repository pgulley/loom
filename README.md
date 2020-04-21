Loom! 
=====

Imagined here is a simple multi-user networking add-on for Twine stories.
It will give real-time monitoring of users progress through a story to a story moderator,
and allow users to see the status of other users in the space with them.


### How it works
It's just a simple python server which recieves event singals from javascript which gets injected into the story. 
The only modification needed is to add a tag: `{LOOM}` to the user javascript of a twine story. The story must use the Snowcone engine for this to work. 


### Whats its for
covid-inspired telepresence weirdness 

### Development Status

- [X] Javascript Injection and Twine Event Binding
- [X] Server-side event-sourced database
- [X] Simple AJAX bodge for client-server interaction. 
- [ ] SocketIO for beaming information back to client-side 
- [ ] client-side UI for user presense
- [ ] client-side admin ui 
