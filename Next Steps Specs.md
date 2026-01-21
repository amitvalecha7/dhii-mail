 Let me break down what is next:

Convert to SaaS Application - Add subscription management, payment tracking, invoicing
Identify gaps in core structure - Look for architectural issues
Identify coupled/decoupled elements - Find tight coupling that needs refactoring
Make it flexible - Core should be untouched, features should be pluggable
Define future refinements and features
Redefine UI aspects
Let me analyze the provided architecture document thoroughly:

Current State Analysis
What's Good:
4-Layer Architecture - Clean separation (Transport, Intelligence, Application, Persistence)
A2UI Protocol - Smart approach to dynamic UI generation
Plugin Framework - Well-designed with manifests, capabilities, lifecycle
SSE Streaming - Good for real-time updates
SQLite with Fernet encryption - Adequate for single-tenant
Gaps & Issues I Can Identify:
1. Multi-tenancy is completely missing

SQLite is single-tenant
No tenant isolation
No user organization/workspace model
No concept of "accounts" vs "users"
2. SaaS Infrastructure Missing:

No subscription/billing system
No usage metering
No feature flags based on plans
No invoice generation
No payment gateway integration
3. Tight Coupling Issues:

Symphony Orchestrator seems to do too much (intent parsing + plugin execution + layout composition)
Database schemas are tightly coupled to plugins (email.db, calendar.db, crm.db as separate files)
No clear separation between core platform and plugin data
4. Scalability Concerns:

SQLite won't scale for SaaS
No message queue for async processing
No caching layer
No CDN consideration for frontend
5. Missing SaaS Essentials:

No admin dashboard for tenant management
No usage analytics or reporting
No audit logging for compliance
No rate limiting per tenant
No API versioning strategy
No webhook system for integrations
6. Security Gaps for SaaS:

JWT alone is not enough
No refresh token strategy mentioned
No API key management for programmatic access
No role-based access control (RBAC)
No organization-level permissions
7. Plugin Isolation for SaaS:

Plugins seem to share the same process
No per-tenant plugin configuration isolation
No metering of plugin usage per tenant
8. UI Gaps:

No mention of responsive design
No multi-tenant UI considerations (workspace switching, org context)
No mention of accessibility standards
No dark mode or theme customization
No internationalization support
No offline capabilities
No mobile-first approach
I need to structure a comprehensive response that addresses the SaaS transformation, identifies the coupling issues, defines what should be core versus pluggable, and maps out a realistic roadmap. The response will cover the multi-tenancy model, billing architecture, gap analysis with recommendations, core isolation strategy, and UI redefinition including design system evolution and accessibility standards.

Dhii-Mail → Dhii SaaS: Complete Transformation Blueprint
This is an extensive analysis. I'll structure it as a actionable blueprint you can execute against.

Table of Contents
Executive Gap Analysis
SaaS Transformation Architecture
Coupling Analysis & Decoupling Strategy
Core Isolation Framework
Billing & Subscription System
UI/UX Redefinition
Future Roadmap
Implementation Phases
1. Executive Gap Analysis
1.1 Critical Gaps (Must Fix for SaaS)
Gap	Current State	SaaS Requirement	Severity
Multi-tenancy	Single SQLite, no isolation	Per-tenant data isolation	🔴 Critical
Billing/Subs	None	Stripe/Paddle integration	🔴 Critical
Authentication	Simple JWT	OAuth2 + RBAC + Org model	🔴 Critical
Database	SQLite files	PostgreSQL/managed DB	🔴 Critical
Usage Metering	None	Per-tenant, per-feature tracking	🔴 Critical
Rate Limiting	None mentioned	Per-tenant throttling	🟠 High
API Versioning	None	/v1/, /v2/ strategy	🟠 High
Audit Logging	None	Compliance-ready logs	🟠 High
Admin Dashboard	None	Tenant management, analytics	🟠 High
1.2 Architectural Coupling Issues
text

CURRENT TIGHT COUPLING DETECTED:
┌─────────────────────────────────────────────────────────────────┐
│  Symphony Orchestrator (GOD OBJECT)                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ❌ Intent Parsing (LLM)                                 │    │
│  │  ❌ Plugin Discovery & Routing                           │    │
│  │  ❌ Plugin Execution                                     │    │
│  │  ❌ Layout Composition                                   │    │
│  │  ❌ A2UI Generation                                      │    │
│  │  ❌ Error Handling                                       │    │
│  │  ❌ Context Management                                   │    │
│  └─────────────────────────────────────────────────────────┘    │
│  This class does TOO MUCH → Hard to extend, test, maintain      │
└─────────────────────────────────────────────────────────────────┘

DATABASE COUPLING:
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│    email.db      │  │   calendar.db    │  │     crm.db       │
└──────────────────┘  └──────────────────┘  └──────────────────┘
         ▲                    ▲                     ▲
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
              ❌ Separate files = No joins
              ❌ No unified transaction
              ❌ Plugin owns schema = Migration hell
              ❌ No tenant isolation
1.3 What's Already Well-Designed (Keep These)
Component	Why It's Good
A2UI Protocol	Brilliant abstraction for dynamic UI
Plugin Capability Model	Clean contract-based design
SSE Streaming	Right choice for real-time updates
4-Layer Architecture	Good conceptual separation
Liquid Glass Design System	Solid design token foundation
2. SaaS Transformation Architecture
2.1 New High-Level Architecture
text

┌─────────────────────────────────────────────────────────────────────────┐
│                           EDGE LAYER                                    │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐    │
│  │   Cloudflare  │  │  Rate Limiter │  │  Geographic Routing       │    │
│  │   CDN/WAF     │  │  (per-tenant) │  │  (latency optimization)   │    │
│  └───────────────┘  └───────────────┘  └───────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY                                      │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐    │
│  │ Auth Middleware│  │ Tenant Context│  │  Usage Metering           │    │
│  │ (JWT + API Key)│  │  Injection    │  │  (event emission)         │    │
│  └───────────────┘  └───────────────┘  └───────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────────┐
│   CORE PLATFORM   │   │  PLUGIN RUNTIME   │   │   BILLING SERVICE     │
│   (Never touched) │   │  (Extensible)     │   │   (Isolated)          │
│                   │   │                   │   │                       │
│ • Auth Service    │   │ • Plugin Manager  │   │ • Subscription Mgmt   │
│ • Tenant Service  │   │ • Sandbox Engine  │   │ • Usage Aggregation   │
│ • A2UI Engine     │   │ • Capability Reg  │   │ • Invoice Generation  │
│ • Stream Manager  │   │ • Health Monitor  │   │ • Payment Gateway     │
│ • Event Bus       │   │                   │   │                       │
└───────────────────┘   └───────────────────┘   └───────────────────────┘
            │                       │                       │
            └───────────────────────┼───────────────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER (Multi-tenant)                          │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────────┐    │
│  │  PostgreSQL   │  │    Redis      │  │  Object Storage (S3)     │    │
│  │  (tenant_id   │  │  (Cache +     │  │  (Attachments,           │    │
│  │   everywhere) │  │   Sessions)   │  │   Plugin Assets)         │    │
│  └───────────────┘  └───────────────┘  └───────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
2.2 Multi-Tenancy Model
Python

# NEW: Tenant Hierarchy Model

"""
Organization (Billing Entity)
    │
    ├── Workspaces (Logical Separation)
    │       │
    │       ├── Users (Access Control)
    │       │
    │       └── Plugins (Per-workspace config)
    │
    └── Subscription (Plan + Usage)
"""

# Database Schema Changes
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True)  # for subdomain: acme.dhii.ai
    
    # Billing
    stripe_customer_id = Column(String(255))
    subscription_tier = Column(Enum("free", "pro", "enterprise"))
    subscription_status = Column(Enum("active", "past_due", "cancelled"))
    
    # Limits (based on plan)
    max_users = Column(Integer, default=5)
    max_workspaces = Column(Integer, default=1)
    max_plugins = Column(Integer, default=10)
    monthly_ai_credits = Column(Integer, default=1000)
    
    created_at = Column(DateTime, default=utcnow)

