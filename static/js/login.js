document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    var data = { username, password };
    document.getElementById('loadingSpinner').style.display = 'block';

    fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            window.location.href = data.redirect;
        } else {
            alert("Login Failed: " + data.message);
        }
        document.getElementById('loadingSpinner').style.display = 'none';
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Error: " + error);
        document.getElementById('loadingSpinner').style.display = 'none';
    });
});

