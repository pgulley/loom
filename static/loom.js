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
	client_obj: null,
	current_passage : null,
	clients_at_current_passage : []
}


//Async Networking concerns
var socket = io(`/${loom.story_id}`)
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
	loom.client_obj = data
	console.log(loom)
	loom.clients_at_current_passage = [data]
	render_loom_ui()
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

socket.on("did_client_update", function(data){
	console.log(data)
})

///////////////////////////////// UI Concerns

function render_loom_ui(){
	var client_boxes = loom.clients_at_current_passage.map(function(client){
		var shortuname = client.username.split(" ").map(function(i){return i[0]}).join(" ").toUpperCase()
		if(client.client_id == loom.client_id){
			return `<div class="loom_client you"> 
						${shortuname} 
						<div class='loom_client_detail'> 
							${client.username}  </br>
							<div class="edit_client_button show">edit</div>
							<div class="edit_client_interface hide">
								<div class="hide_edit_interface"> X </div>
									<label for="uname">Username</label>
  									<input type="text" id="uname" name="uname" value="${client.username}">
							</div> 
						</div> 
					</div>`
		}
		else{
			return `<div class=loom_client > ${shortuname} <div class='loom_client_detail'> ${client.username} </div> </div>`
		}
	})
	var loom_ui = `<div class="loom_ui_main"> ${client_boxes.join('')} <div class='loom_client_detail'>  </div> </div>` 
	$(".loom_ui_main").remove()
	$("body").append(loom_ui)
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
	$(this).parent().addClass("large")
	$(this).toggleClass("show").toggleClass("hide")
	$(this).next().toggleClass("show").toggleClass("hide")
})

$(document).on("click", ".hide_edit_interface", function(){
	$(this).parent().toggleClass("show").toggleClass("hide")
	$(this).parent().prev().toggleClass("show").toggleClass("hide")
	$(this).parent().parent().removeClass("large")
})

$(document).on("keypress", "#uname", function(e){
	if(e.which==13){
		console.log("user pressed enter on name")
		console.log(this.value)
		if(loom.client_obj.username!=this.value){
			loom.client_obj.username = this.value
			console.log(loom.client_obj)
			socket.emit("update_client", {"story_id":loom.story_id, "client":loom.client_obj})
		}
	}
})


