---
name: saga-orchestration
description: "Distributed transactions and long-running business processes across services. Use PROACTIVELY when coordinating multi-service writes, implementing compensating transactions, or building order-fulfillment / approval workflows that must stay consistent without a 2PC distributed lock."
---

# Saga Orchestration

Patterns for managing distributed transactions and long-running business processes that span multiple services. A saga is a sequence of local transactions where each step publishes a command/event; if any step fails, previously completed steps are undone by **compensating transactions** (semantic rollback), since you cannot hold a distributed ACID lock across services.

## Use this skill when

- Coordinating multi-service transactions (inventory + payment + shipping)
- Implementing compensating transactions (semantic undo)
- Managing long-running business workflows
- Handling partial failures in distributed systems
- Building order-fulfillment or approval workflows

## Orchestration vs Choreography

- **Orchestration** — a central coordinator tells each service what to do and tracks state. Choose when business-flow visibility and centralized control matter; easier to reason about and debug.
- **Choreography** — services react to each other's events with no central coordinator. Choose when autonomy is high and coupling must stay low; harder to trace end-to-end.

```
Choreography                    Orchestration
┌─────┐  ┌─────┐  ┌─────┐     ┌─────────────┐
│Svc A│─►│Svc B│─►│Svc C│     │ Orchestrator│
└─────┘  └─────┘  └─────┘     └──────┬──────┘
   │        │        │               │
   ▼        ▼        ▼         ┌─────┼─────┐
 Event    Event    Event       ▼     ▼     ▼
                            ┌────┐┌────┐┌────┐
                            │Svc1││Svc2││Svc3│
                            └────┘└────┘└────┘
```

### Saga execution states

| State            | Description                    |
| ---------------- | ------------------------------ |
| **Started**      | Saga initiated                 |
| **Pending**      | Waiting for step completion    |
| **Compensating** | Rolling back due to failure    |
| **Completed**    | All steps succeeded            |
| **Failed**       | Saga failed after compensation |

## Design checklist

- Define an explicit saga state machine (states above) and persist it.
- Define a compensation action for **every** step that has externally visible effects.
- Use **idempotency keys** for command handling — steps and compensations may be retried.
- Store a **correlation ID** across all events, commands, and logs for end-to-end tracing.
- Define a **timeout policy per step**; do not wait forever.
- Retry transient failures with bounded exponential backoff; escalate non-recoverable failures to the compensation path.
- Capture an operator-visible failure reason and the current step.

## Templates

### Template 1: Saga orchestrator base

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class SagaState(Enum):
    STARTED = "started"
    PENDING = "pending"
    COMPENSATING = "compensating"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SagaStep:
    name: str
    action: str
    compensation: str
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None
    executed_at: Optional[datetime] = None
    compensated_at: Optional[datetime] = None


