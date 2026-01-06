-- dhii Mail Database Schema
-- Multi-tenant email application with AI integration

-- Users table with multi-tenant support
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    avatar_url TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    language VARCHAR(10) DEFAULT 'en',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    metadata JSON
);

-- Tenants/Organizations support
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    settings JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User-Tenant relationships
CREATE TABLE user_tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tenant_id INTEGER NOT NULL,
    role VARCHAR(50) DEFAULT 'member',
    permissions JSON,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    UNIQUE(user_id, tenant_id)
);

-- Email accounts (multiple per user)
CREATE TABLE email_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    tenant_id INTEGER,
    account_name VARCHAR(100) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    provider VARCHAR(50) NOT NULL, -- 'gmail', 'outlook', 'custom', 'local'
    imap_server VARCHAR(255),
    imap_port INTEGER DEFAULT 993,
    imap_ssl BOOLEAN DEFAULT TRUE,
    smtp_server VARCHAR(255),
    smtp_port INTEGER DEFAULT 587,
    smtp_ssl BOOLEAN DEFAULT TRUE,
    username VARCHAR(255),
    password_encrypted TEXT, -- Encrypted password storage
    oauth_token JSON, -- For OAuth2 providers
    is_default BOOLEAN DEFAULT FALSE,
    sync_enabled BOOLEAN DEFAULT TRUE,
    sync_frequency INTEGER DEFAULT 300, -- seconds
    folder_mappings JSON,
    settings JSON,
    is_active BOOLEAN DEFAULT TRUE,
    last_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE SET NULL
);

-- Email folders
CREATE TABLE email_folders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    folder_name VARCHAR(255) NOT NULL,
    folder_type VARCHAR(50), -- 'inbox', 'sent', 'drafts', 'trash', 'spam', 'custom'
    parent_folder_id INTEGER,
    uid_validity INTEGER,
    uid_next INTEGER DEFAULT 1,
    message_count INTEGER DEFAULT 0,
    unread_count INTEGER DEFAULT 0,
    is_system BOOLEAN DEFAULT FALSE,
    sync_enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (account_id) REFERENCES email_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (parent_folder_id) REFERENCES email_folders(id) ON DELETE CASCADE,
    UNIQUE(account_id, folder_name)
);

-- Email messages
CREATE TABLE email_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    folder_id INTEGER NOT NULL,
    message_id VARCHAR(255) NOT NULL, -- IMAP MESSAGE-ID
    uid INTEGER NOT NULL, -- IMAP UID
    thread_id VARCHAR(255), -- For conversation threading
    subject TEXT,
    from_address VARCHAR(255),
    to_addresses TEXT, -- JSON array
    cc_addresses TEXT, -- JSON array
    bcc_addresses TEXT, -- JSON array
    reply_to VARCHAR(255),
    date_sent TIMESTAMP,
    date_received TIMESTAMP,
    flags VARCHAR(255), -- IMAP flags (\Seen, \Answered, etc.)
    priority INTEGER DEFAULT 3, -- 1=high, 3=normal, 5=low
    is_read BOOLEAN DEFAULT FALSE,
    is_answered BOOLEAN DEFAULT FALSE,
    is_flagged BOOLEAN DEFAULT FALSE,
    has_attachments BOOLEAN DEFAULT FALSE,
    size_bytes INTEGER,
    text_content TEXT,
    html_content TEXT,
    headers JSON,
    attachments JSON,
    ai_summary TEXT, -- AI-generated summary
    ai_categories JSON, -- AI-generated categories
    ai_sentiment VARCHAR(20), -- AI-analyzed sentiment
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES email_accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (folder_id) REFERENCES email_folders(id) ON DELETE CASCADE,
    UNIQUE(account_id, folder_id, uid)
);

-- Email threads/conversations
CREATE TABLE email_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    subject VARCHAR(255),
    participants JSON, -- Array of email addresses
    message_count INTEGER DEFAULT 0,
    last_message_date TIMESTAMP,
    is_read BOOLEAN DEFAULT FALSE,
    is_flagged BOOLEAN DEFAULT FALSE,
    folder_ids JSON, -- Array of folder IDs containing messages from this thread
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES email_accounts(id) ON DELETE CASCADE
);

-- AI-generated responses/suggestions
CREATE TABLE ai_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message_id INTEGER,
    response_type VARCHAR(50), -- 'reply', 'forward', 'summary', 'category'
    prompt TEXT,
    response_text TEXT,
    model_used VARCHAR(100),
    tokens_used INTEGER,
    generation_time_ms INTEGER,
    confidence_score FLOAT,
    is_used BOOLEAN DEFAULT FALSE,
    feedback VARCHAR(20), -- 'good', 'bad', 'neutral'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (message_id) REFERENCES email_messages(id) ON DELETE CASCADE
);

-- User preferences and settings
CREATE TABLE user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL, -- 'general', 'email', 'ai', 'notifications'
    key VARCHAR(100) NOT NULL,
    value TEXT,
    data_type VARCHAR(20) DEFAULT 'string', -- 'string', 'integer', 'boolean', 'json'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(user_id, category, key)
);

-- Authentication tokens (PASETO)
CREATE TABLE auth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token_id VARCHAR(255) UNIQUE NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    purpose VARCHAR(50) NOT NULL, -- 'access', 'refresh', 'api'
    scopes JSON, -- Array of permission scopes
    expires_at TIMESTAMP NOT NULL,
    is_revoked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    user_agent TEXT,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- API rate limiting
