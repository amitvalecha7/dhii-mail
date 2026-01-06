#!/usr/bin/env python3
"""
Test script for marketing manager database integration
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timezone
from fastapi import HTTPException
from marketing_manager import MarketingManager, CampaignType, CampaignStatus, CampaignCreate, CampaignUpdate

def test_marketing_db_integration():
    """Test marketing manager database integration"""
    print("Testing marketing manager database integration...")
    
    try:
        # Initialize marketing manager
        manager = MarketingManager()
        
        # Test user
        test_user = "test@example.com"
        
        print("\n1. Testing campaign creation...")
        # Create a test campaign
        campaign_data = CampaignCreate(
            name="Test Campaign",
            description="Testing database integration",
            campaign_type=CampaignType.NEWSLETTER,
            subject_line="Test Subject",
            email_template="Test template content",
            sender_email="sender@example.com",
            sender_name="Test Sender",
            recipient_segments=["all_users"]
        )
        
        campaign = manager.create_campaign(campaign_data, test_user)
        print(f"✓ Created campaign: {campaign.id}")
        print(f"  Name: {campaign.name}")
        print(f"  Status: {campaign.status}")
        print(f"  Created at: {campaign.created_at}")
        
        print("\n2. Testing campaign retrieval...")
        # Retrieve the campaign
        retrieved_campaign = manager.get_campaign(campaign.id)
        print(f"✓ Retrieved campaign: {retrieved_campaign.id}")
        print(f"  Name: {retrieved_campaign.name}")
        print(f"  Status: {retrieved_campaign.status}")
        
        print("\n3. Testing campaign update...")
        # Update the campaign
        update_data = CampaignUpdate(
            name="Updated Test Campaign",
            description="Updated description",
            status=CampaignStatus.SCHEDULED
        )
        updated_campaign = manager.update_campaign(campaign.id, update_data)
        print(f"✓ Updated campaign: {updated_campaign.id}")
        print(f"  New name: {updated_campaign.name}")
        print(f"  New status: {updated_campaign.status}")
        
        print("\n4. Testing campaign listing...")
        # List campaigns
        campaigns = manager.list_campaigns(test_user)
        print(f"✓ Found {len(campaigns)} campaigns")
        for c in campaigns:
            print(f"  - {c.name} ({c.status})")
        
        print("\n5. Testing user engagement...")
        # Test user engagement
        user_id = "test_user_123"
        engagement = manager.get_user_engagement(user_id)
        print(f"✓ Retrieved user engagement: {engagement.user_id}")
        print(f"  Score: {engagement.engagement_score}")
        print(f"  Last activity: {engagement.last_activity}")
        
        # Update engagement
        engagement_data = {
            "email_engagement": {"opens": 10, "clicks": 5},
            "website_visits": {"count": 25, "last_visit": datetime.now(timezone.utc).isoformat()},
            "total_revenue": 150.00
        }
        updated_engagement = manager.update_user_engagement(user_id, engagement_data)
        print(f"✓ Updated user engagement: {updated_engagement.engagement_score}")
        
        print("\n6. Testing marketing dashboard...")
        # Test dashboard
        dashboard = manager.get_marketing_dashboard(test_user)
        print(f"✓ Retrieved dashboard data")
        print(f"  Total campaigns: {dashboard['summary']['total_campaigns']}")
        print(f"  Active campaigns: {dashboard['summary']['active_campaigns']}")
        print(f"  Draft campaigns: {dashboard['summary']['draft_campaigns']}")
        print(f"  Avg open rate: {dashboard['performance_metrics']['avg_open_rate']}%")
        print(f"  Avg click rate: {dashboard['performance_metrics']['avg_click_rate']}%")
        
        print("\n7. Testing campaign deletion...")
        # Delete the campaign
        delete_result = manager.delete_campaign(campaign.id)
        print(f"✓ Deleted campaign: {delete_result}")
        
        # Verify deletion
        try:
            deleted_campaign = manager.get_campaign(campaign.id)
            print("✗ Campaign still exists after deletion")
            return False
        except HTTPException as e:
            if e.status_code == 404:
                print("✓ Campaign successfully deleted from database")
            else:
                print(f"✗ Unexpected error: {e}")
                return False
        
        print("\n✅ All database integration tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_marketing_db_integration()
    sys.exit(0 if success else 1)