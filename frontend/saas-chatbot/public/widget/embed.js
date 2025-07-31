(function() {
    'use strict';
    
    // Get configuration from script tag
    const scripts = document.getElementsByTagName('script');
    const currentScript = scripts[scripts.length - 1];
    const chatbotId = currentScript.getAttribute('data-chatbot-id');
    const chatbotUrl = currentScript.getAttribute('data-chatbot-url') || 'http://localhost:3000';
    
    if (!chatbotId) {
        console.error('AI Chatbot: Missing data-chatbot-id attribute');
        return;
    }
    
    // Prevent multiple instances
    if (window.AIChatbotWidget) {
        console.warn('AI Chatbot: Widget already loaded');
        return;
    }
    
    // Widget class
    class AIChatbotWidget {
        constructor(chatbotId, baseUrl) {
            this.chatbotId = chatbotId;
            this.baseUrl = baseUrl;
            this.isOpen = false;
            this.isLoaded = false;
            this.messages = [];
            this.websocket = null;
            
            this.init();
        }
        
        async init() {
            try {
                // Load chatbot configuration
                await this.loadConfig();
                
                // Create widget elements
                this.createWidget();
                
                // Set up event listeners
                this.setupEventListeners();
                
                // Connect to websocket for real-time chat
                this.connectWebSocket();
                
                this.isLoaded = true;
            } catch (error) {
                console.error('AI Chatbot: Failed to initialize', error);
            }
        }
        
        async loadConfig() {
            const response = await fetch(`${this.baseUrl}/api/chatbots/${this.chatbotId}`);
            if (!response.ok) {
                throw new Error('Failed to load chatbot configuration');
            }
            this.config = await response.json();
        }
        
        createWidget() {
            // Create container
            this.container = document.createElement('div');
            this.container.id = 'ai-chatbot-widget';
            this.container.innerHTML = this.getWidgetHTML();
            
            // Add styles
            this.addStyles();
            
            // Append to body
            document.body.appendChild(this.container);
            
            // Get references to elements
            this.chatWindow = this.container.querySelector('.chatbot-window');
            this.toggleButton = this.container.querySelector('.chatbot-toggle');
            this.messagesContainer = this.container.querySelector('.chatbot-messages');
            this.inputField = this.container.querySelector('.chatbot-input');
            this.sendButton = this.container.querySelector('.chatbot-send');
        }
        
        getWidgetHTML() {
            const position = this.config.appearance_config?.position || 'bottom-right';
            const primaryColor = this.config.appearance_config?.primaryColor || '#3b82f6';
            const botName = this.config.appearance_config?.botName || 'Assistant';
            const greeting = this.config.appearance_config?.greetingMessage || 'Hello! How can I help you?';
            
            return `
                <div class="chatbot-container chatbot-${position}">
                    <div class="chatbot-window" style="display: none;">
                        <div class="chatbot-header" style="background-color: ${primaryColor};">
                            <div class="chatbot-header-content">
                                <div class="chatbot-avatar"></div>
                                <div class="chatbot-info">
                                    <div class="chatbot-name">${botName}</div>
                                    <div class="chatbot-status">Online</div>
                                </div>
                            </div>
                            <button class="chatbot-close">&times;</button>
                        </div>
                        <div class="chatbot-messages">
                            <div class="chatbot-message chatbot-message-bot">
                                <div class="chatbot-message-content">${greeting}</div>
                            </div>
                        </div>
                        <div class="chatbot-input-container">
                            <input type="text" class="chatbot-input" placeholder="Type your message..." />
                            <button class="chatbot-send" style="background-color: ${primaryColor};">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <line x1="22" y1="2" x2="11" y2="13"></line>
                                    <polygon points="22,2 15,22 11,13 2,9"></polygon>
                                </svg>
                            </button>
                        </div>
                    </div>
                    <button class="chatbot-toggle" style="background-color: ${primaryColor};">
                        <svg class="chatbot-icon-chat" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="m3 21 1.9-5.7a8.5 8.5 0 1 1 3.8 3.8z"></path>
                        </svg>
                        <svg class="chatbot-icon-close" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: none;">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
            `;
        }
        
        addStyles() {
            if (document.getElementById('ai-chatbot-styles')) return;
            
            const styles = document.createElement('style');
            styles.id = 'ai-chatbot-styles';
            styles.textContent = `
                #ai-chatbot-widget {
                    position: fixed;
                    z-index: 999999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                
                .chatbot-container {
                    display: flex;
                    flex-direction: column;
                    align-items: flex-end;
                }
                
                .chatbot-bottom-right { bottom: 20px; right: 20px; }
                .chatbot-bottom-left { bottom: 20px; left: 20px; align-items: flex-start; }
                .chatbot-top-right { top: 20px; right: 20px; }
                .chatbot-top-left { top: 20px; left: 20px; align-items: flex-start; }
                
                .chatbot-window {
                    width: 350px;
                    height: 500px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.15);
                    display: flex;
                    flex-direction: column;
                    margin-bottom: 10px;
                    animation: chatbot-slide-up 0.3s ease-out;
                }
                
                @keyframes chatbot-slide-up {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                
                .chatbot-header {
                    padding: 16px;
                    border-radius: 12px 12px 0 0;
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                
                .chatbot-header-content {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .chatbot-avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.2);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .chatbot-name {
                    font-weight: 600;
                    font-size: 14px;
                }
                
                .chatbot-status {
                    font-size: 12px;
                    opacity: 0.9;
                }
                
                .chatbot-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 4px;
                    border-radius: 4px;
                }
                
                .chatbot-close:hover {
                    background: rgba(255, 255, 255, 0.1);
                }
                
                .chatbot-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 16px;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                
                .chatbot-message {
                    display: flex;
                    max-width: 80%;
                }
                
                .chatbot-message-bot {
                    justify-content: flex-start;
                }
                
                .chatbot-message-user {
                    justify-content: flex-end;
                    align-self: flex-end;
                }
                
                .chatbot-message-content {
                    padding: 8px 12px;
                    border-radius: 12px;
                    font-size: 14px;
                    line-height: 1.4;
                }
                
                .chatbot-message-bot .chatbot-message-content {
                    background: #f1f5f9;
                    color: #334155;
                }
                
                .chatbot-message-user .chatbot-message-content {
                    background: var(--chatbot-primary-color, #3b82f6);
                    color: white;
                }
                
                .chatbot-input-container {
                    padding: 16px;
                    border-top: 1px solid #e2e8f0;
                    display: flex;
                    gap: 8px;
                }
                
                .chatbot-input {
                    flex: 1;
                    padding: 10px 12px;
                    border: 1px solid #e2e8f0;
                    border-radius: 8px;
                    font-size: 14px;
                    outline: none;
                }
                
                .chatbot-input:focus {
                    border-color: var(--chatbot-primary-color, #3b82f6);
                }
                
                .chatbot-send {
                    padding: 10px 12px;
                    border: none;
                    border-radius: 8px;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .chatbot-send:hover {
                    opacity: 0.9;
                }
                
                .chatbot-toggle {
                    width: 56px;
                    height: 56px;
                    border: none;
                    border-radius: 50%;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
                    transition: transform 0.2s ease;
                }
                
                .chatbot-toggle:hover {
                    transform: scale(1.05);
                }
                
                @media (max-width: 480px) {
                    .chatbot-window {
                        width: 100vw;
                        height: 100vh;
                        border-radius: 0;
                        margin: 0;
                    }
                    
                    .chatbot-container {
                        top: 0 !important;
                        left: 0 !important;
                        right: 0 !important;
                        bottom: 0 !important;
                    }
                }
            `;
            
            document.head.appendChild(styles);
        }
        
        setupEventListeners() {
            // Toggle button
            this.toggleButton.addEventListener('click', () => {
                this.toggle();
            });
            
            // Close button
            this.container.querySelector('.chatbot-close').addEventListener('click', () => {
                this.close();
            });
            
            // Send button
            this.sendButton.addEventListener('click', () => {
                this.sendMessage();
            });
            
            // Enter key
            this.inputField.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.sendMessage();
                }
            });
        }
        
        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }
        
        open() {
            this.isOpen = true;
            this.chatWindow.style.display = 'flex';
            this.toggleButton.querySelector('.chatbot-icon-chat').style.display = 'none';
            this.toggleButton.querySelector('.chatbot-icon-close').style.display = 'block';
            this.inputField.focus();
        }
        
        close() {
            this.isOpen = false;
            this.chatWindow.style.display = 'none';
            this.toggleButton.querySelector('.chatbot-icon-chat').style.display = 'block';
            this.toggleButton.querySelector('.chatbot-icon-close').style.display = 'none';
        }
        
        async sendMessage() {
            const message = this.inputField.value.trim();
            if (!message) return;
            
            // Add user message
            this.addMessage(message, 'user');
            this.inputField.value = '';
            
            // Send to API
            try {
                const response = await fetch(`${this.baseUrl}/api/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        message,
                        chatbot_id: this.chatbotId
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    this.addMessage(data.message, 'bot');
                } else {
                    this.addMessage('Sorry, I\'m having trouble responding right now.', 'bot');
                }
            } catch (error) {
                this.addMessage('Sorry, I\'m having trouble connecting.', 'bot');
            }
        }
        
        addMessage(content, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `chatbot-message chatbot-message-${sender}`;
            messageDiv.innerHTML = `<div class="chatbot-message-content">${content}</div>`;
            
            this.messagesContainer.appendChild(messageDiv);
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
        
        connectWebSocket() {
            // WebSocket connection for real-time features
            // Implementation would go here for real-time updates
        }
    }
    
    // Initialize widget
    window.AIChatbotWidget = new AIChatbotWidget(chatbotId, chatbotUrl);
})();
