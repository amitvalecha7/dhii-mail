"""
A2UI Intelligence Integration - Application Layer Implementation
Integrates Intelligence Layer insights with A2UI streaming components
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Import Intelligence Layer
from intelligence_layer import IntelligenceLayer

logger = logging.getLogger(__name__)

class A2UIIntelligenceIntegration:
    """Integrates Intelligence Layer with A2UI components for Application Layer"""
    
    def __init__(self, intelligence_layer: IntelligenceLayer):
        self.intelligence = intelligence_layer
        
    def enhance_email_card(self, email_data: Dict[str, Any], original_card: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance email card with AI insights and intelligence badges"""
        
        # Get AI analysis for this email
        email_id = email_data.get('id', 'unknown')
        analysis = self.intelligence.get_email_analysis(email_id)
        
        if analysis:
            # Add AI summary to card content
            original_content = original_card.get('component', {}).get('Card', {}).get('content', {}).get('literalString', '')
            enhanced_content = f"{original_content}\n\n🤖 **AI Summary**: {analysis.get('summary', 'No summary available')}"
            
            # Update card content
            original_card['component']['Card']['content'] = {
                'literalString': enhanced_content
            }
            
            # Add intelligence badges based on analysis
            badges = self._generate_intelligence_badges(analysis)
            if badges:
                original_card['component']['Card']['badges'] = badges
                
        return original_card
    
    def _generate_intelligence_badges(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate intelligence badges based on AI analysis"""
        badges = []
        
        # Urgency badge
        if analysis.get('urgency', 0) > 0.7:
            badges.append({
                'label': '🚨 Urgent',
                'variant': 'danger',
                'tooltip': 'High priority email requiring immediate attention'
            })
        
        # Action required badge
        if analysis.get('action_required', False):
            badges.append({
                'label': '✅ Action Required',
                'variant': 'warning', 
                'tooltip': 'This email requires follow-up action'
            })
            
        # Sentiment badge
        sentiment = analysis.get('sentiment', 0)
        if sentiment > 0.6:
            badges.append({
                'label': '😊 Positive',
                'variant': 'success',
                'tooltip': 'Positive sentiment detected'
            })
        elif sentiment < 0.4:
            badges.append({
                'label': '😠 Negative', 
                'variant': 'danger',
                'tooltip': 'Negative sentiment detected'
            })
            
        return badges
    
    def create_daily_briefing_widget(self) -> Dict[str, Any]:
        """Create A2UI daily briefing widget with aggregated intelligence"""
        
        # Get daily insights from Intelligence Layer
        insights = self.intelligence.get_daily_insights()
        
        briefing_content = f"""
📊 **Daily Briefing - {datetime.now().strftime('%Y-%m-%d')}**

📧 **Emails**: {insights.get('email_count', 0)} total
   • {insights.get('urgent_emails', 0)} urgent emails
   • {insights.get('action_required_emails', 0)} requiring action

📅 **Meetings**: {insights.get('meeting_count', 0)} scheduled
   • {insights.get('optimal_meetings', 0)} optimally scheduled
   • {insights.get('conflicting_meetings', 0)} potential conflicts

🎯 **Top Priorities**:
"""
        
        # Add top priorities
        for i, priority in enumerate(insights.get('top_priorities', [])[:3], 1):
            briefing_content += f"   {i}. {priority}\n"
            
        return {
            'component': {
                'Card': {
                    'title': {'literalString': 'Daily Briefing'},
                    'content': {'literalString': briefing_content},
                    'variant': 'info',
                    'actions': [
                        {
                            'label': 'View Details',
                            'action': 'navigate_to_dashboard',
                            'variant': 'primary'
                        }
                    ]
                }
            }
        }
    
    def enhance_calendar_event(self, event_data: Dict[str, Any], original_component: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance calendar event with meeting optimization insights"""
        
        event_id = event_data.get('id', 'unknown')
        analysis = self.intelligence.get_meeting_analysis(event_id)
        
        if analysis:
            # Add optimization score badge
            optimality = analysis.get('optimality_score', 0)
            
            if optimality < 0.6:
                original_component['component']['Card']['status'] = 'warning'
                original_component['component']['Card']['badges'] = [{
                    'label': f'⚠️ Suboptimal ({int(optimality * 100)}%)',
                    'variant': 'warning',
                    'tooltip': 'Consider rescheduling for better timing'
                }]
            
            # Add participant insights if available
            participant_analysis = analysis.get('participant_analysis', {})
            if participant_analysis.get('conflicts', 0) > 0:
                original_component['component']['Card']['badges'].append({
                    'label': f'🚫 {participant_analysis["conflicts"]} conflicts',
                    'variant': 'danger',
                    'tooltip': 'Participants have scheduling conflicts'
                })
                
        return original_component
    
    def get_intelligence_context(self) -> Dict[str, Any]:
        """Get intelligence context for A2UI state machine"""
        return {
            'intelligence_available': True,
            'last_analysis_time': datetime.now().isoformat(),
            'insights': self.intelligence.get_daily_insights()
        }