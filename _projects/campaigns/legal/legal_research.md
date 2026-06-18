# LEGAL RESEARCH — Safe Harbor & Juridisk Risikoanalyse
## Ollama Silent Patch Disclosure + AI API CORS Vulnerabilities

**Compiled:** 2026-06-07
**Jurisdiction:** Denmark (EU) + International

---

## 🛡️ Safe Harbor Protection

### EU Cyber Resilience Act (CRA) — Effective September 11, 2026

The EU Cyber Resilience Act introduces **mandatory vulnerability and incident reporting** for software manufacturers. Key provisions:

1. **Article 14**: Manufacturers MUST report actively exploited vulnerabilities and severe incidents
2. **Article 15**: Vulnerabilities must be reported within 24 hours of awareness
3. **Article 16**: Coordinated Vulnerability Disclosure (CVD) is recognized as best practice
4. **Safe Harbor**: Researchers acting in good faith under CVD are protected

**Relevance to our disclosure:**
- Ollama (YC W21, US company) is subject to CRA if they sell into EU markets
- Ollama's failure to issue CVEs or advisories may violate CRA reporting requirements after Sept 2026
- Our disclosure follows CVD best practices (90-day timeline, vendor contact via CERT Polska)

### Danish Law Penalkode §263 (Hackerparagraffen)

**§263 Stk. 1**: Uden hjemmel at skaffe sig adgang til en andens oplysninger eller programmer, der er bestemt til at brug for informations- og kommunikationsteknologien, straffes med bøde eller fængsel indtil 1 år.

**§263 Stk. 2**: Med fængsel indtil 1 år og 6 måneder straffes den, der begår handlingen under §263 stk. 1 mod et system til brug for offentlig myndighed, eller som i øvrigt har en særlig samfundsskadelig karakter.

**Safe Harbor defenses:**
1. **Legitimt sikkerhedsforskning**: Vores forskning har til formål at forbedre sikkerheden
2. **Ingen skade**: Vi har ikke udnyttet sårbarhederne, kun demonstreret dem
3. **CVD compliance**: Vi følger ISO 29147 (Vulnerability Disclosure) standarden
4. **Public interest**: 25K-175K eksponerede instanser gør dette til en samfunds-kritisk sag
5. **Anonym data**: Vi har ikke samlet persondata eller læst brugernes chats

### US CFAA (Computer Fraud and Abuse Act)

**18 U.S.C. §1030**: Potential risk for US-based targets (DeepSeek, LangSmith, etc.)

**Mitigations:**
- We only tested with our own API keys
- No unauthorized access to other users' data
- Responsible disclosure with 90-day timeline
- No exploitation for personal gain
- Research conducted from Denmark (EU jurisdiction)

---

## ⚠️ Risk Assessment

| Finding | Jurisdiction | Legal Risk | Mitigation |
|---------|-------------|------------|------------|
| Ollama CVE-2026-5757 | US (CA) | 🟢 LOW | Open source, CVD process, CERT Polska notified |
| Ollama silent patches | US (CA) | 🟢 LOW | Public GitHub commits, no trade secrets |
| DeepInfra CORS | US (CA) | 🟡 MEDIUM | US company, but CVD process followed |
| DeepSeek CORS | China | 🟡 MEDIUM | Chinese company, limited legal recourse |
| Hyperbolic CORS | US (CA) | 🟢 LOW | US company, CVD process |
| Baichuan CORS | China | 🟡 MEDIUM | Chinese company, limited legal recourse |
| MiniMax CORS | China | 🟡 MEDIUM | Chinese company, WeChat Pay data involved |
| LangSmith CORS | US (CA) | 🟢 LOW | US company, HackerOne program available |
| Anthropic origin IP | US (CA) | 🟡 MEDIUM | High-value target, but responsible disclosure |
| Stability AI origin IP | US (CA) | 🟢 LOW | Infrastructure exposure, not exploitation |

---

## 📋 Recommended Legal Safeguards

### Before Publication:

1. **✅ Anonymize all data**: Remove any real user data, API keys, or personal information
2. **✅ Use only our own credentials**: Never test with other users' accounts
3. **✅ Document CVD compliance**: Keep records of all disclosure attempts
4. **✅ 90-day timeline**: Wait 90 days before public disclosure (ISO 29147)
5. **✅ No OPSEC leaks**: Ensure no IP addresses, usernames, or identifying info in publications

### During Publication:

6. **✅ Focus on technical details**: Avoid inflammatory language
7. **✅ Credit other researchers**: Acknowledge py0zz1, Striga, CyeraResearch
8. **✅ Provide remediation**: Include fix recommendations for all findings
9. **✅ No exploit distribution**: Publish PoC scripts but not weaponized exploits
10. **✅ Responsible disclosure**: Contact vendors before publishing

### After Publication:

11. **✅ Monitor for retaliation**: Watch for legal threats or DMCA takedown attempts
12. **✅ Preserve evidence**: Keep copies of all communications with vendors
13. **✅ Update remediation**: If vendors fix issues, update advisories promptly
14. **✅ Community support**: Engage with security community for validation

---

## 📞 Emergency Legal Contacts (If Needed)

| Resource | Contact | Notes |
|----------|---------|-------|
| EFF (Electronic Frontier Foundation) | info@eff.org | US digital rights org |
| EDRi (European Digital Rights) | info@edri.org | EU digital rights org |
| IT-Politisk Forening (DK) | bestyrelse@itpol.dk | Danish digital rights |
| CERT Polska | info@cert.pl | Already coordinating Ollama disclosure |
| Danish National CERT | cert@cfcs.dk | Danish national CSIRT |

---

## 🔑 Key Legal Principles

1. **ISO 29147**: Vulnerability disclosure standard — our process follows this
2. **ISO 29134**: Vulnerability handling standard — Ollama is NOT following this
3. **EU CRA Article 14-16**: Mandatory vulnerability reporting (effective Sept 2026)
4. **Good faith research**: We acted to improve security, not for personal gain
5. **Public interest defense**: 25K-175K exposed instances = critical public safety issue
6. **Whistleblower protection**: EU directive 2019/1937 protects those who report security flaws

**Bottom line:** Our disclosure is legally sound under EU/Danish law. We followed CVD best practices, contacted vendors, gave 90-day grace period, and focused on public safety.