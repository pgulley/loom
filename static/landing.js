var logged_in_user = null
$.ready(function(){
	logged_in_user = $("#logged_in_user")[0].innerHTML
}) 

function render_user_table(user_list){
	user_table = user_list.map(function(user){
		return `<tr class="user" id='user_${user.user_id}'> 
			<td> 
				${ user.username } 
			</td>
			<td>
				<input type="checkbox" value="${ user.username }" class="admin_toggle" 
				${(user.admin ? "checked":"")} ${(user.username==logged_in_user ? "disabled" :"")}}>
			</td>
		</tr>`
	}).join("")
	$("#user_table")[0].innerHTML = user_table
}

function render_story_list(storylist){
	twines =  storylist.map(function(twine){
		return `<div class="box_content twine_entry"> 
			<h3>${ twine.story.title }</h3>
			<a href="/twine/${ twine.story.story_id }"> play story </a> </br>
			${ (twine.admin ? `<a class="admin_link" href="/twine/{{ twine.story.story_id }}/admin"> admin view </a>` : '')}
		</div>`
	}).join("")
	$("#twines_list")[0].innerHTML = twines
}

var socket = io()
socket.on('connect', function() {
	console.log("connected!")
})

socket.on("create_user_response", function(resp){
	if(resp["status"] == "OK"){
		render_user_table(resp["users"])
	}else{
		$("#create_user_errors")[0].innerHTML = resp["error"]
	}
})

socket.on("validate_code_response", function(resp){
	console.log(resp)
	$("#code_errors")[0].innerHTML = resp["message"]
	if(resp["stories"] != null){
		render_story_list(resp["stories"])
	}
})

socket.on("new_twine_response", function(resp){
	console.log(resp)
	if(resp["stories"] != null){
		render_story_list(resp["stories"])
	}
	
})

$(document).on("click","#submit_code", function(){
	$("#code_errors")[0].innerHTML = ""
	var code = $("#code").val()
	socket.emit("validate_code", code)
})

$(document).on("click", "#submit_user", function(){
	$("#create_user_errors")[0].innerHTML = ""
	var uname = $("#uname").val()
	var pass = $("#pword").val()
	if(uname!="" && pass!=""){
		socket.emit("create_user", {"uname":uname, "pass":pass})
	}else{
		$("#create_user_errors")[0].innerHTML = "Field cannot be empty"
	}
})

$(document).on("change", ".admin_toggle", function(){
	socket.emit("user_admin_toggle", {user:$(this).val(), admin:$(this).is(":checked")})
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
		socket.emit("new_twine", {"story_id": story_id, "twine_raw":raw_twine, "auth_scheme":auth_scheme })
	}
	var twine_file = $("#upload_new_twine").prop("files")[0]
	var story_id = twine_file.name.split(".")[0]
	fr.readAsText(twine_file)
	
})