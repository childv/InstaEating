// Javascript to drive dynamic frontend
// Veronica Child, July 2017

// Displays post info on button click
function loadPost(){
	var atSignsArray = json_data.post.at_signs;
	var arrLength = atSignsArray.length;
	// Displays associated '@' signs if present
	if (arrLength != 0) {
		$("#at_signs").append("Find at: ");
		for (var i = 0; i < arrLength; i++) {
			// alert(atSignsArray[i]);
			console.log(atSignsArray[0]);
			console.log("Hi");
			// end of list
			if (i == (arrLength - 1)) {
				$("#at_signs").append(atSignsArray[i]);
			} else {
				$("#at_signs").append(atSignsArray[i] + ", ");
			}
		}
	}
	// Show div
	$('#displayPost').show();
}