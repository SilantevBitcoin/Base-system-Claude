---
name: async-python-patterns
description: "Comprehensive guidance for implementing asynchronous Python applications using asyncio, concurrent programming patterns, and async/await for building high-performance, non-blocking systems."
risk: safe
source: community
date_added: "2026-02-27"
---

# Async Python Patterns

Comprehensive guidance for implementing asynchronous Python applications using asyncio, concurrent programming patterns, and async/await for building high-performance, non-blocking systems.

## Use this skill when

- Building async web APIs (FastAPI, aiohttp, Sanic)
- Implementing concurrent I/O operations (database, file, network)
- Creating web scrapers with concurrent requests
- Developing real-time applications (WebSocket servers, chat systems)
- Processing multiple independent tasks simultaneously
- Building microservices with async communication
- Optimizing I/O-bound workloads
- Implementing async background tasks and queues

## Do not use this skill when

- The workload is CPU-bound with minimal I/O.
- A simple synchronous script is sufficient.
- The runtime environment cannot support asyncio/event loop usage.

Refer to `resources/implementation-playbook.md` for detailed patterns and examples.
