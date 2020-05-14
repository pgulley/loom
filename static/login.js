
$(document).on("click","#submit",function(){
	var uname = $("#uname").val()
	var pass = $("#pword").val()
	if(uname!="" && pass!=""){
		$.ajax({
			url:"/login",
			method:"POST",
			mimeType:'json',
			data:{"user":uname, "pass":pass}
		})
		.done(function(resp){
			if(resp["Status"]=="OK"){
				window.location.replace("/")
			}else{
				$("#login_errors")[0].innerHTML = "Bad Login"
			}
		})
	}
	else{
		$("#login_errors")[0].innerHTML = "field cannot be empty"
	}
})

var socket = io()
socket.on('connect', function() {
	console.log("connected!")
})

$(document).on("click", "#create_user", function(){
	console.log("clicked create")
	$("#create_user_errors")[0].innerHTML = ""
	var uname = $("#create_uname").val()
	var pass = $("#create_pword").val()
	if(uname!="" && pass!=""){
		socket.emit("create_user", {"uname":uname, "pass":pass})
	}else{
		$("#create_user_errors")[0].innerHTML = "Field cannot be empty"
	}
})

socket.on("create_user_response", function(resp){
	if(resp["status"] == "OK"){
		$("#create_user_errors")[0].innerHTML = "Success! You can now log in. "
	}else{
		$("#create_user_errors")[0].innerHTML = resp["error"]
	}
})