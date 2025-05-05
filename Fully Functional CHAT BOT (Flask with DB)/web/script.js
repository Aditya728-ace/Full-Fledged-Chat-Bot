function sendMessage() {
    const userInput = document.getElementById('user_input').value;
    const messagesDiv = document.getElementById('messages');

    if (!userInput.trim()) return;

    messagesDiv.innerHTML += `<div class="message user">USER: ${userInput}</div>`;

    fetch('/get_response', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_input: userInput })
    })
    .then(response => response.json())
    .then(data => {
        messagesDiv.innerHTML += `<div class="message bot">BOT: ${data.response}</div>`;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;

       
        
    })
    .catch(error => console.error('Error:', error));

    document.getElementById('user_input').value = '';
}

document.querySelector('.send-button').addEventListener('click', sendMessage);

document.getElementById('user_input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

function displayMessage(message, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    messageDiv.innerHTML = `<strong>${sender.toUpperCase()}: </strong>${message}`;

    document.getElementById('messages').appendChild(messageDiv);
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}

function speakResponse(response) {
    const speech = new SpeechSynthesisUtterance(response);
    speech.lang = 'en-US';
    window.speechSynthesis.speak(speech);
}

function startVoiceRecognition() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';

    recognition.onresult = function(event) {
        const userInput = event.results[0][0].transcript;
        displayMessage(userInput, 'user');

        fetch('/get_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_input: userInput })
        })
        .then(response => response.json())
        .then(data => {
            displayMessage(data.response, 'bot');
            speakResponse(data.response);
        })
        .catch(error => console.error('Error:', error));
    };

    recognition.onerror = function(event) {
        console.error('Speech recognition error:', event.error);
    };

    recognition.start();
}

window.onload = function() {
    fetch('/load_chat_history')
        .then(response => response.json())
        .then(messages => {
            messages.forEach(message => {
                displayMessage(message[0], 'user');
                displayMessage(message[1], 'bot');
            });
        })
        .catch(error => console.error('Error loading chat history:', error));
};
