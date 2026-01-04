import asyncio
import logging
import sys
import os

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Enable Debug Logging to File
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler("bridge_debug.log", mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("VerifyBridge")

from a2ui_integration.core.kernel import Kernel
from kernel_plugin_integration import KernelPluginIntegration

async def verify_bridge():
    logger.info("🚀 Starting Kernel Bridge Verification...")
    logger.info(f"Path: {sys.path}")
    
    # 1. Initialize DB Schema (Manually for :memory:)
    import sqlite3
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS plugins (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT,
            description TEXT,
            type TEXT,
            author TEXT,
            enabled BOOLEAN,
            status TEXT,
            config TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS capabilities (
            id TEXT PRIMARY KEY,
            plugin_id TEXT,
            domain TEXT,
            name TEXT,
            description TEXT,
            input_schema TEXT,
            output_schema TEXT,
            side_effects TEXT,
            requires_auth BOOLEAN
        );
        CREATE TABLE IF NOT EXISTS plugin_dependencies (
            plugin_id TEXT,
            dependency_id TEXT,
            PRIMARY KEY (plugin_id, dependency_id)
        );
    """)
    conn.commit()
    # Hack: Kernel uses its own connection, so we can't share :memory: easily unless we pass connection.
    # Actually Kernel takes db_path. If we use a file, it's easier.
    db_file = "verify_kernel.db"
    
    if os.path.exists(db_file):
        os.remove(db_file)
        
    kernel = Kernel(db_path=db_file) 
    
    # Init tables in the actual file DB
    k_conn = sqlite3.connect(db_file)
    k_conn.executescript("""
        CREATE TABLE IF NOT EXISTS plugins (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            version TEXT,
            description TEXT,
            type TEXT,
            author TEXT,
            enabled BOOLEAN,
            status TEXT,
            config TEXT,
            created_at TEXT,
            updated_at TEXT
        );
        CREATE TABLE IF NOT EXISTS capabilities (
            id TEXT PRIMARY KEY,
            plugin_id TEXT,
            domain TEXT,
            name TEXT,
            description TEXT,
            input_schema TEXT,
            output_schema TEXT,
            side_effects TEXT,
            requires_auth BOOLEAN
        );
        CREATE TABLE IF NOT EXISTS plugin_dependencies (
            plugin_id TEXT,
            dependency_id TEXT,
            PRIMARY KEY (plugin_id, dependency_id)
        );
    """)
    k_conn.close()

    await kernel.initialize()
    logger.info("✅ Kernel Initialized")
    
    bridge = KernelPluginIntegration(kernel)
    
    logger.info("🔄 Running integrate_all_plugins()...")
    await bridge.integrate_all_plugins()
    
    plugins = await kernel.list_plugins()
    registered_ids = [p.id for p in plugins]
    
    logger.info(f"📋 Registered Plugins ({len(plugins)}): {registered_ids}")
    
    required = ["email_manager", "calendar_manager", "ai_engine"]
    missing = [req for req in required if req not in registered_ids]
    
    if missing:
        logger.error(f"❌ Missing Plugins: {missing}")
        return False
        
    logger.info("✅ All core managers registered as plugins!")
    return True

if __name__ == "__main__":
    success = asyncio.run(verify_bridge())
    sys.exit(0 if success else 1)
