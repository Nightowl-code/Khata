TransactionData = null; // Variable to store the user data

async function getTransaction() {
    console.log("Getting users");

    setRequestHeader(); // Set the CSRF token in the header

    try {
        TransactionData = await $.ajax({
            dataType: 'json',
            type: 'POST',
            url: "/hisab",
            data: {},
        });
        // console.log("Success:", TransactionData);
    } catch (error) {
        alert("Error: " + error);
        TransactionData = null; // Set to null in case of an error
    }
}

// Call the function to fetch and store the data
(async () => {
    await getTransaction();
    console.log(TransactionData); 
})();


function updateTransactionList(filteredData) {
    var container = document.getElementById('transactionlist-container');
    container.innerHTML = ''; // Clear existing content

    filteredData.forEach(function(transaction) {
        var transactionElement = document.createElement('a');
        transactionElement.className = 'transaction-box transaction';
        transactionElement.href = `/hisab/${transaction.id}`; // Adjust URL as needed

        transactionElement.innerHTML = `
            <span class="transactionname">${transaction.date}</span>
            <span class="transaction-name">
                ${transaction.party.username} [${transaction.party.first_name}]
            </span>
            <span class="amount"
                style="font-family:'Times New Roman', Times, serif; color:${transaction.type === 'credit' ? 'green' : 'red'};">
                ${transaction.amount}
            </span>
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
    var fromdate = document.getElementById('from-date').value;
    var todate = document.getElementById('to-date').value;
    var party = document.getElementById('party').value;
    var upperLimit = document.getElementById('Upper_amount').value;
    var lowerLimit = document.getElementById('Lower_amount').value;

    if(fromdate == '' && todate == '' && party == '' && upperLimit == '' && lowerLimit == '') {
        updateTransactionList(TransactionData);
        var filter_box = document.getElementById('pop-up');
        filter_box.style.display = 'none';
        return;
    }
    if(fromdate != '' && todate != '' && fromdate > todate) {
        alert('From date should be less than To date');
        return;
    }
    if(upperLimit != '' && lowerLimit != '' && upperLimit < lowerLimit) {
        alert('Upper limit should be greater than lower limit');
        return;
    }

    // use the TransactionDate to filter the data
    var filteredData = TransactionData;
    if(fromdate != '') {
        filteredData = filteredData.filter(function(item) {
            return item.date >= fromdate;
        });
    }
    if(todate != '') {
        filteredData = filteredData.filter(function(item) {
            return item.date <= todate;
        });
    }

    // Filter the data based on the search value
    if (party !== '') {
        // match party with usernames
        filteredData = filteredData.filter(function(item) {
            return item.party.username === party;
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