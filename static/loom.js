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

function get_shortname(uname){
	return uname.split(" ").map(function(i){return i[0]}).slice(0,2).join(" ").toUpperCase()
}

var loom = {
	story_id: document.URL.split("/").last().split("?")[0],
	client_id : makeid(10),
	client_obj: null,
	current_passage : null,
	clients_at_current_passage : [],
	loaded: false
}

var color_picker = null

//Async Networking concerns
var socket = io(`/${loom.story_id}`)
socket.on('connect', function() {
    socket.emit('confirm_connected', 
    	{
    		"story_id": loom.story_id,
    		"passage_id":"event:enter",
           	"client_id":loom.client_id, 
    		"time":Date.now()
    	})
});

socket.on("client_connect_ok", function(data){
	console.log("connected: "+data["username"])
	loom.client_obj = data
	setup_loom_ui()
})


$(document).on(":passagestart",function(ev){
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
		return (event["event"]["passage_id"] == loom.current_passage) & (event["client"]["client_id"]!=loom.client_id )
 	}).map(function(event){
 		return event["client"]
 	})
 	update_other_clients()
})

socket.on("did_client_update", function(data){
	loom.client_obj = data
	update_current_client()
})

///////////////////////////////// UI Concerns

function get_current_client_ui(){
	if(loom.client_obj.color==undefined){
		var color = '#000000'
	}
	else{
		var color = loom.client_obj.color
	}
	return `<div class="loom_client you" style="background-color:${color};"> 
				<span id="client_shortname"> ${get_shortname(loom.client_obj.username)} </span>
				<div class='loom_client_detail'> 
					<span id="client_uname">${loom.client_obj.username}</span>  </br>
					<div class="edit_client_button show">edit</div>
				</div> 
			</div>`
}

function update_current_client(){
	$(".you").css("background-color",loom.client_obj.color)
	$("#client_shortname")[0].innerHTML = get_shortname(loom.client_obj.username)
	$("#client_uname")[0].innerHTML = loom.client_obj.username
}

//update other clients
function update_other_clients(){
	var client_boxes = loom.clients_at_current_passage.map(function(client){
		if(client.color==undefined){
				var color = '#000000'
		}
		else{
				var color = client.color
		}
		return `<div class=loom_client style="background-color:${color};"> ${get_shortname(client.username)} <div class='loom_client_detail'> ${client.username} </div> </div>`
	})
	$(".other_clients")[0].innerHTML = client_boxes.join("")
}

//setup loom ui. Called once per document
function setup_loom_ui(){
	var loom_ui = `

			<div class="loom_ui_top">
				<div class="current_client"> ${get_current_client_ui()} </div>
				<div class="modal" id="user_modal" tabindex="-1" role="dialog">
				  <div class="modal-dialog" role="document">
				    <div class="modal-content" id="user_modal_content">
				      <div class="modal-header">
				        <h5 class="modal-title">Edit User Properties</h5>
				        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
				          <span aria-hidden="true">&times;</span>
				        </button>
				      </div>
				      <div class="modal-body">
						<label for="uname">Username</label>
						<input type="text" id="uname" name="uname" value="${loom.client_obj.username}">
						<label for="u_col">Color</label>
						<div id="color_picker">
						</div>
				      </div>
				    </div>
				  </div>
				</div>
			</div>
			<div class="loom_ui_bottom"> 
				<div class="other_clients">  </div>
			</div>`
	$("body").append(loom_ui)
	if(loom.client_obj.color==undefined){
		var color = '#000000'
	}
	else{
		var color = loom.client_obj.color
	}
	if(loom.loaded == false){
		var color_picker = new iro.ColorPicker("#color_picker",{
			color:color,
			width:100,
			layoutDirection:'horizontal'
		})
		loom.loaded = true
	}
	else{
		var color_picker = $("#color_picker")
	}
	color_picker.on("input:end", function(color){
		update_color(color.hexString)
	})
	$('#user_modal').modal()
	update_other_clients()
}

$(document).on("click", ".loom_client", function(){
	var detail = $(this).children()
	detail.show()
})

$(document).on("mouseout", ".loom_client_detail", function(){
	var client_detail = $(this)
	setTimeout(function(){
		if(!client_detail.hasClass("large")){
			client_detail.hide()
		}
	}, 1000)
})

$(document).on("click",".edit_client_button", function(){
	$("#user_modal").modal("show")
})

$(document).on("blur", "#uname", function(e){
	if(loom.client_obj.username!=this.value){
		loom.client_obj.username = this.value
		socket.emit("update_client", {"story_id":loom.story_id, "client":loom.client_obj})
	}
})

function update_color(color){
	if(loom.client_obj.color!=color){
		loom.client_obj.color = color
		socket.emit("update_client", {"story_id":loom.story_id, "client":loom.client_obj})
	}
}

