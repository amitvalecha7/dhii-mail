
import { LitElement, html, css } from 'lit';
import { A2UIClient } from '@a2ui/lit';
import { A2AClient } from '@a2a-js/sdk';
import { frontendConfig } from './config.js';
import './components/MeetingDashboard.js'; // Register Custom Components

export class MeetingAssistantApp extends LitElement {
    static properties = {
        isLoading: { type: Boolean },
        errorMessage: { type: String },
        connectionStatus: { type: String },
        chatMessages: { type: Array },
        userEmail: { type: String }
    };

    static styles = css`
        :host {
            display: block;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #333;
        }

        .app-container {
            display: flex;
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .sidebar {
            width: 250px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-right: 1px solid rgba(255, 255, 255, 0.2);
            padding: 20px;
            display: flex;
            flex-direction: column;
        }

        .main-content {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            position: relative;
        }

        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 20px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }

        .content-area {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
        }

        .chat-panel {
            width: 350px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-left: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            flex-direction: column;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }

        .message {
            padding: 10px 15px;
            border-radius: 12px;
            max-width: 85%;
            word-wrap: break-word;
        }

        .message.user {
            background: rgba(255, 255, 255, 0.2);
            align-self: flex-end;
            color: white;
        }

        .message.assistant {
            background: rgba(255, 255, 255, 0.9);
            align-self: flex-start;
            color: #333;
        }

        .chat-input-area {
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            gap: 10px;
        }

        input[type="text"] {
            flex: 1;
            padding: 10px;
            border-radius: 8px;
            border: none;
            background: rgba(255, 255, 255, 0.9);
        }

        button {
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            background: #4F46E5;
            color: white;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover {
            background: #4338ca;
        }

        .nav-item {
            display: block;
            padding: 12px 16px;
            margin: 4px 0;
            background: rgba(255, 255, 255, 0.1);
            border: none;
            border-radius: 8px;
            color: white;
            cursor: pointer;
            text-align: left;
            width: 100%;
        }

        .nav-item:hover {
            background: rgba(255, 255, 255, 0.2);
        }

        .loading-overlay {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 1000;
        }
        
        #a2ui-root {
            height: 100%;
        }
    `;

    constructor() {
        super();
        this.isLoading = false;
        this.errorMessage = '';
        this.connectionStatus = 'Disconnected';
        this.chatMessages = [];
        this.userEmail = '';

        this.a2uiClient = null;
        this.a2aClient = null;
        this.websocket = null;
        this.sessionId = null;
    }

    async firstUpdated() {
        // Initialize logic after DOM is ready
        const userConfig = frontendConfig.getUserConfig();
        this.userEmail = userConfig.email;

        await this.initializeClient();
        this.connectWebSocket();
    }

    async initializeClient() {
        try {
            // Initialize A2UI client attached to the element in shadow DOM
            const rootElement = this.shadowRoot.getElementById('a2ui-root');

            this.a2uiClient = new A2UIClient({
                rootElement: rootElement,
                defaultStyles: {
                    primaryColor: '#4F46E5',
                    font: 'Inter',
                    backgroundColor: 'transparent' // Let container background show through
                }
            });

            this.a2uiClient.on('action', (action) => this.handleA2UIAction(action));

            // Initialize A2A client
            const a2aConfig = frontendConfig.getA2AConfig();
            if (a2aConfig.apiKey) {
                this.a2aClient = new A2AClient({
                    apiKey: a2aConfig.apiKey,
                    model: a2aConfig.model
                });
            }

            // Load initial data
            await this.loadInitialMeetings();

        } catch (error) {
            console.error('Error initializing client:', error);
            this.errorMessage = 'Failed to initialize meeting assistant';
        }
    }

    async loadInitialMeetings() {
        try {
            this.isLoading = true;

            const [calendarResponse, emailResponse] = await Promise.all([
                fetch('/api/a2ui/calendar'),
                fetch('/api/a2ui/email/inbox')
            ]);

            // Allow 404s for others to prevent crash
            const videoResponse = { json: async () => ({ meetings: [] }) };
            const marketingResponse = { json: async () => ({ campaigns: [] }) };

            const calendarData = await calendarResponse.json();
            const emailData = await emailResponse.json();
            const videoData = await videoResponse.json();
            const marketingData = await marketingResponse.json();

            const a2uiComponents = this.createMeetingDashboard(
                calendarData,
                emailData,
                videoData,
                marketingData
            );

            await this.a2uiClient.render(a2uiComponents);
            this.isLoading = false;
        } catch (error) {
            console.error('Error loading meetings:', error);
            this.errorMessage = 'Failed to load meetings';
            this.isLoading = false;
        }
    }

    createMeetingDashboard(calendarData, emailData, videoData, marketingData) {
        return [
            {
                component: 'meeting-dashboard',
                props: {
                    meetings: calendarData.events || [],
                    emails: emailData.emails || [],
                    videoMeetings: videoData.meetings || [],
                    marketingCampaigns: marketingData.campaigns || [],
                    userEmail: this.userEmail,
                    stats: {
                        totalMeetings: (calendarData.events || []).length,
                        pendingEmails: (emailData.emails || []).filter(e => !e.read).length,
                        activeVideoMeetings: (videoData.meetings || []).filter(m => m.status === 'active').length,
                        runningCampaigns: (marketingData.campaigns || []).filter(c => c.status === 'running').length
                    }
                }
            },
            {
                component: 'quick-actions',
                props: {
                    actions: [
                        { label: 'Schedule Meeting', action: 'schedule_meeting', icon: 'calendar' },
                        { label: 'Start Video Call', action: 'start_video_call', icon: 'video' },
                        { label: 'Create Campaign', action: 'create_campaign', icon: 'megaphone' },
                        { label: 'Compose Email', action: 'compose_email', icon: 'email' }
                    ]
                }
            }
        ];
    }