class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    org_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    settings = Column(JSONB, default={})  # Workspace-specific config
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    org_id = Column(UUID, ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(Enum("owner", "admin", "member", "viewer"))
    
    # Every query now includes:
    # WHERE org_id = :current_tenant_id
2.3 Row-Level Security (PostgreSQL)
SQL

-- Enable RLS on all tenant tables
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE crm_deals ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their org's data
CREATE POLICY tenant_isolation ON emails
    FOR ALL
    USING (org_id = current_setting('app.current_org_id')::uuid);

-- In FastAPI middleware:
-- SET app.current_org_id = 'uuid-of-tenant';
3. Coupling Analysis & Decoupling Strategy
3.1 Current Coupling Map
text

                    TIGHTLY COUPLED (BAD)
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │            Symphony Orchestrator                      │     │
│  │                                                       │     │
│  │   Responsibilities (TOO MANY):                        │     │
│  │   1. Parse natural language intent                    │◄────┼── LLM Provider
│  │   2. Match intent to plugin capabilities              │     │
│  │   3. Execute plugins                                  │◄────┼── All Plugins
│  │   4. Handle plugin errors                             │     │
│  │   5. Compose layout                                   │     │
│  │   6. Generate A2UI JSON                               │     │
│  │   7. Stream to frontend                               │◄────┼── SSE Logic
│  │   8. Manage conversation context                      │◄────┼── Context Store
│  │                                                       │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  Problem: Change one thing → Everything breaks                 │
│                                                                │
└────────────────────────────────────────────────────────────────┘

                    SCHEMA COUPLING (BAD)
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Plugin: EmailPlugin                                           │
│      ├── Knows about: email.db schema                          │
│      ├── Writes directly to: messages table                    │
│      └── Breaking change: ALTER TABLE → Plugin breaks          │
│                                                                │
│  Plugin: CRMPlugin                                             │
│      ├── Owns: crm.db (entire file)                            │
│      └── Problem: Can't query across email + CRM               │
│                                                                │
└────────────────────────────────────────────────────────────────┘
3.2 Decoupled Target Architecture
text

                    DECOUPLED (GOOD)
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│   LAYER 1: Intent Understanding (Isolated)                              │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  IntentEngine                                                  │    │
│   │  ├── Input: Raw prompt + Context                               │    │
│   │  ├── Output: IntentGraph (structured intent)                   │    │
│   │  └── Single Responsibility: Understand user                    │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│                              ▼                                          │
│   LAYER 2: Capability Routing (Isolated)                                │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  CapabilityRouter                                              │    │
│   │  ├── Input: IntentGraph                                        │    │
│   │  ├── Output: ExecutionPlan[List[Capability]]                   │    │
│   │  └── Single Responsibility: Match intent → capabilities        │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│                              ▼                                          │
│   LAYER 3: Execution Engine (Isolated)                                  │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  PluginExecutor                                                │    │
│   │  ├── Input: ExecutionPlan                                      │    │
│   │  ├── Output: List[PluginResult]                                │    │
│   │  ├── Handles: Parallelism, retries, timeouts                   │    │
│   │  └── Single Responsibility: Run plugins safely                 │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│                              ▼                                          │
│   LAYER 4: Composition Engine (Isolated)                                │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  LayoutComposer                                                │    │
│   │  ├── Input: List[PluginResult] + Context                       │    │
│   │  ├── Output: A2UIDocument                                      │    │
│   │  └── Single Responsibility: Arrange UI components              │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                              │                                          │
│                              ▼                                          │
│   LAYER 5: Stream Manager (Isolated)                                    │
│   ┌───────────────────────────────────────────────────────────────┐    │
│   │  StreamManager                                                 │    │
│   │  ├── Input: A2UIDocument                                       │    │
│   │  ├── Output: SSE Stream                                        │    │
│   │  └── Single Responsibility: Deliver to frontend                │    │
│   └───────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
3.3 Decoupling Implementation
Python

# BEFORE: God Object
class SymphonyOrchestrator:
    async def process_prompt(self, prompt: str):
        # 200+ lines doing everything
        pass

# AFTER: Single Responsibility Components

# 1. Intent Engine (Pure)
class IntentEngine:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider
    
    async def parse(self, prompt: str, context: ConversationContext) -> IntentGraph:
        """Single responsibility: Understand what user wants"""
        return await self.llm.parse_intent(prompt, context)

# 2. Capability Router (Pure)
class CapabilityRouter:
    def __init__(self, registry: CapabilityRegistry):
        self.registry = registry
    
    def route(self, intent: IntentGraph) -> ExecutionPlan:
        """Single responsibility: Match intent to capabilities"""
        capabilities = self.registry.match(intent.required_capabilities)
        return ExecutionPlan(
            capabilities=capabilities,
            parallel_groups=self._optimize_parallelism(capabilities)
        )

# 3. Plugin Executor (Side-effect boundary)
class PluginExecutor:
    def __init__(self, sandbox: PluginSandbox, metrics: MetricsCollector):
        self.sandbox = sandbox
        self.metrics = metrics
    
    async def execute(self, plan: ExecutionPlan, ctx: TenantContext) -> List[PluginResult]:
        """Single responsibility: Execute plugins safely"""
        results = []
        for group in plan.parallel_groups:
            group_results = await asyncio.gather(*[
                self._execute_one(cap, ctx) for cap in group
            ], return_exceptions=True)
            results.extend(group_results)
        return results

# 4. Layout Composer (Pure)
class LayoutComposer:
    def __init__(self, schema_engine: SchemaEngine):
        self.schema = schema_engine
    
    def compose(self, results: List[PluginResult], context: UIContext) -> A2UIDocument:
        """Single responsibility: Arrange components"""
        components = [self.schema.to_component(r) for r in results]
        return A2UIDocument(
            layout=self._calculate_grid(components, context.viewport),
            components=components
        )

# 5. NEW: Orchestrator is now just a coordinator
class Orchestrator:
    """Thin coordinator - just wires components together"""
    
    def __init__(
        self,
        intent_engine: IntentEngine,
        router: CapabilityRouter,
        executor: PluginExecutor,
        composer: LayoutComposer,
        stream_manager: StreamManager
    ):
        self.intent = intent_engine
        self.router = router
        self.executor = executor
        self.composer = composer
        self.stream = stream_manager
    
    async def process(self, prompt: str, ctx: RequestContext) -> AsyncGenerator:
        # Skeleton immediately
        yield self.stream.skeleton()
        
        # Parse intent
        intent = await self.intent.parse(prompt, ctx.conversation)
        
        # Check for ambiguity
        if intent.needs_clarification:
            yield self.stream.clarification(intent.clarification_options)
            return
        
        # Route to capabilities
        plan = self.router.route(intent)
        
        # Execute
        results = await self.executor.execute(plan, ctx.tenant)
        
        # Compose
        document = self.composer.compose(results, ctx.ui)
        
        # Stream
        async for chunk in self.stream.emit(document):
            yield chunk
3.4 Database Decoupling
Python

# BEFORE: Plugin owns schema
class EmailPlugin:
    def __init__(self):
        self.db = sqlite3.connect("email.db")  # ❌ Direct coupling

# AFTER: Plugin uses Repository Interface

# Core defines the interface
class DataRepository(Protocol):
    """Plugins program against this interface, not concrete DB"""
    
    async def store(self, entity_type: str, data: Dict) -> str:
        """Store data, returns ID"""
        ...
    
    async def query(self, entity_type: str, filters: Dict) -> List[Dict]:
        """Query data"""
        ...
    
    async def get(self, entity_type: str, id: str) -> Optional[Dict]:
        """Get by ID"""
        ...

# Core provides implementation
class PostgresRepository(DataRepository):
    """Tenant-aware PostgreSQL implementation"""
    
    def __init__(self, tenant_id: UUID):
        self.tenant_id = tenant_id
    
    async def store(self, entity_type: str, data: Dict) -> str:
        # Automatically adds tenant_id
        data["tenant_id"] = self.tenant_id
        # Schema is managed by core migrations, not plugin
        ...

# Plugin uses injected repository
class EmailPlugin(PluginInterface):
    async def execute_capability(
        self,
        capability_id: str,
        params: Dict,
        context: ExecutionContext
    ) -> Any:
        # Repository injected by framework
        repo = context.repository
        
        if capability_id == "email.list":
            return await repo.query("emails", {"folder": params.get("folder")})
4. Core Isolation Framework
4.1 Core vs Extension Boundary
text

┌─────────────────────────────────────────────────────────────────────────┐
│                           CORE PLATFORM                                 │
│                     (Never modified for features)                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │   KERNEL (Immutable)                                              │   │
│  │   ├── AuthService         # JWT, OAuth, Sessions                  │   │
│  │   ├── TenantService       # Multi-tenancy, isolation              │   │
│  │   ├── EventBus            # Internal pub/sub                      │   │
│  │   ├── PluginManager       # Lifecycle, sandbox                    │   │
│  │   ├── CapabilityRegistry  # Discovery, routing                    │   │
│  │   ├── StreamManager       # SSE delivery                          │   │
│  │   ├── RepositoryFactory   # Data access abstraction               │   │
│  │   └── MetricsCollector    # Observability                         │   │
│  │                                                                   │   │
│  │   INTERFACES (Stable contracts)                                   │   │
│  │   ├── PluginInterface     # What plugins implement                │   │
│  │   ├── DataRepository      # How plugins access data               │   │
│  │   ├── LLMProvider         # How to call AI models                 │   │
│  │   └── A2UIComponent       # UI component schema                   │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Extension Points (How to add features without touching core):          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │   1. Plugins       → New capabilities                            │   │
│  │   2. Middleware    → Request/response processing                 │   │
│  │   3. Event Hooks   → React to system events                      │   │
│  │   4. UI Components → New A2UI component types                    │   │
│  │   5. LLM Providers → New AI model integrations                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         EXTENSION LAYER                                 │
│                    (All features live here)                             │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                   │   │
│  │   PLUGINS (Dynamically loaded)                                    │   │
│  │   ├── EmailPlugin         # IMAP/SMTP integration                 │   │
│  │   ├── CalendarPlugin      # CalDAV/Google integration             │   │
│  │   ├── CRMPlugin           # Salesforce/HubSpot                    │   │
│  │   ├── MeetingPlugin       # Zoom/Jitsi                            │   │
│  │   ├── BillingPlugin       # Stripe (even billing is a plugin!)    │   │
│  │   └── ...                                                         │   │
│  │                                                                   │   │
│  │   MIDDLEWARE EXTENSIONS                                           │   │
│  │   ├── UsageMeteringMiddleware   # Track API usage                 │   │
│  │   ├── AuditLogMiddleware        # Compliance logging              │   │
│  │   └── FeatureFlagMiddleware     # A/B testing                     │   │
│  │                                                                   │   │
│  │   EVENT HOOKS                                                     │   │
│  │   ├── OnEmailReceived     # Trigger workflows                     │   │
│  │   ├── OnDealClosed        # Notify team                           │   │
│  │   └── OnSubscriptionChanged  # Adjust limits                      │   │
│  │                                                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
4.2 Extension Point Contracts
Python

# === CORE: Stable Interfaces (core/contracts.py) ===

from abc import ABC, abstractmethod
from typing import Protocol, AsyncGenerator

# 1. Plugin Extension Point
class PluginInterface(ABC):
    """Implement this to create a plugin"""
    
    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        """Plugin metadata"""
        ...
    
    @abstractmethod
    async def on_load(self, config: PluginConfig) -> None:
        """Called when plugin is loaded"""
        ...
    
    @abstractmethod
    async def execute(
        self, 
        capability: str, 
        params: Dict,
        context: ExecutionContext
    ) -> PluginResult:
        """Execute a capability"""
        ...

# 2. Middleware Extension Point
class MiddlewareInterface(Protocol):
    """Implement this to process requests/responses"""
    
    async def process_request(
        self, 
        request: Request, 
        context: RequestContext
    ) -> Request:
        ...
    
    async def process_response(
        self, 
        response: Response, 
        context: RequestContext
    ) -> Response:
        ...

# 3. Event Hook Extension Point
class EventHook(Protocol):
    """Implement this to react to events"""
    
    event_types: List[str]  # Which events to subscribe to
    
    async def handle(self, event: SystemEvent) -> None:
        ...

# 4. LLM Provider Extension Point
class LLMProvider(Protocol):
    """Implement this to add AI model support"""
    
    async def complete(self, prompt: str, options: Dict) -> str:
        ...
    
    async def parse_intent(self, prompt: str, context: Dict) -> IntentGraph:
        ...

# 5. A2UI Component Extension Point
class A2UIComponentRenderer(Protocol):
    """Implement this to add new UI components"""
    
    component_type: str  # e.g., "kanban_board"
    
    def validate_props(self, props: Dict) -> ValidationResult:
        ...
    
    def to_json(self, props: Dict) -> Dict:
        ...
4.3 Adding Features Without Touching Core
Python

# Example: Adding Slack Integration

# Step 1: Create Plugin (extensions/plugins/slack_plugin.py)
class SlackPlugin(PluginInterface):
    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            id="slack",
            name="Slack Integration",
            version="1.0.0",
            capabilities=[
                Capability(
                    id="slack.send_message",
                    description="Send a Slack message",
                    parameters=[
                        Param("channel", str, required=True),
                        Param("message", str, required=True)
                    ]
                ),
                Capability(
                    id="slack.list_channels",
                    description="List Slack channels"
                )
            ]
        )
    
    async def execute(self, capability: str, params: Dict, ctx: ExecutionContext):
        if capability == "slack.send_message":
            return await self._send_message(params, ctx)
        elif capability == "slack.list_channels":
            return await self._list_channels(ctx)

