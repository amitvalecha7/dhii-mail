"""
Test script for Email Sync Daemon
"""

import asyncio
import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from email_sync_daemon import EmailSyncDaemon, SyncConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_daemon():
    """Test the email sync daemon"""
    print("Testing Email Sync Daemon...")
    
    # Create daemon with shorter sync interval for testing
    config = SyncConfig(
        sync_interval=10,  # 10 seconds for testing
        max_sync_duration=30,
        retry_interval=5
    )
    
    daemon = EmailSyncDaemon(config=config)
    
    try:
        # Start the daemon
        await daemon.start()
        print("Daemon started successfully")
        
        # Let it run for a short period
        await asyncio.sleep(15)
        
        # Check statistics
        stats = daemon.get_stats()
        print(f"Daemon statistics: {stats}")
        
        # Stop the daemon
        await daemon.stop()
        print("Daemon stopped successfully")
        
    except Exception as e:
        print(f"Error testing daemon: {e}")
        await daemon.stop()

if __name__ == "__main__":
    asyncio.run(test_daemon())