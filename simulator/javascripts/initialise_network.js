//Copyright [2020] [Indian Institute of Science, Bangalore]
//SPDX-License-Identifier: Apache-2.0

function loadJSON_001(file_path) {

    const xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', file_path, false); // Replace 'my_data' with the path to your file
	xobj.send(null);  
    ///xobj.onreadystatechange = function () {
          if (xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            return xobj.responseText;
         }
   // };
    
 }
 
function read_json(file_path) 
 {
  // Parse JSON string into object
     const response = loadJSON_001(file_path);
     console.log(response);
     const actual_JSON = JSON.parse(response);

     console.log(actual_JSON.length)
 }

//var slider = document.getElementById("myRange");
//var output = document.getElementById("slider_demo");
//output.innerHTML = slider.value; // Display the default slider value

// Update the current slider value (each time you drag the slider handle)
//slider.oninput = function() {
//  output.innerHTML = this.value;
//}