
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
