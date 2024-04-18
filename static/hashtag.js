document.getElementById('hashtag-form').addEventListener('submit', function(event) {
    event.preventDefault();
    var hashtag = document.getElementById('hashtag-input').value;
    var data = { hashtag };
    document.getElementById('loadingtweets').style.display = 'block';
    fetch('/process_hashtag', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ hashtag })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Server responded with a non-OK status');
        }
        return response.json();
    })
    .then(data => {
        document.getElementById('loadingtweets').style.display = 'none';
        if (data.status === "success") {
            window.location.href = data.redirect;
        } else if (data.status === "partialSuccess") {
            window.location.href = data.redirect;
            alert("Fetching new Tweets failed, but sentiment analysis will proceed with previously fetched data.");
        } else {
            alert("Error fetching tweets. Please try again later.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Error: " + error);
        document.getElementById('loadingtweets').style.display = 'none';
    });
});    
