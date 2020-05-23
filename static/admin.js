///Admin page
//shows story structure
//shows client states within story structure

var loom_admin = {
	setup:false,
	story_id:document.URL.split("/")[4],
	story_doc:null,
	passages:null,
	client_states:null,
	clients_by_passage:null,
	logged_in_user:null,
	graph_extrema: []
}

$.ready(function(){
	loom_admin.logged_in_user = $("#logged_in_user")[0].innerHTML
}) 

//rendering!

function setup_passage_table(){
	table_rows = loom_admin.passages.map(function(passage){
		return `<tr id="${passage.passage_id}">
			<td class="passage_title"> ${passage.title} </td>
			<td class="num_connected"> </td>
			<td class="client_names"> </td>
		</tr>`
	})

	$(".passages_table").append( 
		`<table class="twine_table">
			<tr>
				<th> Passage Title </th>
				<th> Clients Connected </th>
				<th> Client Names </th>
			</tr>
			${table_rows.join('')}
		</table>
		`)
}

function update_tables(){
	//Updates both the passages table and the user table whenever we recieve an update event

	//need to add some logic here to square the clients against the users.
	//just cause new users might show up, and the users table was generated already
	user_client_ids = loom_admin.users.map(function(u){return u.client_id})
	client_id_list = loom_admin.client_states.map(function(c){

		//if the client's info isn't already in the user table....
		if(!(user_client_ids.includes(c.client.client_id))){
			//a new client has joined the room- add them to the users table
			//this client might belong to an existing user... check that.
			if(c.client.user_id != undefined){
				$(`#${c.client.user_id}`).parent().attr("id", c.client.client_id)				
				//update that users existing entry in the table
			}else{
				//add the client to the usertable with no user info
				$("#users_table_body").append(`<tr id="${c.client.client_id}">
					<td></td>
					<td>
						<input type="checkbox" value="null" class="added_toggle" checked >
					</td>
					<td class="client_name">${c.client.username}</td>
					<td class="location">
					</td>
					<td>
						<input type="checkbox" value="null" class="admin_toggle" >
					</td>
				</tr>`)
			}
			loom_admin.users.push({client_id:c.client.client_id})
		}

		//always update the client username too
		$(`#${c.client.client_id} .client_name`)[0].innerHTML = c.client.username
		return c.client.client_id
	})

	//We'll need one loop through the user list as well, to mark any exited users properly
	user_client_ids.map(function(u){
		if(!client_id_list.includes(u)){
			$(`#${u} .location`)[0].innerHTML = "event:exit"
			$(`#${u}`).addClass("exit")
		}
	})


	loom_admin.passages.map(function(passage){
		passage_info = loom_admin.clients_by_passage.filter(function(item){return item.id == passage.passage_id})[0]
		var num_query = `#${ passage.passage_id } .num_connected`
		var clients_query = `#${ passage.passage_id } .client_names`
		if(passage_info.clients.length > 0){
			var clients = passage_info.clients.map(function(c){
				$(`#${c.client.client_id} .location`)[0].innerHTML = passage.name	
				if(passage.name != "event:exit"){
					$(`#${c.client.client_id}`).removeClass("exit")
				}
				return c.client.username
			})
			$(num_query)[0].innerHTML = passage_info.clients.length
			$(clients_query)[0].innerHTML = clients
		}
		else{
			$(num_query)[0].innerHTML = "0"
			$(clients_query)[0].innerHTML = " "
		}
		
	})
}

function setup_users_table(user_list){
	user_rows = user_list.map(function(user){
		return `<tr id="${user.client_id}" ${(user.location=="event:exit" ? "exit":"")}>
			<td id="${user.user_id}">
				${(user.username ? user.username : "")}
			</td>
			<td>
				<input type="checkbox" value="${user.user_id}" class="added_toggle" 
				${(user.added_to_story ? "checked":"")} 
				${(user.username==loom_admin.logged_in_user ? "disabled" :"")}
				${(user.loom_admin ? "disabled checked" :"")} >
			</td>
			<td class="client_name">
				${(user.client_name ? user.client_name : "")}
			</td>
			<td class="location">
				${(user.location ? user.location : "")}
			</td>
			<td>
				<input type="checkbox" value="${user.client_id}" class="admin_toggle" 
				${(user.story_admin ? "checked":"")} 
				${(user.username==loom_admin.logged_in_user ? "disabled" :"")}
				${(user.loom_admin ? "checked disabled" :"")} 
				${(user.add_to_story ? "" : "disabled")}>
			</td>
		</tr>
		`
	}).join('')
	$("#users_table_body")[0].innerHTML = user_rows
}

function setup_passage_graph(){
	//Generate the graph nodes
	var nodes = loom_admin.passages.map(function(passage){
		var position = passage.position.split(",")
		loom_admin.graph_extrema.push(position[1])
		return `<div class="passage_node" id="node-${passage.passage_id}" style="left:${position[0]}; top:${position[1]}"> 
					<div class="node_badge"></div> 
					${passage.title} 
				</div>`
	}).join("")
	$(".passages_graph_body")[0].innerHTML = nodes
	//Generate the graph edges
	loom_admin.passages.map(function(p){
		p.link_ids.map(function(i){
			$(`#node-${p.passage_id}`).connections({to:`#node-${i}`, class:"graph_link"})
		})
	})
	//Set the canvas size
	var xmin = Math.min.apply(null, loom_admin.graph_extrema)
	var xmax = Math.max.apply(null, loom_admin.graph_extrema)
	var xspan = xmax-xmin
	$(".passages_graph_body").height(xspan+200) 
}

