// A2UI Meeting Assistant Client
// Main application entry point

import { A2UIClient } from '@a2ui/lit';
import { A2AClient } from '@a2a-js/sdk';
import { frontendConfig } from './config.js';

class MeetingAssistantClient {
    constructor() {
        this.a2uiClient = null;
        this.a2aClient = null;
        this.websocket = null;
        
        // Get secure configuration
        const userConfig = frontendConfig.getUserConfig();
        this.userEmail = userConfig.email;
        
        this.sessionId = null;
        
        this.initializeClient();
        this.setupEventListeners();
        this.connectWebSocket();
    }

    async initializeClient() {
        try {
            // Initialize A2UI client
            this.a2uiClient = new A2UIClient({
                rootElement: document.getElementById('a2ui-root'),
                defaultStyles: {
                    primaryColor: '#4F46E5',
                    font: 'Inter',
                    backgroundColor: '#f8fafc'
                }
            });

            // Initialize A2A client for voice interactions
            const a2aConfig = frontendConfig.getA2AConfig();
            
            if (!a2aConfig.apiKey) {
                throw new Error('A2A API key not configured. Please set A2A_API_KEY environment variable.');
            }
            
            this.a2aClient = new A2AClient({
                apiKey: a2aConfig.apiKey,
                model: a2aConfig.model
            });

            // Load initial meeting list
            await this.loadInitialMeetings();
            
        } catch (error) {
            console.error('Error initializing client:', error);
            this.showError('Failed to initialize meeting assistant');
        }
    }

    async loadInitialMeetings() {
        try {
            this.showLoading(true);
            
            // Use existing backend endpoints for comprehensive data
            const [calendarResponse, emailResponse, videoResponse, marketingResponse] = await Promise.all([
                fetch('/calendar/events'),
                fetch('/email/inbox'), 
                fetch('/video/meetings'),
                fetch('/marketing/campaigns')
            ]);
            
            const calendarData = await calendarResponse.json();
            const emailData = await emailResponse.json();
            const videoData = await videoResponse.json();
            const marketingData = await marketingResponse.json();
            
            // Create comprehensive A2UI components from all backend data
            const a2uiComponents = this.createMeetingDashboard(
                calendarData, 
                emailData, 
                videoData, 
                marketingData
            );
            
            await this.a2uiClient.render(a2uiComponents);
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading meetings:', error);
            this.showError('Failed to load meetings');
            this.showLoading(false);
        }
    }

