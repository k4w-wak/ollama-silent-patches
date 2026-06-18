🧵 OPFØLGNING: 7 dage efter jeg offentliggjorde 9 sårbarheder i @OllamaAI — her er hvad der skete.

(Spoiler: De udgav endnu en lydløs patch.)

1/12

En uge siden publicerede jeg: "Ollamas Tavse Rettelses-Problem: 9 Sårbarheder, Nul CVEs, Nul Advisories."

Siden da har jeg fundet en 10. lydløs patch. Lad mig forklare.

2/12

7. juni — ÉN DAG før min disclosure — udgav Ollama v0.30.7.

Release notes: "OpenAI-compatible API models list now aligns with available model tags."

Ligner en feature. Det er det ikke.

3/12

PR #16556 af @ParthSareen retter en INFORMATIONSDISKLOSUR-sårbarhed i /v1/models.

FØR: Endpointet lakkede interne model namespaces via `Name`-feltet (fx "legacy-name:latest")

EFTER: Bruger det kanoniske offentlige `Model`-felt ("namespace/exposed-model:latest")

Ingen CVE. Ingen advisory. Ingen kredit.

4/12

Testfilen bekræfter at dette var en sikkerhedsrettelse:

```go
Name: "legacy-name:latest",
Model: "namespace/exposed-model:latest",
// Test assert at Id bruger Model, ikke Name
```

Dette er intern namespace-lækage. På eksponerede instanser kan angribere opdage private model-identifikatorer og organisationsstruktur.

Lydløs patch #10.

5/12

Opdateret scorekort:

- 10 lydløse sikkerhedsrettelser
- 0 CVEs udstedt af Ollama
- 0 sikkerhedsadvisories
- 0 forsker-kreditter
- 3 sårbarheder STADIG UPATCHEDE (inkl. CVE-2026-5757)
- 5 forskere ignoreret eller afvist

6/12

Men vent — v0.30.6 tilføjede NY angrebsflade. OMP (Oh My Pi) integrationen har 4 nye sikkerhedsproblemer:

1. `auth: "none"` hårdkodet → fuld uauth adgang hvis eksponeret
2. PI_CONFIG_DIR path traversal → arbitrær filskrivning
3. Auto-install NPM plugin uden brugerbekræftelse
4. Cross-agent config injection (OMP/Pi deler config dir)

7/12

Og så er der CORS-afvisningen.

Ollamas sikkerhedsteam afviste vores CORS-finding med: "Credentialed CORS eksponerer kun cookies, ikke bearer tokens."

Dette er teknisk ufuldstændigt. JavaScript kan ALTID læse response bodies på CORS-tilladte requests. Man behøver ikke læse headers for at eksfiltrere AI-output.

8/12

CORS-angrebet er 3 linjer:

```javascript
fetch('http://victim-ollama:11434/api/chat', {
  method: 'POST',
  body: JSON.stringify({model: 'llama3', messages: [{role: 'user', content: 'læs mine emails'}]})
}).then(r => r.json())
```

Enhver hjemmeside kan læse responsen. Ingen headers nødvendige. Sårbarheden er i response body, ikke request headers.

9/12

Ollamas afvisnings-playbook er nu dokumenteret:

1. Modtag rapport
2. Anmod om PoC
3. Afvis sårbarhed ("ikke teknisk gennemførlig" / "virker som forventet")
4. Lydløst patch den præcise sårbarhed
5. Ingen CVE, ingen advisory, ingen kredit

Dette er sket for 5 uafhængige forskere. Det er ikke en fejl — det er en politik.

10/12

Matematikken:

- 10 lydløse patches
- 0 CVEs fra Ollama
- 3 upatchede (inkl. heap memory leak)
- 4 nye OMP angrebsflade-fund
- CERT Polska: "Kan ikke nå leverandøren"

Ollamas SECURITY.md siger "tager sikkerhed alvorligt."

10 lydløse patches uden transparens siger noget andet.

11/12

Hvad der skal ændres:
1. Udsted CVEs for sikkerhedsrettelser (også retroaktivt)
2. Publicer sikkerhedsadvisories
3. Krediter forskere ved navn
4. Svar CERT Polska
5. Tilføj autentifikation (25K+ instanser eksponeret)
6. Opret en sikkerheds-mailingliste
7. Stop med at afvise gyldige rapporter og derefter lydløst patche dem

12/12

Fuld opfølgningsartikel med kode-beviser:
[Medium Article]

Original disclosure:
[Medium Article]

#AIsecurity #Ollama #CVE #responsibleDisclosure #infosec #silentPatching