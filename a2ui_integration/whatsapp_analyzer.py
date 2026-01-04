"""
WhatsApp Chat Analyzer for A2UI Integration
Analyzes WhatsApp chat exports for insights, sentiment, and patterns
"""

import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from collections import Counter, defaultdict
import nltk
from textblob import TextBlob

logger = logging.getLogger(__name__)

class WhatsAppAnalyzer:
    """WhatsApp chat analysis engine"""
    
    def __init__(self):
        self.message_pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}(?::\d{2})?(?: [AP]M)?) - ([^:]+): (.*)$')
        self.date_formats = [
            '%m/%d/%y, %I:%M %p',  # 1/15/24, 2:30 PM
            '%m/%d/%y, %H:%M',     # 1/15/24, 14:30
            '%d/%m/%y, %I:%M %p',  # 15/1/24, 2:30 PM
            '%d/%m/%y, %H:%M',     # 15/1/24, 14:30
            '%m/%d/%Y, %I:%M %p',  # 1/15/2024, 2:30 PM
            '%m/%d/%Y, %H:%M',     # 1/15/2024, 14:30
            '%d/%m/%Y, %I:%M %p',  # 15/1/2024, 2:30 PM
            '%d/%m/%Y, %H:%M',     # 15/1/2024, 14:30
        ]
        
        # Common words to filter out for analysis
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'shall', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'my', 'your', 'his', 'her', 'its', 'our', 'their', 'am', 'so', 'very', 'just', 'now', 'then',
            'than', 'only', 'also', 'back', 'after', 'use', 'used', 'using', 'work', 'worked', 'working',
            'get', 'got', 'getting', 'go', 'went', 'going', 'see', 'saw', 'seen', 'seeing', 'know', 'knew',
            'known', 'knowing', 'think', 'thought', 'thinking', 'say', 'said', 'saying', 'tell', 'told',
            'telling', 'ask', 'asked', 'asking', 'come', 'came', 'coming', 'give', 'gave', 'given', 'giving'
        }
    
    def parse_chat_export(self, content: str, format_type: str = "txt") -> List[Dict[str, Any]]:
        """Parse WhatsApp chat export content into structured messages"""
        if format_type == "json":
            return self._parse_json_format(content)
        else:
            return self._parse_txt_format(content)
    
    def _parse_txt_format(self, content: str) -> List[Dict[str, Any]]:
        """Parse WhatsApp chat file content in text format"""
        messages = []
        lines = content.strip().split('\n')
        
        current_message = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Try to match message pattern
            match = self.message_pattern.match(line)
            if match:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                
                # Parse new message
                timestamp_str, sender, content_text = match.groups()
                
                # Parse timestamp
                timestamp = None
                for date_format in self.date_formats:
                    try:
                        timestamp = datetime.strptime(timestamp_str, date_format)
                        break
                    except ValueError:
                        continue
                
                if timestamp is None:
                    logger.warning(f"Could not parse timestamp: {timestamp_str}")
                    continue
                
                current_message = {
                    'timestamp': timestamp,
                    'sender': sender.strip(),
                    'content': content_text.strip(),
                    'type': 'text'
                }
                
                # Detect media types
                if '<Media omitted>' in content_text:
                    current_message['type'] = 'media'
                    current_message['media_type'] = 'image'  # Default to image
                elif content_text.startswith('http'):
                    current_message['type'] = 'link'
                elif content_text.startswith('📎'):
                    current_message['type'] = 'document'
                    
            else:
                # Continuation of previous message
                if current_message:
                    current_message['content'] += ' ' + line
        
        # Add the last message
        if current_message:
            messages.append(current_message)
        
        return messages
    
    def _parse_json_format(self, content: str) -> List[Dict[str, Any]]:
        """Parse WhatsApp chat export in JSON format"""
        try:
            data = json.loads(content)
            messages = []
            
            # Handle different JSON structures
            if isinstance(data, dict):
                # Single chat export
                if 'messages' in data:
                    message_list = data['messages']
                else:
                    message_list = [data]
            elif isinstance(data, list):
                # Array of messages
                message_list = data
            else:
                logger.warning("Unsupported JSON format")
                return []
            
            for msg in message_list:
                try:
                    # Parse timestamp
                    timestamp_str = msg.get('timestamp') or msg.get('date') or msg.get('time')
                    if not timestamp_str:
                        continue
                    
                    timestamp = None
                    if isinstance(timestamp_str, (int, float)):
                        # Unix timestamp
                        timestamp = datetime.fromtimestamp(timestamp_str)
                    else:
                        # String timestamp
                        for fmt in self.date_formats:
                            try:
                                timestamp = datetime.strptime(timestamp_str, fmt)
                                break
                            except ValueError:
                                continue
                    
                    if not timestamp:
                        continue
                    
                    message = {
                        'timestamp': timestamp,
                        'sender': msg.get('sender', msg.get('from', 'Unknown')),
                        'content': msg.get('message', msg.get('text', msg.get('content', ''))),
                        'type': msg.get('type', 'text')
                    }
                    
                    messages.append(message)
                    
                except Exception as e:
                    logger.warning(f"Error parsing message: {e}")
                    continue
            
            return messages
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Error processing JSON format: {e}")
            return []
    
    def analyze_chat(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze WhatsApp chat messages and return comprehensive analysis"""
        if not messages:
            return {}
        
        # Perform all analysis
        overview = {
            "total_messages": len(messages),
            "total_participants": len(set(msg['sender'] for msg in messages)),
            "date_range": f"{min(msg['timestamp'] for msg in messages).strftime('%Y-%m-%d')} to {max(msg['timestamp'] for msg in messages).strftime('%Y-%m-%d')}",
            "most_active_user": max(set(msg['sender'] for msg in messages), key=lambda x: sum(1 for msg in messages if msg['sender'] == x))
        }
        
        participant_stats = self.analyze_participants(messages)
        activity_patterns = self.analyze_activity_patterns(messages)
        conversation_insights = self.analyze_conversation_insights(messages)
        media_stats = self.analyze_media_statistics(messages)
        
        # Sentiment analysis
        all_text = ' '.join([msg['content'] for msg in messages if msg['type'] == 'text'])
        overall_sentiment = self.analyze_sentiment(all_text)
        
        sentiment_scores = [self.analyze_sentiment(msg['content']) for msg in messages if msg['type'] == 'text']
        positive = sum(1 for score in sentiment_scores if score > 0.1)
        negative = sum(1 for score in sentiment_scores if score < -0.1)
        neutral = len(sentiment_scores) - positive - negative
        
        sentiment_analysis = {
            "overall_sentiment": "Positive" if overall_sentiment > 0.1 else "Negative" if overall_sentiment < -0.1 else "Neutral",
            "positive_ratio": positive / len(sentiment_scores) if sentiment_scores else 0,
            "negative_ratio": negative / len(sentiment_scores) if sentiment_scores else 0,
            "neutral_ratio": neutral / len(sentiment_scores) if sentiment_scores else 0
        }
        
        # Word analysis
        word_analysis = {
            "most_frequent_words": self.extract_keywords(all_text, top_n=15),
            "vocabulary_richness": len(set(re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower()))) / max(1, len(all_text.split()))
        }
        
        # Key insights
        key_insights = [
            f"Chat contains {len(messages)} messages from {len(set(msg['sender'] for msg in messages))} participants",
            f"Most active participant: {overview['most_active_user']}",
            f"Chat has {sentiment_analysis['overall_sentiment'].lower()} sentiment",
            f"Peak activity occurs around {activity_patterns.get('peak_activity_hour', 'unknown')}:00",
            f"Common topics: {', '.join([word for word, count in conversation_insights.get('top_conversation_topics', [])[:5]])}"
        ]
        
        return {
            "overview": overview,
            "participant_stats": participant_stats,
            "activity_patterns": {
                "peak_hours": f"{activity_patterns.get('peak_activity_hour', 0)}:00",
                "most_active_day": activity_patterns.get('most_active_day_name', 'Unknown')
            },
            "sentiment_analysis": sentiment_analysis,
            "conversation_insights": {"key_insights": key_insights},
            "word_analysis": word_analysis,
            "media_statistics": media_stats
        }

    def analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment of text (returns score between -1 and 1)"""
        try:
            blob = TextBlob(text)
            return blob.sentiment.polarity
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return 0.0
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[Tuple[str, int]]:
        """Extract most frequent keywords from text"""
        # Clean and tokenize
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter out stop words
        filtered_words = [word for word in words if word not in self.stop_words]
        
        # Count frequency
        word_counts = Counter(filtered_words)
        
        return word_counts.most_common(top_n)
    
    def analyze_activity_patterns(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze activity patterns in messages"""
        if not messages:
            return {}
        
        # Hourly distribution
        hourly_counts = defaultdict(int)
        daily_counts = defaultdict(int)
        
        for message in messages:
            hour = message['timestamp'].hour
            day_of_week = message['timestamp'].weekday()  # Monday=0
            
            hourly_counts[hour] += 1
            daily_counts[day_of_week] += 1
        
        # Find peak activity
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else 0
        most_active_day = max(daily_counts.items(), key=lambda x: x[1])[0] if daily_counts else 0
        
        # Day names
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        return {
            'peak_activity_hour': peak_hour,
            'most_active_day': most_active_day,
            'most_active_day_name': day_names[most_active_day] if most_active_day < 7 else 'Unknown',
            'hourly_distribution': dict(hourly_counts),
            'daily_distribution': dict(daily_counts)
        }
    
    def analyze_participants(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze participant statistics"""
        if not messages:
            return {}
        
        participant_stats = defaultdict(lambda: {
            'message_count': 0,
            'word_count': 0,
            'avg_message_length': 0,
            'sentiment_scores': [],
            'media_count': 0,
            'link_count': 0
        })
        
        for message in messages:
            sender = message['sender']
            content = message['content']
            
            participant_stats[sender]['message_count'] += 1
            participant_stats[sender]['word_count'] += len(content.split())
            
            # Analyze sentiment
            sentiment = self.analyze_sentiment(content)
            participant_stats[sender]['sentiment_scores'].append(sentiment)
            
            # Count media types
            if message['type'] == 'media':
                participant_stats[sender]['media_count'] += 1
            elif message['type'] == 'link':
                participant_stats[sender]['link_count'] += 1
        
        # Calculate averages
        for sender, stats in participant_stats.items():
            if stats['message_count'] > 0:
                stats['avg_message_length'] = stats['word_count'] / stats['message_count']
                if stats['sentiment_scores']:
                    stats['sentiment_score'] = sum(stats['sentiment_scores']) / len(stats['sentiment_scores'])
                else:
                    stats['sentiment_score'] = 0.0
                # Remove the list to clean up output
                del stats['sentiment_scores']
        
        return dict(participant_stats)
    
    def analyze_conversation_insights(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation patterns and insights"""
        if not messages:
            return {}
        
        # Combine all text for analysis
        all_text = ' '.join([msg['content'] for msg in messages if msg['type'] == 'text'])
        
        # Count questions
        question_count = all_text.count('?')
        total_messages = len([msg for msg in messages if msg['type'] == 'text'])
        question_ratio = question_count / total_messages if total_messages > 0 else 0
        
        # Extract top conversation topics
        keywords = self.extract_keywords(all_text, top_n=15)
        
        # Analyze response times (simplified - would need more sophisticated approach)
        response_times = []
        for i in range(1, len(messages)):
            if messages[i]['sender'] != messages[i-1]['sender']:
                time_diff = messages[i]['timestamp'] - messages[i-1]['timestamp']
                if time_diff < timedelta(hours=1):  # Only consider quick responses
                    response_times.append(time_diff.total_seconds() / 60)  # Convert to minutes
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'question_count': question_count,
            'question_ratio': question_ratio,
            'avg_response_time_minutes': avg_response_time,
            'top_conversation_topics': keywords,
            'total_text_messages': total_messages
        }
    
    def analyze_media_statistics(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze media usage statistics"""
        if not messages:
            return {}
        
        media_counts = Counter()
        
        for message in messages:
            media_counts[message['type']] += 1
        
        total_messages = len(messages)
        text_messages = media_counts.get('text', 0)
        
        return {
            'media_distribution': dict(media_counts),
            'text_to_media_ratio': text_messages / total_messages if total_messages > 0 else 0,
            'total_messages': total_messages
        }
    
    def parse_chat_file(self, content: str) -> List[Dict[str, Any]]:
        """Legacy method for backward compatibility - delegates to parse_chat_export"""
        return self.parse_chat_export(content, "txt")
    
    def process_chat_file(self, content: str, filename: str) -> Dict[str, Any]:
        """Process WhatsApp chat file and return analysis results"""
        try:
            # Parse messages
            messages = self.parse_chat_file(content)
            
            if not messages:
                return {
                    "status": "failed",
                    "error": "No valid messages found in chat file"
                }
            
            # Perform analysis
            overview = {
                "total_messages": len(messages),
                "total_participants": len(set(msg['sender'] for msg in messages)),
                "date_range": [
                    min(msg['timestamp'] for msg in messages).strftime('%Y-%m-%d'),
                    max(msg['timestamp'] for msg in messages).strftime('%Y-%m-%d')
                ],
                "avg_messages_per_day": len(messages) / max(1, (max(msg['timestamp'] for msg in messages) - min(msg['timestamp'] for msg in messages)).days),
                "most_active_user": max(set(msg['sender'] for msg in messages), key=lambda x: sum(1 for msg in messages if msg['sender'] == x)),
                "participants": list(set(msg['sender'] for msg in messages))
            }
            
            participant_stats = self.analyze_participants(messages)
            activity_patterns = self.analyze_activity_patterns(messages)
            conversation_insights = self.analyze_conversation_insights(messages)
            media_stats = self.analyze_media_statistics(messages)
            
            # Overall sentiment analysis
            all_text = ' '.join([msg['content'] for msg in messages if msg['type'] == 'text'])
            overall_sentiment = self.analyze_sentiment(all_text)
            
            # Sentiment distribution
            sentiment_scores = [self.analyze_sentiment(msg['content']) for msg in messages if msg['type'] == 'text']
            positive = sum(1 for score in sentiment_scores if score > 0.1)
            negative = sum(1 for score in sentiment_scores if score < -0.1)
            neutral = len(sentiment_scores) - positive - negative
            
            sentiment_analysis = {
                "overall_sentiment": overall_sentiment,
                "sentiment_distribution": {
                    "positive": positive,
                    "neutral": neutral,
                    "negative": negative
                }
            }
            
            # Word analysis
            word_analysis = {
                "total_unique_words": len(set(re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower()))),
                "most_frequent_words": self.extract_keywords(all_text, top_n=20),
                "vocabulary_richness": len(set(re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower()))) / max(1, len(all_text.split()))
            }
            
            analysis = {
                "overview": overview,
                "participant_stats": participant_stats,
                "activity_patterns": activity_patterns,
                "sentiment_analysis": sentiment_analysis,
                "conversation_insights": conversation_insights,
                "word_analysis": word_analysis,
                "media_statistics": media_stats
            }
            
            summary = {
                "messages_analyzed": len(messages),
                "participants": list(set(msg['sender'] for msg in messages)),
                "date_range": overview["date_range"],
                "key_insights": [
                    f"Chat contains {len(messages)} messages from {len(set(msg['sender'] for msg in messages))} participants",
                    f"Most active participant: {overview['most_active_user']}",
                    f"Chat has {'predominantly positive' if overall_sentiment > 0.1 else 'predominantly negative' if overall_sentiment < -0.1 else 'neutral'} sentiment",
                    f"Peak activity occurs around {activity_patterns.get('peak_activity_hour', 'unknown')}:{activity_patterns.get('peak_activity_minute', '00') or '00'}",
                    f"Common topics: {', '.join([word for word, count in conversation_insights.get('top_conversation_topics', [])[:5]])}"
                ]
            }
            
            return {
                "status": "success",
                "analysis": analysis,
                "summary": summary,
                "filename": filename
            }
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp chat file: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def get_sample_analysis(self) -> Dict[str, Any]:
        """Return sample analysis data for demonstration"""
        return {
            "status": "success",
            "analysis": {
                "overview": {
                    "total_messages": 1247,
                    "total_participants": 4,
                    "date_range": ["2024-01-15", "2024-03-20"],
                    "avg_messages_per_day": 18.3,
                    "most_active_user": "Alice",
                    "participants": ["Alice", "Bob", "Charlie", "Diana"]
                },
                "participant_stats": {
                    "Alice": {
                        "message_count": 456,
                        "word_count": 2847,
                        "avg_message_length": 45.2,
                        "sentiment_score": 0.72,
                        "media_count": 12,
                        "link_count": 8
                    },
                    "Bob": {
                        "message_count": 389,
                        "word_count": 2156,
                        "avg_message_length": 38.9,
                        "sentiment_score": 0.65,
                        "media_count": 8,
                        "link_count": 15
                    },
                    "Charlie": {
                        "message_count": 267,
                        "word_count": 1456,
                        "avg_message_length": 42.1,
                        "sentiment_score": 0.58,
                        "media_count": 6,
                        "link_count": 4
                    },
                    "Diana": {
                        "message_count": 135,
                        "word_count": 789,
                        "avg_message_length": 35.8,
                        "sentiment_score": 0.71,
                        "media_count": 8,
                        "link_count": 7
                    }
                },
                "activity_patterns": {
                    "peak_activity_hour": 14,
                    "most_active_day": 2,
                    "most_active_day_name": "Tuesday",
                    "hourly_distribution": {
                        "9": 89, "10": 124, "11": 98, "12": 156, "13": 134, "14": 189, "15": 167, "16": 145
                    },
                    "daily_distribution": {
                        "0": 145, "1": 189, "2": 167, "3": 134, "4": 98, "5": 89, "6": 124
                    }
                },
                "sentiment_analysis": {
                    "overall_sentiment": 0.68,
                    "sentiment_distribution": {
                        "positive": 743,
                        "neutral": 389,
                        "negative": 115
                    }
                },
                "conversation_insights": {
                    "question_count": 234,
                    "question_ratio": 0.188,
                    "avg_response_time_minutes": 12.5,
                    "top_conversation_topics": [
                        ("project", 89), ("meeting", 67), ("deadline", 45), ("team", 38), ("client", 34),
                        ("presentation", 28), ("report", 25), ("review", 22), ("feedback", 20), ("update", 18)
                    ],
                    "total_text_messages": 1247
                },
                "word_analysis": {
                    "total_unique_words": 1847,
                    "most_frequent_words": [
                        ("project", 89), ("time", 76), ("work", 68), ("team", 54), ("meeting", 45),
                        ("good", 42), ("need", 38), ("client", 34), ("deadline", 32), ("help", 28),
                        ("presentation", 25), ("report", 22), ("review", 20), ("feedback", 18), ("update", 16)
                    ],
                    "vocabulary_richness": 0.65
                },
                "media_statistics": {
                    "media_distribution": {
                        "text": 1189, "image": 34, "video": 12, "audio": 8, "document": 4
                    },
                    "text_to_media_ratio": 0.954,
                    "total_messages": 1247
                }
            },
            "summary": {
                "messages_analyzed": 1247,
                "participants": ["Alice", "Bob", "Charlie", "Diana"],
                "date_range": ["2024-01-15", "2024-03-20"],
                "key_insights": [
                    "Chat contains 1247 messages from 4 participants",
                    "Most active participant: Alice",
                    "Chat has predominantly positive sentiment",
                    "Peak activity occurs around 14:00",
                    "Common topics: project, meeting, deadline, team, client"
                ]
            },
            "filename": "sample_chat.txt"
        }

# Global instance
whatsapp_analyzer = WhatsAppAnalyzer()