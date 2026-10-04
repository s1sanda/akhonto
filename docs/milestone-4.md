# Milestone 4 — Notifications and event bus

## What we are building

This milestone adds an event-driven notification layer so device actions and system events can be recorded and surfaced to the platform without hard-coding ad hoc logic.

## Why it matters

A personal device ecosystem needs a clear way to communicate important events such as battery warnings, failed transfers, connectivity changes, and approval requests. The notification layer gives us a durable record and a foundation for future push delivery, UI badges, and automation triggers.

## Included features

- notification model in the database
- notification creation endpoint
- filtered notification listing by device
- JSON-backed metadata for event details
- SQLite migration support for existing dev databases

## Core API flow

1. A device or server event sends a payload to POST /api/notifications.
2. The server validates the request and records the event.
3. Client code can fetch notifications with GET /api/notifications?device_id=... .
4. Future milestones can attach delivery channels such as mobile push, email, or in-app dashboard updates.

## Security notes

- notifications are intentionally minimal and auditable
- they are not used as a privileged action trigger by themselves
- sensitive actions should still require explicit approval flows and authorization checks

## Testing

Use the API smoke tests to validate:

- notification creation succeeds for a registered device
- notifications are retrievable through the device filter
- the file-transfer flow continues to work alongside the new event system
