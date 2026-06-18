# BEVISER — myway.dk GDPR-brud

## 1. API-endpoint

**URL:** https://www.myway.dk/wp-json/my-shop/v1/subscription-orders

**Tilgængelighed:** Offentligt, ingen autentifikation krævet
**Dokumentationsdato:** [UDFYLD]
**Verificeret af:** [UDFYLD NAVN]

## 2. Datatyper eksponeret

Følgende personoplysninger er tilgængelige for enhver uden login:

| Felt | Beskrivelse | GDPR-kategori |
|------|------------|---------------|
| ID | Internt ordrenummer | Identifikator |
| post_status | Abonnementsstatus (inkl. fogedsag, inkasso, svindel) | **Følsom** (Artikel 9) |
| birthyear | Fødselsår (2 cifre) | Identifikator |
| gender | Køn (M/K) | Identifikator |
| postcode | Postnummer | Lokalisering |
| city | Bopælsby | Lokalisering |
| subhandle | Internt abonnement-ID | Identifikator |
| source | Marketing-kilde | Identifikator |

## 3. Statistik over eksponerede data

| Status | Antal | Procent |
|--------|-------|---------|
| Total eksponerede kunder | 8867 | 100% |
| wc-cancelled | 3655 | 41.2% |
| wc-mw-active-sub | 2702 | 30.5% |
| wc-completed | 2383 | 26.9% |
| wc-mw-fogedsag | 63 | 0.7% |
| wc-mw-opsigelse | 44 | 0.5% |
| wc-mw-incasso | 8 | 0.1% |
| wc-mw-esignature | 6 | 0.1% |
| wc-mw-fraud | 2 | 0.0% |
| wc-mw-creditcheck-in | 2 | 0.0% |
| wc-on-hold | 1 | 0.0% |
| wc-mw-ready-to-ship | 1 | 0.0% |


## 4. Eksempel på fogedsag-data (anonymiseret)

```json
{
  "ID": "[FJERNET]",
  "post_status": "wc-mw-fogedsag",
  "birthyear": "00",
  "gender": "M",
  "postcode": "[FJERNET]",
  "city": "[FJERNET]",
  "subhandle": "[FJERNET]",
  "source": null
}
```

## 5. Eksempel på inkasso-data (anonymiseret)

```json
{
  "ID": "[FJERNET]",
  "post_status": "wc-mw-incasso",
  "birthyear": "41",
  "gender": "M",
  "postcode": "[FJERNET]",
  "city": "[FJERNET]",
  "subhandle": "[FJERNET]",
  "source": null
}
```

## 6. Eksempel på svindel-data (anonymiseret)

```json
{
  "ID": "[FJERNET]",
  "post_status": "wc-mw-fraud",
  "birthyear": "43",
  "gender": "M",
  "postcode": "[FJERNET]",
  "city": "[FJERNET]",
  "subhandle": "[FJERNET]",
  "source": null
}
```

## 7. Rå data

Fuld API-response er gemt i: api_raadata_100.json
**VIGTIGT:** Denne fil indeholder rigtige personoplysninger og skal behandles fortroligt.

## 8. Verifikation

For at verificere bruddet, åbn følgende URL i en browser uden at være logget ind:
https://www.myway.dk/wp-json/my-shop/v1/subscription-orders

Hvis API'et returnerer JSON-data med kundeoplysninger, er bruddet bekræftet.
