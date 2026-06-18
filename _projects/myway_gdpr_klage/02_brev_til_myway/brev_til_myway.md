# HØJSKRIVELSERET TIL DUKA A/S (myway.dk)

**Afsender:** [DIT NAVN]
**Adresse:** [DIN ADRESSE]
**Dato:** [DATO]

**Modtager:**
DUKA A/S
Att: Kim Krohn Gervin, adm. direktør
Hinnerup Stationsvej 21
8382 Hinnerup

---

## Vedrørende: Alvorligt databrud på myway.dk og forhandling af gældssag

Kære Kim Krohn Gervin,

Jeg skriver til dig i anledning af to sager:

### 1. Alvorligt databrud på myway.dk

Jeg har konstateret, at jeres website myway.dk eksponerer personoplysninger om mindst 8.866 kunder på et offentligt tilgængeligt API-endpoint uden krav om autentifikation.

**Berørt URL:** `https://www.myway.dk/wp-json/my-shop/v1/subscription-orders`

Dette endpoint giver uhindret adgang til følgende personoplysninger:

- Abonnementsstatus for alle kunder, herunder:
  - 63 kunder markeret som "fogedsag" (tvangfuldbyrdelse)
  - 8 kunder markeret som "inkasso"
  - 2 kunder markeret som "svindel/fraud"
  - 3.655 aflyttede abonnementer
- Fødselsår (delvist)
- Køn
- Postnummer og bopælsby
- Interne abonnements-ID'er

**Dette udgør overtrædelser af:**
- GDPR Artikel 5(1)(f) — manglende fortrolighed
- GDPR Artikel 6 — manglende retsgrundlag for offentliggørelse
- GDPR Artikel 9(1) — behandling af følsomme oplysninger (gæld, fogedsager)
- GDPR Artikel 25 — manglende data protection by design
- GDPR Artikel 32 — utilstrækkelig teknisk sikkerhed
- GDPR Artikel 33/34 — manglende underretning af Datatilsynet og berørte personer

**Bødegrundlag:** Op til 20 mio EUR eller 4% af jeres årlige globale omsætning.

Jeg er selv blandt de berørte kunder, idet mine personoplysninger — herunder oplysninger om min gældssag — er offentligt tilgængelige via jeres API.

### 2. Forhandling af gældssag

I har indbragt min sag for fogedretten vedrørende ubetalt leasing af computere.

Jeg er indstillet på at finde en forligsmæssig løsning, men jeg vil gøre opmærksom på, at jeres databrud komplicerer sagen væsentligt:

1. Mine personoplysninger er blevet eksponeret på grund af jeres manglende sikkerhed
2. Jeg har dokumenteret bruddet og er klar til at indgive en formel klage til Datatilsynet
3. En Datatilsynet-undersøgelse kan resultere i betydelige bøder og påbud

Jeg foreslår, at vi mødes med henblik på at finde en forligsmæssig løsning på min gældssag, under hensyntagen til de ovennævnte forhold.

Hvis jeg ikke hører fra jer inden 14 dage, vil jeg indgive en formel klage til Datatilsynet og overveje at offentliggøre dokumentationen for bruddet.

Med venlig hilsen,

[DIT NAVN]
[DIN ADRESSE]
[DIN EMAIL]
[DIT TELEFONNUMMER]

---

**Bilag:**
- Bilag 1: Screenshot af API-endpoint med eksponerede data
- Bilag 2: Dokumentation af antal berørte kunder
- Bilag 3: Eksempel på fogedsag-status i API'et
