# JARVIS security model

## Security responsibilities

JARVIS must be designed around a strict ownership model:

- devices must be registered and authenticated
- user identity must be checked before sensitive operations
- permissions must be granted explicitly per device and action
- sensitive actions must require confirmation
- private keys and secrets must never be committed to Git

## Key risks to control early

### 1. Unauthorized tracking

Location and device telemetry must be opt-in and clearly disclosed. No hidden tracking. Device owners must be able to delete location history.

### 2. Credential leakage

Passwords, tokens, API keys, and VPN private keys must use environment variables or secure system storage.

### 3. Command abuse

Remote actions such as lock, shutdown, restart, or file deletion must require explicit consent and an allowlist of safe operations.

### 4. Untrusted automation

AI-generated actions should never be executed freely. Every tool call should be subject to policy checks and approval.

### 5. File exposure

File services must never expose arbitrary filesystem access to the public internet. Only approved shared directories and authenticated destinations should be allowed.

## Recommended security checks

- mTLS or mutual TLS for device-to-server trust where feasible
- device-specific JWT or signed tokens
- permission scopes such as device.read, device.control, file.upload, file.download
- audit logs for privileged actions
- secret rotation and revocation support
- encrypted storage for sensitive local data

## Security-first design rule

The system should assume the network is hostile and verify every request; a device being on the VPN is not enough to grant unrestricted privileges.
