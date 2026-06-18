# AskNova Recon Report — PRE-CHALLENGE

**Target:** asknova.online / api.asknova.online
**Date:** 2026-06-11
**Challenge starts:** 2026-06-12 05:00 CEST

---

## 🔴 CRITICAL FINDINGS

### 1. Information Disclosure — /api/health (SEVERITY: HIGH)
- **URL:** https://asknova.online/api/health AND https://api.asknova.online/api/health
- **Leaked data:**
  - Internal hostname: `unblocker-vm-1`
  - Version: `1.0.9`
  - Environment: `production`
  - Memory layout: rss_mb=154, heap_used_mb=30, system_total_mb=7942
  - Uptime: 79871 seconds (can calculate boot time)
  - API latency stats: p50, p95, rolling avg
  - Database latency: 29-58ms
  - Queue depth: 0
  - Rate limiting: enabled
  - Session protection: configured

### 2. Information Disclosure — /api/config (SEVERITY: MEDIUM)
- **URL:** https://asknova.online/api/config AND https://api.asknova.online/api/config
- **Leaked data:**
  - API URL: https://api.asknova.online
  - Frontend URL: https://asknova.online
  - iOS App API base: https://api.asknova.online/api
  - iOS App URL scheme: asknova://
  - Environment: production

### 3. Exposed Admin Panel — /admin (SEVERITY: MEDIUM)
- **URL:** https://asknova.online/admin
- **Status:** 200 (accessible, loads admin page JS)
- **Auth required on API level:** /api/admin returns 401

### 4. Exposed Auth Endpoints (SEVERITY: INFO)
- /auth/login — 200 (login page)
- /auth/signup — 200 (signup page)
- /auth/reset-password — 200
- /auth/forgot-password — 200
- /api/auth/session — 200 (returns {authenticated: false})
- /api/auth/me — 401

### 5. Protected API Endpoints (SEVERITY: INFO)
- /api/users — 401 (exists, auth required)
- /api/projects — 401 (exists, auth required)
- /api/teams — 401 (exists, auth required)
- /api/admin — 401 (exists, auth required)

### 6. Disallowed Paths in robots.txt (SEVERITY: INFO)
- /admin
- /dashboard
- /auth/reset-password
- /invitations

---

## 🏗️ TECHNOLOGY STACK

| Component | Technology |
|-----------|------------|
| Frontend | Next.js (React) |
| Backend API | Node.js/Express |
| Server | nginx/1.24.0 (Ubuntu) |
| CDN | Cloudflare |
| Database | Unknown (latency ~29-58ms, likely PostgreSQL) |
| Auth | Custom (session-based) |
| Mobile | iOS app (asknova:// URL scheme) |

---

## 🎯 ATTACK SURFACE (PRIORITIZED)

### HIGH PRIORITY
1. **IDOR on /api/users, /api/projects, /api/teams** — Can we access other users' data?
2. **Admin panel bypass** — Can we access /admin without auth?
3. **Prompt injection** — The AI agent processes stack traces. Can we inject malicious input?
4. **SSRF via AI agent** — The AI likely makes requests. Can we make it reach internal services?

### MEDIUM PRIORITY
5. **Auth bypass** — Can we forge sessions or JWT tokens?
6. **Rate limiting bypass** — Can we brute force login?
7. **Path traversal** — Can we access internal files?
8. **API parameter tampering** — Can we manipulate AI behavior?

### LOW PRIORITY
9. **XSS** — In error messages, AI responses
10. **CORS misconfiguration** — Can we steal session data?
11. **Race conditions** — In signup/password reset flows

---

## 📝 NEXT STEPS (for challenge start)

1. Register an account immediately
2. Test IDOR on all authenticated endpoints
3. Test prompt injection via stack trace input
4. Test SSRF via AI agent
5. Fuzz all API endpoints
6. Test admin panel access
7. Check WebSocket connections
8. Analyze JavaScript bundles for hidden endpoints