function update_passage_graph(){
	loom_admin.passages.map(function(p){
		passage_info = loom_admin.clients_by_passage.filter(function(item){return item.id == p.passage_id})[0]
		num_connected = passage_info.clients.length
		if(num_connected > 0){
			$(`#node-${p.passage_id} .node_badge`).css("display", "inline-block")
			$(`#node-${p.passage_id} .node_badge`)[0].innerHTML = num_connected
		}else{
			$(`#node-${p.passage_id} .node_badge`).css("display", "none")
		}
	})
}

function render_codes_list(codes_list){
	$(".code_list").empty()
	$(".code_list")[0].innerHTML = codes_list.map(function(c){
		return `<tr class="${(c.used ? "used" : "")}">
			<td> ${c.code} </td>
			<td> ${(c.used_by==null ? "" : c.used_by)}</td>
		</tr>`
	}).join("")
}

//Sockets!	

var socket = io(`/${loom_admin.story_id}`)
socket.on('connect', function() {
	socket.emit("get_story_structure", loom_admin.story_id)
})

socket.on("story_structure", function(response){
	loom_admin.passages = response["structure"]
	loom_admin.story_doc = response["story"]
	loom_admin.logged_in_user = response["current_user"]
	if(loom_admin.setup == false){
		setup_passage_table()
		setup_passage_graph()
		$(`#auth_${loom_admin.story_doc["auth_scheme"]}`).prop("checked", true)
		$(`#jitsi_${loom_admin.story_doc["jitsi_default"]}`).prop("checked", true)
		socket.emit("get_admin_clients", loom_admin.story_id)
	}

})

socket.on("admin_clients", function(clients){
	loom_admin.users = clients
	setup_users_table(clients)
	loom_admin.setup = true
	socket.emit("get_client_locations", loom_admin.story_id)
	socket.emit("get_codes", loom_admin.story_id)
})

socket.on("clients_present", function(clients){
	if(loom_admin.setup){ //wait for render to finish
		loom_admin.client_states = clients
		loom_admin.clients_by_passage = loom_admin.passages.map(function(passage){
			passage_id = passage.passage_id
			passage_clients = loom_admin.client_states.filter(function(client){return client.event.passage_id==passage.passage_id})
			return {id:passage_id, clients:passage_clients}
		})
		update_tables()
		update_passage_graph()
	}
})

socket.on("invite_codes", function(codes){
	render_codes_list(codes)
})

socket.on("update_twine_text_response", function(resp){
	console.log(resp)
	if(resp["status"] == "OK"){
		$("#new_twine_errors")[0].innerHTML = "Success!"
		window.location.reload()
	}
	else{
		$("#new_twine_errors")[0].innerHTML = resp["message"].map(function(er){return `<li> ${er} </li>`}).join("")
	}
	
})

$(document).on("change", "#auth_scheme_input", function(){
	loom_admin.story_doc.auth_scheme = $("#auth_scheme_input input:checked")[0].id.split("_")[1]
	socket.emit("update_story", loom_admin.story_doc)
})

$(document).on("change", ".admin_toggle", function(){
	socket.emit("client_admin_toggle", {story_id:loom_admin.story_id, client_id:$(this).val(), admin:$(this).is(":checked")})
})

$(document).on("change", ".added_toggle", function(){
	socket.emit("client_added_toggle", {story_id:loom_admin.story_id, user_id:$(this).val(), added:$(this).is(":checked")})
})

$(document).on("click", "#create_codes", function(){
	socket.emit("generate_codes", {story_id:loom_admin.story_id, number:$("#invite_num").val()})
})

$(document).on("change", "#jitsi_default", function(){
	val = $("#jitsi_default input:checked")[0].value
	loom_admin.story_doc.jitsi_default = val
	console.log(loom_admin.story_doc)
	socket.emit("update_story", loom_admin.story_doc)
})

$(document).on("change", "#upload_new_twine", function(){
	console.log($("#upload_new_twine").prop("files"))
	if($("#upload_new_twine").prop("files").length==1){
		$("#submit_new_twine").removeAttr("disabled")
	}
	else{
		$("#submit_new_twine").attr("disabled", true)
	}
})

$(document).on("click", "#submit_new_twine", function(){
	console.log("Click")
	var fr = new FileReader
	fr.onload = function(e){
		var auth_scheme = $("#auth_scheme_input input:checked")[0].id.split("_")[1]
		var raw_twine = e.target.result
		socket.emit("update_twine_text", {"story_id": story_id, "twine_raw":raw_twine})
	}
	var twine_file = $("#upload_new_twine").prop("files")[0]
	var story_id = twine_file.name.split(".")[0]
	fr.readAsText(twine_file)
})
