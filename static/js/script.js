document.addEventListener('DOMContentLoaded', function() {
    // Function to fetch new quote on button click
    function fetchNewQuote() {
        fetch('/new')
        .then(response => response.json())
        .then(data => {
            console.log(data)
            document.querySelector('.quote').innerText = data.quote;
            document.querySelector('.sentiment').innerText = "Sentiment: " + data.sentiment;
            document.querySelector('.summary').innerText = "Summary: " + data.summary;
        })
        .catch(error => console.error('Error fetching new quote:', error));
    }

    // Event listener for 'New Quote' button click
    document.getElementById('newButton').addEventListener('click', fetchNewQuote);
});
