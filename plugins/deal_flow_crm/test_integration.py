"""
Integration tests for Deal-Flow CRM Plugin
Tests the plugin's core functionality and UI components
"""

import asyncio
import tempfile
import os
from datetime import datetime
from decimal import Decimal

from plugins.deal_flow_crm.plugin import DealFlowCRMPlugin

async def test_plugin_initialization():
    """Test plugin initialization"""
    print("Testing plugin initialization...")
    
    plugin = DealFlowCRMPlugin(config={"database_path": "/tmp/dealflow_crm_test.db"})
    await plugin._initialize_plugin()
    
    print(f"✓ Plugin initialized: {plugin.name} v{plugin.version}")
    print(f"✓ Plugin ID: {plugin.plugin_id}")
    print(f"✓ Plugin type: {plugin.plugin_type}")
    
    return plugin

async def test_deal_lifecycle():
    """Test complete deal lifecycle"""
    print("\nTesting deal lifecycle...")
    
    plugin = DealFlowCRMPlugin(config={"database_path": "/tmp/dealflow_crm_test.db"})
    await plugin._initialize_plugin()
    
    # Create a deal
    deal_params = {
        "title": "Test Deal - Enterprise Software",
        "description": "Large enterprise software implementation",
        "value": 125000.0,
        "currency": "USD",
        "stage": "Prospecting",
        "probability": 25,
        "expected_close_date": "2024-06-30T23:59:59Z"
    }
    
    create_result = await plugin._create_deal(deal_params)
    deal_id = create_result["deal_id"]
    print(f"✓ Created deal: {deal_id}")
    
    # Get the deal
    get_result = await plugin._get_deal({"deal_id": deal_id})
    deal = get_result["deal"]
    print(f"✓ Retrieved deal: {deal['title']} (${deal['value']:,.2f})")
    
    # Update the deal
    update_params = {
        "deal_id": deal_id,
        "stage": "Qualification",
        "probability": 50,
        "value": 150000.0
    }
    await plugin._update_deal(update_params)
    print(f"✓ Updated deal stage and value")
    
    # List deals
    list_result = await plugin._list_deals({"limit": 10})
    print(f"✓ Listed {list_result['total']} deals")
    
    # Delete the deal
    await plugin._delete_deal({"deal_id": deal_id})
    print(f"✓ Deleted deal: {deal_id}")
    
    return True

async def test_pipeline_management():
    """Test pipeline management"""
    print("\nTesting pipeline management...")
    
    plugin = DealFlowCRMPlugin(config={"database_path": "/tmp/dealflow_crm_test.db"})
    await plugin._initialize_plugin()
    
    # List pipelines
    pipelines_result = await plugin._list_pipelines({})
    print(f"✓ Found {len(pipelines_result['pipelines'])} pipelines")
    
    default_pipeline = next(p for p in pipelines_result["pipelines"] if p["is_default"])
    print(f"✓ Default pipeline: {default_pipeline['name']}")
    print(f"✓ Stages: {', '.join(default_pipeline['stages'])}")
    
    return True

async def test_analytics():
    """Test analytics capabilities"""
    print("\nTesting analytics...")
    
    plugin = DealFlowCRMPlugin()
    await plugin._initialize_plugin()
    
    # Create some test deals
    test_deals = [
        {"title": "Deal 1", "value": 50000, "stage": "Prospecting", "probability": 25},
        {"title": "Deal 2", "value": 75000, "stage": "Qualification", "probability": 50},
        {"title": "Deal 3", "value": 100000, "stage": "Proposal", "probability": 75},
    ]
    
    for deal_params in test_deals:
        await plugin._create_deal(deal_params)
    
    # Get pipeline metrics
    metrics_result = await plugin._get_pipeline_metrics({"pipeline_id": "default_pipeline"})
    print(f"✓ Pipeline metrics: {metrics_result['total_deals']} deals, ${metrics_result['total_value']:,.2f} total value")
    
    # Get deal forecast
    forecast_result = await plugin._get_deal_forecast({"pipeline_id": "default_pipeline", "forecast_period": 90})
    print(f"✓ Deal forecast: ${forecast_result['total_forecast']:,.2f} for next 90 days")
    
    return True

async def test_ui_components():
    """Test UI component rendering"""
    print("\nTesting UI components...")
    
    plugin = DealFlowCRMPlugin()
    await plugin._initialize_plugin()
    
    # Create some test data
    test_deals = [
        {"title": "Dashboard Deal 1", "value": 25000, "stage": "Prospecting", "probability": 30},
        {"title": "Dashboard Deal 2", "value": 50000, "stage": "Qualification", "probability": 60},
    ]
    
    for deal_params in test_deals:
        await plugin._create_deal(deal_params)
    
    # Test dashboard UI
    dashboard_result = await plugin._render_dashboard_ui({"pipeline_id": "default_pipeline"})
    print(f"✓ Dashboard UI rendered: {len(dashboard_result['ui_operations'])} operations")
    
    # Test pipeline UI
    pipeline_result = await plugin._render_pipeline_ui({"pipeline_id": "default_pipeline"})
    print(f"✓ Pipeline UI rendered: {len(pipeline_result['ui_operations'])} operations")
    
    # Test deal form UI
    form_result = await plugin._render_deal_form_ui({})
    print(f"✓ Deal form UI rendered: {len(form_result['ui_operations'])} operations")
    
    # Test deal list UI
    list_result = await plugin._render_deal_list_ui({"limit": 10})
    print(f"✓ Deal list UI rendered: {len(list_result['ui_operations'])} operations")
    
    return True

async def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("Deal-Flow CRM Plugin Integration Tests")
    print("=" * 60)
    
    try:
        # Test plugin initialization
        plugin = await test_plugin_initialization()
        
        # Test deal lifecycle
        await test_deal_lifecycle()
        
        # Test pipeline management
        await test_pipeline_management()
        
        # Test analytics
        await test_analytics()
        
        # Test UI components
        await test_ui_components()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed successfully!")
        print("=" * 60)
        
        # Cleanup
        if os.path.exists(plugin.db_path):
            os.remove(plugin.db_path)
            print(f"✓ Cleaned up test database: {plugin.db_path}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(run_all_tests())