# Step 2: Register Plugin (extensions/registry.py)
PLUGINS = [
    SlackPlugin,
    # ... other plugins
]

# Step 3: No core changes needed!
# The plugin is automatically:
# - Discovered by PluginManager
# - Registered in CapabilityRegistry
# - Available for intent matching
# - Sandboxed for security
# - Metered for usage
5. Billing & Subscription System
5.1 Billing Architecture
text

┌─────────────────────────────────────────────────────────────────────────┐
│                        BILLING SUBSYSTEM                                │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    Stripe / Paddle                               │  │
│   │               (Payment Gateway)                                  │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                              ▲ │                                        │
│                    Webhooks  │ │ API Calls                             │
│                              │ ▼                                        │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                   Payment Gateway Adapter                        │  │
│   │   (Abstracts Stripe/Paddle - can switch providers)              │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│          ┌──────────────────┼──────────────────┐                       │
│          ▼                  ▼                  ▼                       │
│   ┌─────────────┐   ┌─────────────┐   ┌─────────────────────┐         │
│   │ Subscription│   │   Usage     │   │    Invoice          │         │
│   │   Service   │   │  Service    │   │    Service          │         │
│   └─────────────┘   └─────────────┘   └─────────────────────┘         │
│          │                  │                  │                       │
│          └──────────────────┼──────────────────┘                       │
│                             ▼                                          │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │                    Billing Database                              │  │
│   │   • subscriptions        • usage_events                         │  │
│   │   • invoices             • payment_methods                       │  │
│   │   • credits              • billing_history                       │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
5.2 Database Schema for Billing
SQL