CREATE TABLE rate_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier VARCHAR(255) NOT NULL, -- IP address, user ID, or API key
    endpoint VARCHAR(255) NOT NULL,
    request_count INTEGER DEFAULT 0,
    window_start TIMESTAMP NOT NULL,
    window_duration INTEGER NOT NULL, -- seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(identifier, endpoint, window_start)
);

-- Email sync logs
CREATE TABLE sync_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    sync_type VARCHAR(50), -- 'full', 'incremental', 'folder'
    status VARCHAR(20), -- 'started', 'completed', 'failed'
    messages_processed INTEGER DEFAULT 0,
    messages_added INTEGER DEFAULT 0,
    messages_updated INTEGER DEFAULT 0,
    messages_deleted INTEGER DEFAULT 0,
    error_message TEXT,
    sync_duration_ms INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES email_accounts(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_email_accounts_user_id ON email_accounts(user_id);
CREATE INDEX idx_email_accounts_tenant_id ON email_accounts(tenant_id);
CREATE INDEX idx_email_folders_account_id ON email_folders(account_id);
CREATE INDEX idx_email_messages_account_id ON email_messages(account_id);
CREATE INDEX idx_email_messages_folder_id ON email_messages(folder_id);
CREATE INDEX idx_email_messages_thread_id ON email_messages(thread_id);
CREATE INDEX idx_email_messages_date_received ON email_messages(date_received);
CREATE INDEX idx_email_messages_is_read ON email_messages(is_read);
CREATE INDEX idx_auth_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX idx_auth_tokens_expires_at ON auth_tokens(expires_at);
CREATE INDEX idx_rate_limits_identifier ON rate_limits(identifier);
CREATE INDEX idx_sync_logs_account_id ON sync_logs(account_id);
CREATE INDEX idx_sync_logs_started_at ON sync_logs(started_at);

-- Marketing campaigns table
CREATE TABLE marketing_campaigns (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    subject_line VARCHAR(500) NOT NULL,
    email_template TEXT NOT NULL,
    sender_email VARCHAR(255) NOT NULL,
    sender_name VARCHAR(255) NOT NULL,
    recipient_segments JSON,
    recipient_count INTEGER DEFAULT 0,
    scheduled_time TIMESTAMP,
    sent_time TIMESTAMP,
    created_by VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metrics_emails_sent INTEGER DEFAULT 0,
    metrics_emails_delivered INTEGER DEFAULT 0,
    metrics_emails_bounced INTEGER DEFAULT 0,
    metrics_emails_opened INTEGER DEFAULT 0,
    metrics_emails_clicked INTEGER DEFAULT 0,
    metrics_emails_unsubscribed INTEGER DEFAULT 0,
    metrics_emails_spam INTEGER DEFAULT 0,
    metrics_open_rate FLOAT DEFAULT 0.0,
    metrics_click_rate FLOAT DEFAULT 0.0,
    metrics_bounce_rate FLOAT DEFAULT 0.0,
    metrics_unsubscribe_rate FLOAT DEFAULT 0.0,
    metrics_conversion_rate FLOAT DEFAULT 0.0,
    metrics_revenue_generated FLOAT DEFAULT 0.0,
    metrics_cost_per_email FLOAT DEFAULT 0.0,
    metrics_roi FLOAT DEFAULT 0.0,
    tags JSON,
    is_ab_test BOOLEAN DEFAULT FALSE,
    ab_test_variants JSON
);

-- Email analytics table
CREATE TABLE email_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_address VARCHAR(255) NOT NULL,
    campaign_id VARCHAR(50) NOT NULL,
    sent_time TIMESTAMP,
    delivered_time TIMESTAMP,
    opened_time TIMESTAMP,
    clicked_time TIMESTAMP,
    unsubscribe_time TIMESTAMP,
    bounce_time TIMESTAMP,
    spam_time TIMESTAMP,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    open_count INTEGER DEFAULT 0,
    click_count INTEGER DEFAULT 0,
    ip_address VARCHAR(45),
    user_agent TEXT,
    email_client VARCHAR(100),
    device_type VARCHAR(50),
    location VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id) ON DELETE CASCADE,
    UNIQUE(email_address, campaign_id)
);

-- User engagement table
CREATE TABLE user_engagement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    last_activity TIMESTAMP NOT NULL,
    engagement_score FLOAT DEFAULT 0.0,
    email_engagement FLOAT DEFAULT 0.0,
    website_visits INTEGER DEFAULT 0,
    conversion_events INTEGER DEFAULT 0,
    total_revenue FLOAT DEFAULT 0.0,
    preferred_time VARCHAR(20),
    preferred_day VARCHAR(20),
    unsubscribe_all BOOLEAN DEFAULT FALSE,
    email_preferences JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create indexes for marketing tables
CREATE INDEX idx_marketing_campaigns_created_by ON marketing_campaigns(created_by);
CREATE INDEX idx_marketing_campaigns_status ON marketing_campaigns(status);
CREATE INDEX idx_marketing_campaigns_campaign_type ON marketing_campaigns(campaign_type);
CREATE INDEX idx_marketing_campaigns_created_at ON marketing_campaigns(created_at);
CREATE INDEX idx_email_analytics_email_address ON email_analytics(email_address);
CREATE INDEX idx_email_analytics_campaign_id ON email_analytics(campaign_id);
CREATE INDEX idx_email_analytics_status ON email_analytics(status);
CREATE INDEX idx_user_engagement_user_id ON user_engagement(user_id);
CREATE INDEX idx_user_engagement_email ON user_engagement(email);