#!/usr/bin/env python3
import requests
from time import sleep
from random import random, seed
from opentelemetry import trace,baggage
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator
import os


resource = Resource(attributes={
    "service.name": os.getenv('OTEL_SERVICE_NAME'),
    "deployment.environment": "ww-prod"
})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer("ww-python-manual", "1.0.0")
otlp_exporter = OTLPSpanExporter(endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT'), insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

prop = TraceContextTextMapPropagator()
carrier = {}

seed(1)
url = 'http://localhost:6000/echo'
x=1

def pythonrequests():
    payload = {'key': 'value'}
    with tracer.start_as_current_span("first-span") as span:
        prop.inject(carrier=carrier)
        print("Carrier after injecting span context", carrier)
        try:
            r=requests.post(url, params=payload)
            print('posting: ', r.url, ' ', r.text)
        except requests.exceptions.RequestException as err:
            print(err)

while x:
    pythonrequests()
    y = random()
    print('Sleeping: ', round(y,2))
    sleep(round(y,2))
