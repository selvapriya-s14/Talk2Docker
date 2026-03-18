// DOM Elements - will be initialized on DOMContentLoaded
let chatMessages;
let messageInput;
let sendBtn;
let chatForm;
let loading;
let modeSelect;

// Current mode and last response
let currentMode = 'docker_engine';
let lastDockerfileResponse = null;
let requestStartTime = null;

// Use suggestion chip
function useSuggestion(text) {
    messageInput.value = text;
    messageInput.focus();
    // Hide suggestion chips after use
    const chips = document.getElementById('suggestionChips');
    if (chips) chips.style.display = 'none';
    // Auto-send
    chatForm.dispatchEvent(new Event('submit'));
}

// Show context-aware follow-up suggestions
function showFollowUpChips(tool, response) {
    const chips = document.createElement('div');
    chips.className = 'suggestion-chips';

    const suggestions = [];
    if (tool === 'docker_ps' || tool === 'docker_run') {
        suggestions.push(['📊 Show stats', 'show container stats']);
        suggestions.push(['📋 Show logs', 'show logs for ']);
        suggestions.push(['🛑 Stop container', 'stop container ']);
    }
    if (tool === 'docker_images') {
        suggestions.push(['🚀 Run image', 'run ']);
        suggestions.push(['🗑️ Remove image', 'remove image ']);
    }
    if (tool === 'docker_stop') {
        suggestions.push(['📦 List containers', 'list containers']);
        suggestions.push(['🗑️ Remove container', 'remove container ']);
    }
    if (tool === 'docker_logs') {
        suggestions.push(['🔄 Restart', 'restart container ']);
        suggestions.push(['🔍 Inspect', 'inspect container ']);
    }
    if (tool === 'docker_inspect') {
        suggestions.push(['🔌 Check ports', 'which port is container ']);
        suggestions.push(['📋 Show logs', 'show logs for ']);
    }
    // Default general suggestions
    if (suggestions.length === 0) {
        suggestions.push(['📦 List containers', 'list containers']);
        suggestions.push(['🖼️ Show images', 'show images']);
    }

    for (const [label, cmd] of suggestions) {
        const btn = document.createElement('button');
        btn.className = 'chip';
        btn.textContent = label;
        btn.onclick = () => {
            messageInput.value = cmd;
            messageInput.focus();
        };
        chips.appendChild(btn);
    }

    chatMessages.appendChild(chips);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add message to chat
function addMessage(text, sender, stages = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // Check if output should be formatted (monospace for command outputs)
    const isFormatted = text.includes('CONTAINER ID') || 
                       text.includes('Logs for') || 
                       text.includes('Error Logs:') ||
                       text.includes('📋') ||
                       text.includes('\t');
    if (isFormatted) {
        contentDiv.style.fontFamily = 'monospace';
        contentDiv.style.fontSize = '12px';
        contentDiv.style.whiteSpace = 'pre-wrap';
        contentDiv.style.wordBreak = 'break-word';
    }
    
    contentDiv.textContent = text;
    
    messageDiv.appendChild(contentDiv);
    
    // Add copy button for assistant messages
    if (sender === 'assistant') {
        const copyBtn = document.createElement('button');
        copyBtn.className = 'copy-btn';
        copyBtn.innerHTML = '📋';
        copyBtn.title = 'Copy to clipboard';
        copyBtn.onclick = () => copyToClipboard(text, copyBtn);
        messageDiv.appendChild(copyBtn);
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Copy text to clipboard
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(() => {
        const originalHTML = button.innerHTML;
        button.innerHTML = '✔️';
        button.style.color = '#28a745';
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.style.color = '';
        }, 2000);
    }).catch(err => {
        console.error('Copy failed:', err);
        button.innerHTML = '❌';
        setTimeout(() => {
            button.innerHTML = '📋';
        }, 2000);
    });
}

