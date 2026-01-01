#!/usr/bin/env python3
"""
A2UI Meeting Assistant Integration Script

This script integrates A2UI components with the existing dhii-mail FastAPI backend.
It sets up the database, creates the necessary endpoints, and provides a complete
meeting assistant functionality.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_database():
    """Set up the meeting assistant database tables"""
    logger.info("Setting up meeting assistant database...")
    
    try:
        from a2ui_integration.meeting_models_updated import get_meeting_db_manager
        
        # Initialize the database manager (this creates tables)
        db_manager = get_meeting_db_manager()
        logger.info("Meeting database tables created successfully")
        
        # Create default meeting rooms
        conn = db_manager.init_database.__globals__['sqlite3'].connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Check if rooms already exist
        cursor.execute("SELECT COUNT(*) FROM meeting_rooms")
        existing_rooms = cursor.fetchone()[0]
        
        if existing_rooms == 0:
            default_rooms = [
                {
                    "id": "room_001",
                    "name": "Conference Room A",
                    "description": "Main conference room with video conferencing",
                    "capacity": 12,
                    "location": "Floor 3, Building A",
                    "has_video_conference": True,
                    "has_whiteboard": True,
                    "has_projector": True,
                    "is_active": True,
                    "booking_enabled": True,
                    "working_hours_start": "09:00",
                    "working_hours_end": "18:00",
                    "timezone": "UTC"
                },
                {
                    "id": "room_002", 
                    "name": "Small Meeting Room",
                    "description": "Intimate meeting space for 4-6 people",
                    "capacity": 6,
                    "location": "Floor 2, Building A",
                    "has_video_conference": True,
                    "has_whiteboard": True,
                    "has_projector": False,
                    "is_active": True,
                    "booking_enabled": True,
                    "working_hours_start": "09:00",
                    "working_hours_end": "18:00",
                    "timezone": "UTC"
                },
                {
                    "id": "room_003",
                    "name": "Virtual Meeting",
                    "description": "Online meeting room",
                    "capacity": 50,
                    "location": "Online",
                    "has_video_conference": True,
                    "has_whiteboard": False,
                    "has_projector": False,
                    "is_active": True,
                    "booking_enabled": True,
                    "working_hours_start": "09:00",
                    "working_hours_end": "18:00",
                    "timezone": "UTC"
                }
            ]
            
            for room in default_rooms:
                cursor.execute('''
                    INSERT INTO meeting_rooms (
                        id, name, description, capacity, location, has_video_conference,
                        has_whiteboard, has_projector, is_active, booking_enabled,
                        working_hours_start, working_hours_end, timezone, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    room['id'], room['name'], room['description'], room['capacity'],
                    room['location'], room['has_video_conference'], room['has_whiteboard'],
                    room['has_projector'], room['is_active'], room['booking_enabled'],
                    room['working_hours_start'], room['working_hours_end'], room['timezone'],
                    datetime.now().isoformat()
                ))
            
            conn.commit()
            logger.info("Default meeting rooms created")
        
        conn.close()
        logger.info("Database setup completed")
        
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        raise

def install_dependencies():
    """Install required dependencies for A2UI integration"""
    logger.info("Installing A2UI integration dependencies...")
    
    dependencies = [
        "httpx",
        "sqlalchemy",
        "alembic",
        "python-multipart",
        "websockets"
    ]
    
    for dep in dependencies:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                         check=True, capture_output=True)
            logger.info(f"Installed {dep}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {dep}: {e}")
            raise

def create_a2ui_client_build():
    """Build the A2UI client"""
    logger.info("Building A2UI client...")
    
    client_dir = project_root / "a2ui_integration" / "client"
    
    try:
        # Change to client directory
        os.chdir(client_dir)
        
        # Install npm dependencies
        subprocess.run(["npm", "install"], check=True, capture_output=True)
        logger.info("npm dependencies installed")
        
        # Build the client
        subprocess.run(["npm", "run", "build"], check=True, capture_output=True)
        logger.info("A2UI client built successfully")
        
        # Change back to project root
        os.chdir(project_root)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error building A2UI client: {e}")
        raise
    except FileNotFoundError:
        logger.warning("npm not found, skipping client build. Install npm to build A2UI client.")

def create_environment_file():
    """Create environment file for A2UI integration"""
    logger.info("Creating environment configuration...")
    
    env_content = """
# A2UI Meeting Assistant Configuration
A2UI_ENABLED=true
A2UI_CLIENT_URL=http://localhost:3001
A2UI_BACKEND_URL=http://localhost:8005
A2UI_WEBSOCKET_URL=ws://localhost:8005

# Google API for A2UI (required)
GOOGLE_API_KEY=your-google-api-key-here

# Meeting settings
DEFAULT_MEETING_DURATION=30
DEFAULT_REMINDER_TIME=15
DEFAULT_TIMEZONE=UTC

# Meeting platforms
GOOGLE_MEET_ENABLED=true
ZOOM_ENABLED=false
TEAMS_ENABLED=false

# Voice settings
VOICE_INPUT_ENABLED=true
VOICE_OUTPUT_ENABLED=true
VOICE_LANGUAGE=en-US
"""
    
    env_file = project_root / ".env.a2ui"
    
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content.strip())
        logger.info(f"Created environment file: {env_file}")
        logger.info("Please update the GOOGLE_API_KEY with your actual API key")
    else:
        logger.info(f"Environment file already exists: {env_file}")

def update_main_py():
    """Update main.py to include A2UI integration"""
    logger.info("Updating main.py to include A2UI integration...")
    
    main_py_path = project_root / "main.py"
    
    # Check if A2UI integration is already included
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    if "from a2ui_integration.a2ui_fastapi import" in content:
        logger.info("A2UI integration already included in main.py")
        return
    
    # Add A2UI import at the end of the file
    a2ui_import = """

