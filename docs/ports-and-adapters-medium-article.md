# Ports & Adapters Pattern — Study Notes

> Personal study/navigation notes derived from `ports-and-adapters-medium-article.html` (Anas Issath, "Architecture Series #3").
> Open the HTML alongside this file for the full prose and verbatim code examples — each section here links the corresponding heading anchor.
> Summaries below are paraphrased; code shown is reduced to the minimal pattern shape.

---

## Decouple business logic from infrastructure

**HTML anchor:** `#d283` (subtitle), `#3a03` (title)

**Diagram (intro):** ![intro](https://miro.medium.com/v2/resize:fit:700/1*FGpT-paGObaaTPQpXLhGgA.png)

**Summary.** The article opens with three recurring developer complaints — "we need to switch databases," "we need a GraphQL API," "we need to test without the DB" — and argues each is symptom of the same disease: business logic that is married to infrastructure. The pattern proposed as the cure is Ports & Adapters (Hexagonal Architecture), where the domain sits at the center and everything else (DB, web framework, third-party APIs, queues) plugs in at the edges.

**Definition the article gives.** A Hexagonal codebase has business logic at the center; the outside world (DB, web, APIs, queues) interacts with it only via interfaces ("ports"). Concrete implementations of those interfaces ("adapters") can be swapped without the domain noticing.

---

## The Problem: Coupled Architecture

**HTML anchor:** `#c30b`

### Traditional Django Approach

**HTML anchor:** `#651f`

**Summary.** Article shows a traditional Django `create_order` view where ORM lookups, validation, ORM writes, Stripe API calls, and email sending are all interleaved in one function. The point: this view *is* the business logic, so the logic can't run without Django + Postgres + Stripe + SMTP all wired up.

**Five problems the article lists:**
1. Can't test without Django (ORM-bound logic, slow DB tests)
2. Can't change the database (logic uses ORM methods directly)
3. Can't change the payment provider (Stripe calls are inline)
4. Can't add a new API surface (GraphQL/gRPC would mean duplicating logic in another view)
5. Business rules are scattered across views, models, and helpers

> See original HTML for the full `views.py` example (block under `#651f`).

---

## The Root Cause

**HTML anchor:** `#85c1`

**Diagrams:**
- ![root cause 1](https://miro.medium.com/v2/resize:fit:700/1*6BZqd7VmRDPFiFfkOt7LBg.png)
- ![root cause 2](https://miro.medium.com/v2/resize:fit:700/1*v4IY9CsfBZR_5Av8-sIyXg.png)

**Summary.** Dependency direction is the root issue. In a traditional Django app, business code depends *outward* on Django, the DB driver, and the payment SDK. The fix is to invert that — dependencies should point *inward* toward the domain.

---

## The Solution: Hexagonal Architecture

**HTML anchor:** `#ff21`

![hex overview](https://miro.medium.com/v2/resize:fit:700/1*oNwjoiw7D_YRwIWqwC2K0A.png)

### The Hexagon Diagram

**HTML anchor:** `#7dd8`

![hex diagram](https://miro.medium.com/v2/resize:fit:700/1*gwOMeeuKxnpn0SG-736OAw.png)

**Key principles (article's wording, paraphrased):**
1. Business logic lives at the center, with no outward dependencies.
2. Ports = abstract interfaces declared by the domain.
3. Adapters = concrete implementations of those interfaces.
4. Dependencies always point **inward**.
5. The domain knows nothing about what's outside the hexagon.

### Core Concepts

**HTML anchor:** `#88e2`

**Pattern shape (minimal example).** The article uses standard Python ABCs for ports and shows the service depending only on those interfaces. The textbook shape:

```python
from abc import ABC, abstractmethod

class OrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None: ...
    @abstractmethod
    async def get(self, order_id: UUID) -> Order: ...

class PaymentGateway(ABC):
    @abstractmethod
    async def charge(self, amount: Money, customer_id: str) -> PaymentResult: ...

class OrderService:
    def __init__(self, order_repo: OrderRepository, payments: PaymentGateway):
        self.order_repo = order_repo
        self.payments = payments
    # ... methods call self.order_repo / self.payments — never Django, never Stripe
```

> Full port/adapter/service trio in original HTML under `#88e2`.

---

## Implementing Hexagonal Architecture in Django

**HTML anchor:** `#237d`

### Project Structure

**HTML anchor:** `#09a9`

![project structure](https://miro.medium.com/v2/resize:fit:700/1*93rHcvIcBYhZzhYaIyXjpQ.png)

**Layout the article proposes:**

```
myproject/
├── domain/           # Core — entities, services, ports. No framework imports.
│   ├── models/
│   ├── services/
│   ├── ports/        # repositories.py, gateways.py
│   └── exceptions.py
├── application/      # Use cases (commands, queries)
├── adapters/         # Concrete implementations
│   ├── repositories/ # django_orm/, mongodb/, ...
│   ├── gateways/     # stripe_gateway.py, paypal_gateway.py, ...
│   └── web/          # rest/, graphql/, ...
└── config/
    └── container.py  # Dependency injection wiring
```

**Discipline:** `domain/` imports only from `domain/`. `adapters/` imports `domain/`, never the reverse.

### Step 1: Define Domain Model

**HTML anchor:** `#3802`

**Summary.** Domain entities are plain `@dataclass` objects with no Django/ORM coupling. Business rules (e.g. "an order needs at least one item," "only pending orders can be paid") live as `@staticmethod` factories and instance methods on the entity itself. Domain events (`OrderCreated`, `OrderPaid`) are appended to an internal `_events` list as side outputs.

> Full `Order` dataclass with `create`, `pay`, `cancel`, and `total` in HTML under `#3802`.

### Step 2: Define Ports (Interfaces)

**HTML anchor:** `#fc15`

**Summary.** Ports live in `domain/ports/`. The article separates them into:
- `repositories.py` — `OrderRepository` (save / get / get_by_customer / delete)
- `gateways.py` — `PaymentGateway` (charge / refund), `EmailService` (send_order_confirmation), plus a `PaymentResult` value object

Every method takes domain types and returns domain types. No Django model, no Stripe object leaks through the interface.

### Step 3: Implement Business Logic (Service)

**HTML anchor:** `#b13a`

**Summary.** `OrderService` receives the three port instances via constructor injection and orchestrates the flow: build the `Order` via its factory → persist → charge → mark paid → persist again → send confirmation. The service file imports nothing from `adapters/` or third-party SDKs.

### Step 4: Create Adapters (Implementations)

**HTML anchor:** `#648e`

**Summary.** Two adapters are shown:
- **`DjangoORMOrderRepository`** — implements `OrderRepository`. Has its *own* Django models (`OrderModel`, `OrderItemModel`) separate from domain entities, and translates between them on save/load. The Django models are persistence detail; the domain `Order` is source of truth.
- **`StripePaymentGateway`** — implements `PaymentGateway`. Catches `stripe.error.CardError` / `stripe.error.StripeError` and returns a domain `PaymentResult` either way (no Stripe exception escapes the adapter).

> Full adapter code in HTML under `#648e`.

### Step 5: Dependency Injection

**HTML anchor:** `#a5d4`

![DI](https://miro.medium.com/v2/resize:fit:700/1*U-Kb3UybymzbN11UxLihSA.png)

**Summary.** A `Container` dataclass in `config/container.py` is the only place that knows about concrete classes. Two factory functions are shown:
- `create_production_container()` — wires the real Django ORM repo + Stripe + SMTP.
- `create_test_container()` — wires in-memory / fake adapters for fast tests.

The rest of the codebase pulls services off the container; it never instantiates an adapter directly.

### Step 6: Input Adapters (Web Layer)

**HTML anchor:** `#65a7`

**Summary.** REST views are themselves adapters: parse HTTP → build domain types → call `container.order_service.create_order(...)` → translate domain output (or domain exceptions) back to JSON. The article shows the same pattern translated to a GraphQL `Mutation` — same `OrderService`, different input adapter.

---

## Testing with Hexagonal Architecture

**HTML anchor:** `#7da3`

![testing](https://miro.medium.com/v2/resize:fit:700/1*4tE8fw0snGM7BXcYx_wDqQ.png)

### Unit Tests (No Infrastructure)

**HTML anchor:** `#a953`

**Summary.** Service tests use `unittest.mock.AsyncMock(spec=OrderRepository)` etc. for each port and assert on both the returned domain object and the mock interactions. No Django test DB, no Stripe sandbox — just business logic.

### Integration Tests (With Real Adapters)

**HTML anchor:** `#6c70`

**Summary.** A `TransactionTestCase` uses `create_test_container()` so the real Django ORM adapter hits a real test DB, while payment/email remain fake. This exercises the persistence translation layer without touching external services.

---

## Benefits of Hexagonal Architecture

**HTML anchor:** `#dxxx` (see HTML)

### 1. Testability
Pure-logic unit tests run in <1ms with no infrastructure spin-up.

### 2. Flexibility
Swapping the persistence layer means writing a second `OrderRepository` implementation (`MongoDBOrderRepository`, `InMemoryOrderRepository`, …) and rewiring the container. Domain code is untouched.

### 3. Independence
The domain has zero infrastructure imports — it can be exercised from any context (web, worker, CLI, notebook).

### 4. Evolution
Adding a GraphQL API is a new adapter, not a duplicated service. REST and GraphQL share the same `OrderService`.

![benefits](https://miro.medium.com/v2/resize:fit:700/1*-qVZm3YLR7a8xZpyVc7HOQ.png)

---

## Common Patterns

**HTML anchor:** see HTML

### Pattern 1: Repository per Aggregate
One repository per aggregate root (e.g. `OrderRepository`). Order items are accessed *through* the Order, not via their own repository.

### Pattern 2: Gateway per External System
One port per external collaborator: `PaymentGateway`, `EmailGateway`, `SmsGateway`, `PushNotificationGateway`. Each has a single responsibility.

### Pattern 3: Adapter per Technology
The same port can have many adapters: `PostgreSQLOrderRepository`, `MongoDBOrderRepository`, `InMemoryOrderRepository`. Selection happens in the container.

---

## Migration Strategy

**HTML anchor:** see HTML

The article proposes an incremental, weeks-scale migration:

| Phase | Focus |
|-------|-------|
| 1 | Identify the core domain — extract entities, business rules, bounded contexts. |
| 2 | Define ports — repository, gateway, and event-bus interfaces. |
| 3 | Implement adapters — wrap the existing Django ORM/Stripe/email code behind the new ports while keeping the legacy code running. |
| 4 | Wire with DI — build the container, configure production and test variants. |
| 5 | Migrate incrementally — port one feature at a time, test, deploy, repeat. |

---

## Common Mistakes

**HTML anchor:** see HTML

### Mistake 1: Leaky Abstractions
**Bad:** `OrderRepository.save(self, order: OrderModel)` — the port leaks the Django model.
**Good:** `OrderRepository.save(self, order: Order)` — the port takes the domain entity; the adapter translates internally.

### Mistake 2: Domain Depending on Adapters
**Bad:** `OrderService.__init__` constructs `DjangoORMRepository()` itself (import from `adapters/`).
**Good:** `OrderService.__init__(self, repo: OrderRepository)` — the service takes the port; the container injects the concrete adapter.

### Mistake 3: Too Many Ports
**Bad:** `UserPhotoRepository`, `UserEmailRepository`, `UserNameRepository`, … — one port per field.
**Good:** One port per aggregate (`UserRepository`); the user object owns its own state.

---

## Conclusion

**HTML anchor:** see HTML

![conclusion](https://miro.medium.com/v2/resize:fit:700/1*zCrnV0xNSn1-S7UPfQLg-A.png)

**One-sentence takeaway from the article:** *Dependencies should point inward, not outward.*

The recap the author closes on:
- Business logic at the center, ports as interfaces, adapters as implementations, dependencies inverted.
- Benefits: testable without infrastructure, swappable persistence, framework-independent domain, easy to add new API surfaces.
- Implementation order: domain models (pure) → ports (interfaces) → adapters (implementations) → DI (wiring).
- Testing: mock the ports for unit tests; use real adapters for integration tests.

**Next in the article series (per author):** Event-Driven Django (Domain Events Implementation). This is article #3 of an Advanced Architecture Series.