-- Subscription Plans (Admin-managed)
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,           -- "Free", "Pro", "Enterprise"
    stripe_price_id VARCHAR(255),          -- Stripe price object ID
    
    -- Limits
    max_users INTEGER DEFAULT 5,
    max_workspaces INTEGER DEFAULT 1,
    max_plugins INTEGER DEFAULT 5,
    monthly_ai_credits INTEGER DEFAULT 500,
    monthly_emails INTEGER DEFAULT 1000,
    storage_gb INTEGER DEFAULT 5,
    
    -- Features (JSONB for flexibility)
    features JSONB DEFAULT '{}',
    -- Example: {"priority_support": false, "api_access": true, "custom_domain": false}
    
    price_monthly_cents INTEGER NOT NULL,
    price_yearly_cents INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Subscriptions (Per organization)
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id) NOT NULL,
    plan_id UUID REFERENCES subscription_plans(id) NOT NULL,
    
    status VARCHAR(50) NOT NULL,  -- active, past_due, cancelled, trialing
    
    -- Stripe references
    stripe_subscription_id VARCHAR(255) UNIQUE,
    stripe_customer_id VARCHAR(255),
    
    -- Billing cycle
    current_period_start TIMESTAMP NOT NULL,
    current_period_end TIMESTAMP NOT NULL,
    cancel_at_period_end BOOLEAN DEFAULT false,
    
    -- Trial
    trial_start TIMESTAMP,
    trial_end TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Usage Events (For metering)
CREATE TABLE usage_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id) NOT NULL,
    
    event_type VARCHAR(100) NOT NULL,  -- 'ai_request', 'email_sent', 'api_call'
    quantity INTEGER DEFAULT 1,
    
    -- Context
    user_id UUID REFERENCES users(id),
    plugin_id VARCHAR(100),
    capability_id VARCHAR(100),
    
    -- For aggregation
    timestamp TIMESTAMP DEFAULT NOW(),
    billing_period VARCHAR(7)  -- '2026-01' for monthly aggregation
);

-- Create index for fast aggregation
CREATE INDEX idx_usage_events_billing 
ON usage_events(org_id, event_type, billing_period);

-- Usage Aggregates (Pre-computed monthly totals)
CREATE TABLE usage_aggregates (
    org_id UUID REFERENCES organizations(id),
    billing_period VARCHAR(7),           -- '2026-01'
    event_type VARCHAR(100),
    total_quantity BIGINT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (org_id, billing_period, event_type)
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id) NOT NULL,
    
    stripe_invoice_id VARCHAR(255) UNIQUE,
    
    status VARCHAR(50) NOT NULL,  -- draft, open, paid, void, uncollectible
    
    -- Amounts (in cents)
    subtotal_cents INTEGER NOT NULL,
    tax_cents INTEGER DEFAULT 0,
    total_cents INTEGER NOT NULL,
    amount_paid_cents INTEGER DEFAULT 0,
    amount_due_cents INTEGER NOT NULL,
    
    -- PDF
    invoice_pdf_url TEXT,
    hosted_invoice_url TEXT,
    
    -- Period
    period_start TIMESTAMP NOT NULL,
    period_end TIMESTAMP NOT NULL,
    
    -- Line items
    line_items JSONB DEFAULT '[]',
    
    due_date TIMESTAMP,
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Credits (For overage or promotional credits)
CREATE TABLE credits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    org_id UUID REFERENCES organizations(id) NOT NULL,
    
    credit_type VARCHAR(50) NOT NULL,  -- 'ai_credits', 'promotional', 'refund'
    amount INTEGER NOT NULL,
    remaining INTEGER NOT NULL,
    
    description TEXT,
    expires_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);
5.3 Billing Service Implementation
Python

# billing/service.py

from stripe import StripeClient
from datetime import datetime, timedelta

class BillingService:
    def __init__(
        self, 
        stripe_client: StripeClient,
        usage_repo: UsageRepository,
        subscription_repo: SubscriptionRepository,
        invoice_repo: InvoiceRepository
    ):
        self.stripe = stripe_client
        self.usage = usage_repo
        self.subscriptions = subscription_repo
        self.invoices = invoice_repo
    
    # === Subscription Management ===
    
    async def create_subscription(
        self, 
        org_id: UUID, 
        plan_id: UUID,
        payment_method_id: str
    ) -> Subscription:
        """Create a new subscription for an organization"""
        
        org = await self.org_repo.get(org_id)
        plan = await self.plan_repo.get(plan_id)
        
        # Create Stripe customer if doesn't exist
        if not org.stripe_customer_id:
            customer = await self.stripe.customers.create(
                email=org.billing_email,
                name=org.name,
                metadata={"org_id": str(org_id)}
            )
            org.stripe_customer_id = customer.id
            await self.org_repo.update(org)
        
        # Attach payment method
        await self.stripe.payment_methods.attach(
            payment_method_id,
            customer=org.stripe_customer_id
        )
        
        # Create subscription
        stripe_sub = await self.stripe.subscriptions.create(
            customer=org.stripe_customer_id,
            items=[{"price": plan.stripe_price_id}],
            default_payment_method=payment_method_id,
            metadata={"org_id": str(org_id), "plan_id": str(plan_id)}
        )
        
        # Store locally
        subscription = Subscription(
            org_id=org_id,
            plan_id=plan_id,
            stripe_subscription_id=stripe_sub.id,
            stripe_customer_id=org.stripe_customer_id,
            status=stripe_sub.status,
            current_period_start=datetime.fromtimestamp(stripe_sub.current_period_start),
            current_period_end=datetime.fromtimestamp(stripe_sub.current_period_end)
        )
        
        await self.subscriptions.create(subscription)
        
        # Update org limits based on plan
        await self._apply_plan_limits(org_id, plan)
        
        return subscription
    
    async def change_plan(self, org_id: UUID, new_plan_id: UUID) -> Subscription:
        """Upgrade or downgrade subscription"""
        
        current_sub = await self.subscriptions.get_by_org(org_id)
        new_plan = await self.plan_repo.get(new_plan_id)
        
        # Prorate in Stripe
        stripe_sub = await self.stripe.subscriptions.update(
            current_sub.stripe_subscription_id,
            items=[{
                "id": current_sub.stripe_item_id,
                "price": new_plan.stripe_price_id
            }],
            proration_behavior="create_prorations"
        )
        
        # Update local
        current_sub.plan_id = new_plan_id
        current_sub.status = stripe_sub.status
        await self.subscriptions.update(current_sub)
        
        # Apply new limits
        await self._apply_plan_limits(org_id, new_plan)
        
        return current_sub
    
    async def cancel_subscription(
        self, 
        org_id: UUID, 
        at_period_end: bool = True
    ) -> Subscription:
        """Cancel subscription"""
        
        current_sub = await self.subscriptions.get_by_org(org_id)
        
        if at_period_end:
            # Cancel at end of billing period
            await self.stripe.subscriptions.update(
                current_sub.stripe_subscription_id,
                cancel_at_period_end=True
            )
            current_sub.cancel_at_period_end = True
        else:
            # Cancel immediately
            await self.stripe.subscriptions.cancel(
                current_sub.stripe_subscription_id
            )
            current_sub.status = "cancelled"
        
        await self.subscriptions.update(current_sub)
        return current_sub
    
    # === Usage Tracking ===
    
    async def record_usage(
        self, 
        org_id: UUID,
        event_type: str,
        quantity: int = 1,
        user_id: UUID = None,
        plugin_id: str = None
    ):
        """Record a usage event"""
        
        event = UsageEvent(
            org_id=org_id,
            event_type=event_type,
            quantity=quantity,
            user_id=user_id,
            plugin_id=plugin_id,
            timestamp=datetime.utcnow(),
            billing_period=datetime.utcnow().strftime("%Y-%m")
        )
        
        await self.usage.record(event)
        
        # Check if approaching limits
        await self._check_usage_limits(org_id, event_type)
    
    async def get_usage_summary(
        self, 
        org_id: UUID, 
        period: str = None
    ) -> UsageSummary:
        """Get usage summary for billing period"""
        
        if not period:
            period = datetime.utcnow().strftime("%Y-%m")
        
        subscription = await self.subscriptions.get_by_org(org_id)
        plan = await self.plan_repo.get(subscription.plan_id)
        
        aggregates = await self.usage.get_aggregates(org_id, period)
        
        return UsageSummary(
            period=period,
            usage={
                "ai_requests": {
                    "used": aggregates.get("ai_request", 0),
                    "limit": plan.monthly_ai_credits,
                    "percentage": aggregates.get("ai_request", 0) / plan.monthly_ai_credits * 100
                },
                "emails_sent": {
                    "used": aggregates.get("email_sent", 0),
                    "limit": plan.monthly_emails,
                    "percentage": aggregates.get("email_sent", 0) / plan.monthly_emails * 100
                },
                # ... more metrics
            }
        )
    
    # === Invoice Management ===
    
    async def get_invoices(
        self, 
        org_id: UUID, 
        limit: int = 12
    ) -> List[Invoice]:
        """Get invoices for organization"""
        return await self.invoices.list_by_org(org_id, limit)
    
    async def get_invoice_pdf(self, invoice_id: UUID) -> str:
        """Get invoice PDF URL"""
        invoice = await self.invoices.get(invoice_id)
        return invoice.invoice_pdf_url
    
    # === Webhook Handlers ===
    
    async def handle_stripe_webhook(self, event: Dict):
        """Process Stripe webhook events"""
        
        event_type = event["type"]
        data = event["data"]["object"]
        
        handlers = {
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "invoice.paid": self._handle_invoice_paid,
            "invoice.payment_failed": self._handle_payment_failed,
            "customer.subscription.trial_will_end": self._handle_trial_ending,
        }
        
        handler = handlers.get(event_type)
        if handler:
            await handler(data)
    
    async def _handle_invoice_paid(self, invoice_data: Dict):
        """Handle successful payment"""
        
        org_id = UUID(invoice_data["metadata"]["org_id"])
        
        # Store invoice
        invoice = Invoice(
            org_id=org_id,
            stripe_invoice_id=invoice_data["id"],
            status="paid",
            total_cents=invoice_data["total"],
            invoice_pdf_url=invoice_data["invoice_pdf"],
            period_start=datetime.fromtimestamp(invoice_data["period_start"]),
            period_end=datetime.fromtimestamp(invoice_data["period_end"]),
            paid_at=datetime.utcnow()
        )
        
        await self.invoices.create(invoice)
        
        # Send receipt email
        await self.email_service.send_receipt(org_id, invoice)
