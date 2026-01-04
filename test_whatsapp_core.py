#!/usr/bin/env python3
"""
Simple test script for WhatsApp analyzer core functionality
Tests without FastAPI dependencies
"""

import sys
import os
sys.path.append('/root/dhii-mail')

from datetime import datetime
from a2ui_integration.whatsapp_analyzer import WhatsAppAnalyzer

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

def test_whatsapp_analyzer():
    """Test the WhatsApp analyzer functionality"""
    print("🧪 Testing WhatsApp Analyzer Core Functionality...")
    
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
    
    # Test 5: Legacy method compatibility
    print("\n5. Testing legacy method compatibility...")
    legacy_result = analyzer.parse_chat_file(sample_chat)
    if legacy_result:
        print(f"   ✅ Legacy parse_chat_file method works")
        print(f"   📊 Parsed {len(legacy_result)} messages")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("WhatsApp Analyzer Core Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run the test
        success = test_whatsapp_analyzer()
        
        print()
        print("=" * 60)
        if success:
            print("✅ Test Suite Completed Successfully")
        else:
            print("❌ Test Suite Completed with Errors")
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()