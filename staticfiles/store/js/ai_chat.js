document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('ai-chat-toggle');
    const closeBtn = document.getElementById('ai-chat-close');
    const chatWindow = document.getElementById('ai-chat-window');
    const chatForm = document.getElementById('ai-chat-form');
    const chatInput = document.getElementById('ai-chat-input');
    const chatMessages = document.getElementById('ai-chat-messages');

    let history = [];

    // Toggle Chat Window
    toggleBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('d-none');
        if (!chatWindow.classList.contains('d-none')) {
            chatInput.focus();
        }
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.classList.add('d-none');
    });

    // Handle Form Submission
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (!message) return;

        // Clear input
        chatInput.value = '';

        // Add user message to UI
        addMessage(message, 'user');

        // Add loading state
        const loadingId = addLoading();

        try {
            const response = await fetch('/ai/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    message: message,
                    history: history
                })
            });

            const data = await response.json();
            removeLoading(loadingId);

            if (data.response) {
                addMessage(data.response, 'ai');
                history.push({ role: 'user', text: message });
                history.push({ role: 'ai', text: data.response });
            } else if (data.error) {
                addMessage("Sorry, I'm having trouble connecting right now.", 'ai');
            }
        } catch (error) {
            removeLoading(loadingId);
            addMessage("Error: Could not reach the assistant.", 'ai');
        }
    });

    function addMessage(text, side) {
        const msgDiv = document.createElement('div');
        msgDiv.className = side === 'user' ? 'user-message mb-3 text-end' : 'ai-message mb-3';
        
        const contentClass = side === 'user' ? 'bg-dark text-white' : 'bg-white border shadow-sm';
        
        msgDiv.innerHTML = `
            <div class="${contentClass} p-3 rounded-3 d-inline-block small text-start" style="max-width: 85%;">
                ${text.replace(/\n/g, '<br>')}
            </div>
        `;
        
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addLoading() {
        const id = 'loading-' + Date.now();
        const loadingDiv = document.createElement('div');
        loadingDiv.id = id;
        loadingDiv.className = 'ai-message mb-3';
        loadingDiv.innerHTML = `
            <div class="bg-white border shadow-sm p-3 rounded-3 d-inline-block small">
                <div class="spinner-border spinner-border-sm text-secondary" role="status">
                    <span class="visually-hidden">Thinking...</span>
                </div>
            </div>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return id;
    }

    function removeLoading(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
