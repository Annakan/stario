"""
Telemetry sinks and span types for Stario apps.

Handlers see `Span` on `Context`. Import tracer backends from their modules
when wiring a process:

```python
from stario.telemetry.json import JsonTracer
from stario.telemetry.tty import TTYTracer
from stario.telemetry.noop import NoOpTracer
from stario.telemetry.sqlite import SqliteTracer
```

CLI reads `STARIO_TRACER` via `stario.cli.env.tracer_from_env()`.
"""
from __future__ import annotations

from .core import EventBody, Span, TelemetryStats, Tracer
from .spans import NoOpSpan, ProxySpan, RecordedEvent, RecordedLink, RecordingSpan

__all__ = [
    "EventBody",
    "NoOpSpan",
    "ProxySpan",
    "RecordedEvent",
    "RecordedLink",
    "RecordingSpan",
    "Span",
    "TelemetryStats",
    "Tracer",
]
