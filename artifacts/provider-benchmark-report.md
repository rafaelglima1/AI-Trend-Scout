# AI TREND SCOUT — PROVIDER BENCHMARK REPORT V1.0

**Generated:** 2026-08-20 03:46 UTC

---

# STATUS

```text
STATUS: PASS
```

**PROVIDERS TESTED:** meta_official, bright_data, apify

---

# PROVIDER COMPARISON

| Metric | meta_official | bright_data | apify |
|---|---|---|---|
| Records Returned | 0 | 0 | 333 |
| Unique Records | 0 | 0 | 333 |
| Duplicate Rate | 0.0000 | 0.0000 | 0.0000 |
| Freshness Rate | 0.0000 | 0.0000 | 0.8841 |
| Metadata Completeness | 0.0000 | 0.0000 | 0.8978 |
| Creator Diversity | 0.0000 | 0.0000 | 0.8667 |
| Successful Runs | 0 | 0 | 10 |
| Latency (s) | 0.0000 | 0.0000 | 13.3200 |

---

# DISCOVERY QUALITY SCORES

| Provider | Freshness | Coverage | Metadata | Reliability | Diversity | Cost | Validation | **TOTAL** |
|---|---|---|---|---|---|---|---|---|
| meta_official | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 80.0 | 50.0 | **13.0** |
| bright_data | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 80.0 | 50.0 | **13.0** |
| apify | 88.41 | 100 | 89.78 | 100.0 | 86.67 | 80.0 | 50.0 | **87.82** |

---

# TREND READINESS SCORES

| Provider | Temporal Data | Creator Diversity | Engagement | Dedup Quality | **TOTAL** |
|---|---|---|---|---|---|
| meta_official | 0.0 | 0.0 | 0.0 | 100.0 | **20.0** |
| bright_data | 0.0 | 0.0 | 0.0 | 100.0 | **20.0** |
| apify | 88.41 | 86.67 | 80.0 | 100.0 | **88.61** |

---

# EVIDENCE READINESS SCORES

| Provider | Source Reliability | Metadata Depth | Freshness | Repeatability | **TOTAL** |
|---|---|---|---|---|---|
| meta_official | 0.0 | 0.0 | 0.0 | 100 | **20.0** |
| bright_data | 0.0 | 0.0 | 0.0 | 100 | **20.0** |
| apify | 100.0 | 89.78 | 88.41 | 100 | **94.62** |

---

# RECOMMENDATION

**PRIMARY:** apify (DQ: 87.82)
**SECONDARY:** meta_official (DQ: 13.0)
**VALIDATION:** bright_data (DQ: 13.0)

---

# NOTES

- All providers require environment variables for credentials
- No credentials were hardcoded
- Raw responses were preserved
- Normalization applied deduplication
- Freshness measured against 48h window
