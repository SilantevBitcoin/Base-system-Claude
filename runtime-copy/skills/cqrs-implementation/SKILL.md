---
name: cqrs-implementation
description: "Command Query Responsibility Segregation — separate write (command) and read (query) models, drive read models from events, and handle eventual consistency. Use PROACTIVELY when read and write workloads have very different shapes/scale, when building event-sourced systems, or when one ORM model is being contorted to serve both complex writes and high-volume reads."
---

# CQRS Implementation

CQRS splits the model that **changes** state (commands → write model) from the model that **reads** state (queries → read model). Writes append events/state; one or more **projections** consume those events to build denormalized read models optimized per query. The two sides evolve and scale independently, at the cost of **eventual consistency** between them.

## Use this skill when

- Read and write workloads differ enough that one model serves neither well.
- Reads must scale independently from writes (read replicas, denormalized views).
- Building event-sourced systems (CQRS is the natural read side of event sourcing).
- Complex reporting / search views over the same data.

## Do not use this skill when

- The domain is simple and plain CRUD is sufficient — CQRS adds real operational cost.
- You require strong immediate consistency everywhere (read-your-writes on every path).
- You cannot operate and monitor separate read/write stores plus projection lag.

## Core shape

| Component       | Responsibility                  |
| --------------- | ------------------------------- |
| Command         | Intent to change state          |
| Command Handler | Validates and executes commands |
| Event           | Record of a state change (fact) |
| Query           | Request for data                |
| Query Handler   | Reads from the read model       |
| Projector       | Updates the read model from events |

Commands go through a command bus to handlers that mutate the write model and emit events. A projector reads those events and updates read models. Queries hit the read model only — never the write side.

## Key decisions

1. **Consistency budget.** Decide the acceptable read-model lag (an SLA) and whether any path needs read-your-writes. Most paths tolerate lag; a few may need the consistency-wait pattern (see playbook Template 5).
2. **Projection rebuild.** Read models must be rebuildable from the event log from scratch — design the projector with a checkpoint and a `rebuild()` path from day one.
3. **Event versioning.** Version events from the first release so the write and read schemas can evolve independently.
4. **Don't over-engineer.** Start with the simplest split that solves the problem; add buses, separate stores, and async projectors only as the workload demands.

## Do / Don't

- Do separate command and query models; validate inside command handlers before any state change.
- Do denormalize read models for the queries they serve.
- Don't query the write side from a command path for read purposes — keep the split clean.
- Don't couple read and write schemas; let them evolve on independent migrations.
- Don't ignore consistency SLAs — define and monitor acceptable projection lag.

## Implementation playbook

For runnable patterns — command/query bus, command + query handler implementations, a FastAPI CQRS application, a read-model synchronizer with checkpointing and `rebuild_projection`, and an eventual-consistency / read-your-writes query handler — see `resources/implementation-playbook.md`.

Works well with: `saga-orchestration` (cross-aggregate workflows over the same events), event-sourcing / outbox (reliable event publishing into the projector).
