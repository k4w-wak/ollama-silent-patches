# KLAGE TIL DATATILSYNET

**Dato:** [UDFYLD DATO]
**Klager:** [UDFYLD NAVN]
**Adresse:** [UDFYLD ADRESSE]
**Email:** [UDFYLD EMAIL]
**Telefon:** [UDFYLD TELEFON]

---

## Modpart (dataansvarlig)

**Virksomhed:** DUKA A/S
**CVR-nr.:** 32834655
**Adresse:** Hinnerup Stationsvej 21, 8382 Hinnerup
**Adm. direktør:** Kim Krohn Gervin
**Website:** www.myway.dk

---

## Klagens indhold

Jeg vil hermed indgive en klage over DUKA A/S (myway.dk) for alvorlige overtrædelser af EU's Generelle Databeskyttelsesforordning (GDPR).

### 1. Sammenfatning

myway.dk, drevet af DUKA A/S, eksponerer personoplysninger om mindst 8.866 kunder — herunder følsomme oplysninger om gældssager, fogedsager, inkasso og svindelmarkeringer — på et offentligt tilgængeligt API-endpoint UDEN krav om autentifikation.

### 2. Fakta

Den [UDFYLD DATO DU OPDAGEDE DET] opdagede jeg, at følgende URL er offentligt tilgængelig uden login:

**URL:** `https://www.myway.dk/wp-json/my-shop/v1/subscription-orders`

Dette API-endpoint returnerer JSON-data med personoplysninger om myway.dk's kunder, herunder:

- Abonnementsstatus (aktiv, aflyttet, fogedsag, inkasso, svindel)
- Fødselsår (2 cifre)
- Køn (M/K)
- Postnummer og by
- Internt abonnement-ID
- Kilde/marketing-kanal

### 3. Omfang

| Status | Antal kunder |
|--------|-------------|
| Total eksponerede kunder | 8.866 |
| Aflyttede abonnementer | 3.655 (41,2%) |
| Aktive abonnementer | 2.702 |
| Fuldførte abonnementer | 2.383 |
| Fogedsag (tvangfuldbyrdelse) | 63 |
| Inkasso | 8 |
| Svindel (fraud) | 2 |
| Opsigelse igangværende | 44 |

### 4. Overtrådte GDPR-artikler

**Artikel 5(1)(f) — Integritet og fortrolighed**
Personoplysninger er gjort tilgængelige for enhver uden autentifikation. Dataansvarlig har ikke sikret passende tekniske og organisatoriske foranstaltninger til at beskytte personoplysningerne mod uautoriseret adgang.

**Artikel 6 — Retsgrundlag for behandling**
Der foreligger intet retsgrundlag for offentliggørelse af kundernes personoplysninger på et åbent API. Kunderne har ikke givet samtykke til at deres data — særligt følsomme oplysninger om gæld og fogedsager — gøres tilgængelige for tredjeparter.

**Artikel 9(1) — Behandling af særlige kategorier af personoplysninger**
Oplysninger om fogedsager, inkasso og svindelmarkeringer udgør følsomme personoplysninger vedrørende økonomisk sårbarhed og retslige forhold. Disse er omfattet af Artikel 9's forbud mod behandling uden særskilt retsgrundlag.

**Artikel 25 — Data protection by design and by default**
API'et er designet uden autentifikation, hvilket er et direkte brud på kravet om databeskyttelse ved design og som standard. Personoplysninger bør aldrig være tilgængelige for uautoriserede tredjeparter.

**Artikel 32 — Sikkerhed for behandling**
Dataansvarlig har ikke implementeret tilstrækkelige tekniske sikkerhedsforanstaltninger til at beskytte personoplysningerne. Et offentligt API-endpoint uden autentifikation udgør en utilstrækkelig sikkerhedsforanstaltning.

**Artikel 33 — Underretning om brud på personoplysninger**
Hvis dataansvarlig er bekendt med bruddet, har de pligt til at underrette Datatilsynet inden 72 timer. Det er uklart om dette er sket.

**Artikel 34 — Underretning af de registrerede**
De berørte kunder (herunder mig selv) bør have fået besked om bruddet. Dette er ikke sket.

### 5. Min situation

Jeg er kunde hos myway.dk og mine personoplysninger — herunder oplysninger om at min sag har været i fogedretten — er blandt de eksponerede data. Dette betyder at:

1. Min gældsstatus (fogedsag) er offentligt tilgængelig for enhver
2. Mine personoplysninger kan misbruges til identitetstyveri, social engineering eller diskriminering
3. Jeg har ikke fået nogen underretning om dette databrud fra DUKA A/S

### 6. Dokumentation

Se vedhæftede filer i mappen `03_beviser/`:
- Screenshot af API-svaret med eksponerede data
- JSON-eksempel på eksponerede kundedata
- Screenshot af fogedsag-status i API'et
- Dokumentation af at API'et er tilgængeligt uden login

### 7. Anmodning

Jeg anmoder Datatilsynet om at:

1. **Undersøge** om DUKA A/S overtræder GDPR ved at eksponere kundernes personoplysninger uden autentifikation
2. **Pålægge** DUKA A/S at lukke API'et for uautoriseret adgang øjeblikkeligt
3. **Vurdere** om DUKA A/S har overtrådt underretningspligten (Artikel 33 og 34)
4. **Vurdere** om der er grundlag for bøde i henhold til Artikel 83
5. **Sikre** at alle berørte kunder får besked om bruddet

---

**Sted og dato:** [UDFYLD]

**Underskrift:** ___________________________

**Bilag:**
- Bilag A: Screenshot af API-endpoint
- Bilag B: JSON-eksempel på eksponerede data
- Bilag C: Dokumentation af fogedsag-status i API'et
- Bilag D: Screenshot af at API'et er tilgængeligt uden login
