from fastapi import FastAPI, HTTPException
import psycopg2, os
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

app = FastAPI()

# Traces vers Tempo via OTel Collector
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(
        endpoint="http://otel-collector:4317", insecure=True
    ))
)
FastAPIInstrumentor().instrument_app(app, tracer_provider=tracer_provider)

# Métriques Prometheus sur /metrics
Instrumentator().instrument(app).expose(app)

DB_URL = os.getenv("DATABASE_URL", "postgresql://user:pwd@postgres:5432/demo")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/items")
def get_items():
    conn = psycopg2.connect(DB_URL)
    cur  = conn.cursor()
    cur.execute("SELECT name FROM items LIMIT 20")
    rows = [r[0] for r in cur.fetchall()]
    conn.close()
    return {"items": rows}

@app.get("/fail")
def fail(code: int = 500):
    raise HTTPException(status_code=code, detail="Erreur simulée")
