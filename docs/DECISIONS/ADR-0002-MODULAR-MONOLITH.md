# ADR-0002: Modular Monolith for MVP

- Status: PROPOSED — requires review
- Date: 2026-11-13

Build one deployable FastAPI backend with explicit internal modules and well-defined interfaces. Use PostgreSQL with controlled migrations and clear ownership boundaries.

The MVP budget and team size do not justify distributed service operations. Keep domain logic out of route handlers, avoid direct cross-module data mutation, and separate future lab execution infrastructure from the product API.

Revisit if independent scaling, fault isolation, security boundaries or team ownership require separate deployment units.