    createMeetingDashboard(calendarData, emailData, videoData, marketingData) {
        // Convert all backend data to comprehensive A2UI components
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

    createA2UIResponse(responseText, userMessage) {
        // Create A2UI components from AI response
        return [
            {
                component: 'chat-response',
                props: {
                    message: responseText,
                    userMessage: userMessage,
                    timestamp: new Date().toISOString()
                }
            },
            {
                component: 'action-buttons',
                props: {
                    actions: [
                        { label: 'View Meetings', action: 'view_upcoming_meetings' },
                        { label: 'Schedule Meeting', action: 'schedule_another_meeting' },
                        { label: 'Check Email', action: 'check_email' }
                    ]
                }
            }
        ];
    }

    setupEventListeners() {
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        const voiceInputBtn = document.getElementById('voice-input-btn');
        const voiceOutputBtn = document.getElementById('voice-output-btn');

        // Text input
        sendBtn.addEventListener('click', () => this.sendMessage());
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Voice input
        voiceInputBtn.addEventListener('click', () => this.toggleVoiceInput());
        voiceOutputBtn.addEventListener('click', () => this.toggleVoiceOutput());

        // A2UI action handlers
        if (this.a2uiClient) {
            this.a2uiClient.on('action', (action) => {
                this.handleA2UIAction(action);
            });
        }
    }

    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addChatMessage(message, 'user');
        messageInput.value = '';

        try {
            this.showLoading(true);
            
            // Use existing AI engine endpoint for chat processing
            const aiResponse = await fetch('/api/a2ui/chat', {
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

            const aiData = await aiResponse.json();
            
            if (aiData.a2ui_json) {
                // Parse and render A2UI components from backend
                const a2uiComponents = JSON.parse(aiData.a2ui_json);
                await this.a2uiClient.render(a2uiComponents);
                
                // Extract text response for chat
                const textResponse = this.extractTextFromA2UI(aiData.a2ui_json);
                if (textResponse) {
                    this.addChatMessage(textResponse, 'assistant');
                }
            } else {
                // Fallback to direct response
                this.addChatMessage(aiData.response || 'I processed your request', 'assistant');
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Failed to process your request');
            this.showLoading(false);
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
            console.error('Error extracting text from A2UI:', error);
            return null;
        }
    }

    async handleA2UIAction(action) {
        console.log('A2UI Action received:', action);
        
        try {
            switch (action.name) {
                case 'view_upcoming_meetings':
                case 'refresh_dashboard':
                    await this.loadInitialMeetings();
                    break;
                    
                case 'schedule_another_meeting':
                case 'schedule_meeting':
                    await this.sendMessage('schedule a meeting');
                    break;
                    
                case 'check_email':
                case 'refresh_email':
                    await this.loadEmailInbox();
                    break;
                    
                case 'book_meeting':
                    // Handle meeting booking using existing calendar endpoint
                    await this.handleMeetingBooking(action.data);
                    break;
                    
                case 'cancel_meeting':
                    // Handle meeting cancellation using existing calendar endpoint
                    await this.handleMeetingCancellation(action.data);
                    break;
                    
                case 'get_meeting_details':
                    await this.loadMeetingDetails(action.data.meetingId);
                    break;
                    
                case 'send_email':
                    await this.handleSendEmail(action.data);
                    break;
                    
                case 'start_video_call':
                    await this.handleStartVideoCall(action.data);
                    break;
                    
                case 'create_campaign':
                    await this.handleCreateCampaign(action.data);
                    break;
                    
                case 'view_video_meetings':
                    await this.loadVideoMeetings();
                    break;
                    
                case 'view_campaigns':
                    await this.loadMarketingCampaigns();
                    break;
                    
                case 'get_analytics':
                    await this.loadAnalytics(action.data.type);
                    break;
                    
                case 'search_emails':
                    await this.searchEmails(action.data.query);
                    break;
                    
                case 'update_meeting':
                    await this.handleMeetingUpdate(action.data);
                    break;
                    
                case 'get_availability':
                    await this.checkAvailability(action.data);
                    break;
                    
                default:
                    console.warn('Unknown A2UI action:', action.name);
                    // Send to AI for processing
                    if (action.data && action.data.query) {
                        await this.sendMessage(action.data.query);
                    }
            }
        } catch (error) {
            console.error('Error handling A2UI action:', error);
            this.showError('Failed to handle action: ' + action.name);
        }
    }
                    
                default:
                    console.log('Unknown action:', action.name);
            }
        } catch (error) {
            console.error('Error handling A2UI action:', error);
            this.showError('Failed to handle action');
        }
    }

    async loadEmailInbox() {
        try {
            this.showLoading(true);
            
            // Use existing email endpoint
            const response = await fetch('/email/inbox');
            const emailData = await response.json();
            
            // Create A2UI email components
            const a2uiComponents = this.createEmailDashboard(emailData);
            await this.a2uiClient.render(a2uiComponents);
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading email inbox:', error);
            this.showError('Failed to load email inbox');
            this.showLoading(false);
        }
    }

    createEmailDashboard(emailData) {
        return [
            {
                component: 'email-dashboard',
                props: {
                    emails: emailData.emails || [],
                    unreadCount: emailData.unread_count || 0,
                    userEmail: this.userEmail
                }
            }
        ];
    }

