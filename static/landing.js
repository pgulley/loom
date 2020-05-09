var socket = io()
socket.on('connect', function() {
	console.log("connected!")
})

$(document).on("click", "#submit", function(){
	console.log("click?")
	var uname = $("#uname").val()
	var pass = $("#pword").val()
	socket.emit("create_user", {"uname":uname, "pass":pass})
})

socket.on("create_user_response", function(data){
	console.log("user create ok")
})