-- Marketing tables for Issue #30

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
    campaign_id VARCHAR(50) NOT NULL,
    email_address VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent TEXT,
    status VARCHAR(50) DEFAULT 'active',
    metadata JSON,
    FOREIGN KEY (campaign_id) REFERENCES marketing_campaigns(id) ON DELETE CASCADE
);

-- User engagement table
CREATE TABLE user_engagement (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    email_engagement JSON,
    website_visits JSON,
    conversion_events JSON,
    total_revenue FLOAT DEFAULT 0.0,
    preferred_time VARCHAR(10),
    preferred_day VARCHAR(20),
    unsubscribe_all BOOLEAN DEFAULT FALSE,
    email_preferences JSON,
    engagement_score FLOAT DEFAULT 0.0,
    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Marketing campaigns indexes
CREATE INDEX idx_marketing_campaigns_created_by ON marketing_campaigns(created_by);
CREATE INDEX idx_marketing_campaigns_status ON marketing_campaigns(status);
CREATE INDEX idx_marketing_campaigns_campaign_type ON marketing_campaigns(campaign_type);
CREATE INDEX idx_marketing_campaigns_created_at ON marketing_campaigns(created_at);

-- Email analytics indexes
CREATE INDEX idx_email_analytics_email_address ON email_analytics(email_address);
CREATE INDEX idx_email_analytics_campaign_id ON email_analytics(campaign_id);
CREATE INDEX idx_email_analytics_status ON email_analytics(status);

-- User engagement indexes
CREATE INDEX idx_user_engagement_user_id ON user_engagement(user_id);
CREATE INDEX idx_user_engagement_email ON user_engagement(email);