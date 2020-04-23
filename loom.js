//This code is injected into the twine story before it is sent to the browser.
//Supports client identification and twine event interfacing.
function makeid(length) {
   var result           = '';
   var characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
   var charactersLength = characters.length;
   for ( var i = 0; i < length; i++ ) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
   }
   return result;
}

var loom = {
	client_id : makeid(10),
	current_passage : null,
	clients_at_current_passage : []
}


//Async Networking concerns
var socket = io()
    socket.on('connect', function() {
        socket.emit('connected', {"client_id":loom.client_id, time:Date.now(), "passage_id":"event:enter"});
    });

socket.on("client_connect_ok", function(data){
	console.log("connected: "+data["username"])
})

$(document).on(":passagestart",function(ev){
	loom.current_passage = ev.content.id
	var timestamp = Date.now()
	var event_log = {
		"time":timestamp, 
		"passage_id":loom.current_passage,
		"client_id":loom.client_id
	}
	socket.emit('nav_event',event_log)
})

//make sure an "exit" event is sent when client leaves or refreshes
$(window).on("beforeunload",function() {
	var timestamp = Date.now()
   	var event_log = {
		"time":timestamp, 
		"passage_id":"event:exit",
		"client_id":loom.client_id
	}
	//frustratingly, we need to do this the socketless way. 
    navigator.sendBeacon("/log", JSON.stringify(event_log));
});

socket.on("clients_present", function(data){
	loom.clients_at_current_passage = data.filter(function(event){
		return event["event"]["passage_id"] == loom.current_passage
 	}).map(function(event){
 		return event["client"]
 	})
 	render_loom_ui()
})

// UI Concerns

function render_loom_ui(){
	var client_boxes = loom.clients_at_current_passage.map(function(client){
		if(client.client_id == loom.client_id){
			return `<div class="loom_client you"> ${client.username} </div>`
		}
		else{
			return `<div class=loom_client > ${client.username} </div>`
		}
	})
	var loom_ui = `<div class="loom_ui_main"> ${client_boxes.join('')} </div>`
	console.log(loom_ui)
	$(".loom_ui_main").remove()
	$("body").append(loom_ui)

}
