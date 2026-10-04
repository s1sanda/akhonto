# Android client

This folder is reserved for the Android device client for Milestone 2.

## Planned responsibilities

- secure registration with the JARVIS server
- periodic heartbeat reporting
- battery and network telemetry
- permission-aware location reporting
- local queueing for offline scenarios

## Recommended stack

- Kotlin
- Android Jetpack
- WorkManager for background scheduling
- Android Keystore for secrets
- Retrofit or OkHttp for API access

## Security note

Location collection must be opt-in and clearly disclosed. The app should request OS permission explicitly and avoid collecting hidden telemetry.