@dataclass
class Saga:
    saga_id: str
    saga_type: str
    state: SagaState
    data: Dict[str, Any]
    steps: List[SagaStep]
    current_step: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class SagaOrchestrator(ABC):
    """Base class for saga orchestrators."""

    def __init__(self, saga_store, event_publisher):
        self.saga_store = saga_store
        self.event_publisher = event_publisher

    @abstractmethod
    def define_steps(self, data: Dict) -> List[SagaStep]:
        """Define the saga steps."""
        pass

    @property
    @abstractmethod
    def saga_type(self) -> str:
        """Unique saga type identifier."""
        pass

    async def start(self, data: Dict) -> Saga:
        """Start a new saga."""
        saga = Saga(
            saga_id=str(uuid.uuid4()),
            saga_type=self.saga_type,
            state=SagaState.STARTED,
            data=data,
            steps=self.define_steps(data)
        )
        await self.saga_store.save(saga)
        await self._execute_next_step(saga)
        return saga

    async def handle_step_completed(self, saga_id: str, step_name: str, result: Dict):
        """Handle successful step completion."""
        saga = await self.saga_store.get(saga_id)

        for step in saga.steps:
            if step.name == step_name:
                step.status = "completed"
                step.result = result
                step.executed_at = datetime.utcnow()
                break

        saga.current_step += 1
        saga.updated_at = datetime.utcnow()

        if saga.current_step >= len(saga.steps):
            saga.state = SagaState.COMPLETED
            await self.saga_store.save(saga)
            await self._on_saga_completed(saga)
        else:
            saga.state = SagaState.PENDING
            await self.saga_store.save(saga)
            await self._execute_next_step(saga)

    async def handle_step_failed(self, saga_id: str, step_name: str, error: str):
        """Handle step failure - start compensation."""
        saga = await self.saga_store.get(saga_id)

        for step in saga.steps:
            if step.name == step_name:
                step.status = "failed"
                step.error = error
                break

        saga.state = SagaState.COMPENSATING
        saga.updated_at = datetime.utcnow()
        await self.saga_store.save(saga)
        await self._compensate(saga)

    async def _execute_next_step(self, saga: Saga):
        """Execute the next step in the saga."""
        if saga.current_step >= len(saga.steps):
            return

        step = saga.steps[saga.current_step]
        step.status = "executing"
        await self.saga_store.save(saga)

        await self.event_publisher.publish(
            step.action,
            {
                "saga_id": saga.saga_id,
                "step_name": step.name,
                **saga.data
            }
        )

    async def _compensate(self, saga: Saga):
        """Execute compensation for completed steps, in reverse order."""
        for i in range(saga.current_step - 1, -1, -1):
            step = saga.steps[i]
            if step.status == "completed":
                step.status = "compensating"
                await self.saga_store.save(saga)

                await self.event_publisher.publish(
                    step.compensation,
                    {
                        "saga_id": saga.saga_id,
                        "step_name": step.name,
                        "original_result": step.result,
                        **saga.data
                    }
                )

    async def handle_compensation_completed(self, saga_id: str, step_name: str):
        """Handle compensation completion."""
        saga = await self.saga_store.get(saga_id)

        for step in saga.steps:
            if step.name == step_name:
                step.status = "compensated"
                step.compensated_at = datetime.utcnow()
                break

        all_compensated = all(
            s.status in ("compensated", "pending", "failed")
            for s in saga.steps
        )

        if all_compensated:
            saga.state = SagaState.FAILED
            await self._on_saga_failed(saga)

        await self.saga_store.save(saga)

    async def _on_saga_completed(self, saga: Saga):
        await self.event_publisher.publish(
            f"{self.saga_type}Completed",
            {"saga_id": saga.saga_id, **saga.data}
        )

    async def _on_saga_failed(self, saga: Saga):
        await self.event_publisher.publish(
            f"{self.saga_type}Failed",
            {"saga_id": saga.saga_id, "error": "Saga failed", **saga.data}
        )
```

### Template 2: Order-fulfillment saga (orchestration)

```python
class OrderFulfillmentSaga(SagaOrchestrator):
    """Orchestrates order fulfillment across services."""

    @property
    def saga_type(self) -> str:
        return "OrderFulfillment"

    def define_steps(self, data: Dict) -> List[SagaStep]:
        return [
            SagaStep(
                name="reserve_inventory",
                action="InventoryService.ReserveItems",
                compensation="InventoryService.ReleaseReservation"
            ),
            SagaStep(
                name="process_payment",
                action="PaymentService.ProcessPayment",
                compensation="PaymentService.RefundPayment"
            ),
            SagaStep(
                name="create_shipment",
                action="ShippingService.CreateShipment",
                compensation="ShippingService.CancelShipment"
            ),
            SagaStep(
                name="send_confirmation",
                action="NotificationService.SendOrderConfirmation",
                compensation="NotificationService.SendCancellationNotice"
            )
        ]


async def create_order(order_data: Dict):
    saga = OrderFulfillmentSaga(saga_store, event_publisher)
    return await saga.start({
        "order_id": order_data["order_id"],
        "customer_id": order_data["customer_id"],
        "items": order_data["items"],
        "payment_method": order_data["payment_method"],
        "shipping_address": order_data["shipping_address"]
    })


# Each service reports success/failure back to the orchestrator
class InventoryService:
    async def handle_reserve_items(self, command: Dict):
        try:
            reservation = await self.reserve(command["items"], command["order_id"])
            await self.event_publisher.publish(
                "SagaStepCompleted",
                {
                    "saga_id": command["saga_id"],
                    "step_name": "reserve_inventory",
                    "result": {"reservation_id": reservation.id}
                }
            )
        except InsufficientInventoryError as e:
            await self.event_publisher.publish(
                "SagaStepFailed",
                {
                    "saga_id": command["saga_id"],
                    "step_name": "reserve_inventory",
                    "error": str(e)
                }
            )

    async def handle_release_reservation(self, command: Dict):
        # Compensating action — must be idempotent
        await self.release_reservation(command["original_result"]["reservation_id"])
        await self.event_publisher.publish(
            "SagaCompensationCompleted",
            {"saga_id": command["saga_id"], "step_name": "reserve_inventory"}
        )
