# JARVIS architecture

## System goals

JARVIS is a personal coordination layer for my own devices and services. The central server is not a public surveillance back end; it is a trusted controller for authenticated devices and authorized user actions.

## Major subsystems

### 1. Server core

The server is the control plane. It handles:

- user and device authentication
- device registry and heartbeat data
- authorization and permission checks
- event notifications and alerts
- file metadata and transfer coordination
- automation scheduling
- AI tool execution gatekeeping
- VPN server orchestration

### 2. Device agents

Each device runs an agent that reports status and executes approved commands. The Android agent and Windows agent are separate because they have different APIs and operating-system capabilities.

### 3. Web dashboard

The dashboard gives a central view of device health, files, VPN, assistant actions, and settings. It should be responsive and use authenticated sessions.

### 4. Data layer

PostgreSQL is the right foundation for device metadata, file indexes, task schedules, and audit logs. SQLite may be used for local development, but the production design should favor PostgreSQL.

### 5. Communication layer

The system needs multiple communication patterns:

- REST for authenticated command and query operations
- WebSockets for real-time status and notifications
- direct file transfer where devices are both reachable
- WireGuard tunnels for secure personal network routing
- push or event delivery for remote notifications

## Device communication model

```text
User / Web Dashboard
        |
        v
JARVIS Server
   |       |
   |       +-------------------> Android client
   |
   +--------------------------> Windows client
   |
   +--------------------------> File transfer / event broker
```

The server remains the registry and coordinator, while direct device-to-device communication is used for large transfer payloads when permitted.

## Why this design is practical

It creates a strong separation between:

- identity
- device ownership
- authorization
- network transport
- sensitive action approval

That separation reduces the risk of accidental overreach and makes future features easier to add without rewriting the system.

## Initial milestone scope

Milestone 1 is intentionally small:

- define the repo shape
- create a working server skeleton
- add a device model and registry API
- create a basic dashboard shell
- document security boundaries

This gives us a stable base before adding Android, Windows, file transfer, VPN, and AI layers.
