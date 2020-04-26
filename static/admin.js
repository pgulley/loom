///Admin page
//shows story structure
//shows client states within story structure

var loom_admin = {
	story_id:document.URL.split("/")[4],
	passages:null,
	client_states:null
}

var socket = io()
socket.on('connect', function() {
	socket.emit("get_story_structure", loom_admin.story_id)
})

socket.on("story_structure", function(structure){
	loom_admin.passages = structure
	console.log(loom_admin)
})

socket.on("clients_present", function(clients){
	loom_admin.client_states = clients
	console.log(loom_admin)
})