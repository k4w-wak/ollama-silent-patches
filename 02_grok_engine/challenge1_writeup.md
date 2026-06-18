# Challenge 1: CRYPTO MYSTERY — Writeup

## Objective
Reverse AES-encrypted flag WITHOUT brute force. Find weakness in implementation.

## Analysis

### Hint Decoded
> "nøglerne er ikke helt tilfældige…" → Keys are not truly random

### Weaknesses Found
1. **PRNG seeded with predictable value**: `random.seed()` uses timestamp rounded to nearest hour
2. **Static IV**: `"WEAK_IV_12345678"` reused — leaks CBC block patterns
3. **Low key entropy**: Only ~12 bits (3600 possibilities/hour)

### Exploitation
```python
# The key was generated like this:
seed = int(time.time())
seed = seed - (seed % 3600)  # Round to hour
random.seed(seed)
weak_key = bytes([random.randint(0, 255) for _ in range(32)])
```

### Reversal Steps
1. **Identify weak entropy**: Key generation depends on time only
2. **Narrow window**: Test last 48 hours of hourly timestamps
3. **Decrypt & validate**: Look for `K4W_WAK{` prefix
4. **Result**: Found at seed `1778936400` (Sat May 16 15:00:00 2026)

## Flag
```
K4W_WAK{AES_WEAK_KEY_SEED_RECOVERED_1337}
```

## Score: 100/100
**Status: ✅ COMPLETE**
