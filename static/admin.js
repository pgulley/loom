///Admin page
//shows story structure
//shows client states within story structure

var loom_admin = {
	setup:false,
	story_id:document.URL.split("/")[4],
	passages:null,
	client_states:null,
	clients_sorted:null,
	graph_x_pos: []
}

function setup_table(){
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

function update_table(){
	console.log("Updating Table")
	loom_admin.passages.map(function(passage){
		passage_info = loom_admin.clients_sorted.filter(function(item){return item.id == passage.passage_id})[0]
		var num_query = `#${ passage.passage_id } .num_connected`
		var clients_query = `#${ passage.passage_id } .client_names`
		if(passage_info.clients.length > 0){
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


function get_passage_graph_node(passage){
	var position = passage.position.split(",")
	loom_admin.graph_x_pos.push(position[1])
	return `<div class="passage_node" id="node-${passage.passage_id}" style="left:${position[0]}; top:${position[1]}"> <div class="node_badge"></div> ${passage.title} </div>`
}

function setup_graph(){
	var nodes = loom_admin.passages.map(function(p){return get_passage_graph_node(p)})
	$(".passages_graph_body")[0].innerHTML = nodes.join("")
	loom_admin.passages.map(function(p){
		p.link_ids.map(function(i){
			$(`#node-${p.passage_id}`).connections({to:`#node-${i}`, class:"graph_link"})
		})
	})
	var xmin = Math.min.apply(null, loom_admin.graph_x_pos)
	var xmax = Math.max.apply(null, loom_admin.graph_x_pos)
	var xspan = xmax-xmin
	$(".passages_graph_body").height(xspan+200) 
}

function update_graph(){
	loom_admin.passages.map(function(p){
		passage_info = loom_admin.clients_sorted.filter(function(item){return item.id == p.passage_id})[0]
		num_connected = passage_info.clients.length
		if(num_connected > 0){
			$(`#node-${p.passage_id} .node_badge`).css("display", "inline-block")
			$(`#node-${p.passage_id} .node_badge`)[0].innerHTML = num_connected
		}else{
			$(`#node-${p.passage_id} .node_badge`).css("display", "none")
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
	if(loom_admin.setup == false){
		setup_table()
		setup_graph()
		loom_admin.setup = true
	}

})

socket.on("clients_present", function(clients){
	loom_admin.client_states = clients
	loom_admin.clients_sorted = loom_admin.passages.map(function(passage){
		passage_id = passage.passage_id
		passage_clients = loom_admin.client_states.filter(function(client){return client.event.passage_id==passage.passage_id})
		return {id:passage_id, clients:passage_clients}
	})
	update_table()
	update_graph()
})



