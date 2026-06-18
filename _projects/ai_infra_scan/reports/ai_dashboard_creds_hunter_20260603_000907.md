# AI DASHBOARD+EXPOSED CREDS HUNTER Report

**Date:** 2026-06-02T21:54:23.361312Z
**Scanner:** ai_dashboard_creds_hunter v1.0
**OPSEC:** Tor SOCKS5 (127.0.0.1:9050)
**Exit IP:** 5.45.102.93
**Targets Scanned:** 5

## Vulnerabilities

| Severity | Type | Service | URL | Username | Password |
|----------|------|---------|-----|----------|----------|
| CRITICAL | default_credentials | grafana | http://207.244.225.101:3000 | admin | admin |
| CRITICAL | default_credentials | grafana | http://207.244.225.101:3000 | admin | grafana |
| CRITICAL | default_credentials | grafana | http://207.244.225.101:3000 | admin | password |
| CRITICAL | default_credentials | grafana | http://207.244.225.101:3000 | viewer | viewer |
| CRITICAL | default_credentials | grafana | http://207.244.225.101:3000 | editor | editor |

## Exposed Files

| Severity | URL | Path | Size |
|----------|-----|------|------|
| HIGH | http://207.244.225.101:3000/.env | /.env | 7225 bytes |
| HIGH | http://207.244.225.101:3000/.env.local | /.env.local | 7225 bytes |
| HIGH | http://207.244.225.101:3000/.env.production | /.env.production | 7225 bytes |
| HIGH | http://207.244.225.101:3000/.env.development | /.env.development | 7225 bytes |
| MEDIUM | http://207.244.225.101:3000/.dockerenv | /.dockerenv | 7225 bytes |

## Service Detections

| Service | URL | Title | Version | API Accessible |
|---------|-----|-------|---------|----------------|
| grafana | http://207.244.225.101:3000 | Open WebUI | N/A | True |