```

### Template 3: Choreography-based saga

```python
class OrderChoreographySaga:
    """Choreography-based saga — services react to events, no central coordinator."""

    def __init__(self, event_bus):
        self.event_bus = event_bus
        self._register_handlers()

    def _register_handlers(self):
        self.event_bus.subscribe("OrderCreated", self._on_order_created)
        self.event_bus.subscribe("InventoryReserved", self._on_inventory_reserved)
        self.event_bus.subscribe("PaymentProcessed", self._on_payment_processed)
        self.event_bus.subscribe("ShipmentCreated", self._on_shipment_created)
        # Compensation handlers
        self.event_bus.subscribe("PaymentFailed", self._on_payment_failed)
        self.event_bus.subscribe("ShipmentFailed", self._on_shipment_failed)

    async def _on_order_created(self, event: Dict):
        await self.event_bus.publish("ReserveInventory", {
            "saga_id": event["order_id"],
            "order_id": event["order_id"],
            "items": event["items"]
        })

    async def _on_inventory_reserved(self, event: Dict):
        await self.event_bus.publish("ProcessPayment", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "amount": event["total_amount"],
            "reservation_id": event["reservation_id"]
        })

    async def _on_payment_processed(self, event: Dict):
        await self.event_bus.publish("CreateShipment", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "payment_id": event["payment_id"]
        })

    async def _on_shipment_created(self, event: Dict):
        await self.event_bus.publish("OrderFulfilled", {
            "saga_id": event["saga_id"],
            "order_id": event["order_id"],
            "tracking_number": event["tracking_number"]
        })

    async def _on_payment_failed(self, event: Dict):
        await self.event_bus.publish("ReleaseInventory", {
            "saga_id": event["saga_id"],
            "reservation_id": event["reservation_id"]
        })
        await self.event_bus.publish("OrderFailed", {
            "order_id": event["order_id"], "reason": "Payment failed"
        })

    async def _on_shipment_failed(self, event: Dict):
        # Refund payment AND release inventory — compensate everything done so far
        await self.event_bus.publish("RefundPayment", {
            "saga_id": event["saga_id"], "payment_id": event["payment_id"]
        })
        await self.event_bus.publish("ReleaseInventory", {
            "saga_id": event["saga_id"], "reservation_id": event["reservation_id"]
        })
```

### Template 4: Saga with step timeouts

```python
class TimeoutSagaOrchestrator(SagaOrchestrator):
    """Saga orchestrator with per-step timeouts via an external scheduler."""

    def __init__(self, saga_store, event_publisher, scheduler):
        super().__init__(saga_store, event_publisher)
        self.scheduler = scheduler

    async def _execute_next_step(self, saga: Saga):
        if saga.current_step >= len(saga.steps):
            return

        step = saga.steps[saga.current_step]
        step.status = "executing"
        step.timeout_at = datetime.utcnow() + timedelta(minutes=5)
        await self.saga_store.save(saga)

        await self.scheduler.schedule(
            f"saga_timeout_{saga.saga_id}_{step.name}",
            self._check_timeout,
            {"saga_id": saga.saga_id, "step_name": step.name},
            run_at=step.timeout_at
        )

        await self.event_publisher.publish(
            step.action,
            {"saga_id": saga.saga_id, "step_name": step.name, **saga.data}
        )

    async def _check_timeout(self, data: Dict):
        saga = await self.saga_store.get(data["saga_id"])
        step = next(s for s in saga.steps if s.name == data["step_name"])
        if step.status == "executing":
            await self.handle_step_failed(
                data["saga_id"], data["step_name"], "Step timed out"
            )
```

## Durable execution alternative

The templates above build saga infrastructure from scratch — saga stores, event publishers, compensation tracking. **Durable execution frameworks** (e.g. Temporal, DBOS, Restate) eliminate much of this boilerplate: the workflow runtime automatically persists state to a database, retries failed steps, and resumes from the last checkpoint after a crash. Instead of a `SagaOrchestrator` base class you write a workflow function with steps, and the framework handles persistence, crash recovery, and exactly-once semantics. Reach for durable execution when you want saga-level reliability without owning the coordination infrastructure.

## Verification

- Simulate failure at **every** step and confirm the compensation path runs in reverse order.
- Validate duplicate-message handling (send the same command twice → same outcome).
- Validate recovery from an orchestrator restart mid-saga (state is reloaded from the store).

## Best practices

- **Make steps idempotent** — they will be retried.
- **Design compensations as carefully as the forward path** — an un-runnable compensation is a stuck saga; test it most.
- **Use correlation IDs** for tracing across services.
- **Implement timeouts** — never wait forever for a step ack.
- **Use async messaging** between services; don't couple them with synchronous calls.
- **Don't assume instant completion** — sagas are eventually consistent by nature.

Works well with: `event-sourcing` / outbox pattern (reliable event publishing), `grpc-golang` (inter-service transport), `distributed-tracing` (follow a saga across services via correlation ID).
