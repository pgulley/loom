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

var server_location = "/log"

var client_id = makeid(10)

//Send an event to the server whenever the client moves from one passage to another
$(document).on(":passagerender",function(ev){
	var passage_id = ev.content.id
	var timestamp = Date.now()
	var event_log = {
		"time":timestamp, 
		"passage_id":passage_id,
		"client_id":client_id
	}
	$.post(server_location, JSON.stringify(event_log))
	.done(function(resp){
		console.log(resp)
	})
})

//make sure an "exit" event is sent when client leaves or refreshes
$(window).on("beforeunload",function() {
	var timestamp = Date.now()
   	var event_log = {
		"time":timestamp, 
		"passage_id":"event:exit",
		"client_id":client_id
	}
    navigator.sendBeacon(server_location, JSON.stringify(event_log));
});