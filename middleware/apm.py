
import logging
import os
from fastapi import FastAPI

logger = logging.getLogger(__name__)

def setup_apm(app: FastAPI):
    """
    Setup OpenTelemetry APM instrumentation.
    Gracefully handles missing dependencies.
    """
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        
        # Check if we should enable OTLP exporter
        use_otlp = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT")
        
        resource = Resource.create({
            "service.name": "dhii-mail-backend",
            "service.version": "0.1.0",
            "deployment.environment": os.environ.get("ENVIRONMENT", "development")
        })

        provider = TracerProvider(resource=resource)
        
        if use_otlp:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                processor = BatchSpanProcessor(OTLPSpanExporter())
                provider.add_span_processor(processor)
                logger.info("APM: Configured OTLP exporter")
            except ImportError:
                logger.warning("APM: OTLP exporter requested but opentelemetry-exporter-otlp not installed. Falling back to console.")
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        else:
            # Default to console exporter for development if explicitly enabled or in debug mode
            # But usually we don't want to spam console unless requested
            if os.environ.get("ENABLE_CONSOLE_TRACING", "false").lower() == "true":
                provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
                logger.info("APM: Configured Console exporter")
            else:
                # Set a no-op or just don't add a processor? 
                # If we don't add a processor, traces are generated but dropped.
                pass

        trace.set_tracer_provider(provider)
        
        # Instrument FastAPI
        # excluded_urls allows skipping health checks and metrics from traces
        FastAPIInstrumentor.instrument_app(
            app, 
            tracer_provider=provider,
            excluded_urls="health,metrics,docs,openapi.json"
        )
        
        logger.info("APM: OpenTelemetry instrumentation enabled")
        
    except ImportError as e:
        logger.warning(f"APM: OpenTelemetry dependencies not found. APM disabled. Error: {e}")
    except Exception as e:
        logger.error(f"APM: Failed to initialize OpenTelemetry: {e}")
