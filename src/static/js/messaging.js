
const currRoom = window.djangoVars.currRoom;
const userId = window.djangoVars.userId;
const organizationId = window.djangoVars.organizationId;
const csrfToken = window.djangoVars.csrfToken;
const options = {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "numeric",
    timeZone: "UTC",
    hour12: true
};

var send_messages = true;
const chatContainer = document.getElementById('chatContainer');
function scrollToBottom() {
    var chatContainer = document.getElementById("chatContainer");
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function sendMessage() {
    const messageBody = messageInput.value;
    if (messageBody.trim() === '') return;  // Don't send empty messages
    document.getElementById("sendMsgButton").textContent = "Sending...";
    document.getElementById("sendMsgButton").disabled = true;
    send_messages = false
    messageInput.value = '';
    // Send message data to the server
                fetch('send_message/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken // Django CSRF token for security
                    },
                    body: JSON.stringify({
                        message_body: messageBody
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        send_messages = true
                        messageInput.value = '';  // Clear the input field
                        fetchData();                     
                    } else {
                        console.error('Message failed to send');
                    }
                })
                .catch(error => console.error('Error:', error));
            }


function fetchData() {
    fetch('get_new_messages/')
        .then(response => response.json())
        .then(messages => {
            chatContainer.innerHTML = '';  // Clear the chat container before adding new messages

            // Loop through each message and add it to the chat container
            messages.forEach(message => {
                const sender = message.sender_id;
                const date = new Date(message.time);
                const formattedDate = new Intl.DateTimeFormat("en-US", options).format(date);
                const messageItem = document.createElement('div');
                if (sender == userId || sender == organizationId){
                    messageItem.className = 'message-item has-text-right';
                }else{
                    messageItem.className = 'message-item has-text-left';
                }
                            
                // Create the inner HTML structure
                messageItem.innerHTML = `
                    <p><strong>${message.sender_name}:</strong> ${message.message_body}</p>
                    <p class="is-size-7 has-text-grey">${formattedDate}</p>
                `;

                chatContainer.appendChild(messageItem);
                chatContainer.appendChild(document.createElement('hr'));
            });

            // Optionally, scroll to the latest message
            chatContainer.scrollTop = chatContainer.scrollHeight;
            if(send_messages){
                document.getElementById("sendMsgButton").disabled = false;
                document.getElementById("sendMsgButton").textContent = "Send";
            }
        })
        .catch(error => console.error('Error:', error));
}

if(currRoom){
    setInterval(fetchData, 1000);  // Call fetchData every second
}
            

document.addEventListener("DOMContentLoaded", function() {
    // Get all list items

    const roomItems = document.querySelectorAll("#room-list .list-group-item");
        
    roomItems.forEach(item => {
        item.addEventListener("click", function() {
            // Get room ID from data attribute
            const roomId = item.getAttribute("data-room-id");
            const orgId = item.getAttribute("org-id");
            const url = item.getAttribute("url").replace("ROOM_ID", roomId).replace("ORG_ID", orgId);;
            window.location.href = url;                        
        });
    });
});

$(document).ready(function() {
    $('#organization').select2({
        placeholder: 'Search and select an organization',
        allowClear: true,
        width: '100%',
        dropdownParent: $('#newConversationModal')  // Attach dropdown to modal
    });

    $('#newConversationModal').on('shown.bs.modal', function () {
        $('#organization').select2('focus');  // Focus Select2 input manually
    });
});
            