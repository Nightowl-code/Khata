// Get the checkbox element
const toggleSwitch = document.getElementById('switch');

// Add an event listener to listen for state changes
toggleSwitch.addEventListener('change', function () {
    // Show the confirm box
    message = "Are you sure you want to change the site state to " + (toggleSwitch.checked ? "live" : "offline") + "?";
    const isConfirmed = confirm(message);
    site_url = document.getElementById('superuser-login-url').innerText;
    if (isConfirmed) {
        // If confirmed, call toggleState function
        if (toggleSwitch.checked) {
            UpdateSettings(true,site_url,"site_status")
        } else {
            UpdateSettings(false,site_url,"site_status")
        }
    } else {
        // If not confirmed, revert the toggle state
        toggleSwitch.checked = !toggleSwitch.checked;
    }
});

// Function to handle toggle state
function toggleState(state,updateRequest) {
    if(updateRequest == "site_status"){
    if (state) {
        // If state is on, show alert
        alert('The site is now live');
    } else {
        // If state is off, show alert
        alert('The site is now offline');
    }
}
else{
    alert('The token has been updated');
    location.reload();
}
}

function UpdateSettings(site_state, site_url,updateRequest){
    // send the site state and site url to the server
    setRequestHeader();
    $.ajax({
        dataType: 'json',
        type: 'POST',
        url: "/update_settings",
        data: {
            site_state: site_state,
            site_url: site_url
        },
        success: function(data){
            toggleState(site_state,updateRequest);
        },
        error: function(error){
            alert("Error: " + error);
        }
    });
}

function HideShowPopUp(){
    var popup = document.getElementById("popup");
    if(popup.style.display === "none"){
        popup.style.display = "flex";
    }else{
        popup.style.display = "none";
    }
}

function updateUrlToken(){
    var token = document.getElementById('url_token').value;
    var site_status = document.getElementById('switch').checked;
    // confirm the action
    const isConfirmed = confirm("Are you sure you want to update the URL token?");
    if(!isConfirmed){
        return;
    }
    UpdateSettings(site_status, token,'token');

}

// double click url div
const myButton = document.getElementById('superuser-login-url');

myButton.addEventListener('click', function() {
    

    HideShowPopUp()
//   alert('Button double-clicked!');
  
});


