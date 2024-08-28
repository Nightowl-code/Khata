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




function updateUserList(users) {
    // Get the container where user items will be displayed
    const container = document.getElementById('userlist-container');

    // Clear the existing content
    container.innerHTML = '';

    // Create a new user box for each user in the result
    users.forEach(user => {
        // Create a new anchor element
        const userBox = document.createElement('a');
        userBox.className = 'user-box user';
        userBox.href = `/user/${user.username}`; // Adjust URL according to your routing
        
        // Create and append the username span
        const usernameSpan = document.createElement('span');
        usernameSpan.className = 'username';
        usernameSpan.textContent = user.username;
        userBox.appendChild(usernameSpan);

        // Create and append the user name span
        const userNameSpan = document.createElement('span');
        userNameSpan.className = 'user-name';
        userNameSpan.textContent = `${user.first_name} ${user.last_name}`;
        userBox.appendChild(userNameSpan);

        // Create and append the amount span with conditional styling
        const amountSpan = document.createElement('span');
        amountSpan.className = 'amount';
        amountSpan.style.fontFamily = "'Times New Roman', Times, serif";
        amountSpan.style.color = user.amount_type === 'credit' ? 'green' : 'red';
        amountSpan.textContent = Super_user? user.amount: "---";
        userBox.appendChild(amountSpan);

        // Append the user box to the container
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