// Save Dockerfile
function saveDockerfile() {
    if (!lastDockerfileResponse) {
        alert('No Dockerfile to save');
        return;
    }
    
    const filename = prompt('Enter filename (without .dockerfile):', 'Dockerfile');
    if (!filename) return;
    
    // Create download link
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(lastDockerfileResponse));
    element.setAttribute('download', filename + '.dockerfile');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Update placeholder based on mode
function updatePlaceholder() {
    if (modeSelect.value === 'dockerfile') {
        messageInput.placeholder = 'Describe your app or paste a Dockerfile...';
        document.getElementById('saveDockerfileBtn').style.display = 'block';
    } else if (modeSelect.value === 'rag') {
        messageInput.placeholder = 'Ask a Docker question...';
        document.getElementById('saveDockerfileBtn').style.display = 'none';
    } else {
        messageInput.placeholder = 'Ask about Docker or give a command...';
        document.getElementById('saveDockerfileBtn').style.display = 'none';
    }
}

// Send message
function sendMessage(event) {
    event.preventDefault();
    
    const text = messageInput.value.trim();
    if (!text) return;
    
    currentMode = modeSelect.value;
    
    // Add user message
    addMessage(text, 'user');
    messageInput.value = '';
    messageInput.focus();
    
    // Show loading with dynamic status
    const loadingText = document.querySelector('#loading span:last-child');
    loading.style.display = 'flex';
    sendBtn.disabled = true;
    
    // Simulate progress stages during loading
    let stage = 0;
    const stages = ['🧠 Analyzing query...', '⚙️ Processing...', '✨ Generating response...'];
    if (loadingText) loadingText.textContent = stages[0];
    
    const stageInterval = setInterval(() => {
        stage = (stage + 1) % stages.length;
        if (loadingText) loadingText.textContent = stages[stage];
    }, 1000);
    
    // Send to backend
    requestStartTime = performance.now();
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, mode: modeSelect.value })
    })
    .then(res => res.json())
    .then(data => {
        clearInterval(stageInterval);
        loading.style.display = 'none';
        sendBtn.disabled = false;
        
        // Calculate response time
        const elapsed = ((performance.now() - requestStartTime) / 1000).toFixed(1);
        
        if (data.status !== 'success') {
            const errMsg = '❌ ' + (data.message || 'Error');
            addMessage(errMsg, 'assistant');
            return;
        }
        
        // Add agent response (clean, concise)
        const response = data.response || 'Done';
        addMessage(response + `\n⏱️ ${elapsed}s`, 'assistant');
        
        // Show context-aware follow-up chips
        const tool = data.tool || '';
        showFollowUpChips(tool, response);
        
        // Store Dockerfile if in dockerfile mode
        if (modeSelect.value === 'dockerfile' && data.dockerfile_mode === 'generate') {
            lastDockerfileResponse = response;
            document.getElementById('saveDockerfileBtn').style.display = 'block';
        }
    })
    .catch(err => {
        clearInterval(stageInterval);
        loading.style.display = 'none';
        sendBtn.disabled = false;
        const errMsg = '❌ Network error: ' + err.message;
        addMessage(errMsg, 'assistant');
    });
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements with null checks
    chatMessages = document.getElementById('chatMessages');
    messageInput = document.getElementById('messageInput');
    sendBtn = document.getElementById('sendBtn');
    chatForm = document.getElementById('chatForm');
    loading = document.getElementById('loading');
    modeSelect = document.getElementById('modeSelect');
    
    // Verify all required elements exist
    if (!chatForm || !messageInput || !sendBtn || !modeSelect) {
        console.error('ERROR: Missing required DOM elements');
        return;
    }
    
    // Set up event listeners only for elements that exist
    chatForm.addEventListener('submit', sendMessage);
    
    if (modeSelect) {
        modeSelect.addEventListener('change', updatePlaceholder);
    }
    
    // Initialize UI
    messageInput.focus();
    updatePlaceholder();
});