5.4 Usage Metering Middleware
Python

# core/middleware/usage_metering.py

class UsageMeteringMiddleware:
    """Automatically track usage for billing"""
    
    def __init__(self, billing_service: BillingService):
        self.billing = billing_service
    
    async def process_request(
        self, 
        request: Request, 
        context: RequestContext
    ) -> Request:
        # Mark request start time for duration tracking
        context.start_time = time.time()
        return request
    
    async def process_response(
        self, 
        response: Response, 
        context: RequestContext
    ) -> Response:
        # Skip if no tenant context
        if not context.tenant:
            return response
        
        # Track based on endpoint
        await self._track_usage(context, response)
        
        return response
    
    async def _track_usage(self, context: RequestContext, response: Response):
        """Track usage based on what was done"""
        
        # Track AI requests
        if context.used_ai:
            await self.billing.record_usage(
                org_id=context.tenant.org_id,
                event_type="ai_request",
                quantity=context.ai_tokens_used,
                user_id=context.user.id
            )
        
        # Track plugin executions
        for plugin_id in context.plugins_executed:
            await self.billing.record_usage(
                org_id=context.tenant.org_id,
                event_type="plugin_execution",
                plugin_id=plugin_id,
                user_id=context.user.id
            )
        
        # Track API calls
        await self.billing.record_usage(
            org_id=context.tenant.org_id,
            event_type="api_call",
            user_id=context.user.id
        )
5.5 Plan Feature Gates
Python

# core/feature_gates.py

class FeatureGate:
    """Check if org can use a feature based on plan"""
    
    def __init__(self, subscription_repo: SubscriptionRepository):
        self.subscriptions = subscription_repo
    
    async def can_use(
        self, 
        org_id: UUID, 
        feature: str
    ) -> tuple[bool, str]:
        """Check if feature is allowed"""
        
        subscription = await self.subscriptions.get_by_org(org_id)
        plan = await self.plan_repo.get(subscription.plan_id)
        
        # Check feature flags
        if feature in plan.features:
            return plan.features[feature], ""
        
        return False, f"Feature '{feature}' not available in {plan.name} plan"
    
    async def check_limit(
        self, 
        org_id: UUID, 
        limit_type: str
    ) -> tuple[bool, int, int]:
        """Check if within limits"""
        
        subscription = await self.subscriptions.get_by_org(org_id)
        plan = await self.plan_repo.get(subscription.plan_id)
        
        current_usage = await self.billing.get_current_usage(org_id, limit_type)
        
        limits = {
            "users": plan.max_users,
            "workspaces": plan.max_workspaces,
            "plugins": plan.max_plugins,
            "ai_credits": plan.monthly_ai_credits,
            "emails": plan.monthly_emails,
        }
        
        limit = limits.get(limit_type, float("inf"))
        within_limit = current_usage < limit
        
        return within_limit, current_usage, limit

# Usage in API
@router.post("/api/ai/complete")
async def ai_complete(request: AIRequest, ctx: RequestContext = Depends()):
    # Check AI credit limit
    within_limit, used, limit = await feature_gate.check_limit(
        ctx.tenant.org_id, 
        "ai_credits"
    )
    
    if not within_limit:
        raise HTTPException(
            status_code=402,
            detail={
                "error": "AI_CREDITS_EXHAUSTED",
                "message": f"You've used {used}/{limit} AI credits this month",
                "upgrade_url": "/settings/billing/upgrade"
            }
        )
    
    # Proceed with AI request
    result = await ai_service.complete(request)
    return result
6. UI/UX Redefinition
6.1 Current UI Assessment
Aspect	Current State	Issue
Responsiveness	Not mentioned	❌ No mobile support
Accessibility	Not mentioned	❌ No a11y
Internationalization	Not mentioned	❌ English only
Offline Support	None	❌ Requires connection
State Management	React Context	⚠️ May not scale
Error States	Basic	⚠️ Need improvement
6.2 Enhanced Design System
text

DHII DESIGN SYSTEM 2.0

