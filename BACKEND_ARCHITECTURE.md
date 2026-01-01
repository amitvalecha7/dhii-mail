# Backend Architecture & API Documentation

## 🏗️ Backend Architecture Overview

The dhii Mail backend is built on a modern, scalable architecture using FastAPI as the primary framework. It implements a microservices-oriented design with clear separation of concerns, asynchronous processing, and comprehensive API coverage.

---

## 🔧 Core Backend Files

### 1. Main Application Server
**File**: [`main.py`](main.py)
- **Port**: 8005
- **Framework**: FastAPI
- **Description**: Primary application server with all major endpoints

#### Key Features
- **Multi-protocol Support**: HTTP/HTTPS and WebSocket
- **CORS Enabled**: Cross-origin resource sharing
- **Rate Limiting**: Request throttling
- **Authentication**: JWT/PASETO token-based
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

#### Server Initialization
```python
app = FastAPI(
    title="dhii Mail API",
    description="Comprehensive email management platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

---

### 2. Chat API Server
**File**: [`chat_api_v2.py`](chat_api_v2.py)
- **Port**: 8006
- **Framework**: FastAPI
- **Description**: Dedicated chat and AI processing server

#### Chat Processing Pipeline
```python
class ChatIntentProcessor:
    """Processes natural language to determine user intent"""
    
    IntentType.EMAIL_SEARCH      # Search emails
    IntentType.EMAIL_ANALYSIS     # Analyze email patterns
    IntentType.EMAIL_SUMMARY      # Summarize emails
    IntentType.EMAIL_SENTIMENT   # Sentiment analysis
    IntentType.AUTH_REQUEST      # Authentication requests
```

---

### 3. Authentication API
**File**: [`auth_api.py`](auth_api.py)
- **Port**: 8007
- **Framework**: FastAPI
- **Description**: Dedicated authentication and authorization server

#### Authentication Flow
```
1. User Registration → Password Hashing → Token Generation
2. User Login → Credential Validation → JWT Token Issued
3. Token Validation → Middleware Check → Resource Access
4. Token Refresh → Expiration Check → New Token Issued
```

---

## 🧠 AI Engine Architecture

### AI Processing System
**File**: [`ai_engine.py`](ai_engine.py)

#### AI Capabilities
```python
class AIEngine:
    """Central AI processing engine"""
    
    # Email Intelligence
    analyze_sentiment(text)          # Sentiment analysis
    extract_keywords(text)           # Keyword extraction
    classify_email(email)            # Email categorization
    generate_summary(emails)         # Email summarization
    
    # Chat Intelligence
    process_intent(message)          # Intent recognition
    generate_response(context)       # Contextual responses
    extract_entities(text)           # Named entity recognition
    
    # Security AI
    detect_phishing(email)           # Phishing detection
    analyze_threats(content)         # Threat analysis
    classify_spam(email)             # Spam classification
```

#### Machine Learning Models
- **Sentiment Analysis**: Pre-trained NLP models
- **Text Classification**: Custom email categorization
- **Pattern Recognition**: User behavior analysis
- **Anomaly Detection**: Security threat identification

---

## 📧 Email Management System

### Email Manager
**File**: [`email_manager.py`](email_manager.py)

#### IMAP/SMTP Integration
```python
class EmailManager:
    """Comprehensive email management system"""
    
    # IMAP Operations
    fetch_emails(account_id, folder, limit)
    search_emails(account_id, criteria)
    mark_as_read(email_id)
    move_email(email_id, folder)
    delete_email(email_id)
    
    # SMTP Operations
    send_email(from_addr, to_addr, subject, body)
    send_bulk_emails(recipients, template)
    schedule_email(email_data, send_time)
    
    # Email Processing
    parse_email(raw_message)           # Parse raw email
    extract_attachments(email)         # Handle attachments
    analyze_content(email)             # Content analysis
    categorize_email(email)            # Auto-categorization
```

#### Email Sync Process
```
1. Connect to IMAP Server
2. Authenticate User Account
3. Fetch Email List
4. Parse Individual Emails
5. Store in Database
6. Apply AI Analysis
7. Update User Interface
```

---

## 🔐 Security Management System

### Security Manager
**File**: [`security_manager.py`](security_manager.py)

#### Security Features
```python
class SecurityManager:
    """Comprehensive security management"""
    
    # Authentication
    hash_password(password)            # Bcrypt hashing
    verify_password(password, hash)    # Password verification
    generate_token(user_id)           # JWT generation
    validate_token(token)             # Token validation
    
    # Threat Detection
    detect_brute_force(ip_address)    # Rate limiting
    analyze_email_security(email)     # Email security check
    scan_attachments(attachments)     # Virus scanning
    
    # Access Control
    check_permissions(user, resource) # Permission checking
    audit_log(event, user)            # Security auditing
    encrypt_sensitive_data(data)      # Data encryption
```

#### Security Protocols
- **Password Security**: Bcrypt with salt rounds
- **Token Security**: JWT with expiration
- **Rate Limiting**: IP-based request limits
- **Input Validation**: SQL injection prevention
- **CORS Protection**: Cross-origin security

---

## 📊 Database Architecture

### Database Manager
**File**: [`database.py`](database.py)

#### Database Schema
```sql
-- Users Table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE
);

