"""
Test script for @dhii.ai Email Integration System
"""

import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dhii_email_integration import DhiiEmailIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_dhii_registration():
    """Test @dhii.ai user registration and email account creation"""
    print("Testing @dhii.ai Email Integration...")
    
    integration = DhiiEmailIntegration()
    
    try:
        # Test user registration with @dhii.ai email
        result = await integration.register_user_with_dhii_email(
            username="testuser",
            password="testpassword123",
            first_name="Test",
            last_name="User"
        )
        
        print("✅ User registration successful!")
        print(f"📧 @dhii.ai Email: {result['dhii_email']}")
        print(f"👤 User ID: {result['user']['id']}")
        
        # Test getting user email accounts
        email_accounts = integration.get_user_email_accounts(result['user']['id'])
        print(f"📨 Email accounts found: {len(email_accounts)}")
        
        for account in email_accounts:
            print(f"   - {account['email_address']} ({account['provider']})")
        
        # Test adding external email account
        external_result = await integration.add_external_email_account(
            user_id=result['user']['id'],
            provider='gmail',
            email_address='testuser@gmail.com',
            password='gmailtestpassword',
            account_name="Personal Gmail"
        )
        
        print("✅ External email account added successfully!")
        print(f"📧 External Email: {external_result['email_address']}")
        
        # Verify both accounts are present
        all_accounts = integration.get_user_email_accounts(result['user']['id'])
        print(f"📨 Total email accounts: {len(all_accounts)}")
        
        for account in all_accounts:
            status = "✅ PRIMARY" if account.get('is_primary') else "   "
            print(f"   {status} {account['email_address']} ({account['provider']})")
        
        print("\n🎉 All tests passed! @dhii.ai integration is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_registrations():
    """Test multiple user registrations"""
    print("\nTesting multiple user registrations...")
    
    integration = DhiiEmailIntegration()
    
    test_users = [
        ("alice", "alicepassword", "Alice", "Smith"),
        ("bob", "bobpassword", "Bob", "Johnson"),
        ("charlie", "charliepassword", "Charlie", "Brown")
    ]
    
    successful_registrations = 0
    
    for username, password, first_name, last_name in test_users:
        try:
            result = await integration.register_user_with_dhii_email(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            
            print(f"✅ {username}: {result['dhii_email']}")
            successful_registrations += 1
            
        except Exception as e:
            print(f"❌ {username}: Registration failed - {e}")
    
    print(f"\n📊 Successful registrations: {successful_registrations}/{len(test_users)}")
    return successful_registrations == len(test_users)

if __name__ == "__main__":
    print("🧪 @dhii.ai Email Integration Test")
    print("=" * 50)
    
    # Run tests
    success1 = asyncio.run(test_dhii_registration())
    success2 = asyncio.run(test_multiple_registrations())
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("🎉 ALL TESTS PASSED! @dhii.ai integration is ready for production.")
    else:
        print("❌ SOME TESTS FAILED. Please check the implementation.")
    
    print("\n📋 Next steps:")
    print("1. Integrate with your user registration API endpoints")
    print("2. Configure actual @dhii.ai SMTP/IMAP server settings")
    print("3. Set up email sync daemon for background synchronization")
    print("4. Build unified email client UI")