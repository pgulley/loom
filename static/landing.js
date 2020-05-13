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
})

$(document).click("#submit_code", function(){
	console.log("clickn")
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