┌─────────────────────────────────────────────────────────────────────────┐
│                         DESIGN TOKENS                                   │
│                                                                         │
│   Colors (with semantic naming)                                         │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  --color-bg-primary      : #0A0E17   (Dark base)               │  │
│   │  --color-bg-secondary    : #141B2D   (Card backgrounds)         │  │
│   │  --color-bg-tertiary     : #1E2738   (Elevated surfaces)        │  │
│   │                                                                   │  │
│   │  --color-text-primary    : #FFFFFF   (Headings)                  │  │
│   │  --color-text-secondary  : #A0AEC0   (Body text)                 │  │
│   │  --color-text-muted      : #64748B   (Hints, placeholders)       │  │
│   │                                                                   │  │
│   │  --color-accent-blue     : #3B82F6   (Primary actions)           │  │
│   │  --color-accent-green    : #10B981   (Success states)            │  │
│   │  --color-accent-yellow   : #F59E0B   (Warnings)                  │  │
│   │  --color-accent-red      : #EF4444   (Errors, destructive)       │  │
│   │                                                                   │  │
│   │  --color-glass-bg        : rgba(255,255,255,0.05)               │  │
│   │  --color-glass-border    : rgba(255,255,255,0.1)                │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   Typography (Fluid scale)                                              │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  --font-family-sans      : 'Inter', -apple-system, sans-serif   │  │
│   │  --font-family-mono      : 'JetBrains Mono', monospace          │  │
│   │                                                                   │  │
│   │  --font-size-xs          : clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem)  │
│   │  --font-size-sm          : clamp(0.875rem, 0.8rem + 0.3vw, 1rem)      │
│   │  --font-size-base        : clamp(1rem, 0.9rem + 0.4vw, 1.125rem)      │
│   │  --font-size-lg          : clamp(1.125rem, 1rem + 0.5vw, 1.25rem)     │
│   │  --font-size-xl          : clamp(1.25rem, 1.1rem + 0.6vw, 1.5rem)     │
│   │  --font-size-2xl         : clamp(1.5rem, 1.3rem + 0.8vw, 2rem)        │
│   │  --font-size-3xl         : clamp(2rem, 1.6rem + 1.2vw, 2.5rem)        │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   Spacing (8px grid)                                                    │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  --space-1  : 0.25rem (4px)    --space-6  : 1.5rem (24px)       │  │
│   │  --space-2  : 0.5rem  (8px)    --space-8  : 2rem   (32px)       │  │
│   │  --space-3  : 0.75rem (12px)   --space-10 : 2.5rem (40px)       │  │
│   │  --space-4  : 1rem    (16px)   --space-12 : 3rem   (48px)       │  │
│   │  --space-5  : 1.25rem (20px)   --space-16 : 4rem   (64px)       │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   Shadows & Effects                                                     │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  --shadow-sm   : 0 1px 2px rgba(0,0,0,0.1)                      │  │
│   │  --shadow-md   : 0 4px 12px rgba(0,0,0,0.15)                    │  │
│   │  --shadow-lg   : 0 10px 40px rgba(0,0,0,0.2)                    │  │
│   │  --shadow-glow : 0 0 20px rgba(59,130,246,0.3)                  │  │
│   │                                                                   │  │
│   │  --blur-sm     : blur(8px)                                       │  │
│   │  --blur-md     : blur(16px)                                      │  │
│   │  --blur-lg     : blur(24px)                                      │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│   Motion (Reduced motion support)                                       │
│   ┌─────────────────────────────────────────────────────────────────┐  │
│   │  --duration-fast   : 150ms                                       │  │
│   │  --duration-normal : 250ms                                       │  │
│   │  --duration-slow   : 400ms                                       │  │
│   │                                                                   │  │
│   │  --ease-out   : cubic-bezier(0, 0, 0.2, 1)                       │  │
│   │  --ease-in    : cubic-bezier(0.4, 0, 1, 1)                       │  │
│   │  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275)         │  │
│   │                                                                   │  │
│   │  @media (prefers-reduced-motion: reduce) {                       │  │
│   │    --duration-fast   : 0ms;                                      │  │
│   │    --duration-normal : 0ms;                                      │  │
│   │  }                                                               │  │
│   └─────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
6.3 Responsive Layout System
React

// components/layout/ResponsiveShell.tsx

interface BreakpointConfig {
  mobile: number;    // 0-639
  tablet: number;    // 640-1023
  desktop: number;   // 1024-1279
  wide: number;      // 1280+
}

const BREAKPOINTS: BreakpointConfig = {
  mobile: 0,
  tablet: 640,
  desktop: 1024,
  wide: 1280,
};

// Responsive Layout Modes
type LayoutMode = 
  | 'mobile-stack'      // Single column, bottom nav
  | 'tablet-split'      // Side drawer, main content
  | 'desktop-full'      // Full ribbon + canvas + panels
  | 'wide-expanded';    // Extra columns for power users

export function ResponsiveShell({ children }: PropsWithChildren) {
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('desktop-full');
  
  useEffect(() => {
    const updateLayout = () => {
      const width = window.innerWidth;
      if (width < BREAKPOINTS.tablet) setLayoutMode('mobile-stack');
      else if (width < BREAKPOINTS.desktop) setLayoutMode('tablet-split');
      else if (width < BREAKPOINTS.wide) setLayoutMode('desktop-full');
      else setLayoutMode('wide-expanded');
    };
    
    updateLayout();
    window.addEventListener('resize', updateLayout);
    return () => window.removeEventListener('resize', updateLayout);
  }, []);
  
  return (
    <LayoutContext.Provider value={{ mode: layoutMode }}>
      <div className={`shell shell--${layoutMode}`}>
        {layoutMode === 'mobile-stack' ? (
          <MobileLayout>{children}</MobileLayout>
        ) : layoutMode === 'tablet-split' ? (
          <TabletLayout>{children}</TabletLayout>
        ) : (
          <DesktopLayout>{children}</DesktopLayout>
        )}
      </div>
    </LayoutContext.Provider>
  );
}

// Mobile Layout: Chat-first, bottom nav
function MobileLayout({ children }) {
  return (
    <div className="mobile-layout">
      <header className="mobile-header">
        <Logo size="sm" />
        <button className="hamburger" aria-label="Menu">
          <MenuIcon />
        </button>
      </header>
      
      <main className="mobile-main">
        {children}
      </main>
      
      <nav className="mobile-nav" role="navigation" aria-label="Main">
        <NavItem icon={<HomeIcon />} label="Home" href="/" />
        <NavItem icon={<MailIcon />} label="Mail" href="/mail" />
        <NavItem icon={<CalendarIcon />} label="Calendar" href="/calendar" />
        <NavItem icon={<PlugIcon />} label="Plugins" href="/plugins" />
      </nav>
      
      {/* Floating chat input */}
      <div className="mobile-prompt">
        <PromptBar compact />
      </div>
    </div>
  );
}
6.4 Accessibility (a11y) Implementation
React

// components/ui/AccessibleCard.tsx

interface AccessibleCardProps {
  title: string;
  description?: string;
  actions?: CardAction[];
  children: ReactNode;
}

export function AccessibleCard({ 
  title, 
  description, 
  actions,
  children 
}: AccessibleCardProps) {
  const titleId = useId();
  const descId = useId();
  
  return (
    <article
      role="region"
      aria-labelledby={titleId}
      aria-describedby={description ? descId : undefined}
      className="card"
    >
      <header className="card-header">
        <h2 id={titleId} className="card-title">
          {title}
        </h2>
        {description && (
          <p id={descId} className="card-description">
            {description}
          </p>
        )}
      </header>
      
      <div className="card-content" role="group">
        {children}
      </div>
      
      {actions && (
        <footer className="card-actions" role="group" aria-label="Card actions">
          {actions.map((action, i) => (
            <Button
              key={i}
              onClick={action.onClick}
              variant={action.variant}
              aria-label={action.ariaLabel || action.label}
            >
              {action.icon && <span aria-hidden="true">{action.icon}</span>}
              {action.label}
            </Button>
          ))}
        </footer>
      )}
    </article>
  );
}

// Keyboard Navigation for Lists
export function AccessibleList<T>({ 
  items, 
  renderItem,
  onSelect 
}: AccessibleListProps<T>) {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const listRef = useRef<HTMLUListElement>(null);
  
  const handleKeyDown = (e: KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setFocusedIndex(i => Math.min(i + 1, items.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setFocusedIndex(i => Math.max(i - 1, 0));
        break;
      case 'Enter':
      case ' ':
        e.preventDefault();
        onSelect?.(items[focusedIndex]);
        break;
      case 'Home':
        e.preventDefault();
        setFocusedIndex(0);
        break;
      case 'End':
        e.preventDefault();
        setFocusedIndex(items.length - 1);
        break;
    }
  };
  
  return (
    <ul
      ref={listRef}
      role="listbox"
      tabIndex={0}
      onKeyDown={handleKeyDown}
      aria-activedescendant={`item-${focusedIndex}`}
      className="accessible-list"
    >
      {items.map((item, i) => (
        <li
          key={i}
          id={`item-${i}`}
          role="option"
          aria-selected={focusedIndex === i}
          className={focusedIndex === i ? 'focused' : ''}
          onClick={() => {
            setFocusedIndex(i);
            onSelect?.(item);
          }}
        >
          {renderItem(item, i)}
        </li>
      ))}
    </ul>
  );
}

// Screen Reader Announcements for Dynamic Content
export function useLiveAnnouncement() {
  const announce = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    const el = document.createElement('div');
    el.setAttribute('role', 'status');
    el.setAttribute('aria-live', priority);
    el.setAttribute('aria-atomic', 'true');
    el.className = 'sr-only';
    el.textContent = message;
    
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1000);
  }, []);
  
  return announce;
}