    async handleMeetingBooking(bookingData) {
        try {
            this.showLoading(true);
            
            // Use existing calendar endpoint for meeting booking
            const response = await fetch('/calendar/events', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    title: bookingData.title,
                    start_time: `${bookingData.date}T${bookingData.time}`,
                    end_time: `${bookingData.date}T${this.addDuration(bookingData.time, bookingData.duration_minutes)}`,
                    description: bookingData.description,
                    attendees: bookingData.participants,
                    meeting_type: bookingData.meeting_type || 'google_meet'
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                // Create success A2UI components
                const successComponents = [
                    {
                        component: 'success-message',
                        props: {
                            message: 'Meeting booked successfully!',
                            meetingId: data.id,
                            details: data
                        }
                    }
                ];
                await this.a2uiClient.render(successComponents);
                this.addChatMessage('Meeting booked successfully!', 'assistant');
            } else {
                throw new Error(data.detail || 'Failed to book meeting');
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error booking meeting:', error);
            this.showError('Failed to book meeting: ' + error.message);
            this.showLoading(false);
        }
    }

    addDuration(time, durationMinutes) {
        // Helper function to add duration to time
        const [hours, minutes] = time.split(':').map(Number);
        const date = new Date();
        date.setHours(hours, minutes + durationMinutes);
        return date.toTimeString().slice(0, 5);
    }

    async handleMeetingCancellation(cancellationData) {
        try {
            this.showLoading(true);
            
            // Use existing calendar endpoint for meeting cancellation
            const response = await fetch(`/calendar/events/${cancellationData.meetingId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            if (response.ok) {
                // Create success A2UI components
                const successComponents = [
                    {
                        component: 'success-message',
                        props: {
                            message: 'Meeting cancelled successfully!',
                            meetingId: cancellationData.meetingId
                        }
                    }
                ];
                await this.a2uiClient.render(successComponents);
                this.addChatMessage('Meeting cancelled successfully!', 'assistant');
                await this.loadInitialMeetings(); // Refresh the list
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to cancel meeting');
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error cancelling meeting:', error);
            this.showError('Failed to cancel meeting: ' + error.message);
            this.showLoading(false);
        }
    }

    async loadMeetingDetails(meetingId) {
        try {
            this.showLoading(true);
            
            const response = await fetch(`/api/a2ui/meetings/${meetingId}`);
            const data = await response.json();
            
            if (data.a2ui_json) {
                await this.a2uiClient.render(JSON.parse(data.a2ui_json));
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading meeting details:', error);
            this.showError('Failed to load meeting details');
            this.showLoading(false);
        }
    }

    async handleSendEmail(emailData) {
        try {
            this.showLoading(true);
            
            // Use existing email endpoint
            const response = await fetch('/email/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    to: emailData.to,
                    subject: emailData.subject,
                    body: emailData.body,
                    cc: emailData.cc || [],
                    bcc: emailData.bcc || []
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                // Create success A2UI components
                const successComponents = [
                    {
                        component: 'success-message',
                        props: {
                            message: 'Email sent successfully!',
                            emailId: data.id
                        }
                    }
                ];
                await this.a2uiClient.render(successComponents);
                this.addChatMessage('Email sent successfully!', 'assistant');
            } else {
                throw new Error(data.detail || 'Failed to send email');
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error sending email:', error);
            this.showError('Failed to send email: ' + error.message);
            this.showLoading(false);
        }
    }

    connectWebSocket() {
        try {
            this.websocket = new WebSocket(`ws://localhost:8005/ws/a2ui/${this.userEmail}`);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected');
                this.updateConnectionStatus('Connected');
            };
            
            this.websocket.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleWebSocketMessage(data);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                this.updateConnectionStatus('Disconnected');
                // Reconnect after 3 seconds
                setTimeout(() => this.connectWebSocket(), 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('Error');
            };
            
        } catch (error) {
            console.error('Error connecting WebSocket:', error);
            this.updateConnectionStatus('Error');
        }
    }

    handleWebSocketMessage(data) {
        if (data.type === 'a2ui_update') {
            // Update A2UI components
            this.a2uiClient.render(JSON.parse(data.a2ui_json));
        }
    }

    // Voice input/output methods
    async toggleVoiceInput() {
        const btn = document.getElementById('voice-input-btn');
        
        if (btn.classList.contains('active')) {
            // Stop voice input
            btn.classList.remove('active');
            this.stopVoiceInput();
        } else {
            // Start voice input
            btn.classList.add('active');
            this.startVoiceInput();
        }
    }

    async startVoiceInput() {
        try {
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                this.showError('Voice input not supported in your browser');
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                document.getElementById('message-input').value = transcript;
                this.sendMessage();
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.showError('Voice input error: ' + event.error);
                document.getElementById('voice-input-btn').classList.remove('active');
            };
            
            this.recognition.onend = () => {
                document.getElementById('voice-input-btn').classList.remove('active');
            };
            
            this.recognition.start();
            
        } catch (error) {
            console.error('Error starting voice input:', error);
            this.showError('Failed to start voice input');
            document.getElementById('voice-input-btn').classList.remove('active');
        }
    }

