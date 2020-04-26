///Admin page
//shows story structure
//shows client states within story structure

var loom_admin = {
	story_id:document.URL.split("/")[4],
	passages:null,
	client_states:null,
	clients_sorted:null
}

function setup_table(){
	table_rows = loom_admin.passages.map(function(passage){
		return `<tr id="${passage.passage_id}">
			<td class="passage_title"> ${passage.title} </td>
			<td class="num_connected"> </td>
			<td class="client_names"> </td>
		</tr>`
	})

	$(".passages").append( 
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

function update_table(){
	console.log("Updating Table")
	loom_admin.passages.map(function(passage){
		passage_info = loom_admin.clients_sorted.filter(function(item){return item.id == passage.passage_id})[0]
		console.log(passage_info)

		var num_query = `#${ passage.passage_id } .num_connected`
		var clients_query = `#${ passage.passage_id } .client_names`
		console.log(num_query)
		console.log(clients_query)
		if(passage_info.clients.length > 0){
			console.log(passage_info)
			var clients = passage_info.clients.map(function(c){return c.client.username})
			$(num_query)[0].innerHTML = passage_info.clients.length
			$(clients_query)[0].innerHTML = clients
		}
		else{
			$(num_query)[0].innerHTML = "0"
			$(clients_query)[0].innerHTML = " "
		}
		
	})
}


var socket = io(`/${loom_admin.story_id}`)
socket.on('connect', function() {
	socket.emit("get_story_structure", loom_admin.story_id)
	socket.emit("get_client_locations", loom_admin.story_id)
})

socket.on("story_structure", function(structure){
	loom_admin.passages = structure
	setup_table()
})

socket.on("clients_present", function(clients){
	loom_admin.client_states = clients
	loom_admin.clients_sorted = loom_admin.passages.map(function(passage){
		passage_id = passage.passage_id
		passage_clients = loom_admin.client_states.filter(function(client){return client.event.passage_id==passage.passage_id})
		return {id:passage_id, clients:passage_clients}
	})
	console.log(loom_admin)
	update_table()
})



