UserData = null; // Variable to store the user data
Super_user = false; // Variable to store the user type

async function getUsers() {
    console.log("Getting users");

    setRequestHeader(); // Set the CSRF token in the header

    try {
        Data = await $.ajax({
            dataType: 'json',
            type: 'POST',
            url: "/users",
            data: {},
        });
        // console.log("Success:", UserData);
        UserData = Data['users_data'];
        Super_user = Data['user_type'];
        // console.log("Success:", UserData);
    } catch (error) {
        alert("Error: " + error);
        UserData = null; // Set to null in case of an error
    }
}

// Call the function to fetch and store the data
(async () => {
    await getUsers();
    console.log(UserData); 
    console.log(Super_user);
})();




function updateUserList(users, isSuperUser) {
    // Get the container where user items will be displayed
    const container = document.getElementById('userlist-container');

    // Clear the existing content
    container.innerHTML = '';

    // Create a new user box for each user in the result
    users.forEach(user => {
        // Create a new table row
        const userBox = document.createElement('tr');
        userBox.className = 'user-box user';

        // Create and append the username cell
        const usernameTd = document.createElement('td');
        usernameTd.className = 'username';
        const usernameLink = document.createElement('a');
        usernameLink.href = `/user/${user.username}`;
        usernameLink.textContent = `${user.username} [${user.is_active ? "Active" : "Inactive"}]`;
        usernameTd.appendChild(usernameLink);
        userBox.appendChild(usernameTd);

        // Create and append the user name cell
        const userNameTd = document.createElement('td');
        userNameTd.className = 'user-name';
        const nameLink = document.createElement('a');
        nameLink.href = `/user/${user.username}`;
        nameLink.textContent = user.first_name || user.last_name ? `${user.first_name} ${user.last_name}` : "---";
        userNameTd.appendChild(nameLink);
        userBox.appendChild(userNameTd);

        // Create and append the amount cell with conditional styling
        const amountTd = document.createElement('td');
        amountTd.className = 'amount';
        const amountLink = document.createElement('a');
        amountLink.href = `/user/${user.username}`;
        amountLink.style.fontFamily = "'Times New Roman', Times, serif";
        amountLink.style.color = user.amount_type === 'credit' ? 'green' : 'red';
        amountLink.textContent = Super_user ? parseFloat(user.amount).toFixed(2) : "---";
        amountTd.appendChild(amountLink);
        userBox.appendChild(amountTd);

        // Append the user row to the container
        container.appendChild(userBox);
    });
}




// when something is changed in the search-box
$("#search-box").on("input", GetUpdatedData);

// when something is changed in the sort-box
$("#sort-box").on("change", GetUpdatedData);

// when something is changed in the order-box
$("#order-box").on("change", GetUpdatedData);

function GetUpdatedData() {
    // console.log("Search box changed");
    // console.log("Userdata:", UserData);
    result=searchInFields(UserData, $("#search-box").val());
    // oder by value in sort-box
    if ($("#sort-box").val() == "username") {
        result.sort((a, b) => a.username.localeCompare(b.username));
    } else if ($("#sort-box").val() == "amount") {
        result.sort((a, b) => a.amount - b.amount);
    } else if ($("#sort-box").val() == "name") {
        // compare both first_name and last_name
        result.sort((a, b) => {
            if (a.first_name == b.first_name) {
                return a.last_name.localeCompare(b.last_name);
            } else {
                return a.first_name.localeCompare(b.first_name);
            }
        });
    }

    // order in decending if the value in order-box is desc
    if ($("#order-box").val() == "desc") {
        result.reverse();
    }
    // console.log("Result:", result);
    // console.log("Search box value:", $("#search-box").val());
    updateUserList(result);
}


// Function to search for a text in specific fields
function searchInFields(data, searchText) {
    // Convert searchText to lowercase for case-insensitive search
    const lowerCaseSearchText = searchText.toLowerCase();

    return data.filter(item => {
        // Convert fields to lowercase and check if searchText is included
        return (item.username.toLowerCase().includes(lowerCaseSearchText) ||
                item.first_name.toLowerCase().includes(lowerCaseSearchText) ||
                item.last_name.toLowerCase().includes(lowerCaseSearchText));
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

function VerifyDate(){
    var date = document.getElementById("block_date").value;
    var dateInput = new Date(date);
    var currentDate = new Date();
    if(dateInput > currentDate || dateInput == "Invalid Date"){
        alert("Please select a valid date");
        return false;
    }
    return true;
}

function clearBlockDate(username){
    if(confirm("Do u want to clear block date of all users?") == false){
        return;
    }
    // send the username to the server
    setRequestHeader();
    $.ajax({
        dataType: 'json',
        type: 'POST',
        url: "/clear_block_date",
        data: {
            username: username
        },
        success: function(data){
            alert(data.status);
            location.reload();
        },
        error: function(error){
            alert("Error: " + error);
        }
    });
}