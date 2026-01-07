"""
Email Integration Plugin - Framework 2.0
Standardized email plugin with manifest and proper contract implementation
"""

from a2ui_integration.framework.contract import (
    PluginInterface, PluginManifest, PluginCapability
)
from a2ui_integration.framework.types import PluginType, CapabilityType
from typing import Dict, Any
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailPlugin(PluginInterface):
    """Email Integration Plugin - Framework 2.0"""
    
    def __init__(self):
        self._manifest =         self._health_status = HealthStatus.HEALTHY
        self._kernel_api: Optional[Dict[str, Any]] = None
        None
        self._kernel_api = None
        self._smtp_connections = {}
    
    @property
    def manifest(self) -> PluginManifest:
        """Plugin manifest"""
        return self._manifest
    
    def initialize(self, kernel_api: Dict[str, Any]) -> None:
        """Initialize plugin with kernel API"""
        self._kernel_api = kernel_api
        self._manifest = self._create_manifest()
        logger.info("Email plugin initialized")
    
    def _create_manifest(self) -> PluginManifest:
        """Create plugin manifest"""
        return PluginManifest(
            id="email",
            name="Email Integration",
            version="2.0.0",
            plugin_type=PluginType.INTEGRATION,
            author="dhii-team",
            description="Email integration with SMTP support",
            capabilities=[
                PluginCapability(
                    id="email.send_email",
                    name="Send Email",
                    description="Send email via SMTP",
                    capability_type=CapabilityType.ACTION,
                    input_schema={
                        "type": "object",
                        "properties": {
                            "to_email": {"type": "string", "format": "email"},
                            "subject": {"type": "string"},
                            "body": {"type": "string"},
                            "from_email": {"type": "string", "format": "email"},
                            "smtp_config": {
                                "type": "object",
                                "properties": {
                                    "host": {"type": "string"},
                                    "port": {"type": "integer"},
                                    "username": {"type": "string"},
                                    "password": {"type": "string"},
                                    "use_tls": {"type": "boolean"}
                                },
                                "required": ["host", "port"]
                            }
                        },
                        "required": ["to_email", "subject", "body", "smtp_config"]
                    },
                    output_schema={
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "message_id": {"type": "string"},
                            "error": {"type": "string"}
                        }
                    },
                    requires_auth=True,
                    timeout_seconds=30
                ),
                PluginCapability(
                    id="email.test_connection",
                    name="Test Connection",
                    description="Test SMTP connection",
                    capability_type=CapabilityType.QUERY,
                    input_schema={
                        "type": "object",
                        "properties": {
                            "smtp_config": {
                                "type": "object",
                                "properties": {
                                    "host": {"type": "string"},
                                    "port": {"type": "integer"},
                                    "username": {"type": "string"},
                                    "password": {"type": "string"},
                                    "use_tls": {"type": "boolean"}
                                },
                                "required": ["host", "port"]
                            }
                        },
                        "required": ["smtp_config"]
                    },
                    output_schema={
                        "type": "object",
                        "properties": {
                            "status": {"type": "string"},
                            "error": {"type": "string"}
                        }
                    },
                    timeout_seconds=10
                )
            ],
            dependencies=["core"],
            sandbox_config={
                "allowed_modules": [
                    "smtplib", "ssl", "email.mime.text", "email.mime.multipart"
                ],
                "max_memory_mb": 50,
                "timeout_seconds": 30
            }
        )
    
    def execute_capability(self, capability_id: str, params: Dict[str, Any]) -> Any:
        """Execute a capability"""
        if capability_id == "email.send_email":
            return self._send_email(params)
        elif capability_id == "email.test_connection":
            return self._test_connection(params)
        else:
            raise ValueError(f"Unknown capability: {capability_id}")
    
    def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send email via SMTP"""
        self._kernel_api["log"]("Sending email...")
        
        try:
            to_email = params["to_email"]
            subject = params["subject"]
            body = params["body"]
            from_email = params.get("from_email", "noreply@dhii.io")
            smtp_config = params["smtp_config"]
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = from_email
            message["To"] = to_email
            
            # Add body
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            # Send email
            with self._get_smtp_connection(smtp_config) as server:
                server.send_message(message)
                
            message_id = f"email_{hash(to_email + subject)}"
            self._kernel_api["log"](f"Email sent successfully to {to_email}")
            
            return {
                "status": "sent",
                "message_id": message_id
            }
            
        except Exception as e:
            self._kernel_api["error"](f"Failed to send email: {e}")
            return {
                "status": "failed",
                "message_id": None,
                "error": str(e)
            }
    
    def _test_connection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Test SMTP connection"""
        self._kernel_api["log"]("Testing SMTP connection...")
        
        try:
            smtp_config = params["smtp_config"]
            
            # Test connection
            with self._get_smtp_connection(smtp_config) as server:
                # Just connect and quit to test
                pass
                
            self._kernel_api["log"]("SMTP connection test successful")
            return {
                "status": "connected"
            }
            
        except Exception as e:
            self._kernel_api["error"](f"SMTP connection test failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _get_smtp_connection(self, smtp_config: Dict[str, Any]):
        """Get SMTP connection"""
        host = smtp_config["host"]
        port = smtp_config["port"]
        username = smtp_config.get("username")
        password = smtp_config.get("password")
        use_tls = smtp_config.get("use_tls", True)
        
        if use_tls:
            context = ssl.create_default_context()
            server = smtplib.SMTP(host, port)
            server.starttls(context=context)
        else:
            server = smtplib.SMTP(host, port)
        
        if username and password:
            server.login(username, password)
        
        return server
    
    def shutdown(self) -> None:
        """Cleanup SMTP connections"""
        self._kernel_api["log"]("Shutting down email plugin...")
        for connection in self._smtp_connections.values():
            try:
                connection.quit()
            except:
                pass
        self._smtp_connections.clear()

def register(kernel_api: Dict[str, Any]) -> PluginInterface:
    """Standard registration function"""
    plugin = EmailPlugin()
    plugin.initialize(kernel_api)
    
    # Register capabilities
    for capability in plugin.manifest.capabilities:
        kernel_api["register_capability"](
            capability.id,
            capability,
            plugin.execute_capability
        )
    
    return plugin
    def get_health_status(self) -> PluginHealth:
        """Get plugin health status (Framework 2.0)"""
        return PluginHealth(
            plugin_id="email",
            status=self._health_status,
            message="Email plugin operational",
            capabilities={
                "email.send": HealthStatus.HEALTHY,
                "email.receive": HealthStatus.HEALTHY,
                "email.search": HealthStatus.HEALTHY
            }
        )



def register(kernel_api: Dict[str, Any]) -> PluginInterface:
    """Register the EmailPluginV2 with Framework 2.0"""
    plugin = EmailPluginV2()
    plugin.initialize(kernel_api)
    return plugin
