# AskNova Recon Findings Summary
## Target: asknova.online / api.asknova.online
## Date: 2026-06-11
## Researcher: admin_user

---

## 🔴 CRITICAL FINDINGS

### 1. Sensitive Data Exposure via PUT /api/users/me
- **Endpoint**: `PUT /api/users/me`
- **Severity**: CRITICAL
- **Description**: The PUT /api/users/me endpoint returns the COMPLETE user object including:
  - **Password hash** (bcrypt `$2a$12$...`) — should NEVER be sent to the client
  - `githubAccessToken` (null but field exists)
  - `googleAccessToken` (null but field exists)
  - `stripeCustomerId`, `stripeSubscriptionId`, `stripePriceId`
  - `authVersion`, `sessionsRevokedAt`
  - All internal fields like `suspendedAt`, `suspensionReason`
- **Impact**: Password hash exposure enables offline cracking, OAuth token leak if linked

### 2. Broken Access Control: /api/system/access-unlock
- **Endpoint**: `POST /api/system/access-unlock`
- **Severity**: HIGH
- **Description**: The site password gate endpoint accepts ANY password and returns `{"success":true,"enabled":false}`. The password validation is completely bypassed.
- **Impact**: Site access protection is non-functional

### 3. AI Prompt Injection in /api/ai/debug
- **Endpoint**: `POST /api/ai/debug`
- **Severity**: HIGH
- **Description**: The `errorText` field is passed directly to the AI (Novara engine) without proper sanitization. Prompt injection can:
  - Influence AI output to mention internal env var names (DATABASE_URL, JWT_SECRET, OPENROUTER_API_KEY)
  - Manipulate the AI's classification system
  - Generate misleading "fixes" that could lead to security issues
- **Impact**: Prompt injection can influence AI behavior, extract internal system information

### 4. Information Disclosure via /api/health
- **Endpoint**: `GET /api/health` (no auth required)
- **Severity**: MEDIUM
- **Description**: Leaks:
  - Hostname: `unblocker-vm-1`
  - Version: `1.0.9`
  - Environment details
  - Memory usage
  - Database latency (29-58ms)
  - Uptime
- **Impact**: Internal infrastructure information exposure

### 5. Internal System Exposure via /api/ai/debug Response
- **Endpoint**: `POST /api/ai/debug`
- **Severity**: MEDIUM
- **Description**: The response exposes extensive internal system information:
  - AI engine name: "Novara"
  - AI provider: "openrouter" with model "openai/gpt-4o-mini"
  - Internal routing: "routerTarget": "openrouter-primary"
  - Tier policy: "free"
  - Prompt version: "2026-04-25.v2"
  - Full decision engine with strategy scores
  - Health snapshot with status info
  - Classification system details
  - Validation system details
  - Telemetry data
- **Impact**: Full internal system architecture disclosure

---

## 🟡 MEDIUM FINDINGS

### 6. Mass Assignment on PUT /api/users/me
- **Severity**: MEDIUM
- **Description**: Can send arbitrary fields including `role`, `emailVerified`, `billingPlan`, `githubAccessToken`, etc.
- **Note**: Fields like `role` and `emailVerified` don't persist, but the endpoint accepts them without validation

### 7. Admin Endpoints Exist (403 not 404)
- **Endpoints**: /api/admin/users, dashboard, config, settings, stats, analytics, logs, audit, system
- **Severity**: MEDIUM
- **Description**: All return 403 (Forbidden) not 404 (Not Found), confirming they exist and could be accessible with role escalation

### 8. DELETE /api/users/me Returns Internal Server Error
- **Severity**: MEDIUM
- **Description**: `DELETE /api/users/me` returns `{"error":"Internal server error"}` instead of proper 405 Method Not Allowed, suggesting the endpoint exists but crashes

### 9. /api/config Leaks Internal URLs
- **Severity**: LOW
- **Description**: Leaks API URLs and iOS app scheme (asknova://)

---

## 🔵 LOW FINDINGS

### 10. CUID-based IDs Enable Enumeration
- User ID: `cmq9tkatt0000mwj7vl35mfu8`
- Project ID: `cmq9tmevk000imwj750e9ahyd`
- Issue ID: `cmq9vqhbt002smwj71jbw6s9d`
- CUIDs are somewhat predictable

### 11. CORS/Origin Configuration
- api.asknova.online is the API subdomain
- asknova.online is the frontend
- Both behind Cloudflare

---

## TECH STACK IDENTIFIED
- **Frontend**: Next.js (React)
- **Backend**: Node.js/Express
- **Database**: PostgreSQL (Prisma ORM, CUID IDs)
- **AI Engine**: Novara (custom) → OpenRouter → GPT-4o-mini
- **Auth**: JWT (HS256), bcrypt password hashing
- **CDN**: Cloudflare
- **Server**: nginx/1.24.0 (Ubuntu)
- **Version**: 1.0.9
- **Hostname**: unblocker-vm-1

## ACCOUNT CREATED
- Email: testuser99k4w@proton.me
- Password: SecureP@ss1234!
- User ID: cmq9tkatt0000mwj7vl35mfu8
- Username: testuser99k4w
- Project ID: cmq9tmevk000imwj750e9ahyd
