#!/usr/bin/env python3
from flask import Flask, make_response, request
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


app = Flask(__name__)
   
@app.route('/echo', methods=['GET', 'POST'])
def echo():
	data = request.get_json()
	trace_id_str = data['traceid']
	carrier = {'traceparent': trace_id_str}
	ctx = TraceContextTextMapPropagator().extract(carrier=carrier)
	with tracer.start_as_current_span("next-span", ctx) as span:
		if request.method == 'POST':
			print('You posted ')
			return(request.data)
		else:
			print('You getted ')
			return(request.data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
