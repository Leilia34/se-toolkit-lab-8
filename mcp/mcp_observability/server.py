"""MCP server exposing VictoriaLogs and VictoriaTraces APIs as typed tools."""

from __future__ import annotations

import json
import os
import httpx
from collections.abc import Awaitable, Callable, Sequence
from typing import Any
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel, Field

server = Server("observability")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_VICTORIALOGS_URL: str = ""
_VICTORIATRACES_URL: str = ""
def _get_victorialogs_url() -> str:
    return _VICTORIALOGS_URL or os.environ.get("VICTORIALOGS_URL", "http://victorialogs:9428")


def _get_victoriatraces_url() -> str:
    return _VICTORIATRACES_URL or os.environ.get("VICTORIATRACES_URL", "http://victoriatraces:10428")


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class _LogsSearchArgs(BaseModel):
    query: str = Field(description="LogsQL query string (e.g., 'level:error')")
    limit: int = Field(default=20, ge=1, le=1000, description="Max entries to return")
    time_range: str = Field(default="1h", description="Time range (e.g., '1h', '30m', '24h')")


class _LogsErrorCountArgs(BaseModel):
    time_range: str = Field(default="1h", description="Time window (e.g., '1h', '30m')")
    service: str = Field(default="", description="Filter by service name (optional)")


class _TracesListArgs(BaseModel):
    service: str = Field(default="Learning Management Service", description="Service name")
    limit: int = Field(default=10, ge=1, le=100, description="Max traces to return")
    time_range: str = Field(default="1h", description="Time range (e.g., '1h', '30m')")

class _TracesGetArgs(BaseModel):
    trace_id: str = Field(description="Trace ID to fetch")


class _NoArgs(BaseModel):
    """Empty input model."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _text(data: Any) -> list[TextContent]:
    """Serialize data to JSON text."""
    if isinstance(data, (dict, list)):
        return [TextContent(type="text", text=json.dumps(data, indent=2, ensure_ascii=False))]
    return [TextContent(type="text", text=str(data))]
async def _http_get(url: str, params: dict | None = None) -> dict | list:
    """Make HTTP GET request."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()


# ---------------------------------------------------------------------------
# VictoriaLogs tool handlers
# ---------------------------------------------------------------------------


async def _logs_search(args: _LogsSearchArgs) -> list[TextContent]:
    """Search logs using VictoriaLogs LogsQL."""
    url = f"{_get_victorialogs_url()}/select/logsql/query"
    params = {
        "query": args.query,
        "limit": args.limit,
    }
    # VictoriaLogs accepts time range in the query or as separate params
    try:
        result = await _http_get(url, params)
        # Format result for readability
        if isinstance(result, list):
            return _text({"entries": result, "count": len(result)})
        return _text(result)
    except Exception as e:
        return _text({"error": str(e), "url": url})


async def _logs_error_count(args: _LogsErrorCountArgs) -> list[TextContent]:
    """Count errors per service over a time window."""
    url = f"{_get_victorialogs_url()}/select/logsql/query"
    
    # Build query for errors
    if args.service:
        query = f'_stream:{{service="{args.service}"}} AND (level:error OR level:ERROR)'
    else:
        query = "_stream:{service!=\"\"} AND (level:error OR level:ERROR)"
    
    params = {
        "query": query,
        "limit": 1000,
    }
    
    try:
        result = await _http_get(url, params)
        
        # Count errors by service
        error_counts: dict[str, int] = {}
        if isinstance(result, list):
            for entry in result:
                service = entry.get("_stream", {}).get("service", "unknown")
                error_counts[service] = error_counts.get(service, 0) + 1
        
        return _text({
            "time_range": args.time_range,
            "error_counts": error_counts,
            "total_errors": sum(error_counts.values())
        })
    except Exception as e:
        return _text({"error": str(e)})


# ---------------------------------------------------------------------------
# VictoriaTraces tool handlers
# ---------------------------------------------------------------------------


