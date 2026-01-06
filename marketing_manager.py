"""
Marketing Tools and Analytics Module for dhii Mail
Handles marketing campaigns, email analytics, user engagement tracking, and campaign performance metrics
"""

import uuid
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from enum import Enum
from database import get_db

# Configure logging
logger = logging.getLogger(__name__)

class CampaignStatus(str, Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENT = "sent"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CampaignType(str, Enum):
    """Campaign type enumeration"""
    EMAIL = "email"
    NEWSLETTER = "newsletter"
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    WELCOME = "welcome"
    ABANDONED_CART = "abandoned_cart"

class EmailStatus(str, Enum):
    """Email status enumeration"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"
    UNSUBSCRIBED = "unsubscribed"
    SPAM = "spam"

class CampaignMetrics(BaseModel):
    """Campaign performance metrics"""
    emails_sent: int = 0
    emails_delivered: int = 0
    emails_bounced: int = 0
    emails_opened: int = 0
    emails_clicked: int = 0
    emails_unsubscribed: int = 0
    emails_spam: int = 0
    open_rate: float = 0.0
    click_rate: float = 0.0
    bounce_rate: float = 0.0
    unsubscribe_rate: float = 0.0
    conversion_rate: float = 0.0
    revenue_generated: float = 0.0
    cost_per_email: float = 0.0
    roi: float = 0.0

class MarketingCampaign(BaseModel):
    """Marketing campaign model"""
    id: str
    name: str
    description: Optional[str] = None
    campaign_type: CampaignType
    status: CampaignStatus = CampaignStatus.DRAFT
    subject_line: str
    email_template: str
    sender_email: str
    sender_name: str
    recipient_segments: List[str] = []
    recipient_count: int = 0
    scheduled_time: Optional[datetime] = None
    sent_time: Optional[datetime] = None
    created_by: str
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    metrics: CampaignMetrics = CampaignMetrics()
    tags: List[str] = []
    is_ab_test: bool = False
    ab_test_variants: List[Dict[str, Any]] = []

class EmailAnalytics(BaseModel):
    """Email analytics model"""
    email_address: str
    campaign_id: str
    sent_time: Optional[datetime] = None
    delivered_time: Optional[datetime] = None
    opened_time: Optional[datetime] = None
    clicked_time: Optional[datetime] = None
    unsubscribe_time: Optional[datetime] = None
    bounce_time: Optional[datetime] = None
    spam_time: Optional[datetime] = None
    status: EmailStatus = EmailStatus.PENDING
    open_count: int = 0
    click_count: int = 0
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    email_client: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None

class CampaignCreate(BaseModel):
    """Campaign creation request"""
    name: str
    description: Optional[str] = None
    campaign_type: CampaignType
    subject_line: str
    email_template: str
    sender_email: str
    sender_name: str
    recipient_segments: List[str] = []
    scheduled_time: Optional[datetime] = None
    tags: List[str] = []
    is_ab_test: bool = False
    ab_test_variants: List[Dict[str, Any]] = []

class CampaignUpdate(BaseModel):
    """Campaign update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    subject_line: Optional[str] = None
    email_template: Optional[str] = None
    sender_email: Optional[str] = None
    sender_name: Optional[str] = None
    recipient_segments: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None
    tags: Optional[List[str]] = None
    status: Optional[CampaignStatus] = None

class UserEngagement(BaseModel):
    """User engagement tracking model"""
    user_id: str
    email: str
    last_activity: datetime
    engagement_score: float = 0.0
    email_engagement: Dict[str, Any] = {}
    website_visits: Dict[str, Any] = {}
    conversion_events: List[Dict[str, Any]] = []
    total_revenue: float = 0.0
    preferred_time: Optional[str] = None
    preferred_day: Optional[str] = None
    unsubscribe_all: bool = False
    email_preferences: Dict[str, bool] = {}

class MarketingManager:
    """Marketing Tools and Analytics Manager"""
    
    def __init__(self):
        self.db = get_db()  # Database connection
        self.segments = {
            "all_users": [],
            "active_users": [],
            "inactive_users": [],
            "premium_users": [],
            "new_users": [],
            "returning_users": []
        }
        self.email_templates = {
            "welcome": {
                "subject": "Welcome to dhii Mail!",
                "template": "Welcome to our platform, {{first_name}}! We're excited to have you on board."
            },
            "newsletter": {
                "subject": "Monthly Newsletter",
                "template": "Here's what's new this month at dhii Mail..."
            },
            "promotional": {
                "subject": "Special Offer Just for You",
                "template": "Get 20% off your next purchase with code {{promo_code}}!"
            }
        }
    
    def create_campaign(self, campaign_data: CampaignCreate, created_by: str) -> MarketingCampaign:
        """Create a new marketing campaign"""
        try:
            campaign_id = str(uuid.uuid4())
            
            campaign = MarketingCampaign(
                id=campaign_id,
                name=campaign_data.name,
                description=campaign_data.description,
                campaign_type=campaign_data.campaign_type,
                subject_line=campaign_data.subject_line,
                email_template=campaign_data.email_template,
                sender_email=campaign_data.sender_email,
                sender_name=campaign_data.sender_name,
                recipient_segments=campaign_data.recipient_segments,
                recipient_count=0,  # Will be calculated when recipients are added
                scheduled_time=campaign_data.scheduled_time,
                created_by=created_by,
                is_ab_test=campaign_data.is_ab_test,
                ab_test_variants=campaign_data.ab_test_variants
            )
            
            # Save to database
            self._save_campaign_to_db(campaign)
            
            logger.info(f"Created marketing campaign: {campaign_id} by {created_by}")
            return campaign
            
        except Exception as e:
            logger.error(f"Error creating marketing campaign: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create campaign: {str(e)}")
    
    def get_campaign(self, campaign_id: str) -> MarketingCampaign:
        """Get campaign details"""
        campaign = self._get_campaign_from_db(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        return campaign
    
    def update_campaign(self, campaign_id: str, update_data: CampaignUpdate) -> MarketingCampaign:
        """Update campaign details"""
        campaign = self._get_campaign_from_db(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Update fields if provided
        if update_data.name is not None:
            campaign.name = update_data.name
        if update_data.description is not None:
            campaign.description = update_data.description
        if update_data.subject_line is not None:
            campaign.subject_line = update_data.subject_line
        if update_data.email_template is not None:
            campaign.email_template = update_data.email_template
        if update_data.sender_email is not None:
            campaign.sender_email = update_data.sender_email
        if update_data.sender_name is not None:
            campaign.sender_name = update_data.sender_name
        if update_data.recipient_segments is not None:
            campaign.recipient_segments = update_data.recipient_segments
        if update_data.scheduled_time is not None:
            campaign.scheduled_time = update_data.scheduled_time
        if update_data.tags is not None:
            campaign.tags = update_data.tags
        if update_data.status is not None:
            campaign.status = update_data.status
        
        campaign.updated_at = datetime.now(timezone.utc)
        
        # Update in database
        self._update_campaign_in_db(campaign)
        
        logger.info(f"Updated marketing campaign: {campaign_id}")
        return campaign
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """Delete a campaign"""
        # Check if campaign exists
        campaign = self._get_campaign_from_db(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Delete from database
        query = "DELETE FROM marketing_campaigns WHERE id = ?"
        self.db.execute_update(query, (campaign_id,))
        
        logger.info(f"Deleted marketing campaign: {campaign_id}")
        return True
    
    def list_campaigns(self, user_email: str, status: Optional[CampaignStatus] = None) -> List[MarketingCampaign]:
        """List campaigns for a user"""
        try:
            if status:
                query = "SELECT * FROM marketing_campaigns WHERE created_by = ? AND status = ? ORDER BY created_at DESC"
                results = self.db.execute_query(query, (user_email, status.value))
            else:
                query = "SELECT * FROM marketing_campaigns WHERE created_by = ? ORDER BY created_at DESC"
                results = self.db.execute_query(query, (user_email,))
            
            return [self._row_to_campaign(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error listing campaigns: {e}")
            return []
    
    def schedule_campaign(self, campaign_id: str, scheduled_time: datetime) -> MarketingCampaign:
        """Schedule a campaign for future delivery"""
        campaign = self._get_campaign_from_db(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        campaign.scheduled_time = scheduled_time
        campaign.status = CampaignStatus.SCHEDULED
        
        # Update in database
        self._update_campaign_in_db(campaign)
        
        logger.info(f"Scheduled campaign {campaign_id} for {scheduled_time}")
        return campaign
    
    def send_campaign(self, campaign_id: str) -> MarketingCampaign:
        """Send a campaign immediately"""
        campaign = self._get_campaign_from_db(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Simulate sending emails
        campaign.status = CampaignStatus.SENT
        campaign.sent_time = datetime.now(timezone.utc)
        campaign.metrics.emails_sent = campaign.recipient_count
        campaign.metrics.emails_delivered = int(campaign.recipient_count * 0.95)  # 95% delivery rate
        campaign.metrics.emails_bounced = campaign.recipient_count - campaign.metrics.emails_delivered
        
        # Update in database
        self._update_campaign_in_db(campaign)
        
        logger.info(f"Sent marketing campaign: {campaign_id} to {campaign.recipient_count} recipients")
        return campaign
    
    def track_email_event(self, email_address: str, campaign_id: str, event_type: str, 
                         metadata: Optional[Dict[str, Any]] = None) -> EmailAnalytics:
        """Track email events (open, click, bounce, etc.)"""
        try:
            # Get existing analytics or create new
            analytics = self._get_email_analytics(email_address, campaign_id)
            if analytics is None:
                analytics = EmailAnalytics(
                    email_address=email_address,
                    campaign_id=campaign_id
                )
            
            current_time = datetime.now(timezone.utc)
            
            # Update based on event type
            if event_type == "sent":
                analytics.status = EmailStatus.SENT
                analytics.sent_time = current_time
            elif event_type == "delivered":
                analytics.status = EmailStatus.DELIVERED
                analytics.delivered_time = current_time
            elif event_type == "opened":
                analytics.status = EmailStatus.OPENED
                analytics.opened_time = current_time
                analytics.open_count += 1
            elif event_type == "clicked":
                analytics.status = EmailStatus.CLICKED
                analytics.clicked_time = current_time
                analytics.click_count += 1
            elif event_type == "bounced":
                analytics.status = EmailStatus.BOUNCED
                analytics.bounce_time = current_time
            elif event_type == "unsubscribed":
                analytics.status = EmailStatus.UNSUBSCRIBED
                analytics.unsubscribe_time = current_time
            elif event_type == "spam":
                analytics.status = EmailStatus.SPAM
                analytics.spam_time = current_time
            
            # Add metadata if provided
            if metadata:
                if "ip_address" in metadata:
                    analytics.ip_address = metadata["ip_address"]
                if "user_agent" in metadata:
                    analytics.user_agent = metadata["user_agent"]
                    # Parse user agent for email client and device info
                    analytics.email_client = self._parse_email_client(metadata["user_agent"])
                    analytics.device_type = self._parse_device_type(metadata["user_agent"])
                if "location" in metadata:
                    analytics.location = metadata["location"]
            
            # Save analytics to database
            self._save_email_analytics(analytics)
            
            # Update campaign metrics
            self._update_campaign_metrics(campaign_id, event_type)
            
            logger.info(f"Tracked email event: {event_type} for {email_address} in campaign {campaign_id}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error tracking email event: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to track email event: {str(e)}")
    
    def get_campaign_analytics(self, campaign_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a campaign"""
        campaign = self._get_campaign_from_db(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campaign not found")
        
        # Calculate rates
        if campaign.metrics.emails_sent > 0:
            campaign.metrics.open_rate = (campaign.metrics.emails_opened / campaign.metrics.emails_sent) * 100
            campaign.metrics.click_rate = (campaign.metrics.emails_clicked / campaign.metrics.emails_sent) * 100
            campaign.metrics.bounce_rate = (campaign.metrics.emails_bounced / campaign.metrics.emails_sent) * 100
            campaign.metrics.unsubscribe_rate = (campaign.metrics.emails_unsubscribed / campaign.metrics.emails_sent) * 100
        
        # Get individual email analytics from database
        email_analytics_list = self._get_email_analytics_for_campaign(campaign_id)
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "metrics": campaign.metrics,
            "email_analytics": email_analytics_list,
            "performance_summary": {
                "total_recipients": campaign.recipient_count,
                "successful_deliveries": campaign.metrics.emails_delivered,
                "engagement_rate": campaign.metrics.open_rate,
                "click_through_rate": campaign.metrics.click_rate,
                "overall_performance": self._get_performance_rating(campaign.metrics)
            }
        }
    
    def get_user_engagement(self, user_id: str) -> UserEngagement:
        """Get user engagement data"""
        engagement = self._get_user_engagement_from_db(user_id)
        if engagement is None:
            # Create new engagement data
            engagement = UserEngagement(
                user_id=user_id,
                email="user@example.com",  # This would come from user data
                last_activity=datetime.now(timezone.utc)
            )
            self._save_user_engagement(engagement)
        
        return engagement
    
    def update_user_engagement(self, user_id: str, engagement_data: Dict[str, Any]) -> UserEngagement:
        """Update user engagement metrics"""
        engagement = self.get_user_engagement(user_id)
        
        if "email_engagement" in engagement_data:
            engagement.email_engagement = engagement_data["email_engagement"]
        if "website_visits" in engagement_data:
            engagement.website_visits = engagement_data["website_visits"]
        if "conversion_events" in engagement_data:
            engagement.conversion_events = engagement_data["conversion_events"]
        if "total_revenue" in engagement_data:
            engagement.total_revenue = engagement_data["total_revenue"]
        if "preferred_time" in engagement_data:
            engagement.preferred_time = engagement_data["preferred_time"]
        if "preferred_day" in engagement_data:
            engagement.preferred_day = engagement_data["preferred_day"]
        if "unsubscribe_all" in engagement_data:
            engagement.unsubscribe_all = engagement_data["unsubscribe_all"]
        if "email_preferences" in engagement_data:
            engagement.email_preferences = engagement_data["email_preferences"]
        
        engagement.last_activity = datetime.now(timezone.utc)
        
        # Calculate overall engagement score
        engagement.engagement_score = self._calculate_engagement_score(engagement)
        
        # Save to database
        self._save_user_engagement(engagement)
        
        logger.info(f"Updated user engagement for {user_id}: score {engagement.engagement_score}")
        return engagement
    
    def get_marketing_dashboard(self, user_email: str) -> Dict[str, Any]:
        """Get marketing dashboard data"""
        try:
            user_campaigns = self.list_campaigns(user_email)
            
            # Calculate summary statistics
            total_campaigns = len(user_campaigns)
            active_campaigns = len([c for c in user_campaigns if c.status == CampaignStatus.SENT])
            draft_campaigns = len([c for c in user_campaigns if c.status == CampaignStatus.DRAFT])
            
            # Calculate aggregate metrics
            total_emails_sent = sum(c.metrics.emails_sent for c in user_campaigns)
            total_emails_delivered = sum(c.metrics.emails_delivered for c in user_campaigns)
            total_emails_opened = sum(c.metrics.emails_opened for c in user_campaigns)
            total_emails_clicked = sum(c.metrics.emails_clicked for c in user_campaigns)
            
            avg_open_rate = (total_emails_opened / total_emails_sent * 100) if total_emails_sent > 0 else 0
            avg_click_rate = (total_emails_clicked / total_emails_sent * 100) if total_emails_sent > 0 else 0
            avg_delivery_rate = (total_emails_delivered / total_emails_sent * 100) if total_emails_sent > 0 else 0
            
            return {
                "summary": {
                    "total_campaigns": total_campaigns,
                    "active_campaigns": active_campaigns,
                    "draft_campaigns": draft_campaigns,
                    "total_emails_sent": total_emails_sent,
                    "total_emails_delivered": total_emails_delivered,
                    "total_emails_opened": total_emails_opened,
                    "total_emails_clicked": total_emails_clicked
                },
                "performance_metrics": {
                    "avg_open_rate": round(avg_open_rate, 2),
                    "avg_click_rate": round(avg_click_rate, 2),
                    "avg_delivery_rate": round(avg_delivery_rate, 2),
                    "avg_engagement_score": avg_open_rate + avg_click_rate
                },
                "recent_campaigns": user_campaigns[-5:],  # Last 5 campaigns
                "top_performing_campaigns": sorted(user_campaigns, key=lambda x: x.metrics.open_rate, reverse=True)[:3],
                "campaigns_by_status": {
                    "draft": len([c for c in user_campaigns if c.status == CampaignStatus.DRAFT]),
                    "scheduled": len([c for c in user_campaigns if c.status == CampaignStatus.SCHEDULED]),
                    "sent": len([c for c in user_campaigns if c.status == CampaignStatus.SENT]),
                    "completed": len([c for c in user_campaigns if c.status == CampaignStatus.COMPLETED])
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting marketing dashboard: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")
    
    def get_email_templates(self) -> Dict[str, Any]:
        """Get available email templates"""
        return self.email_templates
    
    def create_email_template(self, template_name: str, subject: str, template_content: str) -> Dict[str, Any]:
        """Create a new email template"""
        self.email_templates[template_name] = {
            "subject": subject,
            "template": template_content
        }
        logger.info(f"Created email template: {template_name}")
        return self.email_templates[template_name]
    
    def _parse_email_client(self, user_agent: str) -> Optional[str]:
        """Parse email client from user agent"""
        user_agent_lower = user_agent.lower()
        if "gmail" in user_agent_lower:
            return "Gmail"
        elif "outlook" in user_agent_lower or "microsoft" in user_agent_lower:
            return "Outlook"
        elif "apple" in user_agent_lower or "mac" in user_agent_lower:
            return "Apple Mail"
        elif "yahoo" in user_agent_lower:
            return "Yahoo Mail"
        elif "thunderbird" in user_agent_lower:
            return "Thunderbird"
        else:
            return "Unknown"
    
    def _parse_device_type(self, user_agent: str) -> Optional[str]:
        """Parse device type from user agent"""
        user_agent_lower = user_agent.lower()
        if "mobile" in user_agent_lower or "android" in user_agent_lower or "iphone" in user_agent_lower:
            return "Mobile"
        elif "tablet" in user_agent_lower or "ipad" in user_agent_lower:
            return "Tablet"
        else:
            return "Desktop"
    
    def _update_campaign_metrics(self, campaign_id: str, event_type: str):
        """Update campaign metrics based on email event"""
        if campaign_id not in self.campaigns:
            return
        
        campaign = self.campaigns[campaign_id]
        
        if event_type == "sent":
            campaign.metrics.emails_sent += 1
        elif event_type == "delivered":
            campaign.metrics.emails_delivered += 1
        elif event_type == "opened":
            campaign.metrics.emails_opened += 1
        elif event_type == "clicked":
            campaign.metrics.emails_clicked += 1
        elif event_type == "bounced":
            campaign.metrics.emails_bounced += 1
        elif event_type == "unsubscribed":
            campaign.metrics.emails_unsubscribed += 1
        elif event_type == "spam":
            campaign.metrics.emails_spam += 1
    
    def _calculate_engagement_score(self, engagement: UserEngagement) -> float:
        """Calculate user engagement score (0-100)"""
        score = 0.0
        
        # Email engagement (40% weight) - calculate from email_engagement dict
        email_score = 0.0
        if engagement.email_engagement:
            # Use opens and clicks if available
            opens = engagement.email_engagement.get('opens', 0)
            clicks = engagement.email_engagement.get('clicks', 0)
            email_score = min((opens * 0.5 + clicks * 1.0) / 10, 1.0) * 40
        score += email_score
        
        # Website visits (30% weight) - calculate from website_visits dict
        visit_score = 0.0
        if engagement.website_visits:
            count = engagement.website_visits.get('count', 0)
            visit_score = min(count / 10, 1.0) * 30
        score += visit_score
        
        # Conversion events (30% weight) - calculate from conversion_events list
        conversion_score = 0.0
        if engagement.conversion_events:
            conversion_score = min(len(engagement.conversion_events) / 5, 1.0) * 30
        score += conversion_score
        
        # Penalty for unsubscribing
        if engagement.unsubscribe_all:
            score = max(0, score - 50)
        
        return min(score, 100.0)
    
    def _get_performance_rating(self, metrics: CampaignMetrics) -> str:
        """Get performance rating based on metrics"""
        if metrics.emails_sent == 0:
            return "No Data"
        
        # Calculate weighted score
        score = 0
        score += metrics.open_rate * 0.4  # 40% weight for open rate
        score += metrics.click_rate * 0.4  # 40% weight for click rate
        score += (100 - metrics.bounce_rate) * 0.2  # 20% weight for low bounce rate
        
        if score >= 80:
            return "Excellent"
        elif score >= 60:
            return "Good"
        elif score >= 40:
            return "Average"
        elif score >= 20:
            return "Below Average"
        else:
            return "Poor"

    def _save_campaign_to_db(self, campaign: MarketingCampaign) -> None:
        """Save campaign to database"""
        try:
            query = """
                INSERT INTO marketing_campaigns (
                    id, name, description, campaign_type, status, subject_line, email_template,
                    sender_email, sender_name, recipient_segments, recipient_count,
                    scheduled_time, sent_time, created_by, created_at, updated_at,
                    metrics_emails_sent, metrics_emails_delivered, metrics_emails_bounced,
                    metrics_emails_opened, metrics_emails_clicked, metrics_emails_unsubscribed,
                    metrics_emails_spam, metrics_open_rate, metrics_click_rate,
                    metrics_bounce_rate, metrics_unsubscribe_rate, metrics_conversion_rate,
                    metrics_revenue_generated, metrics_cost_per_email, metrics_roi,
                    tags, is_ab_test, ab_test_variants
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                campaign.id, campaign.name, campaign.description, campaign.campaign_type.value,
                campaign.status.value, campaign.subject_line, campaign.email_template,
                campaign.sender_email, campaign.sender_name, json.dumps(campaign.recipient_segments),
                campaign.recipient_count, campaign.scheduled_time, campaign.sent_time,
                campaign.created_by, campaign.created_at, campaign.updated_at,
                campaign.metrics.emails_sent, campaign.metrics.emails_delivered,
                campaign.metrics.emails_bounced, campaign.metrics.emails_opened,
                campaign.metrics.emails_clicked, campaign.metrics.emails_unsubscribed,
                campaign.metrics.emails_spam, campaign.metrics.open_rate,
                campaign.metrics.click_rate, campaign.metrics.bounce_rate,
                campaign.metrics.unsubscribe_rate, campaign.metrics.conversion_rate,
                campaign.metrics.revenue_generated, campaign.metrics.cost_per_email,
                campaign.metrics.roi, json.dumps(campaign.tags), campaign.is_ab_test,
                json.dumps(campaign.ab_test_variants)
            )
            
            self.db.execute_update(query, params)
            
        except Exception as e:
            logger.error(f"Error saving campaign to database: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save campaign: {str(e)}")

    def _get_campaign_from_db(self, campaign_id: str) -> Optional[MarketingCampaign]:
        """Get campaign from database"""
        try:
            query = "SELECT * FROM marketing_campaigns WHERE id = ?"
            results = self.db.execute_query(query, (campaign_id,))
            
            if not results:
                return None
            
            row = results[0]
            return self._row_to_campaign(row)
            
        except Exception as e:
            logger.error(f"Error getting campaign from database: {e}")
            return None

    def _row_to_campaign(self, row: Dict[str, Any]) -> MarketingCampaign:
        """Convert database row to MarketingCampaign object"""
        return MarketingCampaign(
            id=row['id'],
            name=row['name'],
            description=row['description'],
            campaign_type=CampaignType(row['campaign_type']),
            status=CampaignStatus(row['status']),
            subject_line=row['subject_line'],
            email_template=row['email_template'],
            sender_email=row['sender_email'],
            sender_name=row['sender_name'],
            recipient_segments=row['recipient_segments'] if row['recipient_segments'] else [],
            recipient_count=row['recipient_count'],
            scheduled_time=row['scheduled_time'],
            sent_time=row['sent_time'],
            created_by=row['created_by'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            metrics=CampaignMetrics(
                emails_sent=row['metrics_emails_sent'],
                emails_delivered=row['metrics_emails_delivered'],
                emails_bounced=row['metrics_emails_bounced'],
                emails_opened=row['metrics_emails_opened'],
                emails_clicked=row['metrics_emails_clicked'],
                emails_unsubscribed=row['metrics_emails_unsubscribed'],
                emails_spam=row['metrics_emails_spam'],
                open_rate=row['metrics_open_rate'],
                click_rate=row['metrics_click_rate'],
                bounce_rate=row['metrics_bounce_rate'],
                unsubscribe_rate=row['metrics_unsubscribe_rate'],
                conversion_rate=row['metrics_conversion_rate'],
                revenue_generated=row['metrics_revenue_generated'],
                cost_per_email=row['metrics_cost_per_email'],
                roi=row['metrics_roi']
            ),
            tags=row['tags'] if row['tags'] else [],
            is_ab_test=bool(row['is_ab_test']),
            ab_test_variants=row['ab_test_variants'] if row['ab_test_variants'] else []
        )

    def _update_campaign_in_db(self, campaign: MarketingCampaign) -> None:
        """Update campaign in database"""
        try:
            query = """
                UPDATE marketing_campaigns SET
                    name = ?, description = ?, status = ?, subject_line = ?, email_template = ?,
                    sender_email = ?, sender_name = ?, recipient_segments = ?, recipient_count = ?,
                    scheduled_time = ?, sent_time = ?, updated_at = ?,
                    metrics_emails_sent = ?, metrics_emails_delivered = ?, metrics_emails_bounced = ?,
                    metrics_emails_opened = ?, metrics_emails_clicked = ?, metrics_emails_unsubscribed = ?,
                    metrics_emails_spam = ?, metrics_open_rate = ?, metrics_click_rate = ?,
                    metrics_bounce_rate = ?, metrics_unsubscribe_rate = ?, metrics_conversion_rate = ?,
                    metrics_revenue_generated = ?, metrics_cost_per_email = ?, metrics_roi = ?,
                    tags = ?, is_ab_test = ?, ab_test_variants = ?
                WHERE id = ?
            """
            
            params = (
                campaign.name, campaign.description, campaign.status.value,
                campaign.subject_line, campaign.email_template, campaign.sender_email,
                campaign.sender_name, json.dumps(campaign.recipient_segments),
                campaign.recipient_count, campaign.scheduled_time, campaign.sent_time,
                campaign.updated_at, campaign.metrics.emails_sent,
                campaign.metrics.emails_delivered, campaign.metrics.emails_bounced,
                campaign.metrics.emails_opened, campaign.metrics.emails_clicked,
                campaign.metrics.emails_unsubscribed, campaign.metrics.emails_spam,
                campaign.metrics.open_rate, campaign.metrics.click_rate,
                campaign.metrics.bounce_rate, campaign.metrics.unsubscribe_rate,
                campaign.metrics.conversion_rate, campaign.metrics.revenue_generated,
                campaign.metrics.cost_per_email, campaign.metrics.roi,
                json.dumps(campaign.tags), campaign.is_ab_test,
                json.dumps(campaign.ab_test_variants), campaign.id
            )
            
            self.db.execute_update(query, params)
            
        except Exception as e:
            logger.error(f"Error updating campaign in database: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to update campaign: {str(e)}")

    def _get_email_analytics(self, email_address: str, campaign_id: str) -> Optional[EmailAnalytics]:
        """Get email analytics from database"""
        try:
            query = "SELECT * FROM email_analytics WHERE email_address = ? AND campaign_id = ?"
            results = self.db.execute_query(query, (email_address, campaign_id))
            
            if not results:
                return None
            
            row = results[0]
            return self._row_to_email_analytics(row)
            
        except Exception as e:
            logger.error(f"Error getting email analytics from database: {e}")
            return None

    def _save_email_analytics(self, analytics: EmailAnalytics) -> None:
        """Save email analytics to database"""
        try:
            # Check if analytics already exists
            existing = self._get_email_analytics(analytics.email_address, analytics.campaign_id)
            
            if existing:
                # Update existing analytics
                query = """
                    UPDATE email_analytics SET
                        sent_time = ?, delivered_time = ?, opened_time = ?, clicked_time = ?,
                        unsubscribe_time = ?, bounce_time = ?, spam_time = ?, status = ?,
                        open_count = ?, click_count = ?, ip_address = ?, user_agent = ?,
                        email_client = ?, device_type = ?, location = ?, updated_at = ?
                    WHERE email_address = ? AND campaign_id = ?
                """
                params = (
                    analytics.sent_time, analytics.delivered_time, analytics.opened_time,
                    analytics.clicked_time, analytics.unsubscribe_time, analytics.bounce_time,
                    analytics.spam_time, analytics.status.value, analytics.open_count,
                    analytics.click_count, analytics.ip_address, analytics.user_agent,
                    analytics.email_client, analytics.device_type, analytics.location,
                    datetime.now(timezone.utc), analytics.email_address, analytics.campaign_id
                )
            else:
                # Insert new analytics
                query = """
                    INSERT INTO email_analytics (
                        email_address, campaign_id, sent_time, delivered_time, opened_time,
                        clicked_time, unsubscribe_time, bounce_time, spam_time, status,
                        open_count, click_count, ip_address, user_agent, email_client,
                        device_type, location, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    analytics.email_address, analytics.campaign_id, analytics.sent_time,
                    analytics.delivered_time, analytics.opened_time, analytics.clicked_time,
                    analytics.unsubscribe_time, analytics.bounce_time, analytics.spam_time,
                    analytics.status.value, analytics.open_count, analytics.click_count,
                    analytics.ip_address, analytics.user_agent, analytics.email_client,
                    analytics.device_type, analytics.location, datetime.now(timezone.utc),
                    datetime.now(timezone.utc)
                )
            
            self.db.execute_update(query, params)
            
        except Exception as e:
            logger.error(f"Error saving email analytics to database: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save email analytics: {str(e)}")

    def _row_to_email_analytics(self, row: Dict[str, Any]) -> EmailAnalytics:
        """Convert database row to EmailAnalytics object"""
        return EmailAnalytics(
            email_address=row['email_address'],
            campaign_id=row['campaign_id'],
            sent_time=row['sent_time'],
            delivered_time=row['delivered_time'],
            opened_time=row['opened_time'],
            clicked_time=row['clicked_time'],
            unsubscribe_time=row['unsubscribe_time'],
            bounce_time=row['bounce_time'],
            spam_time=row['spam_time'],
            status=EmailStatus(row['status']),
            open_count=row['open_count'],
            click_count=row['click_count'],
            ip_address=row['ip_address'],
            user_agent=row['user_agent'],
            email_client=row['email_client'],
            device_type=row['device_type'],
            location=row['location']
        )

    def _get_email_analytics_for_campaign(self, campaign_id: str) -> List[EmailAnalytics]:
        """Get all email analytics for a campaign"""
        try:
            query = "SELECT * FROM email_analytics WHERE campaign_id = ?"
            results = self.db.execute_query(query, (campaign_id,))
            return [self._row_to_email_analytics(row) for row in results]
            
        except Exception as e:
            logger.error(f"Error getting email analytics for campaign: {e}")
            return []

    def _get_user_engagement_from_db(self, user_id: str) -> Optional[UserEngagement]:
        """Get user engagement from database"""
        try:
            query = "SELECT * FROM user_engagement WHERE user_id = ?"
            results = self.db.execute_query(query, (user_id,))
            
            if not results:
                return None
            
            row = results[0]
            return self._row_to_user_engagement(row)
            
        except Exception as e:
            logger.error(f"Error getting user engagement from database: {e}")
            return None

    def _save_user_engagement(self, engagement: UserEngagement) -> None:
        """Save user engagement to database"""
        try:
            # Check if engagement already exists
            existing = self._get_user_engagement_from_db(engagement.user_id)
            
            if existing:
                # Update existing engagement
                query = """
                    UPDATE user_engagement SET
                        email = ?, email_engagement = ?, website_visits = ?, conversion_events = ?,
                        total_revenue = ?, preferred_time = ?, preferred_day = ?, unsubscribe_all = ?,
                        email_preferences = ?, engagement_score = ?, last_activity = ?, updated_at = ?
                    WHERE user_id = ?
                """
                params = (
                    engagement.email, json.dumps(engagement.email_engagement), json.dumps(engagement.website_visits),
                    json.dumps(engagement.conversion_events), engagement.total_revenue,
                    engagement.preferred_time, engagement.preferred_day, engagement.unsubscribe_all,
                    json.dumps(engagement.email_preferences), engagement.engagement_score,
                    engagement.last_activity, datetime.now(timezone.utc), engagement.user_id
                )
            else:
                # Insert new engagement
                query = """
                    INSERT INTO user_engagement (
                        user_id, email, email_engagement, website_visits, conversion_events,
                        total_revenue, preferred_time, preferred_day, unsubscribe_all,
                        email_preferences, engagement_score, last_activity, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (
                    engagement.user_id, engagement.email, json.dumps(engagement.email_engagement),
                    json.dumps(engagement.website_visits), json.dumps(engagement.conversion_events),
                    engagement.total_revenue, engagement.preferred_time, engagement.preferred_day,
                    engagement.unsubscribe_all, json.dumps(engagement.email_preferences),
                    engagement.engagement_score, engagement.last_activity,
                    datetime.now(timezone.utc), datetime.now(timezone.utc)
                )
            
            self.db.execute_update(query, params)
            
        except Exception as e:
            logger.error(f"Error saving user engagement to database: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save user engagement: {str(e)}")

    def _row_to_user_engagement(self, row: Dict[str, Any]) -> UserEngagement:
        """Convert database row to UserEngagement object"""
        return UserEngagement(
            user_id=row['user_id'],
            email=row['email'],
            email_engagement=row['email_engagement'] if row['email_engagement'] else {},
            website_visits=row['website_visits'] if row['website_visits'] else {},
            conversion_events=row['conversion_events'] if row['conversion_events'] else [],
            total_revenue=row['total_revenue'],
            preferred_time=row['preferred_time'],
            preferred_day=row['preferred_day'],
            unsubscribe_all=row['unsubscribe_all'],
            email_preferences=row['email_preferences'] if row['email_preferences'] else {},
            engagement_score=row['engagement_score'],
            last_activity=row['last_activity']
        )

# Global marketing manager instance
marketing_manager = MarketingManager()