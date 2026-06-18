# BUG BOUNTY PENTEST RAPPORT

**Target:** scanme.nmap.org  
**IP:** 45.33.32.156 (IPv6: 2600:3c01::f03c:91ff:fe18:bb2f)  
**Dato:** Juni 2025  
**Tester:** Lead Pentester (admin_user)  

---

## 1. FUND OVERSIGT

| # | Fund | Port/Scope | Severity |
|---|------|-----------|----------|
| 1 | Unencrypted HTTP (ingen HTTPS/TLS) | TCP 80 | **Medium** |
| 2 | Eksposeret SSH service | TCP 22 | **Info** |
| 3 | Manglende DNSSEC på domæne | DNS | **Low** |
| 4 | Manglende email autentificering (SPF/DKIM/DMARC) | DNS | **Info** |
| 5 | DNS zone data leakage (NS/MX/TXT tomme) | DNS | **Info** |
| 6 | 98 lukkede porte med RST — fingerprintbar host | Netværk | **Info** |

---

## 2. DETALJERET FUND ANALYSE

---

### FUND 1: Unencrypted HTTP — Ingen HTTPS/TLS på port 443

**Beskrivelse:**  
Målet eksponerer kun HTTP på port 80. Port 443 er lukket/udevendig, og der forefindes ingen TLS-certifikat. Al kommunikation foregår ukrypteret.

**CVSS v3.1 Score:** **5.3 (Medium)**  
- **Vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N`
- Attack Vector: Network
- Attack Complexity: Low
- Privileges Required: None
- User Interaction: None
- Scope: Unchanged
- Impact: Low confidentiality impact (aflytning af HTTP-trafik)

**Exploit Vektorer:**
1. **Man-in-the-Middle (MITM):** Angriber på samme netværk kan intercepte al trafik via ARP spoofing + packet capture.
2. **Session Hijacking:** Hvis målet sætter cookies uden Secure-flag, kan disse sniffes og genbruges.
3. **Credential Theft:** Login-forms på HTTP kan aflyttes i cleartext.
4. **SSL Stripping:** Hvis der findes mixed content eller subdomains med HTTPS, kan angriber force downgrade.
5. **Content Injection:** ISP eller netværksangribere kan injicere JavaScript i responses.

**Remediation:**
- Implementer TLS 1.2+ på port 443 med et gyldigt certifikat (Let's Encrypt anbefales)
- Redirect al HTTP (80) trafik permanent til HTTPS (301)
- Aktiver HSTS-header: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`
- Deaktiver svage cipher suites og gamle TLS versioner (<1.2)

---

### FUND 2: Eksposeret SSH Service

**Beskrivelse:**  
SSH (OpenSSH) kører på port 22/tcp og er tilgængelig fra internettet. Dette er normalt for UNIX-servere, men øger angrebsfladen.

**CVSS v3.1 Score:** **0.0 (Info)** — *Ingen aktuel sårbarhed bekræftet*
- **Vector:** `CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:N`
- Bemærk: Ingen version fundet, ingen auth bypass bekræftet. Markeret som Info indtil credentials eller sårbar version verificeres.

**Exploit Vektorer:**
1. **Brute-force:** Brug af default/common credentials mod root/admin konti.
2. **CVE exploitation:** Hvis forældet OpenSSH-version køres, kan sårbarheder som CVE-2024-6387 (regreSSHion) være aktuelle.
3. **Key Spraying:** Test af lækkede private SSH keys mod serveren.

**Remediation:**
- Begræns SSH-adgang via firewall (whitelist IP-ranges hvis muligt)
- Deaktiver password-auth, brug kun key-baseret autentificering
- Skift til non-standard port (security through obscurity + log noise reduktion)
- Hold OpenSSH opdateret og overvåg CVE-lists
- Implementer fail2ban eller lignende til rate-limiting

---

### FUND 3: Manglende DNSSEC

**Beskrivelse:**  
Domænet har ikke DNSSEC aktiveret. Dette betyder, at DNS-responses ikke er kryptografisk validerede og kan manipuleres.

**CVSS v3.1 Score:** **3.7 (Low)**  
- **Vector:** `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N`
- Integrity impact: Low — DNS-poisoning muligt under visse betingelser

**Exploit Vektorer:**
1. **DNS Cache Poisoning:** Angriber kan injecte falske DNS-records hvis resolver ikke validerer DNSSEC.
2. **Subdomain Takeover facilitator:** Manglende DNSSEC gør det nemmere at spoofe delegations.
3. **Phishing facilitator:** Man-in-the-middle kan omdirigere trafik til ondsindet server ved at forfalske A/AAAA records.

**Remediation:**
- Aktiver DNSSEC på domæne hos registrar
- Verificer DS records i parent zone
- Overvåg DNSSEC validation med third-party tools

