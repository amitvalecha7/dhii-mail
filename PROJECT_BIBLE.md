# dhii-mail Project Bible / Wiki

## 🎯 Project Overview

dhii-mail is a comprehensive Smart Meeting Assistant application that combines email management, calendar integration, AI-powered meeting assistance, and real-time communication. The project features a modern web interface built with A2UI (Google's Agent-to-Agent UI framework), a robust FastAPI backend, and advanced AI integration through Google ADK (Agent Development Kit).

## 🏗️ Architecture Overview

```
dhii-mail/
├── Core Backend (FastAPI)
│   ├── Authentication (PASETO-based)
│   ├── Email Management
│   ├── Calendar Integration
│   ├── AI Engine
│   ├── Video Conferencing
│   ├── WebSocket Communication
│   └── Database Layer (SQLite)
├── A2UI Integration
│   ├── Meeting Assistant Agent
│   ├── Frontend Client (Lit/Web Components)
│   ├── Real-time UI Updates
│   └── Voice Command Processing
├── External Integrations
│   ├── Google ADK Agent
│   ├── OpenRouter/Hugging Face AI
│   ├── Faster-Whisper (Voice)
│   └── PASETO Authentication
└── Development Tools
    ├── Vite Build System
    ├── Testing Framework
    └── Development Scripts
```

## 🎨 Frontend Components

### A2UI Meeting Assistant Client
**Location**: `/root/dhii-mail/a2ui_integration/client/`

#### Core Technologies
- **A2UI Lit Renderer**: Google's Web Components framework for agent-to-agent UI
- **Lit**: Modern reactive web components library
- **Vite**: Fast build tool and development server
- **Web Speech API**: Voice command processing and speech recognition
- **WebSocket**: Real-time communication with backend

#### Key Files
- `index.html`: Main application entry point with modern glassmorphism design
- `main.js`: Core client logic, A2UI integration, and WebSocket management
- `package.json`: Frontend dependencies and build configuration
- `vite.config.js`: Vite build configuration

#### UI Features
- **Modern Glassmorphism Design**: Translucent, blurred background effects
- **Responsive Layout**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: Live meeting status and availability changes
- **Voice Commands**: Natural language meeting management
- **Interactive Components**: Meeting cards, booking forms, calendar views

### A2UI Component Schema
The A2UI system uses a three-phase rendering approach:

1. **beginRendering**: Initialize component structure
2. **surfaceUpdate**: Update visual elements and styling
3. **dataModelUpdate**: Sync data models and state

#### Component Types
- **MeetingList**: Displays upcoming meetings with status indicators
- **BookingForm**: Interactive meeting scheduling interface
- **CalendarView**: Visual calendar with availability slots
- **VoiceInterface**: Speech recognition and command processing
- **StatusPanel**: Real-time connection and system status

## 🔧 Backend Architecture

### Core FastAPI Application
**Location**: `/root/dhii-mail/main.py`

#### Main Components
- **FastAPI Framework**: Modern, fast web framework for APIs
- **WebSocket Manager**: Real-time bidirectional communication
- **CORS Middleware**: Cross-origin resource sharing configuration
- **Authentication System**: PASETO-based secure token authentication
- **Database Integration**: SQLite with SQLAlchemy ORM

#### API Endpoints
- **Authentication**: `/auth/*` - User login, registration, token management
- **Email**: `/email/*` - Email sending, receiving, folder management
- **Calendar**: `/calendar/*` - Event scheduling, availability checking
- **AI Chat**: `/chat/*` - AI-powered conversation and assistance
- **Video**: `/video/*` - Video conference creation and management
- **WebSocket**: `/ws/*` - Real-time communication endpoints

### Manager Classes

#### 1. AuthManager (`/root/dhii-mail/auth.py`)
- **PASETO Authentication**: Platform-Agnostic Security Tokens
- **Password Hashing**: bcrypt-based secure password storage
- **Token Management**: Access, refresh, and API token lifecycle
- **User Management**: Registration, login, profile management

#### 2. DatabaseManager (`/root/dhii-mail/database.py`)
- **SQLite Integration**: Lightweight, serverless database
- **Email Data Integration**: Real email data for chat interface
- **Statistics Tracking**: Database health and usage metrics
- **Connection Management**: Efficient database connection handling

#### 3. AIEngine (`/root/dhii-mail/ai_engine.py`)
- **Intent Recognition**: Natural language processing for user requests
- **Multi-modal AI**: Text, voice, and visual processing
- **Context Management**: Conversation history and session tracking
- **Response Generation**: Intelligent, contextual responses

#### 4. CalendarManager (`/root/dhii-mail/calendar_manager.py`)
- **Event Scheduling**: Create, update, delete calendar events
- **Availability Checking**: Find suitable meeting times
- **Time Zone Support**: Multi-timezone event management
- **Recurring Events**: Support for repeating meetings

#### 5. EmailManager (`/root/dhii-mail/email_manager.py`)
- **Multi-provider Support**: Gmail, Outlook, custom SMTP
- **Auto-discovery**: Automatic email provider detection
- **Folder Management**: Inbox, sent, drafts, custom folders
- **Real-time Sync**: Live email updates and notifications

#### 6. VideoManager (`/root/dhii-mail/video_manager.py`)
- **Meeting Creation**: Generate video conference links
- **Provider Integration**: Google Meet, Zoom, Teams support
- **Meeting Management**: Start, end, participant control
- **Recording Support**: Session recording and storage

#### 7. WebSocketManager (`/root/dhii-mail/websocket_manager.py`)
- **Real-time Communication**: Bidirectional message exchange
- **Connection Management**: Handle multiple concurrent connections
- **Message Broadcasting**: Send updates to multiple clients
- **Error Handling**: Robust connection failure management

#### 8. SecurityManager (`/root/dhii-mail/security_manager.py`)
- **Event Logging**: Security event tracking and auditing
- **Threat Detection**: Suspicious activity monitoring
- **Access Control**: Permission and role management
- **Encryption**: Data protection and privacy

#### 9. MarketingManager (`/root/dhii-mail/marketing_manager.py`)
- **Campaign Management**: Create and track marketing campaigns
- **Analytics**: Performance metrics and reporting
- **User Segmentation**: Target audience identification
- **Automation**: Scheduled campaign execution

## 🤖 A2UI Integration & Meeting Assistant

### Meeting Database Manager
**Location**: `/root/dhii-mail/a2ui_integration/meeting_models_updated.py`

#### Features
- **Meeting Tables**: Structured meeting data storage
- **Participant Management**: Attendee tracking and permissions
- **Time Slot Management**: Availability and booking system
- **Room Allocation**: Meeting space and resource management
- **Preference Storage**: User meeting preferences and settings

#### Database Schema
- **meetings**: Core meeting information (title, time, status, organizer)
- **meeting_participants**: Attendee relationships and roles
- **meeting_rooms**: Available meeting spaces and resources
- **time_slots**: Bookable time periods and availability
- **meeting_preferences**: User-specific meeting settings

### Meeting Assistant Agent
**Location**: `/root/dhii-mail/a2ui_integration/agent/agent_updated_v2.py`

#### Google ADK Integration
- **Agent Development Kit**: Google's framework for AI agents
- **LiteLlm Model**: Gemini 2.0 Flash for fast AI responses
- **Tool Integration**: Meeting management capabilities
- **Context Awareness**: User email and session context

#### Agent Capabilities
- **Meeting Scheduling**: Book meetings with natural language
- **Availability Checking**: Find suitable time slots
- **Meeting Details**: Retrieve comprehensive meeting information
- **Cancellation**: Cancel meetings with confirmation
- **Updates**: Modify existing meeting details
- **Preferences**: Learn and adapt to user preferences

### Meeting Tools
**Location**: `/root/dhii-mail/a2ui_integration/agent/meeting_tools_updated_v2.py`

#### Tool Functions
- `get_upcoming_meetings()`: Retrieve user's upcoming meetings
- `get_available_time_slots()`: Find bookable time periods
- `book_meeting()`: Create new meeting reservations
- `get_meeting_details()`: Fetch detailed meeting information
- `cancel_meeting()`: Cancel existing meetings
- `update_meeting()`: Modify meeting details
- `get_user_meeting_preferences()`: Retrieve user preferences

## 🚀 Features & Functionality

### Core Features

#### 1. Smart Meeting Assistant
- **Natural Language Processing**: Book meetings using conversational language
- **AI-Powered Scheduling**: Intelligent time slot recommendations
- **Voice Commands**: Speech-to-text meeting management
- **Contextual Awareness**: Understanding of user preferences and history

#### 2. Email Integration
- **Multi-Provider Support**: Gmail, Outlook, Exchange, IMAP
- **Real-time Synchronization**: Live email updates
- **Smart Filtering**: AI-powered email categorization
- **Automated Responses**: Template-based reply suggestions

#### 3. Calendar Management
- **Multi-Calendar Support**: Personal, work, shared calendars
- **Availability Detection**: Free/busy time analysis
- **Conflict Resolution**: Intelligent scheduling conflict handling
- **Recurring Events**: Support for repeating meetings

#### 4. Video Conferencing
- **Provider Integration**: Google Meet, Zoom, Microsoft Teams
- **One-Click Meetings**: Instant meeting creation
- **Participant Management**: Invite, manage, and track attendees
- **Recording & Transcription**: Meeting capture and processing

#### 5. AI Chat Interface
- **Natural Conversations**: Human-like interaction patterns
- **Multi-Modal Input**: Text, voice, and visual processing
- **Context Retention**: Conversation history and continuity
- **Task Automation**: Execute complex multi-step operations

### Advanced Features

#### 1. Voice Processing
- **Faster-Whisper Integration**: Fast, accurate speech recognition
- **Real-time Transcription**: Live voice-to-text conversion
- **Command Recognition**: Voice-controlled meeting operations
- **Multi-language Support**: International language processing

#### 2. Real-time Collaboration
- **WebSocket Communication**: Instant bidirectional updates
- **Live Status Updates**: Real-time meeting status changes
- **Collaborative Editing**: Shared document and note editing
- **Presence Detection**: User availability and status tracking

#### 3. Security & Privacy
- **PASETO Authentication**: State-of-the-art token security
- **End-to-End Encryption**: Private communication protection
- **Audit Logging**: Comprehensive security event tracking
- **Data Privacy**: GDPR-compliant data handling

#### 4. Analytics & Insights
- **Meeting Analytics**: Usage patterns and efficiency metrics
- **Email Insights**: Communication analysis and trends
- **Productivity Reports**: Time management and optimization
- **Performance Monitoring**: System health and reliability tracking

## 🛠️ Technology Stack

### Backend Technologies

#### Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
- **Python 3.12**: Latest Python version with async support
- **Uvicorn**: Lightning-fast ASGI server
- **Pydantic**: Data validation using Python type hints

#### Database & Storage
- **SQLite**: Lightweight, serverless database engine
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **aiosqlite**: Async SQLite driver

#### Authentication & Security
- **PASETO**: Platform-Agnostic Security Tokens
- **bcrypt**: Password hashing library
- **python-multipart**: Multipart form data parsing
- **PyJWT**: JSON Web Token implementation (legacy)

#### Communication
- **WebSockets**: Real-time bidirectional communication
- **aiosmtplib**: Async SMTP client
- **aiosmtpd**: Async SMTP server
- **email-validator**: Email address validation

#### AI & Machine Learning
- **Google ADK**: Agent Development Kit
- **LiteLlm**: Lightweight LLM interface
- **Google Gemini**: Advanced AI model
- **Faster-Whisper**: Fast speech recognition

### Frontend Technologies

#### Core Framework
- **A2UI Lit**: Google's Agent-to-Agent UI framework
- **Lit**: Simple, fast web components
- **TypeScript**: Typed JavaScript superset
- **Vite**: Fast build tool and dev server

#### UI Components
- **Web Components**: Native browser component standard
- **CSS Grid & Flexbox**: Modern layout systems
- **CSS Custom Properties**: Dynamic styling
- **Inter Font**: Modern typeface family

#### Build Tools
- **Vite**: Next-generation frontend tooling
- **Rollup**: Module bundler
- **ESBuild**: Fast JavaScript bundler
- **PostCSS**: CSS transformation tool

### External Integrations

#### AI Services
- **OpenRouter**: Unified AI model API
- **Hugging Face**: Model hosting and inference
- **Google Gemini**: Advanced language model
- **Anthropic Claude**: Conversational AI

#### Communication Services
- **Google Meet**: Video conferencing
- **Zoom**: Meeting platform
- **Microsoft Teams**: Collaboration platform
- **SendGrid**: Email delivery service

#### Development Tools
- **Git**: Version control
- **Docker**: Containerization
- **pytest**: Testing framework
- **Black**: Code formatting

## 📁 Project Structure

```
/root/dhii-mail/
├── Core Application Files
│   ├── main.py                    # FastAPI application entry point
│   ├── auth.py                    # PASETO authentication system
│   ├── database.py                # SQLite database manager
│   ├── ai_engine.py               # AI processing engine
│   ├── calendar_manager.py        # Calendar integration
│   ├── email_manager.py           # Email management system
│   ├── video_manager.py           # Video conferencing
│   ├── websocket_manager.py       # Real-time communication
│   ├── security_manager.py        # Security and auditing
│   └── marketing_manager.py       # Campaign management
├── A2UI Integration
│   └── a2ui_integration/
│       ├── a2ui_fastapi.py      # A2UI FastAPI endpoints
│       ├── meeting_models_updated.py  # Meeting database manager
│       ├── setup_final.py         # A2UI setup and initialization
│       ├── complete_integration.py    # Full integration logic
│       ├── client/                # Frontend client
│       │   ├── index.html         # Main UI entry point
│       │   ├── main.js            # Client-side logic
│       │   ├── package.json       # Frontend dependencies
│       │   └── vite.config.js     # Build configuration
│       └── agent/                 # AI agent components
│           ├── agent_updated_v2.py    # Google ADK agent
│           ├── meeting_tools_updated_v2.py  # Meeting tools
│           └── ...
├── External Dependencies
│   └── external/                  # Git submodule integrations
│       ├── A2UI/                  # A2UI framework
│       ├── FastAPI/               # FastAPI documentation
│       ├── PASETO/                # PASETO libraries
│       └── faster-whisper/        # Voice processing
├── Database
│   ├── database/                  # Database modules
│   └── dhii_mail.db              # SQLite database file
├── Configuration
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example              # Environment variables
│   └── PROJECT_BIBLE.md          # This documentation
└── Development
    ├── test_*.py                  # Test files
    ├── demo_*.py                  # Demo scripts
    └── setup scripts              # Installation and setup
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git
- Virtual environment (recommended)

### Backend Setup
```bash
# Clone the repository
git clone <repository-url>
cd dhii-mail

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install additional A2UI dependencies
pip install google-adk[extensions]
pip install faster-whisper

# Initialize database
python a2ui_integration/setup_final.py

# Start the application
python main.py
```

### Frontend Setup
```bash
# Navigate to client directory
cd a2ui_integration/client

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Environment Configuration
Create a `.env` file with the following variables:
```env
# Authentication
SECRET_KEY=your-secret-key-here
PASETO_KEY=your-paseto-key-here

# AI Services
GOOGLE_API_KEY=your-google-api-key
OPENROUTER_API_KEY=your-openrouter-api-key
HUGGINGFACE_API_KEY=your-huggingface-api-key

# Email Services
SMTP_SERVER=your-smtp-server
SMTP_PORT=587
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password

# Database
DATABASE_URL=sqlite:///dhii_mail.db

# WebSocket
WS_HOST=localhost
WS_PORT=8000
```

## 🚀 Running the Application

### Development Mode
```bash
# Terminal 1: Start backend
python main.py

# Terminal 2: Start frontend (in a2ui_integration/client)
npm run dev

# Terminal 3: Start WebSocket server
python websocket_manager.py
```

### Production Mode
```bash
# Build frontend
cd a2ui_integration/client && npm run build

# Start production server
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```bash
# Build Docker image
docker build -t dhii-mail .

# Run container
docker run -p 8000:8000 -p 3000:3000 dhii-mail
```

## 📊 API Documentation

### Authentication Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Token refresh
- `GET /auth/profile` - User profile
- `POST /auth/logout` - User logout

### Email Endpoints
- `GET /email/accounts` - List email accounts
- `POST /email/send` - Send email
- `GET /email/messages` - Get messages
- `POST /email/sync` - Sync email
- `DELETE /email/{message_id}` - Delete message

### Calendar Endpoints
- `GET /calendar/events` - List events
- `POST /calendar/events` - Create event
- `PUT /calendar/events/{event_id}` - Update event
- `DELETE /calendar/events/{event_id}` - Delete event
- `GET /calendar/availability` - Check availability

### AI Chat Endpoints
- `POST /chat/message` - Send message
- `GET /chat/history` - Get chat history
- `POST /chat/voice` - Process voice input
- `GET /chat/intents` - Get available intents

### A2UI Meeting Endpoints
- `POST /a2ui/meetings` - Get meetings (A2UI format)
- `POST /a2ui/book` - Book meeting (A2UI format)
- `POST /a2ui/cancel` - Cancel meeting (A2UI format)
- `WS /a2ui/ws` - A2UI WebSocket connection

### Video Endpoints
- `POST /video/meetings` - Create video meeting
- `GET /video/meetings/{meeting_id}` - Get meeting details
- `POST /video/meetings/{meeting_id}/start` - Start meeting
- `POST /video/meetings/{meeting_id}/end` - End meeting

## 🔒 Security Features

### Authentication & Authorization
- **PASETO Tokens**: State-of-the-art security tokens
- **Multi-factor Authentication**: Optional 2FA support
- **Role-based Access Control**: User permission management
- **Session Management**: Secure session handling

### Data Protection
- **End-to-End Encryption**: Private communication protection
- **Data Anonymization**: Privacy-preserving data handling
- **Secure Storage**: Encrypted data storage
- **Audit Logging**: Comprehensive security event tracking

### Network Security
- **HTTPS/TLS**: Secure communication channels
- **CORS Protection**: Cross-origin request security
- **Rate Limiting**: API abuse prevention
- **Input Validation**: SQL injection and XSS protection

## 📈 Performance & Scalability

### Backend Optimization
- **Async Processing**: Non-blocking I/O operations
- **Connection Pooling**: Efficient database connections
- **Caching**: Redis-based response caching
- **Load Balancing**: Multi-instance deployment support

### Frontend Optimization
- **Code Splitting**: Lazy loading of components
- **Tree Shaking**: Dead code elimination
- **Image Optimization**: Responsive image loading
- **Service Workers**: Offline functionality

### Database Optimization
- **Indexing**: Optimized query performance
- **Query Optimization**: Efficient SQL queries
- **Connection Management**: Proper connection handling
- **Backup & Recovery**: Data protection strategies

## 🧪 Testing & Quality Assurance

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: System integration testing
- **End-to-End Tests**: Complete workflow testing
- **Performance Tests**: Load and stress testing

### Code Quality
- **Type Checking**: Static type analysis
- **Linting**: Code style enforcement
- **Formatting**: Consistent code formatting
- **Documentation**: Comprehensive code documentation

### Security Testing
- **Vulnerability Scanning**: Security weakness detection
- **Penetration Testing**: Simulated attack testing
- **Code Review**: Manual security review
- **Compliance Testing**: Regulatory compliance verification

## 📚 Additional Resources

### Development Tools
- **API Documentation**: Auto-generated OpenAPI docs
- **Database Schema**: Visual database diagrams
- **Architecture Diagrams**: System component relationships
- **Deployment Guides**: Step-by-step deployment instructions

### External Integrations
- **GitHub Repositories**: A2UI, FastAPI, PASETO, Faster-Whisper
- **API Documentation**: External service APIs
- **SDK References**: Client library documentation
- **Community Resources**: Forums, tutorials, examples

### Support & Maintenance
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed system logging
- **Monitoring**: System health monitoring
- **Backup & Recovery**: Data protection procedures

## 🔄 Development Workflow

### Branch Strategy
- **main**: Production-ready code
- **develop**: Integration branch
- **feature/***: New feature development
- **bugfix/***: Bug fix branches
- **hotfix/***: Emergency fixes

### Release Process
1. **Feature Development**: Implement new features
2. **Code Review**: Peer review and testing
3. **Integration Testing**: System-wide testing
4. **Documentation**: Update documentation
5. **Deployment**: Production deployment
6. **Monitoring**: Post-deployment monitoring

### Contribution Guidelines
- **Code Style**: Follow PEP 8 and project conventions
- **Testing**: Write comprehensive tests
- **Documentation**: Document all public APIs
- **Security**: Follow security best practices
- **Performance**: Optimize for performance

## 📞 Contact & Support

### Development Team
- **Project Lead**: [Contact Information]
- **Backend Team**: [Contact Information]
- **Frontend Team**: [Contact Information]
- **DevOps Team**: [Contact Information]

### Support Channels
- **Documentation**: This comprehensive wiki
- **Issue Tracking**: GitHub Issues
- **Community Forum**: [Forum URL]
- **Email Support**: [Support Email]

### Emergency Contacts
- **Security Issues**: [Security Email]
- **System Outages**: [Emergency Contact]
- **Critical Bugs**: [Critical Issues Email]

---

**Last Updated**: December 31, 2024  
**Version**: 1.0.0  
**Status**: Production Ready  
**License**: [License Information]  

*This document is continuously updated as the project evolves. For the latest information, always refer to the current version in the repository.*