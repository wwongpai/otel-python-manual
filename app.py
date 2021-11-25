#!/usr/bin/env python3
from opentelemetry import trace,baggage
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import os


resource = Resource(attributes={
    "service.name": os.getenv('OTEL_SERVICE_NAME')
})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("ww-python-manual", "1.0.0")
otlp_exporter = OTLPSpanExporter(endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT'), insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# first trace
with tracer.start_as_current_span("parent", kind=trace.SpanKind.SERVER) as span:
    if span.is_recording():
        span.set_attribute("key1", "ABC")
        span.set_attributes({"key2": 123, "key3": [1, 2, 3]})

        span.add_event(
            "log",
            {
                "log.severity": "error",
                "log.message": "User not found",
                "enduser.id": "123",
            },
        )

    try:
        raise ValueError("hello! there's an error")
    except ValueError as err:
        span.record_exception(err)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(err)))

# second trace
with tracer.start_as_current_span("parent") as parent:
    span.set_attribute("key4", 4)
    if trace.get_current_span() == parent:
        print("parent is active")

    with tracer.start_as_current_span("child") as child:
        span.set_attribute("key1", 1)
        if trace.get_current_span() == child:
            print("child is active")

    if trace.get_current_span() == parent:
        print("parent is active again")


# third trace
third = tracer.start_span("parent", kind=trace.SpanKind.CLIENT)

with trace.use_span(third, end_on_exit=True):
    if trace.get_current_span() == third:
        print("third is active (manually)")
