# Milestone 3 — File transfer

## What we are building

This milestone adds secure file transfer to the JARVIS server. Devices can register, upload files, list files, and fetch a download stream from the central storage layer.

## Why it matters

The platform needs trustworthy storage and transfer primitives before it can support notifications, cloud sync, or remote device actions reliably. A secure upload/download base gives us a foundation for later peer-to-peer transfer optimization.

## What is included

- file metadata model
- secure server-side storage directory per device
- upload endpoint
- file listing endpoint
- download endpoint
- dashboard visibility for recent transfers

## Security notes

- file access is constrained to the authenticated device and the server's storage path
- uploads are stored server-side under a private folder, not exposed to arbitrary public filesystem access
- the system should later add more granular permissions and optional direct device-to-device transfer

## How it works

1. A device registers with the server.
2. The device uploads a file as multipart data.
3. The server saves the content under its private storage directory.
4. The server stores metadata in SQLite.
5. The dashboard can list the most recent files from the server.

## What could fail

- storage directory permissions
- device not found error before registration
- missing or invalid file name
- file download attempted after storage removal or corruption

## How we test it

- register a device
- upload a file
- list files for that device
- download the saved file and verify it matches the original bytes