-- Email Accounts Table
CREATE TABLE email_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    email_address TEXT NOT NULL,
    imap_server TEXT NOT NULL,
    imap_port INTEGER NOT NULL,
    imap_username TEXT NOT NULL,
    imap_password TEXT NOT NULL,
    smtp_server TEXT NOT NULL,
    smtp_port INTEGER NOT NULL,
    smtp_username TEXT NOT NULL,
    smtp_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Emails Table
CREATE TABLE emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    message_id TEXT UNIQUE NOT NULL,
    sender TEXT NOT NULL,
    recipients TEXT NOT NULL,
    subject TEXT,
    body TEXT,
    html_body TEXT,
    date TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    is_deleted BOOLEAN DEFAULT FALSE,
    folder TEXT DEFAULT 'INBOX',
    sentiment TEXT,
    sentiment_score REAL,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES email_accounts(id)
);
```

#### Database Operations
```python
class DatabaseManager:
    """Database abstraction layer"""
    
    # User Operations
    create_user(user_data)              # User registration
    get_user_by_email(email)          # User lookup
    update_user(user_id, updates)      # User updates
    delete_user(user_id)              # User deletion
    
    # Email Operations
    get_user_emails(user_id, limit)   # User emails
    search_emails(query, user_id)     # Email search
    insert_email(email_data)           # Email storage
    update_email(email_id, updates)    # Email updates
    
    # Analytics Operations
    get_user_stats(user_id)           # User statistics
    get_email_stats(user_id)          # Email statistics
    get_security_events(user_id)       # Security logs
```

---

## 🌐 WebSocket Architecture

### WebSocket Manager
**File**: [`websocket_manager.py`](websocket_manager.py)

#### Real-time Communication
```python
class WebSocketManager:
    """WebSocket connection manager"""
    
    # Connection Management
    connect(websocket, user_id)        # New connection
    disconnect(user_id)                  # Connection closed
    send_message(user_id, message)     # Send to specific user
    broadcast_message(message)           # Send to all users
    
    # Message Types
    CHAT_MESSAGE                         # Chat messages
    EMAIL_UPDATE                         # Email notifications
    USER_TYPING                          # Typing indicators
    NOTIFICATION                         # System notifications
```

#### WebSocket Events
```javascript
// Client-side WebSocket handling
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onopen = function() {
    console.log('Connected to chat server');
};

ws.onmessage = function(event) {
    const message = JSON.parse(event.data);
    handleMessage(message);
};

ws.onclose = function() {
    console.log('Disconnected from chat server');
};
```

---

## 📅 Calendar Integration

### Calendar Manager
**File**: [`calendar_manager.py`](calendar_manager.py)

#### Calendar Features
```python
class CalendarManager:
    """Calendar and scheduling system"""
    
    # Event Management
    create_event(event_data)            # New calendar event
    get_events(user_id, date_range)    # User events
    update_event(event_id, updates)    # Event updates
    delete_event(event_id)              # Event deletion
    
    # Scheduling
    find_free_times(user_id, duration) # Available slots
    schedule_meeting(meeting_data)      # Meeting scheduling
    send_invitations(event_id)          # Email invitations
    
    # Integration
    sync_with_email(event)              # Email sync
    integrate_with_video(event)          # Video meeting setup
```

---

## 🎥 Video Conferencing System

### Video Manager
**File**: [`video_manager.py`](video_manager.py)

#### Video Features
```python
class VideoManager:
    """Video conferencing system"""
    
    # Meeting Management
    create_meeting(meeting_data)        # New video meeting
    get_meeting(meeting_id)             # Meeting details
    update_meeting(meeting_id, data)    # Meeting updates
    delete_meeting(meeting_id)          # Meeting cancellation
    
    # Video Streaming
    start_stream(meeting_id)            # Begin streaming
    stop_stream(meeting_id)             # End streaming
    record_meeting(meeting_id)          # Recording setup
    
    # Participant Management
    add_participant(meeting_id, user)   # Add attendee
    remove_participant(meeting_id, user) # Remove attendee
    mute_participant(meeting_id, user)   # Audio control
```

#### Video Technology Stack
- **WebRTC**: Real-time communication
- **RTMP**: Streaming protocol
- **HLS**: HTTP Live Streaming
- **VP8/VP9**: Video codecs
- **Opus**: Audio codec

---

## 📈 Marketing Automation

### Marketing Manager
**File**: [`marketing_manager.py`](marketing_manager.py)

#### Marketing Features
```python
class MarketingManager:
    """Marketing campaign management"""
    
    # Campaign Management
    create_campaign(campaign_data)      # New campaign
    get_campaigns(user_id)            # User campaigns
    update_campaign(campaign_id, data) # Campaign updates
    delete_campaign(campaign_id)        # Campaign deletion
    
    # Audience Management
    create_audience(audience_data)      # Target audience
    segment_audience(criteria)          # Audience segmentation
    import_contacts(contact_list)       # Contact import
    
    # Analytics
    get_campaign_stats(campaign_id)     # Campaign metrics
    track_email_open(email_id)          # Open tracking
    track_link_click(link_id)           # Click tracking
    generate_analytics_report(campaign)  # Analytics report
