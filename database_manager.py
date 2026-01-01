#!/usr/bin/env python3
"""
Mock Database Manager for Chat API
Temporary implementation until full integration
"""

class DatabaseManager:
    """Mock database manager for chat interface"""
    
    def __init__(self):
        self.mock_data = {
            "users": {
                1: {
                    "id": 1,
                    "email": "user@example.com",
                    "name": "Test User",
                    "email_count": 156,
                    "last_sync": "2025-12-31T00:00:00Z"
                }
            },
            "emails": {
                1: [
                    {"id": 1, "sender": "john@company.com", "subject": "Project Update", "date": "2025-12-30T10:00:00Z", "sentiment": "positive"},
                    {"id": 2, "sender": "sarah@client.com", "subject": "Meeting Request", "date": "2025-12-30T14:00:00Z", "sentiment": "neutral"},
                    {"id": 3, "sender": "finance@company.com", "subject": "Invoice Approval", "date": "2025-12-29T09:00:00Z", "sentiment": "neutral"}
                ]
            }
        }
    
    def get_user(self, user_id: int):
        """Get user by ID"""
        return self.mock_data["users"].get(user_id)
    
    def get_user_emails(self, user_id: int, limit: int = 10):
        """Get emails for user"""
        return self.mock_data["emails"].get(user_id, [])[:limit]
    
    def search_emails(self, user_id: int, query: str, sender: str = None, date_range: str = None, timeframe: str = None):
        """Search emails with filters"""
        emails = self.mock_data["emails"].get(user_id, [])
        results = []
        
        for email in emails:
            # Simple search logic
            if query.lower() in email["subject"].lower() or query.lower() in email["sender"].lower():
                if sender and sender.lower() not in email["sender"].lower():
                    continue
                results.append(email)
        
        return results[:5]  # Return top 5 results