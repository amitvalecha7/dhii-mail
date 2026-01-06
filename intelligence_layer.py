"""
Intelligence Layer for dhii Mail
Provides advanced AI analysis and real-time event processing
"""

import asyncio
import logging
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable

# Import existing infrastructure
from a2ui_integration.core.shared_services import EventBus, EventType, Event
from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator

logger = logging.getLogger(__name__)


class IntelligenceLayer:
    """Core intelligence service for real-time AI analysis"""
    
    def __init__(self, event_bus: EventBus, db_path: str):
        self.event_bus = event_bus
        self.db_path = db_path
        self.ai_engine = A2UIOrchestrator()
        self.analysis_workers = {}
        self.subscriptions = {}
        self.running = False
        
    async def start(self):
        """Start intelligence layer and subscribe to events"""
        if self.running:
            logger.warning("Intelligence layer already running")
            return
            
        logger.info("Starting Intelligence Layer")
        
        # Initialize database schema
        await self._initialize_database()
        
        # Setup event subscriptions
        await self._setup_event_subscriptions()
        
        # Initialize analysis workers
        await self._initialize_analysis_workers()
        
        self.running = True
        logger.info("Intelligence Layer started successfully")
        
    async def stop(self):
        """Stop intelligence layer and cleanup"""
        if not self.running:
            return
            
        logger.info("Stopping Intelligence Layer")
        
        # Unsubscribe from events
        for event_type, subscription_id in self.subscriptions.items():
            await self.event_bus.unsubscribe(event_type, subscription_id)
        
        # Stop analysis workers
        for worker_name, worker in self.analysis_workers.items():
            if hasattr(worker, 'stop') and callable(getattr(worker, 'stop')):
                await worker.stop()
        
        self.running = False
        logger.info("Intelligence Layer stopped")
        
    async def _initialize_database(self):
        """Initialize intelligence database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create AI insights tables
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_email_insights (
                    email_id TEXT PRIMARY KEY,
                    sentiment_score REAL,
                    urgency_level TEXT,
                    key_entities TEXT,
                    analysis_timestamp DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_behavior_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    action_type TEXT, 
                    action_context TEXT,
                    timestamp DATETIME,
                    frequency_score REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meeting_intelligence (
                    meeting_id TEXT PRIMARY KEY,
                    optimality_score REAL,
                    participant_analysis TEXT,
                    time_slot_quality TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("Intelligence database tables initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize intelligence database: {e}")
            raise
            
    async def _setup_event_subscriptions(self):
        """Subscribe to relevant system events for real-time analysis"""
        try:
            self.subscriptions = {
                EventType.EMAIL_RECEIVED: await self.event_bus.subscribe(
                    EventType.EMAIL_RECEIVED, self._analyze_email_received
                ),
                EventType.EMAIL_SENT: await self.event_bus.subscribe(
                    EventType.EMAIL_SENT, self._analyze_email_sent
                ),
                EventType.MEETING_CREATED: await self.event_bus.subscribe(
                    EventType.MEETING_CREATED, self._analyze_meeting_created
                ),
                EventType.MEETING_UPDATED: await self.event_bus.subscribe(
                    EventType.MEETING_UPDATED, self._analyze_meeting_updated
                ),
                EventType.CAPABILITY_EXECUTED: await self.event_bus.subscribe(
                    EventType.CAPABILITY_EXECUTED, self._analyze_user_behavior
                )
            }
            logger.info("Event subscriptions established")
            
        except Exception as e:
            logger.error(f"Failed to setup event subscriptions: {e}")
            raise
            
    async def _initialize_analysis_workers(self):
        """Initialize specialized analysis workers"""
        self.analysis_workers = {
            'email_analyzer': EmailAnalyzer(self.db_path),
            'calendar_analyzer': CalendarAnalyzer(self.db_path),
            'behavior_analyzer': BehaviorAnalyzer(self.db_path)
        }
        
        # Start all workers
        for worker_name, worker in self.analysis_workers.items():
            if hasattr(worker, 'start') and callable(getattr(worker, 'start')):
                await worker.start()
        
        logger.info("Analysis workers initialized")
        
    async def _analyze_email_received(self, event: Event):
        """Analyze incoming email for sentiment and urgency"""
        try:
            email_data = event.data.get('email', {})
            email_id = email_data.get('id', 'unknown')
            
            logger.info(f"Analyzing received email: {email_id}")
            
            # Use AI engine for analysis
            content = email_data.get('body', '') or email_data.get('snippet', '')
            
            # Store analysis results
            await self.analysis_workers['email_analyzer'].analyze_email(
                email_id, content, 'received'
            )
            
        except Exception as e:
            logger.error(f"Email analysis failed: {e}")
            
    async def _analyze_email_sent(self, event: Event):
        """Analyze sent email for effectiveness"""
        try:
            email_data = event.data.get('email', {})
            email_id = email_data.get('id', 'unknown')
            
            logger.info(f"Analyzing sent email: {email_id}")
            
            content = email_data.get('body', '') or email_data.get('snippet', '')
            
            await self.analysis_workers['email_analyzer'].analyze_email(
                email_id, content, 'sent'
            )
            
        except Exception as e:
            logger.error(f"Sent email analysis failed: {e}")
            
    async def _analyze_meeting_created(self, event: Event):
        """Analyze newly created meeting"""
        try:
            meeting_data = event.data.get('meeting', {})
            meeting_id = meeting_data.get('id', 'unknown')
            
            logger.info(f"Analyzing created meeting: {meeting_id}")
            
            await self.analysis_workers['calendar_analyzer'].analyze_meeting(
                meeting_id, meeting_data
            )
            
        except Exception as e:
            logger.error(f"Meeting analysis failed: {e}")
            
    async def _analyze_user_behavior(self, event: Event):
        """Analyze user behavior patterns"""
        try:
            capability_data = event.data.get('capability', {})
            user_id = event.data.get('user_id', 'unknown')
            
            logger.info(f"Analyzing user behavior: {user_id}")
            
            await self.analysis_workers['behavior_analyzer'].track_behavior(
                user_id, capability_data, event.timestamp
            )
            
        except Exception as e:
            logger.error(f"Behavior analysis failed: {e}")


class EmailAnalyzer:
    """Specialized email content analysis"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def start(self):
        """Initialize email analyzer"""
        logger.info("Email Analyzer started")
        
    async def analyze_email(self, email_id: str, content: str, direction: str):
        """Analyze email content and store insights"""
        try:
            # Simple sentiment analysis (placeholder for LLM integration)
            sentiment_score = self._analyze_sentiment(content)
            urgency_level = self._detect_urgency(content)
            key_entities = self._extract_entities(content)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO ai_email_insights 
                (email_id, sentiment_score, urgency_level, key_entities, analysis_timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (email_id, sentiment_score, urgency_level, json.dumps(key_entities), datetime.now()))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Email analysis completed for {email_id}")
            
        except Exception as e:
            logger.error(f"Email analysis failed: {e}")
            
    def _analyze_sentiment(self, content: str) -> float:
        """Advanced sentiment analysis with LLM integration"""
        # Try to use OpenRouter LLM if available
        if self.ai_engine.use_openrouter:
            try:
                return self._analyze_sentiment_with_llm(content)
            except Exception as e:
                logger.warning(f"LLM sentiment analysis failed, falling back to basic: {e}")
        
        # Fallback to basic sentiment analysis
        return self._basic_sentiment_analysis(content)
    
    def _analyze_sentiment_with_llm(self, content: str) -> float:
        """Use OpenRouter LLM for advanced sentiment analysis"""
        import aiohttp
        import asyncio
        
        # Truncate content to avoid token limits
        truncated_content = content[:1000]
        
        prompt = f"""Analyze the sentiment of this email content and provide a score between 0.0 (very negative) and 1.0 (very positive). 
        Return only the numerical score, no explanation.
        
        Email content: {truncated_content}
        
        Sentiment score:"""
        
        # For now, use basic analysis as we'd need async context
        # In production, this would make actual API calls to OpenRouter
        return self._basic_sentiment_analysis(content)
    
    def _basic_sentiment_analysis(self, content: str) -> float:
        """Basic sentiment analysis as fallback"""
        positive_words = ['great', 'excellent', 'thanks', 'appreciate', 'wonderful', 'awesome', 'perfect', 'good', 'nice', 'happy']
        negative_words = ['problem', 'issue', 'sorry', 'concern', 'urgent', 'bad', 'terrible', 'awful', 'disappoint', 'fail']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        total = positive_count + negative_count
        if total == 0:
            return 0.5  # Neutral
            
        # Weighted score with more emphasis on negative sentiment
        score = (positive_count * 0.7 + (total - negative_count) * 0.3) / total
        return max(0.0, min(1.0, score))
        
    def _detect_urgency(self, content: str) -> str:
        """Detect email urgency level"""
        urgent_phrases = ['asap', 'urgent', 'immediately', 'right away', 'emergency']
        content_lower = content.lower()
        
        if any(phrase in content_lower for phrase in urgent_phrases):
            return 'high'
        elif 'please' in content_lower or 'request' in content_lower:
            return 'medium'
        else:
            return 'low'
            
    def _extract_entities(self, content: str) -> List[str]:
        """Extract key entities from email content with advanced detection"""
        # Try to use OpenRouter LLM if available
        if self.ai_engine.use_openrouter:
            try:
                return self._extract_entities_with_llm(content)
            except Exception as e:
                logger.warning(f"LLM entity extraction failed, falling back to basic: {e}")
        
        # Fallback to basic entity extraction
        return self._basic_entity_extraction(content)
    
    def _extract_entities_with_llm(self, content: str) -> List[str]:
        """Use OpenRouter LLM for advanced entity extraction"""
        # Placeholder for LLM entity extraction
        # In production, this would call OpenRouter API to extract
        # people, organizations, dates, locations, etc.
        return self._basic_entity_extraction(content)
    
    def _basic_entity_extraction(self, content: str) -> List[str]:
        """Basic entity extraction as fallback"""
        entities = []
        
        # Extract potential names (words starting with capital letters)
        words = content.split()
        for i, word in enumerate(words):
            if len(word) > 2 and word[0].isupper() and not word.isupper():
                # Check if it might be a name (not at start of sentence)
                if i > 0 and words[i-1][-1] not in ['.', '!', '?']:
                    entities.append(word)
        
        # Extract email addresses
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, content)
        entities.extend(emails)
        
        # Extract potential dates (simple pattern)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
        dates = re.findall(date_pattern, content, re.IGNORECASE)
        entities.extend(dates)
        
        return list(set(entities))[:8]  # Return top 8 unique entities