    async sendMessage() {
        const input = this.shadowRoot.getElementById('message-input');
        const message = input.value.trim();
        if (!message) return;

        this.chatMessages = [...this.chatMessages, { text: message, type: 'user' }];
        input.value = '';

        try {
            this.isLoading = true;

            const response = await fetch('/api/a2ui/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    message: message,
                    session_id: this.sessionId
                })
            });

            const aiData = await response.json();

            if (aiData.a2ui_json) {
                const components = JSON.parse(aiData.a2ui_json);
                await this.a2uiClient.render(components);

                const textResponse = this.extractTextFromA2UI(aiData.a2ui_json);
                if (textResponse) {
                    this.chatMessages = [...this.chatMessages, { text: textResponse, type: 'assistant' }];
                }
            } else {
                this.chatMessages = [...this.chatMessages, { text: aiData.response || 'Processed', type: 'assistant' }];
            }

            this.isLoading = false;
        } catch (error) {
            console.error('Error sending message:', error);
            this.errorMessage = 'Failed to process request';
            this.isLoading = false;
        }
    }

    extractTextFromA2UI(a2uiJson) {
        try {
            const components = JSON.parse(a2uiJson);
            for (const component of components) {
                if (component.component === 'chat-response' && component.props.message) {
                    return component.props.message;
                }
                if (component.component === 'text-display' && component.props.text) {
                    return component.props.text;
                }
            }
            return null;
        } catch (error) {
            return null;
        }
    }

    async handleA2UIAction(action) {
        console.log('A2UI Action:', action);

        // Map local button clicks to backend actions
        // Sidebar buttons send {name: 'check_email'} -> map to 'navigate_email_inbox'
        // Or if standard A2UI buttons, they send {name: 'navigate_email_inbox'} directly

        let backendAction = action.name;
        if (action.name === 'check_email') backendAction = 'navigate_email_inbox';
        if (action.name === 'view_calendar') backendAction = 'navigate_calendar';
        if (action.name === 'refresh_dashboard') backendAction = 'navigate_dashboard';

        try {
            this.isLoading = true;
            const response = await fetch('/api/a2ui/ui/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    action: backendAction,
                    data: action.data || {},
                    state: 'current_state' // TODO: Track state if needed
                })
            });

            if (!response.ok) throw new Error('Action failed');

            const result = await response.json();

            // Backend returns { component: ..., state_info: ... }
            if (result.component) {
                await this.a2uiClient.render(result.component);
            }

            this.isLoading = false;
        } catch (error) {
            console.error('Error handling action:', error);
            this.errorMessage = 'Failed to perform action';
            this.isLoading = false;
        }
    }

    connectWebSocket() {
        try {
            this.websocket = new WebSocket(`ws://localhost:8005/ws/a2ui/${this.userEmail}`);
            this.websocket.onopen = () => { this.connectionStatus = 'Connected'; };
            this.websocket.onclose = () => {
                this.connectionStatus = 'Disconnected';
                setTimeout(() => this.connectWebSocket(), 3000);
            };
        } catch (e) {
            console.error("WS Error", e);
        }
    }

    getAuthToken() {
        return localStorage.getItem('auth_token') || 'dummy_token';
    }

    render() {
        return html`
            <div class="app-container">
                <aside class="sidebar">
                    <h2 style="color: white; margin-bottom: 20px;">dhii Mail</h2>
                    <nav>
                        <button class="nav-item" @click=${this.loadInitialMeetings}>Dashboard</button>
                        <button class="nav-item" @click=${() => this.handleA2UIAction({ name: 'check_email' })}>Email</button>
                        <button class="nav-item" @click=${() => this.handleA2UIAction({ name: 'view_calendar' })}>Calendar</button>
                    </nav>
                </aside>

                <main class="main-content">
                    <header class="header">
                        <div>Status: ${this.connectionStatus}</div>
                        <div>${this.userEmail}</div>
                    </header>

                    <div class="content-area">
                        <div id="a2ui-root"></div>
                    </div>

                    <div class="chat-panel">
                        <div class="chat-messages">
                            ${this.chatMessages.map(msg => html`
                                <div class="message ${msg.type}">
                                    ${msg.text}
                                </div>
                            `)}
                        </div>
                        <div class="chat-input-area">
                            <input type="text" id="message-input" placeholder="Ask AI assistant..." @keypress=${(e) => e.key === 'Enter' && this.sendMessage()}>
                            <button @click=${this.sendMessage}>Send</button>
                        </div>
                    </div>

                    ${this.isLoading ? html`
                        <div class="loading-overlay">
                            <div>Loading...</div>
                        </div>
                    ` : ''}

                    ${this.errorMessage ? html`
                        <div style="position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); background: #ef4444; color: white; padding: 10px 20px; border-radius: 8px;">
                            ${this.errorMessage}
                            <button @click=${() => this.errorMessage = ''} style="margin-left: 10px; background: transparent; padding: 0;">X</button>
                        </div>
                    ` : ''}
                </main>
            </div>
        `;
    }
}

customElements.define('meeting-assistant-app', MeetingAssistantApp);
