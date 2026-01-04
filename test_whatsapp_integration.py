#!/usr/bin/env python3
"""
Test script for WhatsApp integration
Tests the WhatsApp analyzer functionality
"""

import asyncio
import json
from datetime import datetime
from a2ui_integration.whatsapp_analyzer import WhatsAppAnalyzer
from a2ui_integration.plugin_manager import PluginManager
from a2ui_integration.skill_store import initialize_skill_store

def create_sample_chat():
    """Create a sample WhatsApp chat for testing"""
    sample_chat = """1/15/24, 2:30 PM - Alice: Hey everyone! How's the project going?
1/15/24, 2:32 PM - Bob: Going well! Just finished the UI mockups
1/15/24, 2:33 PM - Charlie: Great work Bob! The designs look amazing
1/15/24, 2:35 PM - Diana: I love the new color scheme. Very modern
1/15/24, 2:36 PM - Alice: Thanks team! Let's schedule a review meeting
1/15/24, 2:37 PM - Bob: How about tomorrow at 3 PM?
1/15/24, 2:38 PM - Charlie: Works for me! Should we invite the client?
1/15/24, 2:40 PM - Diana: Yes, definitely. They should see the progress
1/15/24, 2:41 PM - Alice: Perfect! I'll send the calendar invite
1/15/24, 2:42 PM - Bob: <Media omitted>
1/15/24, 2:43 PM - Charlie: That's the final mockup I was working on
1/15/24, 2:45 PM - Diana: Looks fantastic! The animations are smooth
1/15/24, 2:46 PM - Alice: Excellent work everyone. This project is going to be a success
1/15/24, 2:47 PM - Bob: Thanks Alice! Couldn't have done it without the team
1/15/24, 2:48 PM - Charlie: Teamwork makes the dream work! 😊
1/15/24, 2:50 PM - Diana: Let's celebrate after the client meeting!
"""
    return sample_chat

async def test_whatsapp_analyzer():
    """Test the WhatsApp analyzer functionality"""
    print("🧪 Testing WhatsApp Analyzer Integration...")
    
    # Initialize analyzer
    analyzer = WhatsAppAnalyzer()
    
    # Test 1: Parse chat export
    print("\n1. Testing chat parsing...")
    sample_chat = create_sample_chat()
    messages = analyzer.parse_chat_export(sample_chat, "txt")
    print(f"   ✅ Parsed {len(messages)} messages")
    
    # Test 2: Analyze chat
    print("\n2. Testing chat analysis...")
    analysis = analyzer.analyze_chat(messages)
    print(f"   ✅ Analysis complete")
    print(f"   📊 Total messages: {analysis['overview']['total_messages']}")
    print(f"   👥 Participants: {analysis['overview']['total_participants']}")
    print(f"   😊 Sentiment: {analysis['sentiment_analysis']['overall_sentiment']}")
    print(f"   ⏰ Peak hours: {analysis['activity_patterns']['peak_hours']}")
    
    # Test 3: Process chat file
    print("\n3. Testing file processing...")
    result = analyzer.process_chat_file(sample_chat, "test_chat.txt")
    if result["status"] == "success":
        print(f"   ✅ File processed successfully")
        print(f"   📋 Summary: {result['summary']['messages_analyzed']} messages analyzed")
    else:
        print(f"   ❌ File processing failed: {result['error']}")
    
    # Test 4: Get sample analysis
    print("\n4. Testing sample analysis...")
    sample_analysis = analyzer.get_sample_analysis()
    if sample_analysis["status"] == "success":
        print(f"   ✅ Sample analysis generated")
        print(f"   📊 Sample contains {sample_analysis['analysis']['overview']['total_messages']} messages")
    
    return True

async def test_plugin_manager():
    """Test the plugin manager functionality"""
    print("\n🔌 Testing Plugin Manager...")
    
    # Initialize plugin manager
    pm = PluginManager()
    
    # Test 1: Initialize skill store
    print("\n1. Testing skill store initialization...")
    initialize_skill_store(pm)
    print(f"   ✅ Skill store initialized")
    
    # Test 2: Check if WhatsApp plugin is registered
    print("\n2. Testing plugin registration...")
    whatsapp_plugin = pm.get_plugin_info("whatsapp_analyzer")
    if whatsapp_plugin:
        print(f"   ✅ WhatsApp analyzer plugin registered")
        print(f"   📋 Plugin name: {whatsapp_plugin['config']['name']}")
        print(f"   🔧 Status: {whatsapp_plugin['status']}")
        print(f"   📊 Usage count: {whatsapp_plugin['usage_count']}")
    else:
        print(f"   ❌ WhatsApp analyzer plugin not found")
    
    # Test 3: Get plugin analytics
    print("\n3. Testing plugin analytics...")
    analytics = pm.get_plugin_analytics("whatsapp_analyzer")
    if analytics:
        print(f"   ✅ Analytics retrieved")
        print(f"   📊 Total usage: {analytics['total_usage']}")
        print(f"   ❌ Total errors: {analytics['total_errors']}")
    
    return True

async def test_integration():
    """Test the complete integration"""
    print("🚀 Testing Complete WhatsApp Integration...")
    
    # Test analyzer
    analyzer_test = await test_whatsapp_analyzer()
    
    # Test plugin manager
    plugin_test = await test_plugin_manager()
    
    if analyzer_test and plugin_test:
        print("\n🎉 All tests passed! WhatsApp integration is working correctly.")
        return True
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("WhatsApp Integration Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run the test
    success = asyncio.run(test_integration())
    
    print()
    print("=" * 60)
    if success:
        print("✅ Test Suite Completed Successfully")
    else:
        print("❌ Test Suite Completed with Errors")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)