```

---

## 🔧 API Endpoint Reference

### Authentication Endpoints
```http
POST   /auth/register                    # User registration
POST   /auth/login                       # User login
POST   /auth/logout                      # User logout
GET    /auth/verify                      # Token verification
GET    /auth/status                      # Authentication status
POST   /auth/refresh                     # Token refresh
POST   /auth/forgot-password             # Password reset
POST   /auth/reset-password              # Password update
```

### Email Endpoints
```http
GET    /emails                          # List user emails
GET    /emails/{id}                     # Get specific email
POST   /emails                          # Create draft email
PUT    /emails/{id}                     # Update email
DELETE /emails/{id}                     # Delete email
POST   /emails/send                     # Send email
POST   /emails/search                   # Search emails
GET    /emails/folders                  # List folders
POST   /emails/sync                     # Sync with server
GET    /emails/stats                    # Email statistics
```

### Chat Endpoints
```http
POST   /api/chat/process                # Process chat message
GET    /api/auth/status                 # Check auth status
GET    /api/chat/suggestions            # Get suggestions
POST   /api/chat/voice                  # Voice message processing
GET    /api/chat/history                # Message history
POST   /api/chat/typing                 # Typing indicator
```

### Video Endpoints
```http
POST   /video/meetings                  # Create meeting
GET    /video/meetings                  # List meetings
GET    /video/meetings/{id}             # Get meeting details
PUT    /video/meetings/{id}             # Update meeting
DELETE /video/meetings/{id}             # Delete meeting
POST   /video/meetings/{id}/start       # Start meeting
POST   /video/meetings/{id}/stop        # Stop meeting
POST   /video/meetings/{id}/record      # Record meeting
```

### Marketing Endpoints
```http
POST   /marketing/campaigns            # Create campaign
GET    /marketing/campaigns            # List campaigns
GET    /marketing/campaigns/{id}         # Get campaign
PUT    /marketing/campaigns/{id}         # Update campaign
DELETE /marketing/campaigns/{id}         # Delete campaign
POST   /marketing/campaigns/{id}/send    # Send campaign
GET    /marketing/analytics              # Get analytics
POST   /marketing/audiences              # Create audience
GET    /marketing/templates              # Email templates
```

---

## 📊 Performance Optimization

### Database Optimization
- **Indexing**: Optimized database indexes
- **Query Optimization**: Efficient SQL queries
- **Connection Pooling**: Database connection reuse
- **Caching**: Redis caching layer
- **Async Operations**: Non-blocking database calls

### API Optimization
- **Response Caching**: HTTP cache headers
- **Compression**: Gzip compression
- **Pagination**: Large dataset handling
- **Rate Limiting**: Request throttling
- **Connection Keep-Alive**: Persistent connections

### Asynchronous Processing
```python
# Async email processing
async def process_email_async(email_data):
    # Non-blocking email processing
    await email_manager.process_email(email_data)
    
# Background task processing
from celery import Celery
app = Celery('dhii_mail')

@app.task
def send_email_campaign(campaign_id):
    # Background campaign sending
    marketing_manager.send_campaign(campaign_id)
```

---

## 🔒 Security Architecture

### Multi-layered Security
1. **Network Layer**: Firewall and DDoS protection
2. **Application Layer**: Input validation and sanitization
3. **Authentication Layer**: JWT tokens and MFA
4. **Data Layer**: Encryption and access control
5. **Audit Layer**: Logging and monitoring

### Security Headers
```python
# Security middleware
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
```

---

## 🧪 Testing Architecture

### Test Structure
```python
# Unit tests
test_email_manager.py      # Email functionality tests
test_auth_api.py          # Authentication tests
test_chat_integration.py  # Chat system tests
test_security.py          # Security tests

# Integration tests
test_phase6.py            # Feature validation tests
test_api_endpoints.py     # API endpoint tests
test_websocket.py         # WebSocket tests

# Performance tests
test_load.py              # Load testing
test_stress.py            # Stress testing
test_endurance.py         # Endurance testing
```

### Test Execution
```bash
# Run all tests
pytest

# Run specific test category
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Generate coverage report
pytest --cov=dhii_mail --cov-report=html
```

---

## 📈 Monitoring & Logging

### Logging Configuration
```python
import logging
import structlog

# Structured logging
logger = structlog.get_logger()

logger.info(
    "User login successful",
    user_id=user.id,
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent")
)
```

### Monitoring Metrics
- **Request Volume**: API call frequency
- **Response Time**: API latency metrics
- **Error Rate**: Failed request percentage
- **Active Users**: Concurrent user count
- **Resource Usage**: CPU, memory, disk utilization

---

This backend documentation provides comprehensive coverage of the dhii Mail server-side architecture, APIs, and implementation details. The system is designed for scalability, security, and maintainability.