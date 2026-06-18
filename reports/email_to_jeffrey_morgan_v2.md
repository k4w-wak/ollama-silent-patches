Jeffrey,

Jeg skriver direkte til dig, fordi dit security-team har ignoreret os i uger — og så patchedde I de samme sårbarheder vi rapporterede, uden advisory, uden credit.

Kort fortalt:

1. **18. maj**: Vi rapporterede critical vulns til security@ollama.com (unauthenticated model injection, GGUF OOB read). Bruce MacDonald bad om PoC. Vi leverede.

2. **1. juni**: Vi rapporterede CORS-angrebskæde via MiniMax API (PII theft — navn, email, Stripe ID). Michael Chiang afviste det som "not technically viable" — og sagde I havde ingen disclosure-aftale med os.

3. **3. juni** — to dage efter Michael afviste os — udgav I v0.30.2, som **silently patched de tre vulns vi identificerede**:
   - SSRF via BrowserOpen (CWE-918)
   - Data Exfiltration via Markdown Image Tags (CWE-200)
   - URL Policy Bypass via TrimRight (CWE-20)

Ingen advisory. Ingen CVE. Ingen credit. Release notes siger "Harden app markdown URL handling" — så vagt at det kunne være en kosmetisk ændring.

Jeffrey, det her er ikke responsible disclosure. Det er silent patching. Og det betyder at alle der kører pre-v0.30.2 stadig er sårbare — uden at vide det.

Jeg beder om tre ting:

1. **Udgiv en security advisory** for de tre vulns i v0.30.2
2. **Etabler en ordentlig disclosure-process** — jeres nuværende Google Group virker ikke
3. **Giv researchers credit** når I patcher det de har rapporteret

Jeg har allerede sendt CVE-anmodning til MITRE (MCID15789529) — det var en last resort, ikke en first choice.

Jeg tror på Ollama som projekt. Men jeres security-process er i stykker lige nu. Lad os fikse det sammen.

— admin_user
Security Researcher
admin_user@proton.me