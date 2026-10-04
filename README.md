# JARVIS

## Personal Multi-Device Cloud, Control & AI Assistant

JARVIS is a personal platform for coordinating my own devices and services through a central server. The goal is not a public surveillance tool or a generic VPN app; it is a secure, modular ecosystem for device health, file transfer, notifications, remote commands, automation, and an AI assistant that works only with approved actions.

## Core principles

- Device ownership and authorization are mandatory.
- Authentication and authorization are separate concerns.
- Sensitive actions require explicit confirmation.
- Private keys, tokens, and secrets stay out of source control.
- Communication should be encrypted and minimal-by-default.
- Features are added in milestones rather than all at once.

## Current milestone

Milestone 1 focuses on the platform foundation:

- repository structure
- server skeleton
- database and device model
- authentication flow scaffolding
- basic web dashboard shell
- secure documentation and setup guidance

## Proposed subsystem layout

- server: API gateway, auth, registry, notifications, automation scaffolding
- android: device client and local reporting
- windows: device agent and system monitoring
- web: dashboard and control UI
- docs: architecture, security, setup, and troubleshooting

## Recommended technology stack

- Server: Python + FastAPI + PostgreSQL
- Android client: Kotlin + Android Jetpack + secure storage
- Windows client: C# + .NET 8 + background service
- Dashboard: lightweight web app served from the server or a React frontend
- Communication: REST + WebSocket + TLS + WireGuard for VPN
- Data store: PostgreSQL for core metadata and device state

## Documentation

- [docs/architecture.md](docs/architecture.md)
- [docs/security.md](docs/security.md)
- [docs/setup.md](docs/setup.md)

## Quick start

```bash
cd jarvis/server
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server exposes:

- GET /api/health
- POST /api/auth/register-device
- GET /api/devices

## Development roadmap

1. Foundation and secure architecture
2. Device connectivity and heartbeat
3. File transfer and progress tracking
4. Notifications and event bus
5. Controlled remote actions
6. WireGuard VPN integration
7. Media download management
8. Automation engine
9. AI assistant with approved tool calls
10. Advanced personal features

## Important security note

This project is for devices I own or am explicitly authorized to manage. It does not include stealth monitoring, unauthorized device tracking, credential theft, or bypassing access controls.
