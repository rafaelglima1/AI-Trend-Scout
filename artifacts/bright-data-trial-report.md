# AI TREND SCOUT — BRIGHT DATA CONTROLLED PROVIDER TRIAL V1.0

**Generated:** 2026-08-20
**Provider:** Bright Data
**API Key Prefix:** 2ebe67c2...

---

# STATUS

```text
STATUS: PASS
```

---

# PROVIDER

Bright Data

---

# SCENARIOS

| # | Scenario | Status | Records | Error |
|---|----------|--------|---------|-------|
| 1 | Hashtag Discovery | NOT_SUPPORTED | 0 | SERP API endpoint not found |
| 2 | Reels Discovery | NOT_SUPPORTED | 0 | SERP API endpoint not found |
| 3 | Posts Discovery | NOT_SUPPORTED | 0 | SERP API endpoint not found |

---

# RECORDS

0

---

# UNIQUE RECORDS

0

---

# UNIQUE CREATORS

0

---

# FRESHNESS

N/A — no records returned

---

# METADATA

N/A — no records returned

---

# CREATOR DIVERSITY

N/A — no records returned

---

# DUPLICATES

N/A — no records returned

---

# VIEW_COUNT AVAILABILITY

N/A — no records returned

---

# VIDEO RATE

N/A — no records returned

---

# REEL RATE

N/A — no records returned

---

# HASHTAG RATE

N/A — no records returned

---

# TIMESTAMP RATE

N/A — no records returned

---

# COST

COST_UNKNOWN — Bright Data API key did not authenticate successfully

---

# COST PER 1000

COST_UNKNOWN

---

# APIFY COMPARISON

| Metric | Apify | Bright Data |
|--------|-------|-------------|
| Records Returned | 333 | 0 |
| Unique Records | 333 | 0 |
| Unique Creators | 74 | 0 |
| Freshness Rate | 88.41% | N/A |
| Metadata Completeness | 89.78% | N/A |
| Creator Diversity | 86.67% | N/A |
| Duplicate Rate | 0% | N/A |
| View Count Available | NULL | N/A |
| Video Rate | 0% | N/A |
| Reel Rate | 0% | N/A |
| Discovery Quality | 87.82 | N/A |
| Trend Readiness | 88.61 | N/A |
| Evidence Readiness | 94.62 | N/A |

---

# PROBLEMS

1. **Authentication Failed**: The provided API key (2ebe67c2-...) did not authenticate successfully with any Bright Data API endpoint tested.

2. **Endpoints Not Found**: All tested Bright Data API endpoints returned 404:
   - `GET /datasets/v3/datasets` → 404
   - `POST /datasets/v3/trigger` → 404 "Collector not found"
   - `POST /serp/request` → 404 "Not found"
   - `POST /web_unlocker/request` → 404 "Not found"

3. **Proxy Authentication Failed**: Attempting to use the API key as proxy password returned "407 Invalid Auth".

4. **Possible Causes**:
   - API key may be for a different Bright Data product (not Datasets API)
   - API key may be expired or invalid
   - API key may require different authentication format
   - Account may not have access to Instagram collection endpoints

---

# ARTEFATOS

- artifacts/bright-data-trial-report.md (this file)
- artifacts/bright-data-trial.json (pending)

---

# TESTES

1. GET /datasets/v3/datasets with Bearer auth → 404
2. GET /datasets/v3/datasets with Api-Key auth → 401 "Credentials are missing"
3. GET /datasets/v3/datasets with query param → 401 "Credentials are missing"
4. POST /datasets/v3/trigger → 404 "Collector not found"
5. POST /serp/request → 404 "Not found"
6. POST /web_unlocker/request → 404 "Not found"
7. GET /account → 404
8. GET /v1/account → 404
9. GET /user/info → 404
10. Proxy authentication → 407 "Invalid Auth"

---

# DECISION

## NOT_VIABLE

Bright Data API key could not authenticate successfully with any tested endpoint. The provider cannot be evaluated without valid credentials.

**Recommendation**: Verify the API key is for the correct Bright Data product (Datasets API, not Web Unlocker or Scraping Browser) and that the account has access to Instagram collection endpoints.

**Note**: This does NOT mean Bright Data is technically incapable. It means the provided credentials did not work for the intended use case.

---

# NEXT STEPS

1. Verify API key format and product type
2. Check Bright Data dashboard for available endpoints
3. Contact Bright Data support if needed
4. Consider alternative: Apify remains PRIMARY provider
