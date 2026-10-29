# ADR-001: Modular Monolith First

**Date:** 2026-10-29  
**Status:** Accepted  
**Deciders:** Project founder

---

## Context

InsightFlow AI is a new product with no users, no production traffic, and one
developer. We need to make a decision about the initial deployment topology.

The main options are:

1. **Modular monolith** — one Python process, one codebase, internal module
   boundaries enforced by import structure.
2. **Microservices** — separate services for analytics, AI, data ingestion, etc.,
   communicating over HTTP or a message queue.
3. **Serverless functions** — individual Lambda/Cloud Function handlers per
   endpoint.

---

## Decision

We start with a **modular monolith**.

---

## Reasons

**Against microservices now:**
- Network calls between services add latency, failure modes, and debugging
  complexity without adding value at this scale.
- Each service needs its own CI pipeline, container image, secrets management,
  and health monitoring.
- Distributed tracing, service discovery, and inter-service authentication are
  non-trivial engineering problems.
- One developer cannot maintain five deployment targets while simultaneously
  building the product.

**Against serverless now:**
- Cold starts affect user experience for a BI tool where queries can take seconds.
- Long-running AI inference calls exceed typical function timeouts.
- Local development is harder with serverless.

**For a modular monolith:**
- One `docker compose up` starts the entire stack.
- All code runs in the same process — easy to debug with a single breakpoint.
- Module boundaries (`api/`, `services/`, `repositories/`) enforce separation
  of concerns without the operational overhead of separate services.
- If a single service genuinely needs independent scaling later, we extract it.
  Martin Fowler calls this the "monolith-first" strategy.

---

## Consequences

- All backend code lives in `backend/app/`.
- Internal module dependencies are the only coupling mechanism — no internal
  HTTP calls.
- A future extraction to microservices is possible but not planned.
- If we hit a genuine scalability limit (e.g., ML inference blocking the API),
  we will write a new ADR before changing the architecture.

---

## References

- [Martin Fowler — MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html)
- [Sam Newman — Monolith to Microservices](https://samnewman.io/books/monolith-to-microservices/)