// Usage in Stream Component
function StreamingContent({ chunks }) {
  const announce = useLiveAnnouncement();
  
  useEffect(() => {
    if (chunks.length > 0) {
      const lastChunk = chunks[chunks.length - 1];
      if (lastChunk.type === 'display') {
        announce(`Loaded: ${lastChunk.component_type}`);
      }
    }
  }, [chunks, announce]);
  
  // ... render
}
6.5 State Management Upgrade (Zustand)
React

// stores/appStore.ts
import { create } from 'zustand';
import { devtools, persist, subscribeWithSelector } from 'zustand/middleware';

interface AppState {
  // User & Auth
  user: User | null;
  tenant: Tenant | null;
  
  // UI State
  sidebarOpen: boolean;
  activeView: string;
  theme: 'light' | 'dark' | 'system';
  
  // Streaming
  activeStream: StreamState | null;
  streamHistory: StreamChunk[];
  
  // Actions
  setUser: (user: User | null) => void;
  toggleSidebar: () => void;
  setActiveView: (view: string) => void;
  appendStreamChunk: (chunk: StreamChunk) => void;
  clearStream: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    persist(
      subscribeWithSelector((set, get) => ({
        // Initial state
        user: null,
        tenant: null,
        sidebarOpen: true,
        activeView: 'home',
        theme: 'dark',
        activeStream: null,
        streamHistory: [],
        
        // Actions
        setUser: (user) => set({ user }),
        
        toggleSidebar: () => set((state) => ({ 
          sidebarOpen: !state.sidebarOpen 
        })),
        
        setActiveView: (view) => set({ activeView: view }),
        
        appendStreamChunk: (chunk) => set((state) => ({
          streamHistory: [...state.streamHistory, chunk]
        })),
        
        clearStream: () => set({ 
          activeStream: null, 
          streamHistory: [] 
        }),
      })),
      {
        name: 'dhii-app-state',
        partialize: (state) => ({ 
          theme: state.theme,
          sidebarOpen: state.sidebarOpen 
        }),
      }
    ),
    { name: 'DhiiStore' }
  )
);

// Plugin Store (Separate concern)
interface PluginState {
  plugins: PluginInfo[];
  installedIds: Set<string>;
  loading: boolean;
  
  fetchPlugins: () => Promise<void>;
  installPlugin: (id: string) => Promise<void>;
  uninstallPlugin: (id: string) => Promise<void>;
}

export const usePluginStore = create<PluginState>()(
  devtools((set, get) => ({
    plugins: [],
    installedIds: new Set(),
    loading: false,
    
    fetchPlugins: async () => {
      set({ loading: true });
      const plugins = await api.getPlugins();
      set({ 
        plugins, 
        installedIds: new Set(plugins.filter(p => p.installed).map(p => p.id)),
        loading: false 
      });
    },
    
    installPlugin: async (id) => {
      await api.installPlugin(id);
      set((state) => ({
        installedIds: new Set([...state.installedIds, id])
      }));
    },
    
    uninstallPlugin: async (id) => {
      await api.uninstallPlugin(id);
      set((state) => {
        const newSet = new Set(state.installedIds);
        newSet.delete(id);
        return { installedIds: newSet };
      });
    },
  }))
);
6.6 Enhanced A2UI Components
React

// components/a2ui/EnhancedComponents.tsx

// Skeleton with shimmer animation
export function SkeletonCard({ lines = 3, avatar = false }) {
  return (
    <div className="skeleton-card" role="status" aria-label="Loading">
      {avatar && <div className="skeleton-avatar skeleton-shimmer" />}
      <div className="skeleton-content">
        {Array.from({ length: lines }).map((_, i) => (
          <div 
            key={i} 
            className="skeleton-line skeleton-shimmer"
            style={{ 
              width: `${Math.random() * 40 + 60}%`,
              animationDelay: `${i * 100}ms`
            }}
          />
        ))}
      </div>
    </div>
  );
}

// Error Card with recovery options
export function ErrorCard({ 
  error, 
  onRetry, 
  fallback 
}: ErrorCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  
  return (
    <div 
      className="error-card" 
      role="alert" 
      aria-live="assertive"
    >
      <div className="error-icon">
        <AlertTriangleIcon aria-hidden="true" />
      </div>
      
      <div className="error-content">
        <h3 className="error-title">Something went wrong</h3>
        <p className="error-message">{error.message}</p>
        
        {showDetails && (
          <pre className="error-details">
            <code>{JSON.stringify(error.details, null, 2)}</code>
          </pre>
        )}
      </div>
      
      <div className="error-actions">
        <Button onClick={onRetry} variant="primary">
          <RefreshIcon /> Retry
        </Button>
        <Button 
          onClick={() => setShowDetails(!showDetails)} 
          variant="ghost"
        >
          {showDetails ? 'Hide' : 'Show'} Details
        </Button>
      </div>
      
      {fallback && (
        <div className="error-fallback">
          <p className="fallback-label">While we fix this:</p>
          {fallback}
        </div>
      )}
    </div>
  );
}

// Aggregated Card with tabs
export function AggregatedCard({ sources, sections }: AggregatedCardProps) {
  const [activeTab, setActiveTab] = useState(0);
  
  return (
    <div className="aggregated-card">
      <div className="card-tabs" role="tablist">
        {sources.map((source, i) => (
          <button
            key={source.id}
            role="tab"
            aria-selected={activeTab === i}
            aria-controls={`panel-${source.id}`}
            onClick={() => setActiveTab(i)}
            className={`tab ${activeTab === i ? 'active' : ''}`}
          >
            <PluginIcon pluginId={source.id} />
            {source.name}
            {source.loading && <Spinner size="sm" />}
          </button>
        ))}
      </div>
      
      <div className="card-panels">
        {sections.map((section, i) => (
          <div
            key={section.source}
            id={`panel-${section.source}`}
            role="tabpanel"
            hidden={activeTab !== i}
            aria-labelledby={`tab-${section.source}`}
          >
            <A2UIRenderer component={section.component} />
          </div>
        ))}
      </div>
    </div>
  );
}
7. Future Roadmap
7.1 Feature Phases
text

PHASE 1: SaaS Foundation (Weeks 1-6)
════════════════════════════════════════════════════════════════════

  Week 1-2: Multi-tenancy
  ├── PostgreSQL migration from SQLite
  ├── Tenant isolation (RLS)
  ├── Organization/Workspace model
  └── User roles (RBAC)

  Week 3-4: Billing Core
  ├── Stripe integration
  ├── Subscription CRUD
  ├── Usage metering
  └── Invoice generation

  Week 5-6: Core Decoupling
  ├── Split Symphony Orchestrator
  ├── Extract IntentEngine
  ├── Extract CapabilityRouter
  └── Extract PluginExecutor


PHASE 2: Enterprise Features (Weeks 7-12)
════════════════════════════════════════════════════════════════════

  Week 7-8: Security Hardening
  ├── OAuth2 (Google, Microsoft)
  ├── SSO (SAML 2.0)
  ├── API key management
  └── Audit logging

  Week 9-10: Admin Dashboard
  ├── Tenant management
  ├── Usage analytics
  ├── System health monitoring
  └── Plugin marketplace admin

  Week 11-12: Developer Experience
  ├── Plugin SDK refinement
  ├── CLI tools enhancement
  ├── Documentation portal
  └── API versioning (v1)