    stopVoiceInput() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    toggleVoiceOutput() {
        const btn = document.getElementById('voice-output-btn');
        
        if (btn.classList.contains('active')) {
            btn.classList.remove('active');
            this.voiceOutputEnabled = false;
        } else {
            btn.classList.add('active');
            this.voiceOutputEnabled = true;
        }
    }

    speakText(text) {
        if (this.voiceOutputEnabled && 'speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            utterance.volume = 0.8;
            speechSynthesis.speak(utterance);
        }
    }

    // Utility methods
    addChatMessage(message, sender) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = message;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Speak assistant messages if voice output is enabled
        if (sender === 'assistant' && this.voiceOutputEnabled) {
            this.speakText(message);
        }
    }

    showLoading(show) {
        const loading = document.getElementById('loading');
        if (show) {
            loading.classList.add('active');
        } else {
            loading.classList.remove('active');
        }
    }

    showError(message) {
        const errorDiv = document.getElementById('error-message');
        errorDiv.textContent = message;
        errorDiv.classList.add('active');
        
        setTimeout(() => {
            errorDiv.classList.remove('active');
        }, 5000);
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        statusElement.textContent = status;
        
        const indicator = document.querySelector('.status-indicator');
        if (status === 'Connected') {
            indicator.style.background = '#10b981';
        } else if (status === 'Error') {
            indicator.style.background = '#ef4444';
        } else {
            indicator.style.background = '#6b7280';
        }
    }

    extractTextFromA2UI(a2uiJson) {
        try {
            const components = JSON.parse(a2uiJson);
            let text = '';
            
            // Extract text from dataModelUpdate
            for (const component of components) {
                if (component.dataModelUpdate && component.dataModelUpdate.contents) {
                    for (const content of component.dataModelUpdate.contents) {
                        if (content.key === 'message' && content.valueString) {
                            text += content.valueString + ' ';
                        }
                    }
                }
            }
            
            return text.trim() || null;
        } catch (error) {
            console.error('Error extracting text from A2UI:', error);
            return null;
        }
    }

    getAuthToken() {
        // This should get the actual auth token from your auth system
        return localStorage.getItem('auth_token') || 'demo-token';
    }

    // New methods for comprehensive backend integration
    async loadVideoMeetings() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/video/meetings', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            const data = await response.json();
            
            const videoComponents = [
                {
                    component: 'video-meetings-list',
                    props: {
                        meetings: data.meetings || [],
                        userEmail: this.userEmail
                    }
                }
            ];
            
            await this.a2uiClient.render(videoComponents);
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading video meetings:', error);
            this.showError('Failed to load video meetings');
            this.showLoading(false);
        }
    }

    async loadMarketingCampaigns() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/marketing/campaigns', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            const data = await response.json();
            
            const campaignComponents = [
                {
                    component: 'marketing-campaigns',
                    props: {
                        campaigns: data.campaigns || [],
                        userEmail: this.userEmail
                    }
                }
            ];
            
            await this.a2uiClient.render(campaignComponents);
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading marketing campaigns:', error);
            this.showError('Failed to load marketing campaigns');
            this.showLoading(false);
        }
    }

    async loadEmailInbox() {
        try {
            this.showLoading(true);
            
            const response = await fetch('/email/inbox', {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            const data = await response.json();
            
            const emailComponents = [
                {
                    component: 'email-inbox',
                    props: {
                        emails: data.emails || [],
                        userEmail: this.userEmail
                    }
                }
            ];
            
            await this.a2uiClient.render(emailComponents);
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading email inbox:', error);
            this.showError('Failed to load email inbox');
            this.showLoading(false);
        }
    }

    async handleStartVideoCall(videoData) {
        try {
            this.showLoading(true);
            
            const response = await fetch('/video/meetings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    title: videoData.title || 'Video Meeting',
                    participants: videoData.participants || [],
                    scheduled_time: videoData.scheduledTime || new Date().toISOString()
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const successComponents = [
                    {
                        component: 'video-meeting-created',
                        props: {
                            meeting: data,
                            joinUrl: data.join_url,
                            meetingId: data.id
                        }
                    }
                ];
                await this.a2uiClient.render(successComponents);
                this.addChatMessage(`Video meeting created: ${data.title}`, 'assistant');
            } else {
                throw new Error(data.detail || 'Failed to create video meeting');
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error creating video meeting:', error);
            this.showError('Failed to create video meeting: ' + error.message);
            this.showLoading(false);
        }
    }

    async handleCreateCampaign(campaignData) {
        try {
            this.showLoading(true);
            
            const response = await fetch('/marketing/campaigns', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify({
                    name: campaignData.name,
                    subject: campaignData.subject,
                    content: campaignData.content,
                    recipients: campaignData.recipients || []
                })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const successComponents = [
                    {
                        component: 'campaign-created',
                        props: {
                            campaign: data,
                            campaignId: data.id
                        }
                    }
                ];
                await this.a2uiClient.render(successComponents);
                this.addChatMessage(`Marketing campaign created: ${data.name}`, 'assistant');
            } else {
                throw new Error(data.detail || 'Failed to create campaign');
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error creating campaign:', error);
            this.showError('Failed to create campaign: ' + error.message);
            this.showLoading(false);
        }
    }

    async loadAnalytics(type) {
        try {
            this.showLoading(true);
            
            let endpoint = '';
            switch (type) {
                case 'video':
                    endpoint = '/video/meetings/analytics';
                    break;
                case 'marketing':
                    endpoint = '/marketing/dashboard';
                    break;
                case 'email':
                    endpoint = '/email/analytics';
                    break;
                default:
                    endpoint = '/marketing/dashboard';
            }
            
            const response = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            const data = await response.json();
            
            const analyticsComponents = [
                {
                    component: 'analytics-dashboard',
                    props: {
                        analytics: data,
                        type: type
                    }
                }
            ];
            
            await this.a2uiClient.render(analyticsComponents);
            this.showLoading(false);
        } catch (error) {
            console.error('Error loading analytics:', error);
            this.showError('Failed to load analytics');
            this.showLoading(false);
        }
    }

    async searchEmails(query) {
        try {
            this.showLoading(true);
            
            const response = await fetch(`/email/search?q=${encodeURIComponent(query)}`, {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            const data = await response.json();
            
            const searchComponents = [
                {
                    component: 'email-search-results',
                    props: {
                        emails: data.emails || [],
                        query: query
                    }
                }
            ];
            
            await this.a2uiClient.render(searchComponents);
            this.showLoading(false);
        } catch (error) {
            console.error('Error searching emails:', error);
            this.showError('Failed to search emails');
            this.showLoading(false);
        }
    }

    async handleMeetingUpdate(updateData) {
        try {
            this.showLoading(true);
            
            const response = await fetch(`/calendar/events/${updateData.meetingId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                },
                body: JSON.stringify(updateData.updates)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const successComponents = [
                    {
                        component: 'meeting-updated',
                        props: {
                            meeting: data,
                            meetingId: updateData.meetingId
                        }
                    }
                ];
                await this.a2uiClient.render(successComponents);
                this.addChatMessage('Meeting updated successfully!', 'assistant');
                await this.loadInitialMeetings(); // Refresh the list
            } else {
                throw new Error(data.detail || 'Failed to update meeting');
            }
            
            this.showLoading(false);
        } catch (error) {
            console.error('Error updating meeting:', error);
            this.showError('Failed to update meeting: ' + error.message);
            this.showLoading(false);
        }
    }

    async checkAvailability(availabilityData) {
        try {
            this.showLoading(true);
            
            const params = new URLSearchParams({
                date: availabilityData.date,
                duration: availabilityData.duration || '60'
            });
            
            const response = await fetch(`/calendar/availability?${params}`, {
                headers: {
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });
            
            const data = await response.json();
            
            const availabilityComponents = [
                {
                    component: 'availability-display',
                    props: {
                        availableSlots: data.available_slots || [],
                        date: availabilityData.date
                    }
                }
            ];
            
            await this.a2uiClient.render(availabilityComponents);
            this.showLoading(false);
        } catch (error) {
            console.error('Error checking availability:', error);
            this.showError('Failed to check availability');
            this.showLoading(false);
        }
    }

}

// Initialize the client when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new MeetingAssistantClient();
});