async def _traces_list(args: _TracesListArgs) -> list[TextContent]:
    """List recent traces for a service."""
    # VictoriaTraces Jaeger-compatible API
    url = f"{_get_victoriatraces_url()}/jaeger/api/traces"
    params = {
        "service": args.service,
        "limit": args.limit,

    }
    
    try:
        result = await _http_get(url, params)
        
        # Extract summary info
        traces_summary = []
        if isinstance(result, dict) and "data" in result:
            for trace in result["data"]:
                traces_summary.append({
                    "trace_id": trace.get("traceID"),
                    "spans": len(trace.get("spans", [])),
                    "start_time": trace.get("startTime"),
                })
        
        return _text({
            "service": args.service,
            "traces": traces_summary,
            "count": len(traces_summary)
        })

    except Exception as e:
        return _text({"error": str(e), "url": url})


async def _traces_get(args: _TracesGetArgs) -> list[TextContent]:
    """Fetch a specific trace by ID."""
    url = f"{_get_victoriatraces_url()}/jaeger/api/traces/{args.trace_id}"
    
    try:
        result = await _http_get(url)
        return _text(result)
    except Exception as e:
        return _text({"error": str(e), "trace_id": args.trace_id})


async def _traces_errors(args: _NoArgs) -> list[TextContent]:
    """Find traces with errors in the last hour."""
    url = f"{_get_victoriatraces_url()}/jaeger/api/traces"
    params = {"limit": 20}
    try:
        result = await _http_get(url, params)
        
        error_traces = []
        if isinstance(result, dict) and "data" in result:
            for trace in result["data"]:
                # Check if any span has error tag
                spans = trace.get("spans", [])
                for span in spans:
                    tags = span.get("tags", [])
                    for tag in tags:
                        if tag.get("key") == "error" or "error" in str(tag.get("value", "")).lower():
                            error_traces.append({
                                "trace_id": trace.get("traceID"),
                                "service": span.get("process", {}).get("serviceName", "unknown"),
                                "operation": span.get("operationName"),
                            })
                            break
        return _text({
            "error_traces": error_traces,
            "count": len(error_traces)
        })
    except Exception as e:
        return _text({"error": str(e)})


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_Registry = tuple[type[BaseModel], Callable[..., Awaitable[list[TextContent]]], Tool]

_TOOLS: dict[str, _Registry] = {}

def _register(
    name: str,
    description: str,
    model: type[BaseModel],
    handler: Callable[..., Awaitable[list[TextContent]]],
) -> None:
    schema = model.model_json_schema()
    schema.pop("$defs", None)
    schema.pop("title", None)
    _TOOLS[name] = (model, handler, Tool(name=name, description=description, inputSchema=schema))


# Register VictoriaLogs tools
_register(
    "logs_search",
    "Search logs in VictoriaLogs using LogsQL query. Returns matching log entries.",
    _LogsSearchArgs,
    _logs_search,
)

_register(
    "logs_error_count",
    "Count errors per service over a time window. Use to find which services have errors.",
    _LogsErrorCountArgs,
    _logs_error_count,
)

# Register VictoriaTraces tools
_register(
    "traces_list",
    "List recent traces for a service. Shows trace IDs and span counts.",
    _TracesListArgs,
    _traces_list,
)
_register(
    "traces_get",
    "Fetch a specific trace by ID. Returns full trace with all spans.",
    _TracesGetArgs,
    _traces_get,
)

_register(
    "traces_errors",
    "Find traces containing errors in the last hour. Useful for debugging failures.",
    _NoArgs,
    _traces_errors,
)


# ---------------------------------------------------------------------------
# MCP handlers
# ---------------------------------------------------------------------------


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [entry[2] for entry in _TOOLS.values()]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    entry = _TOOLS.get(name)
    if entry is None:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    model_cls, handler, _ = entry
    try:
        args = model_cls.model_validate(arguments or {})
        return await handler(args)
    except Exception as exc:
        return [TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