PHASE 3: Scale & Polish (Weeks 13-18)
════════════════════════════════════════════════════════════════════

  Week 13-14: Performance
  ├── Redis caching layer
  ├── Query optimization
  ├── CDN for static assets
  └── Connection pooling

  Week 15-16: UI/UX Overhaul
  ├── Responsive redesign
  ├── Accessibility audit
  ├── Mobile web optimization
  └── Dark/light themes

  Week 17-18: Reliability
  ├── Error monitoring (Sentry)
  ├── Distributed tracing
  ├── Graceful degradation
  └── Disaster recovery


PHASE 4: Growth Features (Weeks 19-24)
════════════════════════════════════════════════════════════════════

  Week 19-20: Collaboration
  ├── Shared workspaces
  ├── Real-time presence
  ├── Comments/mentions
  └── Activity feed

  Week 21-22: Automation
  ├── Workflow builder UI
  ├── Trigger library
  ├── Action marketplace
  └── Scheduling engine

  Week 23-24: Intelligence
  ├── Custom AI training
  ├── Personalization engine
  ├── Predictive suggestions
  └── Cross-plugin insights
7.2 Technical Debt Items
Item	Current State	Target State	Priority
SQLite → PostgreSQL	Multiple .db files	Single managed DB	🔴 P0
God Object Orchestrator	Single class, 200+ lines	5 focused services	🔴 P0
No test coverage	Ad-hoc testing	80%+ coverage	🟠 P1
Hardcoded config	Values in code	Environment-based	🟠 P1
No API versioning	Single version	/v1/, /v2/	🟠 P1
Missing error boundaries	Errors crash app	Graceful recovery	🟡 P2
No caching	Direct DB queries	Redis cache layer	🟡 P2
Sync IMAP polling	5-min intervals	Webhooks + IDLE	🟡 P2
7.3 New Plugin Ideas
text

NEAR-TERM (3-6 months)
┌────────────────────────────────────────────────────────────────────────┐
│  Analytics Plugin                                                       │
│  ├── Personal productivity metrics                                      │
│  ├── Email response time tracking                                       │
│  └── Meeting load analysis                                              │
│                                                                         │
│  Notion/Obsidian Bridge                                                │
│  ├── Sync notes bidirectionally                                         │
│  ├── Link emails to notes                                               │
│  └── Meeting notes auto-capture                                         │
│                                                                         │
│  AI Writing Assistant (Enhanced)                                        │
│  ├── Email reply suggestions                                            │
│  ├── Tone adjustment                                                    │
│  └── Template library                                                   │
└────────────────────────────────────────────────────────────────────────┘

MID-TERM (6-12 months)
┌────────────────────────────────────────────────────────────────────────┐
│  Workflow Automation                                                    │
│  ├── Visual workflow builder                                            │
│  ├── Trigger library (email received, deal stage changed, etc.)         │
│  └── Action library (send email, create task, update CRM)               │
│                                                                         │
│  Voice Interface                                                        │
│  ├── Voice commands                                                     │
│  ├── Voice notes transcription                                          │
│  └── Meeting transcription                                              │
│                                                                         │
│  Custom Integrations Builder                                            │
│  ├── No-code API connector                                              │
│  ├── Webhook receiver                                                   │
│  └── Data transformation                                                │
└────────────────────────────────────────────────────────────────────────┘

LONG-TERM (12+ months)
┌────────────────────────────────────────────────────────────────────────┐
│  Mobile Native Apps                                                     │
│  ├── iOS app                                                            │
│  ├── Android app                                                        │
│  └── Offline sync                                                       │
│                                                                         │
│  AI Agent Mode                                                          │
│  ├── Autonomous task execution                                          │
│  ├── Multi-step reasoning                                               │
│  └── Human-in-the-loop approval                                         │
│                                                                         │
│  Enterprise Suite                                                       │
│  ├── Team analytics                                                     │
│  ├── Compliance dashboards                                              │
│  └── Custom LLM deployment                                              │
└────────────────────────────────────────────────────────────────────────┘
8. Implementation Phases
8.1 Immediate Actions (This Week)
Bash

# 1. Set up PostgreSQL
docker run -d --name dhii-postgres \
  -e POSTGRES_DB=dhii \
  -e POSTGRES_USER=dhii \
  -e POSTGRES_PASSWORD=secure_password \
  -p 5432:5432 \
  postgres:16

# 2. Create migration script
# migrations/001_initial_schema.sql
# (Include all tenant-aware tables)

# 3. Update requirements.txt
echo "psycopg2-binary==2.9.9" >> requirements.txt
echo "stripe==7.0.0" >> requirements.txt
echo "redis==5.0.0" >> requirements.txt

# 4. Create .env.example
cat > .env.example << EOF
DATABASE_URL=postgresql://dhii:password@localhost:5432/dhii
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
EOF
8.2 Directory Structure (Target)
text

dhii-mail/
├── core/                          # NEVER TOUCH FOR FEATURES
│   ├── kernel/
│   │   ├── __init__.py
│   │   ├── orchestrator.py        # Thin coordinator
│   │   ├── intent_engine.py       # NLU
│   │   ├── capability_router.py   # Routing
│   │   ├── plugin_executor.py     # Sandboxed execution
│   │   └── stream_manager.py      # SSE delivery
│   ├── contracts/
│   │   ├── plugin.py              # PluginInterface
│   │   ├── repository.py          # DataRepository
│   │   ├── llm.py                 # LLMProvider
│   │   └── a2ui.py                # Component schemas
│   ├── auth/
│   │   ├── jwt.py
│   │   ├── oauth.py
│   │   └── rbac.py
│   ├── tenant/
│   │   ├── context.py
│   │   ├── isolation.py
│   │   └── limits.py
│   └── events/
│       ├── bus.py
│       └── types.py
│
├── extensions/                     # ALL FEATURES LIVE HERE
│   ├── plugins/
│   │   ├── email/
│   │   ├── calendar/
│   │   ├── crm/
│   │   ├── meeting/
│   │   ├── slack/                 # New plugin = new folder
│   │   └── billing/               # Even billing is a plugin!
│   ├── middleware/
│   │   ├── usage_metering.py
│   │   ├── audit_log.py
│   │   └── feature_flags.py
│   └── hooks/
│       ├── on_email_received.py
│       └── on_subscription_changed.py
│
├── billing/                        # Billing subsystem
│   ├── service.py
│   ├── stripe_adapter.py
│   ├── usage.py
│   └── invoices.py
│
├── api/                            # HTTP Layer
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   ├── plugins.py
│   │   ├── billing.py
│   │   └── admin.py
│   └── middleware/
│       ├── auth.py
│       ├── tenant.py
│       └── rate_limit.py
│
├── client/                         # Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── a2ui/              # A2UI renderers
│   │   │   ├── ui/                # Design system
│   │   │   └── layout/            # Responsive layouts
│   │   ├── stores/                # Zustand stores
│   │   ├── hooks/                 # Custom hooks
│   │   ├── lib/                   # Utilities
│   │   └── pages/                 # Route pages
│   └── public/
│
├── migrations/                     # Database migrations
│   ├── 001_initial_schema.sql
│   └── 002_billing_tables.sql
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.client
│   └── docker-compose.yml
│
├── docs/
│   ├── architecture.md
│   ├── plugin-sdk.md
│   └── api-reference.md
│
└── scripts/
    ├── migrate.py
    ├── seed.py
    └── dev.sh
Summary: Key Takeaways
What to Do Now
Migrate to PostgreSQL — SQLite won't scale for SaaS
Split the Symphony Orchestrator — It's a god object
Add tenant isolation — Every query needs WHERE org_id = ?
Integrate Stripe — Start with simple subscription flow
What to Protect
A2UI Protocol — It's brilliant, don't change it
Plugin Capability Model — Clean contract, keep it
SSE Streaming — Right architectural choice
Design Token System — Solid foundation
What to Add
Billing Subsystem — Full Stripe integration
Usage Metering — Track everything, bill accordingly
Admin Dashboard — Tenant management, analytics
Responsive UI — Mobile-first redesign