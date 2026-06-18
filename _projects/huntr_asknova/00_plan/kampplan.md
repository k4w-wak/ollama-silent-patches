# KAMPPLAN — Hack AskNova Challenge

**Target:** asknova.online
**Prize:** $15,000
**Start:** 12 juni 2026, 05:00 CEST
**Type:** AI/ML bug bounty challenge

## TIDLINJE

| Tidspunkt | Handling |
|-----------|----------|
| 04:50 CEST | Vågn op. Kaffe. Klar. |
| 05:00 CEST | Challenge starter — BEGYND RECON |
| 05:00-06:00 | Fuld recon: nmap, httpx, nuclei, dir_scan |
| 06:00-08:00 | Identificer attack surface |
| 08:00-12:00 | Eksploitér — test alt |
| 12:00+ | Skriv submissions, dokumentér findings |

## ATTACK SURFACE — AI/ML Platform

### Hoej prioritet (AI-specifik)
1. Prompt injection — manipuler AI-agenten
2. Data exfiltration — adgang til andre brugeres data
3. Authentication bypass — tilgaa andres konti
4. SSRF — AI-agent laver requests til interne systemer
5. Stock manipulation — manipuler AI'ens handelsbeslutninger
6. API abuse — usikre API-endpoints

### Medium prioritet (Web)
7. IDOR — tilgaa andre brugeres data via ID
8. XSS — reflected/stored i AI-interaktioner
9. SQL injection — i soeg/filter-funktioner
10. Rate limiting — brute-force eller spam

### Lav prioritet
11. Information disclosure — debug-endpoints
12. CORS misconfiguration
13. JWT manipulation
14. Race conditions — handelslogik

## VAERKTOEJER

RECON:     nmap, httpx, dns_enum, dir_scan, nuclei, osint
EXPLOIT:   ffuf, curl_api, playwright
DOC:       structured_finding, poc_video, poc_recorder

## PRE-CHALLENGE PREP

- [ ] Opret konto paa huntr.com
- [ ] Laes challenge regler grundigt
- [ ] Soerg for at alle vaerktoejer virker
- [ ] Kaffe klar
- [ ] Soevn nok i aften
