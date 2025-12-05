// *** CONFIGURATION ***
const WEBSOCKET_URL = 'ws://localhost:8000/vehicle-position';
// *********************

// Get DOM elements
const output = document.getElementById('output');
const input = document.getElementById('input');
let socket;

/**
 * Logs a message to the output text area.
 * @param {string} message - The message to log.
 * @param {string} type - 'system', 'server', 'client', or 'error'.
 */
function log(message, type = 'system') {
    const timestamp = new Date().toLocaleTimeString();
    output.value += `[${timestamp}][${type.toUpperCase()}] ${message}\n`;
    // Scroll to the bottom
    output.scrollTop = output.scrollHeight;
}

/**
 * Establishes the WebSocket connection.
 */
function connect() {
    log(`Attempting to connect to ${WEBSOCKET_URL}...`);
    // 1. Create a new WebSocket instance
    socket = new WebSocket(WEBSOCKET_URL);

    // 2. Define event handlers

    // Connection established
    socket.onopen = function(e) {
        log('Successfully connected!', 'system');
    };

    // Message received from the server
    socket.onmessage = function(event) {
        log(`Received: ${event.data}`, 'server');
    };

    // Connection closed
    socket.onclose = function(event) {
        if (event.wasClean) {
            log(`Connection closed cleanly, code=${event.code}`, 'system');
        } else {
            log('Connection died unexpectedly (e.g., server process killed).', 'error');
        }
    };

    // Error occurred
    socket.onerror = function(error) {
        // The browser will often close the connection immediately after an error
        log(`Error: ${error.message}`, 'error');
    };
}

/**
 * Sends the message from the input field to the server.
 * This function is called by the button's 'onclick' attribute in index.html.
 */
function sendMessage() {
    const message = input.value;
    // Check if a message exists and the socket is open (readyState === 1)
    if (!message || !socket || socket.readyState !== WebSocket.OPEN) {
        log('Cannot send: Not connected or no message.', 'system');
        return;
    }
    
    // Send the message
    socket.send(message);
    log(`Sent: ${message}`, 'client');
    input.value = ''; // Clear the input field
}

// Connect automatically when the page loads
window.onload = connect;
