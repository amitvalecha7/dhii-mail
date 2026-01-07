"""
Kernel API Router - Exposes kernel functionality via HTTP endpoints
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from datetime import datetime

from a2ui_integration.core.kernel import Kernel
from a2ui_integration.core.types import PluginStatus
from a2ui_integration.core.shared_services import EventType
from a2ui_integration.core.shared_services import SharedServices
from a2ui_integration.core.logging import get_logger

logger = get_logger(__name__)

# Create router
router = APIRouter(prefix="/kernel", tags=["kernel"])

# Request/Response models
class PluginResponse(BaseModel):
    id: str
    name: str
    version: str
    description: str
    type: str
    status: str
    installed_at: datetime
    last_updated: Optional[datetime] = None
    usage_count: int = 0
    error_count: int = 0
    config: Dict[str, Any] = {}

class CapabilityRequest(BaseModel):
    capability_id: str
    parameters: Dict[str, Any] = {}

class CapabilityResponse(BaseModel):
    success: bool
    result: Any = None
    error: Optional[str] = None

class EventResponse(BaseModel):
    id: str
    type: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime

class PluginHealthResponse(BaseModel):
    plugin_id: str
    status: str  # healthy, degraded, failed
    error_count: int
    last_error: Optional[str] = None
    uptime: float

class KernelMetricsResponse(BaseModel):
    total_plugins: int
    active_plugins: int
    total_capabilities: int
    total_events: int
    error_rate: float
    uptime: float
    memory_usage: Dict[str, Any]

# Global kernel instance - will be initialized in main.py
kernel: Optional[Kernel] = None

def get_kernel() -> Kernel:
    """Get the global kernel instance"""
    if kernel is None:
        raise HTTPException(status_code=503, detail="Kernel not initialized")
    return kernel

@router.get("/plugins/{plugin_id}", response_model=PluginResponse)
async def get_plugin(plugin_id: str):
    """Get specific plugin details"""
    try:
        kernel_instance = get_kernel()
        plugin = await kernel_instance.get_plugin(plugin_id)
        
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin {plugin_id} not found")
        
        return PluginResponse(
            id=plugin.id,
            name=plugin.name,
            version=plugin.version,
            description=plugin.description,
            type=plugin.type.value,
            status=plugin.status.value,
            installed_at=plugin.installed_at,
            last_updated=plugin.last_updated,
            usage_count=plugin.usage_count,
            error_count=plugin.error_count,
            config=plugin.config
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin {plugin_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.put("/plugins/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    """Enable a plugin"""
    try:
        kernel_instance = get_kernel()
        success = await kernel_instance.enable_plugin(plugin_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Plugin {plugin_id} not found or already enabled")
        
        return {"success": True, "message": f"Plugin {plugin_id} enabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling plugin {plugin_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.put("/plugins/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    """Disable a plugin"""
    try:
        kernel_instance = get_kernel()
        success = await kernel_instance.disable_plugin(plugin_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Plugin {plugin_id} not found or already disabled")
        
        return {"success": True, "message": f"Plugin {plugin_id} disabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling plugin {plugin_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.post("/capabilities/execute", response_model=CapabilityResponse)
async def execute_capability(request: CapabilityRequest):
    """Execute a capability"""
    try:
        kernel_instance = get_kernel()
        result = await kernel_instance.execute_capability(
            request.capability_id, 
            request.parameters
        )
        
        return CapabilityResponse(
            success=True,
            result=result
        )
    except ValueError as e:
        # Capability not found or invalid parameters
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing capability {request.capability_id}: {e}")
        return CapabilityResponse(
            success=False,
            error=str(e)
        )

@router.get("/events", response_model=List[EventResponse])
async def get_event_history(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    source: Optional[str] = Query(None, description="Filter by event source"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events to return")
):
    """Get event history"""
    try:
        kernel_instance = get_kernel()
        
        # Convert string event_type to EventType enum if provided
        event_type_enum = None
        if event_type:
            try:
                event_type_enum = EventType(event_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid event type: {event_type}")
        
        events = kernel_instance.shared_services.event_bus.get_event_history(
            event_type=event_type_enum,
            limit=limit
        )
        
        return [
            EventResponse(
                id=event.id,
                type=event.type.value,
                source=event.source,
                data=event.data,
                timestamp=event.timestamp
            )
            for event in events
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting event history: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.get("/plugins/{plugin_id}/health", response_model=PluginHealthResponse)
async def get_plugin_health(plugin_id: str):
    """Get plugin health status"""
    try:
        kernel_instance = get_kernel()
        plugin = await kernel_instance.get_plugin(plugin_id)
        
        if not plugin:
            raise HTTPException(status_code=404, detail=f"Plugin {plugin_id} not found")
        
        # Determine health status based on error count
        if plugin.error_count == 0:
            status = "healthy"
        elif plugin.error_count < 5:
            status = "degraded"
        else:
            status = "failed"
        
        # Calculate uptime (simplified - based on installation time)
        uptime = (datetime.now() - plugin.installed_at).total_seconds()
        
        return PluginHealthResponse(
            plugin_id=plugin_id,
            status=status,
            error_count=plugin.error_count,
            last_error=None,  # PluginInfo doesn't have last_error field
            uptime=uptime
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting plugin health for {plugin_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.get("/metrics", response_model=KernelMetricsResponse)
async def get_kernel_metrics():
    """Get kernel metrics"""
    try:
        kernel_instance = get_kernel()
        
        # Get all plugins
        all_plugins = await kernel_instance.list_plugins()
        
        # Calculate metrics
        total_plugins = len(all_plugins)
        active_plugins = sum(1 for p in all_plugins if p.status == PluginStatus.ENABLED)
        total_capabilities = 0  # PluginInfo doesn't have capabilities field
        
        # Get event count (simplified)
        events = kernel_instance.shared_services.event_bus.get_event_history(limit=1000)
        total_events = len(events)
        
        # Calculate error rate (simplified)
        total_errors = sum(p.error_count for p in all_plugins)
        error_rate = (total_errors / max(total_plugins, 1)) * 100
        
        # Calculate uptime (simplified)
        uptime = 3600  # 1 hour placeholder
        
        # Memory usage (placeholder)
        memory_usage = {
            "total_plugins": total_plugins,
            "active_plugins": active_plugins,
            "total_capabilities": total_capabilities,
            "total_errors": total_errors
        }
        
        return KernelMetricsResponse(
            total_plugins=total_plugins,
            active_plugins=active_plugins,
            total_capabilities=total_capabilities,
            total_events=total_events,
            error_rate=error_rate,
            uptime=uptime,
            memory_usage=memory_usage
        )
    except Exception as e:
        logger.error(f"Error getting kernel metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.get("/plugins", response_model=List[PluginResponse])
async def list_plugins(
    enabled_only: bool = Query(False, description="Return only enabled plugins"),
    plugin_type: Optional[str] = Query(None, description="Filter by plugin type")
):
    """List all plugins"""
    try:
        kernel_instance = get_kernel()
        
        # Get all plugins
        all_plugins = await kernel_instance.list_plugins()
        
        # Apply filters
        filtered_plugins = all_plugins
        
        if enabled_only:
            filtered_plugins = [p for p in filtered_plugins if p.status == PluginStatus.ENABLED]
        
        if plugin_type:
            filtered_plugins = [p for p in filtered_plugins if p.type.value == plugin_type]
        
        return [
            PluginResponse(
                id=plugin.id,
                name=plugin.name,
                version=plugin.version,
                description=plugin.description,
                type=plugin.type.value,
                status=plugin.status.value,
                installed_at=plugin.installed_at,
                last_updated=plugin.last_updated,
                usage_count=plugin.usage_count,
                error_count=plugin.error_count,
                config=plugin.config
            )
            for plugin in filtered_plugins
        ]
    except Exception as e:
        logger.error(f"Error listing plugins: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

@router.get("/search/plugins")
async def search_plugins(
    query: str = Query(..., description="Search query"),
    search_type: str = Query("all", description="Search type: all, name, description, capability")
):
    """Search plugins"""
    try:
        kernel_instance = get_kernel()
        
        # Get all plugins
        all_plugins = await kernel_instance.list_plugins()
        
        # Search logic
        results = []
        query_lower = query.lower()
        
        for plugin in all_plugins:
            match = False
            
            if search_type == "all" or search_type == "name":
                if query_lower in plugin.name.lower():
                    match = True
            
            if search_type == "all" or search_type == "description":
                if query_lower in plugin.description.lower():
                    match = True
            
            # Capability search removed - PluginInfo doesn't have capabilities field
            
            if match:
                results.append({
                    "id": plugin.id,
                    "name": plugin.name,
                    "description": plugin.description,
                    "type": plugin.type.value,
                    "status": plugin.status.value,
                    "score": 1.0  # Simple scoring - could be improved
                })
        
        return {"results": results, "total": len(results)}
    except Exception as e:
        logger.error(f"Error searching plugins: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")