class CalendarAnalyzer:
    """Specialized calendar event analysis"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def start(self):
        """Initialize calendar analyzer"""
        logger.info("Calendar Analyzer started")
        
    async def analyze_meeting(self, meeting_id: str, meeting_data: Dict):
        """Analyze meeting and store insights"""
        try:
            # Simple meeting analysis (placeholder for advanced AI)
            optimality_score = self._calculate_optimality(meeting_data)
            participant_analysis = self._analyze_participants(meeting_data)
            time_slot_quality = self._assess_time_slot(meeting_data)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO meeting_intelligence 
                (meeting_id, optimality_score, participant_analysis, time_slot_quality)
                VALUES (?, ?, ?, ?)
            """, (meeting_id, optimality_score, json.dumps(participant_analysis), time_slot_quality))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Meeting analysis completed for {meeting_id}")
            
        except Exception as e:
            logger.error(f"Meeting analysis failed: {e}")
            
    def _calculate_optimality(self, meeting_data: Dict) -> float:
        """Calculate advanced meeting optimality score"""
        # Try to use AI engine for advanced optimization
        if self.ai_engine.use_openrouter:
            try:
                return self._calculate_optimality_with_ai(meeting_data)
            except Exception as e:
                logger.warning(f"AI meeting optimization failed, falling back to basic: {e}")
        
        # Fallback to basic optimality calculation
        return self._basic_optimality_calculation(meeting_data)
    
    def _calculate_optimality_with_ai(self, meeting_data: Dict) -> float:
        """Use AI for advanced meeting optimization"""
        # Placeholder for AI-powered meeting optimization
        # In production, this would analyze meeting context, participant availability,
        # historical meeting success rates, and other factors
        return self._basic_optimality_calculation(meeting_data)
    
    def _basic_optimality_calculation(self, meeting_data: Dict) -> float:
        """Basic meeting optimality calculation as fallback"""
        duration = meeting_data.get('duration', 60)
        participant_count = len(meeting_data.get('attendees', []))
        
        # Multi-factor optimality scoring
        duration_score = max(0.0, min(1.0, 1.0 - (duration / 120.0)))  # 0-120 minutes
        participant_score = max(0.0, min(1.0, 1.0 - (participant_count / 15.0)))  # 0-15 participants
        
        # Time of day scoring (prefer 9-11am and 2-4pm)
        time_score = 0.5
        start_time = meeting_data.get('start', {}).get('dateTime')
        if start_time:
            try:
                dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                hour = dt.hour
                if 9 <= hour <= 11:
                    time_score = 0.9
                elif 14 <= hour <= 16:
                    time_score = 0.8
                elif hour < 9 or hour > 17:
                    time_score = 0.3
            except (ValueError, AttributeError):
                pass
        
        # Weighted average of factors
        optimality_score = (duration_score * 0.4 + participant_score * 0.3 + time_score * 0.3)
        return max(0.1, min(0.95, optimality_score))  # Keep within reasonable bounds
            
    def _analyze_participants(self, meeting_data: Dict) -> Dict:
        """Analyze meeting participants"""
        attendees = meeting_data.get('attendees', [])
        return {
            'count': len(attendees),
            'external_count': sum(1 for att in attendees if att.get('external', False)),
            'internal_count': sum(1 for att in attendees if not att.get('external', True))
        }
        
    def _assess_time_slot(self, meeting_data: Dict) -> str:
        """Assess meeting time slot quality"""
        start_time = meeting_data.get('start', {}).get('dateTime')
        if not start_time:
            return 'unknown'
            
        # Parse time and check if it's during typical working hours
        try:
            dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            hour = dt.hour
            
            if 9 <= hour <= 11:
                return 'optimal_morning'
            elif 14 <= hour <= 16:
                return 'optimal_afternoon'
            elif hour < 9 or hour > 17:
                return 'off_hours'
            else:
                return 'standard_hours'
                
        except (ValueError, AttributeError):
            return 'unknown'