# A2UI Meeting Assistant Integration
try:
    from a2ui_integration.a2ui_fastapi import *
    logger.info("A2UI meeting assistant integration loaded")
except ImportError as e:
    logger.warning(f"A2UI integration not available: {e}")
"""
    
    with open(main_py_path, 'a') as f:
        f.write(a2ui_import)
    
    logger.info("Updated main.py with A2UI integration")

def create_startup_script():
    """Create a startup script for the complete system"""
    logger.info("Creating startup script...")
    
    startup_script = """#!/bin/bash

# A2UI Meeting Assistant Startup Script

echo "Starting A2UI Meeting Assistant..."

# Check if Python environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Please activate your Python virtual environment first"
    exit 1
fi

# Set environment variables
export $(cat .env.a2ui | xargs)

# Start the FastAPI backend
echo "Starting FastAPI backend..."
python main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start the A2UI client (if built)
if [ -d "a2ui_integration/client/dist" ]; then
    echo "Starting A2UI client..."
    cd a2ui_integration/client/dist
    python -m http.server 3001 &
    CLIENT_PID=$!
    cd ../../..
else
    echo "A2UI client not built. Run 'python a2ui_integration/setup.py --build-client' to build it."
fi

echo "A2UI Meeting Assistant started!"
echo "Backend: http://localhost:8005"
echo "A2UI Client: http://localhost:3001"
echo "WebSocket: ws://localhost:8005/ws/a2ui"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null
    if [ ! -z "$CLIENT_PID" ]; then
        kill $CLIENT_PID 2>/dev/null
    fi
    exit 0
}

trap cleanup EXIT

# Wait for processes
wait
"""
    
    script_path = project_root / "start_a2ui.sh"
    with open(script_path, 'w') as f:
        f.write(startup_script)
    
    # Make script executable
    os.chmod(script_path, 0o755)
    logger.info(f"Created startup script: {script_path}")

def create_demo_data():
    """Create demo meeting data for testing"""
    logger.info("Creating demo meeting data...")
    
    try:
        from a2ui_integration.meeting_models_updated import get_meeting_db_manager
        import sqlite3
        from datetime import datetime, timedelta
        
        db_manager = get_meeting_db_manager()
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # Create some demo meetings
        demo_meetings = [
            {
                "id": "demo_001",
                "title": "Team Standup Meeting",
                "description": "Daily team sync to discuss progress and blockers",
                "start_time": (datetime.now() + timedelta(hours=2)).isoformat(),
                "end_time": (datetime.now() + timedelta(hours=2, minutes=30)).isoformat(),
                "organizer_email": "demo@example.com",
                "meeting_type": "google_meet",
                "meeting_link": "https://meet.google.com/demo-001",
                "status": "confirmed"
            },
            {
                "id": "demo_002",
                "title": "Client Presentation",
                "description": "Q4 results presentation to important client",
                "start_time": (datetime.now() + timedelta(days=1, hours=10)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=1, hours=11)).isoformat(),
                "organizer_email": "demo@example.com",
                "meeting_type": "zoom",
                "meeting_link": "https://zoom.us/j/demo002",
                "status": "confirmed"
            }
        ]
        
        for meeting in demo_meetings:
            cursor.execute("SELECT id FROM meetings WHERE id = ?", (meeting['id'],))
            existing = cursor.fetchone()
            
            if not existing:
                cursor.execute('''
                    INSERT INTO meetings (
                        id, title, description, start_time, end_time,
                        organizer_email, meeting_type, meeting_link, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    meeting['id'], meeting['title'], meeting['description'],
                    meeting['start_time'], meeting['end_time'], meeting['organizer_email'],
                    meeting['meeting_type'], meeting['meeting_link'], meeting['status'],
                    datetime.now().isoformat()
                ))
        
        # Create some demo time slots
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        time_slots = []
        for date in [today, tomorrow]:
            for hour in [9, 10, 11, 14, 15, 16]:
                slot_id = f"slot_{date}_{hour:02d}00"
                cursor.execute("SELECT id FROM time_slots WHERE id = ?", (slot_id,))
                existing = cursor.fetchone()
                
                if not existing:
                    cursor.execute('''
                        INSERT INTO time_slots (
                            id, date, start_time, end_time, is_available, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        slot_id, date, f"{hour:02d}:00", f"{hour+1:02d}:00",
                        True, datetime.now().isoformat()
                    ))
        
        conn.commit()
        conn.close()
        logger.info("Demo data created successfully")
        
    except Exception as e:
        logger.error(f"Error creating demo data: {e}")

def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="A2UI Meeting Assistant Setup")
    parser.add_argument("--build-client", action="store_true", help="Build A2UI client")
    parser.add_argument("--demo-data", action="store_true", help="Create demo data")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency installation")
    
    args = parser.parse_args()
    
    logger.info("Starting A2UI Meeting Assistant setup...")
    
    try:
        # Install dependencies (unless skipped)
        if not args.skip_deps:
            install_dependencies()
        
        # Set up database
        setup_database()
        
        # Create environment file
        create_environment_file()
        
        # Update main.py
        update_main_py()
        
        # Build client (if requested)
        if args.build_client:
            create_a2ui_client_build()
        
        # Create demo data (if requested)
        if args.demo_data:
            create_demo_data()
        
        # Create startup script
        create_startup_script()
        
        logger.info("A2UI Meeting Assistant setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Update .env.a2ui with your Google API key")
        logger.info("2. Run './start_a2ui.sh' to start the system")
        logger.info("3. Open http://localhost:3001 for the A2UI client")
        logger.info("4. Use the chat interface to interact with the meeting assistant")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()