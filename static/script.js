document.getElementById('save_url').addEventListener('click', function() {
    const baseUrl = document.getElementById('base_url').value;
    if (baseUrl === '') {
        document.getElementById('url_message').textContent = 'Please enter a URL.';
        return;
    }
    document.getElementById('url_message').textContent = 'Processing...';
    fetch('/CreateFAISSDatabase', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_url: baseUrl })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === 'Success: FAISS Vector Database has been created.') {
            document.getElementById('url_message').textContent = data.message;
            localStorage.setItem('base_url', baseUrl);
            console.log(`URL saved to localStorage: ${baseUrl}`);
        } else {
            document.getElementById('url_message').textContent = 'Error: Could not create database.';
        }
    })
    .catch(error => {
        document.getElementById('url_message').textContent = 'Error: ' + error.message;
    });
});

document.getElementById('send_message').addEventListener('click', function() {
    const message = document.getElementById('chat_input').value;
    const baseUrl = localStorage.getItem('base_url');
    if (!baseUrl) {
        alert('Please save a URL first.');
        return;
    }
    if (message === '') {
        return;
    }
    document.getElementById('chat_input').value = '';
    addMessageToChatBox('user-message', message);

    const processingMessage = addMessageToChatBox('processing', 'Processing...');

    console.log(`Sending message with URL: ${baseUrl}`);
    fetch('/Chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ base_url: baseUrl, message: message })
    })
    .then(response => response.json())
    .then(data => {
        removeProcessingMessage(processingMessage);
        addMessageToChatBox('bot-message', data.response);
    })
    .catch(error => {
        removeProcessingMessage(processingMessage);
        addMessageToChatBox('bot-message', 'Error: ' + error.message);
    });
});

function addMessageToChatBox(className, message) {
    const messageElement = document.createElement('div');
    messageElement.className = 'message ' + className;
    messageElement.textContent = message;
    document.getElementById('chat_box').appendChild(messageElement);
    document.getElementById('chat_box').scrollTop = document.getElementById('chat_box').scrollHeight;
    return messageElement;
}

function removeProcessingMessage(messageElement) {
    if (messageElement) {
        document.getElementById('chat_box').removeChild(messageElement);
    }
}

// Debugging: Check localStorage content
window.addEventListener('load', function() {
    console.log('Stored base_url:', localStorage.getItem('base_url'));
});
