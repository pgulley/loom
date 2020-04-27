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
	story_id: document.URL.split("/").last(),
	client_id : makeid(10),
	current_passage : null,
	clients_at_current_passage : []
}


//Async Networking concerns
var socket = io(`/${loom.story_id}`)
console.log(socket)
socket.on('connect', function() {
    socket.emit('connected', 
    	{
    		"story_id": loom.story_id,
    		"passage_id":"event:enter",
           	"client_id":loom.client_id, 
    		"time":Date.now()
    	})
});

socket.on("client_connect_ok", function(data){
	console.log("connected: "+data["username"])
	loom.clients_at_current_passage = [data]
	render_loom_ui()
})

socket.on("load_story_structure", function(data){
	//called only once per story per deployment
	//does some parsing to grab the links between stories
	console.log(_)
	var all_passages = SugarCube.Story.lookup()
	
	var title_id_map = all_passages.map(function(p){
		return {
			"title":p.title, 
			"id":p.domId
			}
		})

	function get_links(passage_text){
		var link_regex = /\[\[([^\[]+)\]\]/g
		var links = passage_text.match(link_regex)
		var processed_links = links.map(function(link){
			if(link.includes("->")){
				var link_title = link.replace("[[", "").replace("]]","").split("->")[1]
			}else{
				var link_title = link.replace("[[", "").replace("]]","")
			}
			return title_id_map.filter(function(map){
				return map["title"]==link_title
			})[0]["id"]
		})
		return processed_links
	}

	var passage_objs = all_passages.map(function(passage){
		return {
			"passage_id":passage.domId,
			"title":passage.title,
			"links":get_links(passage.element.textContent)
		}
	})

	console.log(passage_objs)

	socket.emit("process_story_structure", {"story":loom.story_id, "passages":passage_objs})
})


$(document).on(":passagestart",function(ev){
	console.log("look I'm here")
	loom.current_passage = ev.content.id
	var timestamp = Date.now()
	var event_log = {
		"story_id": loom.story_id, 
		"passage_id":loom.current_passage,
		"client_id":loom.client_id,
		"time":Date.now()
	}
	socket.emit('nav_event',event_log)
})

//make sure an "exit" event is sent when client leaves or refreshes
$(window).on("beforeunload",function() {
   	var event_log = {
   		"story_id": loom.story_id,
		"passage_id":"event:exit",
		"client_id":loom.client_id,
		"time":Date.now()
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

///////////////////////////////// UI Concerns

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
	$(".loom_ui_main").remove()
	$("body").append(loom_ui)

}
