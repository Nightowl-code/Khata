UserData = null; // Variable to store the user data

async function getTransaction() {
    console.log("Getting users");

    setRequestHeader(); // Set the CSRF token in the header

    try {
        UserData = await $.ajax({
            dataType: 'json',
            type: 'POST',
            url: "/hisab",
            data: {},
        });
        // console.log("Success:", TransactionData);
    } catch (error) {
        alert("Error: " + error);
        UserData = null; // Set to null in case of an error
    }
}

// Call the function to fetch and store the data
(async () => {
    await getTransaction();
    console.log(UserData); 
})();


function updateTransactionList(filteredData) {
    var container = document.getElementById('transactionlist-container');
    container.innerHTML = ''; // Clear existing content

    filteredData.forEach(function(user) {
        var transactionElement = document.createElement('tr');
        transactionElement.className = 'transaction-box transaction';

        transactionElement.innerHTML = `
            <td class="user-username">${user.username}</td>
            <td class="user-name">
                ${user.first_name} ${user.last_name}
            </td>
            <td class="user-amount"
                style="font-family:'Times New Roman', Times, serif; color:${user.amount_type === 'credit' ? 'green' : 'red'};">
                ${parseFloat(user.amount.toFixed(4))}
            </td>
        `;
        container.appendChild(transactionElement);
    });
}

document.getElementById('filter-button').onclick = function() {
    var filter_box = document.getElementById('pop-up');
    filter_box.style.display = 'block';
}

document.getElementById('filter-button-clear').onclick = function() {
    var filter_box = document.getElementById('pop-up');
    filter_box.style.display = 'none';
}

document.getElementById('filter-button-apply').onclick = function() {
    filteredData = UserData;
    var party = document.getElementById('party').value;
    var upperLimit = document.getElementById('Upper_amount').value;
    var lowerLimit = document.getElementById('Lower_amount').value;

    if(party == '' && upperLimit == '' && lowerLimit == '') {
        updateTransactionList(UserData);
        var filter_box = document.getElementById('pop-up');
        filter_box.style.display = 'none';
        return;
    }
    console.log(party, upperLimit, lowerLimit,parseInt(upperLimit)<parseInt(lowerLimit));
    if(upperLimit != '' && lowerLimit != '' && parseInt(upperLimit)<parseInt(lowerLimit)) {
        alert('Upper limit should be greater than lower limit');
        return;
    }

    // Filter the data based on the search value
    if (party !== '') {
        // match party with usernames
        filteredData = filteredData.filter(function(item) {
            return item.username === party;
        });
    }
    if(upperLimit != '') {
        filteredData = filteredData.filter(function(item) {
            return item.amount <= upperLimit;
        });
    }
    if(lowerLimit != '') {
        filteredData = filteredData.filter(function(item) {
            return item.amount >= lowerLimit;
        });
    }

    // console.log(filteredData);
    updateTransactionList(filteredData);
    var filter_box = document.getElementById('pop-up');
    filter_box.style.display = 'none';

}

function downloadFile() {
    const type = document.getElementById('download-choice').value;
    console.log(type);

    // Map UserData to only include full name and amount
    const filteredData = UserData.map(item => ({
        full_name: item.first_name + " " + item.last_name,
        amount: item.amount
    }));

    if (type === 'excel') {
        // Convert filtered data to Excel
        const worksheet = XLSX.utils.json_to_sheet(filteredData);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "UserData");
        XLSX.writeFile(workbook, "UserData.xlsx");

    } else if (type === 'pdf') {
        // Convert filtered data to PDF
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();

        const columns = ["Full Name", "Amount"];
        const rows = filteredData.map(item => [
            item.full_name, item.amount
        ]);

        // Add table to PDF
        doc.autoTable({
            head: [columns],
            body: rows
        });

        doc.save('UserData.pdf');
    } else {
        console.error('Invalid type passed. Expected "excel" or "pdf".');
    }
}


function HideShowDownloadWindow(){
    var popup = document.getElementById("popup");
    if(popup.style.display === "none"){
        popup.style.display = "flex";
    }else{
        popup.style.display = "none";
    }
}