class BehaviorAnalyzer:
    """Specialized user behavior analysis"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    async def start(self):
        """Initialize behavior analyzer"""
        logger.info("Behavior Analyzer started")
        
    async def track_behavior(self, user_id: str, capability_data: Dict, timestamp: datetime):
        """Track and analyze user behavior patterns"""
        try:
            action_type = capability_data.get('id', 'unknown')
            action_context = json.dumps(capability_data.get('input', {}))
            
            # Simple frequency scoring (placeholder for advanced analysis)
            frequency_score = self._calculate_frequency_score(user_id, action_type)
            
            # Store in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_behavior_patterns 
                (user_id, action_type, action_context, timestamp, frequency_score)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, action_type, action_context, timestamp, frequency_score))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Behavior tracked for user {user_id}: {action_type}")
            
        except Exception as e:
            logger.error(f"Behavior tracking failed: {e}")
            
    def _calculate_frequency_score(self, user_id: str, action_type: str) -> float:
        """Calculate frequency score for user action"""
        # Placeholder implementation - would query historical data
        # For now, return a default score
        return 0.5


# Global instance for easy access
intelligence_layer: Optional[IntelligenceLayer] = None


def get_intelligence_layer() -> IntelligenceLayer:
    """Get or create global intelligence layer instance"""
    global intelligence_layer
    if intelligence_layer is None:
        from a2ui_integration.core.shared_services import event_bus
        intelligence_layer = IntelligenceLayer(event_bus, 'dhii_mail.db')
    return intelligence_layer


async def initialize_intelligence_layer():
    """Initialize the global intelligence layer"""
    global intelligence_layer
    intelligence_layer = get_intelligence_layer()
    await intelligence_layer.start()
    return intelligence_layer