"""
Skill Store for A2UI - Plugin Management Interface
Provides UI components and API endpoints for plugin discovery, installation, and management
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import json

# Import plugin infrastructure
from a2ui_integration.plugin_manager import PluginManager, PluginConfig, PluginInfo, PluginStatus, PluginType
from a2ui_integration.whatsapp_analyzer import whatsapp_analyzer

logger = logging.getLogger(__name__)

# Create Skill Store router
skill_store_router = APIRouter(prefix="/api/skill-store", tags=["skill-store"])

# Pydantic models for API
class PluginResponse(BaseModel):
    """Plugin response model"""
    plugin_id: str
    name: str
    description: str
    plugin_type: str
    version: str
    author: str
    status: str
    requires_auth: bool
    capabilities: List[str]
    last_updated: datetime
    error_message: Optional[str] = None

class PluginInstallRequest(BaseModel):
    """Plugin installation request"""
    plugin_id: str
    enable_after_install: bool = True

class ChatAnalysisRequest(BaseModel):
    """Chat analysis request"""
    chat_content: str
    filename: str = "chat.txt"

class ChatAnalysisResponse(BaseModel):
    """Chat analysis response"""
    status: str
    analysis: Optional[Dict[str, Any]] = None
    summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Initialize plugin manager (will be set up in main app)
plugin_manager = None

def initialize_skill_store(pm: PluginManager):
    """Initialize skill store with plugin manager"""
    global plugin_manager
    plugin_manager = pm
    logger.info("Skill Store initialized with plugin manager")
    
    # Register WhatsApp analyzer plugin
    register_whatsapp_plugin()

def register_whatsapp_plugin():
    """Register WhatsApp analyzer plugin"""
    if not plugin_manager:
        logger.warning("Plugin manager not initialized, skipping WhatsApp plugin registration")
        return
    
    try:
        whatsapp_config = PluginConfig(
            plugin_id="whatsapp_analyzer",
            name="WhatsApp Chat Analyzer",
            description="Analyze WhatsApp chat exports for insights, sentiment, and communication patterns",
            plugin_type=PluginType.ANALYTICS,
            version="1.0.0",
            author="A2UI Team",
            requires_auth=False,
            capabilities=[
                "Chat export parsing (txt/json formats)",
                "Message analysis and statistics",
                "Participant activity patterns",
                "Sentiment analysis",
                "Media usage statistics",
                "Conversation insights",
                "Privacy-aware processing"
            ],
            settings={
                "max_file_size_mb": 10,
                "supported_formats": ["txt", "json"],
                "privacy_mode": True,
                "enable_sentiment_analysis": True
            },
            icon="💬",
            documentation_url="https://docs.a2ui.com/plugins/whatsapp-analyzer",
            support_url="https://support.a2ui.com/plugins/whatsapp-analyzer",
            privacy_policy_url="https://a2ui.com/privacy"
        )
        
        success = plugin_manager.register_plugin(whatsapp_config)
        if success:
            logger.info("WhatsApp analyzer plugin registered successfully")
            # Enable it by default
            plugin_manager.enable_plugin("whatsapp_analyzer")
        else:
            logger.error("Failed to register WhatsApp analyzer plugin")
            
    except Exception as e:
        logger.error(f"Error registering WhatsApp plugin: {e}")

@skill_store_router.get("/plugins", response_model=List[PluginResponse])
async def list_plugins(plugin_type: Optional[str] = None, status: Optional[str] = None):
    """List available plugins"""
    if not plugin_manager:
        raise HTTPException(status_code=503, detail="Skill Store not initialized")
    
    plugins = plugin_manager.get_all_plugins()
    
    # Filter by type if specified
    if plugin_type:
        plugins = [p for p in plugins if p.config.plugin_type.value == plugin_type]
    
    # Filter by status if specified
    if status:
        plugins = [p for p in plugins if p.status.value == status]
    
    return [
        PluginResponse(
            plugin_id=p.config.plugin_id,
            name=p.config.name,
            description=p.config.description,
            plugin_type=p.config.plugin_type.value,
            version=p.config.version,
            author=p.config.author,
            status=p.status.value,
            requires_auth=p.config.requires_auth,
            capabilities=p.capabilities,
            last_updated=p.last_updated,
            error_message=p.error_message
        )
        for p in plugins
    ]

@skill_store_router.get("/plugins/{plugin_id}", response_model=PluginResponse)
async def get_plugin(plugin_id: str):
    """Get specific plugin details"""
    if not plugin_manager:
        raise HTTPException(status_code=503, detail="Skill Store not initialized")
    
    plugin = plugin_manager.get_plugin(plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    return PluginResponse(
        plugin_id=plugin.config.plugin_id,
        name=plugin.config.name,
        description=plugin.config.description,
        plugin_type=plugin.config.plugin_type.value,
        version=plugin.config.version,
        author=plugin.config.author,
        status=plugin.status.value,
        requires_auth=plugin.config.requires_auth,
        capabilities=plugin.capabilities,
        last_updated=plugin.last_updated,
        error_message=plugin.error_message
    )

@skill_store_router.post("/plugins/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    """Enable a plugin"""
    if not plugin_manager:
        raise HTTPException(status_code=503, detail="Skill Store not initialized")
    
    success = plugin_manager.enable_plugin(plugin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to enable plugin")
    
    return {"message": f"Plugin {plugin_id} enabled successfully"}

@skill_store_router.post("/plugins/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    """Disable a plugin"""
    if not plugin_manager:
        raise HTTPException(status_code=503, detail="Skill Store not initialized")
    
    success = plugin_manager.disable_plugin(plugin_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to disable plugin")
    
    return {"message": f"Plugin {plugin_id} disabled successfully"}

@skill_store_router.get("/plugin-types")
async def get_plugin_types():
    """Get available plugin types"""
    return [
        {"value": pt.value, "label": pt.value.replace("_", " ").title()}
        for pt in PluginType
    ]

@skill_store_router.get("/featured")
async def get_featured_plugins():
    """Get featured/recommended plugins"""
    featured_plugins = [
        {
            "plugin_id": "whatsapp_analyzer",
            "name": "WhatsApp Chat Analyzer",
            "description": "Analyze WhatsApp chat exports for insights, sentiment, and patterns",
            "category": "Analytics",
            "featured_reason": "Popular for team communication analysis",
            "installation_count": 0,  # Would be populated from analytics
            "rating": 4.8,
            "icon": "💬"
        },
        {
            "plugin_id": "email_analytics",
            "name": "Email Analytics",
            "description": "Analyze email patterns and communication effectiveness",
            "category": "Analytics",
            "featured_reason": "Essential for email productivity",
            "installation_count": 0,
            "rating": 4.6,
            "icon": "📧"
        },
        {
            "plugin_id": "meeting_optimizer",
            "name": "Meeting Optimizer",
            "description": "Optimize meeting schedules and reduce meeting fatigue",
            "category": "Productivity",
            "featured_reason": "Helps reduce unnecessary meetings",
            "installation_count": 0,
            "rating": 4.7,
            "icon": "🗓️"
        }
    ]
    
    return featured_plugins

# WhatsApp Analysis Endpoints
@skill_store_router.post("/whatsapp/analyze-chat", response_model=ChatAnalysisResponse)
async def analyze_whatsapp_chat(
    chat_content: str = Form(...),
    filename: str = Form("chat.txt")
):
    """Analyze WhatsApp chat content"""
    try:
        # Process the chat
        result = whatsapp_analyzer.process_chat_file(chat_content, filename)
        
        if result["status"] == "failed":
            return ChatAnalysisResponse(
                status="failed",
                error=result.get("error", "Unknown error")
            )
        
        return ChatAnalysisResponse(
            status="success",
            analysis=result.get("analysis"),
            summary=result.get("summary")
        )
        
    except Exception as e:
        logger.error(f"WhatsApp chat analysis failed: {e}")
        return ChatAnalysisResponse(
            status="failed",
            error=str(e)
        )

@skill_store_router.post("/whatsapp/upload-chat")
async def upload_whatsapp_chat(file: UploadFile = File(...)):
    """Upload and analyze WhatsApp chat file"""
    try:
        # Read file content
        content = await file.read()
        chat_content = content.decode('utf-8')
        
        # Process the chat
        result = whatsapp_analyzer.process_chat_file(chat_content, file.filename)
        
        if result["status"] == "failed":
            raise HTTPException(status_code=400, detail=result.get("error", "Analysis failed"))
        
        return {
            "status": "success",
            "filename": file.filename,
            "analysis": result.get("analysis"),
            "summary": result.get("summary")
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded text")
    except Exception as e:
        logger.error(f"WhatsApp chat upload failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@skill_store_router.get("/whatsapp/sample-analysis")
async def get_sample_whatsapp_analysis():
    """Get sample WhatsApp analysis for demonstration"""
    sample_analysis = {
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
                "sentiment_score": 0.72
            },
            "Bob": {
                "message_count": 389,
                "word_count": 2156,
                "avg_message_length": 38.9,
                "sentiment_score": 0.65
            }
        },
        "activity_patterns": {
            "peak_activity_hour": 14,
            "most_active_day": 2,  # Tuesday
            "hourly_distribution": {
                "9": 89, "10": 124, "11": 98, "12": 156, "13": 134, "14": 189, "15": 167, "16": 145
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
                ("project", 89), ("meeting", 67), ("deadline", 45), ("team", 38), ("client", 34)
            ]
        },
        "word_analysis": {
            "total_unique_words": 1847,
            "most_frequent_words": [
                ("project", 89), ("time", 76), ("work", 68), ("team", 54), ("meeting", 45),
                ("good", 42), ("need", 38), ("client", 34), ("deadline", 32), ("help", 28)
            ],
            "vocabulary_richness": 0.65
        },
        "media_statistics": {
            "media_distribution": {
                "text": 1189, "image": 34, "video": 12, "audio": 8, "document": 4
            },
            "text_to_media_ratio": 0.954
        }
    }
    
    return {
        "status": "success",
        "analysis": sample_analysis,
        "summary": {
            "messages_analyzed": 1247,
            "participants": ["Alice", "Bob", "Charlie", "Diana"],
            "date_range": ["2024-01-15", "2024-03-20"],
            "key_insights": [
                "Chat contains 1247 messages from 4 participants",
                "Most active participant: Alice",
                "Chat has predominantly positive sentiment",
                "Peak activity occurs around 14:00",
                "Common topics: project, meeting, deadline"
            ]
        }
    }

# A2UI Component Generation
@skill_store_router.get("/whatsapp/a2ui-components")
async def get_whatsapp_a2ui_components():
    """Get A2UI components for WhatsApp analysis display"""
    components = {
        "overview_card": {
            "type": "InfoCard",
            "title": "Chat Overview",
            "fields": [
                {"label": "Total Messages", "value": "overview.total_messages"},
                {"label": "Participants", "value": "overview.total_participants"},
                {"label": "Date Range", "value": "overview.date_range"},
                {"label": "Most Active User", "value": "overview.most_active_user"}
            ]
        },
        "sentiment_card": {
            "type": "ChartCard", 
            "title": "Sentiment Analysis",
            "chart_type": "pie",
            "data_source": "sentiment_analysis.sentiment_distribution"
        },
        "activity_chart": {
            "type": "ChartCard",
            "title": "Activity by Hour", 
            "chart_type": "bar",
            "data_source": "activity_patterns.hourly_distribution"
        },
        "participant_list": {
            "type": "ListCard",
            "title": "Participant Statistics",
            "items_source": "participant_stats",
            "display_fields": ["message_count", "word_count", "sentiment_score"]
        },
        "top_words": {
            "type": "ListCard", 
            "title": "Most Frequent Words",
            "items_source": "word_analysis.most_frequent_words",
            "max_items": 10
        },
        "insights": {
            "type": "InfoCard",
            "title": "Key Insights",
            "content_source": "summary.key_insights",
            "display_as": "list"
        }
    }
    
    return components

# Plugin Analytics
@skill_store_router.get("/analytics")
async def get_plugin_analytics():
    """Get plugin usage analytics"""
    # This would typically query the plugin analytics database
    # For now, return mock data
    return {
        "total_plugins": 3,
        "enabled_plugins": 1,
        "total_installations": 5,
        "popular_plugins": [
            {"plugin_id": "whatsapp_analyzer", "usage_count": 12},
            {"plugin_id": "email_analytics", "usage_count": 8}
        ],
        "recent_activity": [
            {"plugin_id": "whatsapp_analyzer", "action": "chat_analyzed", "timestamp": datetime.now().isoformat()}
        ]
    }