---

### FUND 4: Manglende Email Autentificering (SPF/DKIM/DMARC)

**Beskrivelse:**  
Ingen TXT records fundet for SPF, DKIM eller DMARC. Selvom MX-record ikke findes (ingen mailserver), er dette en DNS-hygiene svaghed.

**CVSS v3.1 Score:** **0.0 (Info)**  
- **Vector:** Ikke scoret — ingen mail-infrastruktur detekteret
- Impact: Hvis mail senere aktiveres, vil domæne være sårbar overfor spoofing

**Exploit Vektorer:**
1. **Email Spoofing:** Hvis mail aktiveres senere, kan angribere spoofe @scanme.nmap.org uden beskyttelse.
2. **Phishing:** Brand misbrug via e-mail uden autentificeringschecks.

**Remediation:**
- Hvis mail skal bruges: Implementer SPF (`v=spf1`), DKIM key og DMARC (`p=quarantine` eller `p=reject`)
- Overvej at sætte en neutral/null DMARC record selv uden mail: `_dmarc.scanme.nmap.org TXT "v=DMARC1; p=none;"`

---

### FUND 5: DNS Zone Data (NS/MX/TXT tomme)

**Beskrivelse:**  
DNS enumeration afslørede ingen NS-records i DNSRECON output samt ingen MX eller TXT records. Dette indikerer enten en privat/ekstern DNS-konfiguration eller en begrænset zone.

**CVSS v3.1 Score:** **0.0 (Info)**  
- Ingen direkte sikkerhedsrisiko, men giver indsigt i infrastrukturen.

**Exploit Vektorer:**
- Recon facilitator: Begrænset DNS-data reducerer angribers informationsindsamling (positivt).
- Hvis dette skyldes misconfiguration, kan zone transfers (AXFR) testes yderligere.

**Remediation:**
- Verificer at dette er intended behavior
- Sørg for at DNS-servere ikke tillader zone transfers fra unauthorised hosts
- Test med `dig @ns1.example.com scanme.nmap.org AXFR`

---

### FUND 6: Host Fingerprinting via 98 lukkede porte

**Beskrivelse:**  
Nmap scan afslørede 98 lukkede TCP-porte, der returnerede RST-pakker. Dette bekræfter hostens eksistens og giver mulighed for OS fingerprinting.

**CVSS v3.1 Score:** **0.0 (Info)**  
- **Vector:** Ikke scoret — informationsafsløring

**Exploit Vektorer:**
1. **OS Fingerprinting:** RST-timing og TTL-værdier kan bruges til at gætte OS (f.eks. Linux kernel version).
2. **Network Mapping:** Angriber kan kortlægge firewall-regler og netværkssegmenter.

**Remediation:**
- Overvej at droppe pakker i stedet for RST på lukkede porte (stealth mode)
- Implementer IDS/IPS til at detektere og blokere scanning
- Brug host-firewall (iptables/nftables) til at begrænse responses

---

## 3. SAMLET RISIKOVURDERING

| Kategori | Antal |
|----------|-------|
| Critical | 0 |
| High | 0 |
| Medium | 1 (Unencrypted HTTP) |
| Low | 1 (Missing DNSSEC) |
| Info | 4 |

**Samlet vurdering:** Målet er en bevidst åben test-server (scanme.nmap.org). De identificerede fund er primært konfigurationsrelaterede og reflekterer formålet med hosten. Den mest signifikante risiko er fraværet af kryptering (HTTPS), som bør adresseres hvis målet anvendes til andet end public scanning-øvelser.

---

## 4. TEKNISKE NOTER OG BEGRÆNSNINGER

- **Dir scan** kunne ikke gennemføres pga. manglende wordlist (`/home/admin_user/SecLists/Discovery/Web-Content/common.txt`). Anbefaling: Installer SecLists eller angiv korrekt sti for at enable directory brute-force.
- **HTTPS** blev testet men port 443 var lukket — ikke en misconfiguration per se, men en manglende sikkerhedskontrol.
- **SSH-version** blev ikke fingerprintet i dette scan-sæt — anbefales tilføjet til næste runde (`nmap -sV -p22`).

---

## 5. ANBEFALET NÆSTE TRIN

1. Verificer SSH-version med service detection (`nmap -sV -p22`)
2. Genkør dir scan med SecLists wordlist installeret
3. Test for virtual hosts (vhost brute-force)
4. Test for API-endpoints (`/api`, `/swagger.json`, `/graphql`)
5. Content Discovery via waybackurls og gau (hvis scope tillader)
6. Hvis HTTPS implementeres: kør sslscan + sslyze for at verificere cipher-styrke

---

*Rapport genereret af Lead Pentester*  
*Scope: scanme.nmap.org | 45.33.32.156*
