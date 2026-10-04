# Milestone 2 — Device connectivity

## What we are building

This milestone adds real device connectivity features to the JARVIS platform. Instead of only registering a device once, we track whether it is online, when it last reported a heartbeat, and which telemetry it is sending.

## Why it matters

The server needs a reliable heartbeat model before it can manage files, notifications, remote commands, VPN access, or AI requests. Without connectivity status, the platform cannot confidently tell whether an action is safe or possible.

## What is implemented in this milestone

- device heartbeat endpoint
- live online/offline state tracking
- device metadata updates such as battery and network mode
- dashboard rendering based on the server's device list
- Windows agent stub and Android planning guide

## How it works

1. Device registers with the server.
2. Device sends periodic heartbeats.
3. Server updates last seen and health state.
4. Dashboard fetches live device status and renders the device cards.

## Security implications

- Heartbeats should be authenticated with a device token.
- Sensitive telemetry such as location should not be collected without explicit permission.
- Offline state is useful metadata, but it must not be used to infer hidden personal activity.

## What could fail

- device offline or unreachable
- stale heartbeats after a crash or network outage
- wrong device identity if registration is abused

## How we test it

- register a device
- call the heartbeat endpoint
- confirm the device appears as online
- verify the dashboard shows the last seen timestamp
- simulate offline behavior by not sending heartbeats
