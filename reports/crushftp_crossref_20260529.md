# CrushFTP CVE-2024-4040 Cross-Reference Report
**Date:** 2026-05-29 07:27
**Source:** Censys Search Results — 100 hosts
**CVE:** CVE-2024-4040 (VFS Sandbox Escape, CVSS 10.0, CISA KEV)
**Query:** `host.services.port: "8080" AND host.services.endpoints.http.body: "CrushFTP WebInterface"`
**Method:** Passive analysis — no network requests, no OSINT tools

---

## (a) CIDR Overlap: 205.237.104.0/22

| Check | Result |
|-------|--------|
| **IPs in 205.237.104.0/22** | **0 of 100** |
| C2 range | 205.237.104.0 – 205.237.107.255 (1024 IPs) |
| CrushFTP overlap | **NONE** |

**Conclusion:** Zero CrushFTP hosts fall within the C2 infrastructure CIDR. The CrushFTP instances are NOT hosted on the same network as the C2 servers.

---

## (b) Provider Match: AS24940 / AS14061 / AS40021

| ASN | Provider | Hosts | IPs |
|-----|----------|-------|-----|
| AS24940 | Hetzner | 1 | 94.130.220.179 |
| AS14061 | DigitalOcean | 4 | 142.93.15.156, 165.22.104.156, 139.59.13.122, 143.198.47.116 |
| AS40021 | Krystal | 0 | — |
| **UNKNOWN** | Unmatched | 95 | Various |

**Provider match rate:** 5/100 (5%) — minimal overlap with known threat-actor hosting providers.

---

## (c) /24 Clusters (2+ hosts)

| /24 CIDR | Count | Organization Hint | IPs |
|----------|-------|-------------------|-----|
| **190.184.199.0/24** | **11** | MediaLine / PressSpot (Argentina) | .131–.152 |
| **12.234.252.0/24** | **5** | Colonial Press International (US) | .2–.9 |
| 50.222.125.0/24 | 2 | Comcast (US) | .4, .8 |
| 223.255.159.0/24 | 2 | Unknown (AP) | .214, .218 |
| 66.59.109.0/24 | 2 | Telecom Argentina | .20, .26 |
| 184.185.77.0/24 | 2 | Comcast (US) | .170, .179 |

**Key cluster:** 190.184.199.0/24 with 11 hosts — likely a single organization (MediaLine/PressSpot) running CrushFTP across multiple servers. This is a **high-value target cluster** for CVE-2024-4040 exploitation.

---

## (d) Version Fingerprint

| Status | Count | Notes |
|--------|-------|-------|
| **VULN** (<10.7.1 or <11.1.0) | 0 | No version headers in Censys data |
| **PATCHED** (≥10.7.1 or ≥11.1.0) | 0 | No version headers in Censys data |
| **UNKNOWN** | **100** | Censys body match only, no version leak |

> ⚠️ **All 100 hosts have UNKNOWN version status.** Censys matched on `CrushFTP WebInterface` in the HTTP body, but did not capture the `Server` header or version string. Active fingerprinting would be needed to determine patch status.

---

## (e) Top-5 Countries

| Rank | Country | Hosts |
|------|---------|-------|
| 1 | 🇺🇸 US | 35 |
| 2 | ❓ UNKNOWN | 63 |
| 3 | 🇦🇺 AU | 1 |
| 4 | 🇧🇷 BR | 1 |

> Note: 63 hosts have no reverse DNS TLD — country is unknown from passive data alone.

---

## Summary

| Metric | Value |
|--------|-------|
| **CIDR overlap (205.237.104.0/22)** | **0** |
| **Provider match (AS24940/AS14061/AS40021)** | **5** |
| **/24 clusters with 2+** | **6** |
| **Version VULN** | **0** |
| **Version UNKNOWN** | **100** |

---

## Conclusion: **SEPARATE**

The CrushFTP hosts are **unrelated** to the C2 infrastructure at 205.237.104.0/22:

1. **Zero CIDR overlap** — No CrushFTP host falls within the C2 network range
2. **Minimal provider overlap** — Only 5/100 hosts on Hetzner/DigitalOcean (common cloud providers)
3. **No shared infrastructure** — The CrushFTP clusters (190.184.199.x, 12.234.252.x) are in completely different network ranges
4. **These are potential VICTIMS** — The 100 CrushFTP hosts are likely **targets** of CVE-2024-4040 exploitation, not the C2 operators themselves

The most interesting finding is the **190.184.199.0/24 cluster** (11 hosts, MediaLine/PressSpot) which represents a single organization with a large CrushFTP footprint — potentially already compromised.

---

*Report generated passively — no network requests made.*
*All data from local Censys HTML export.*
