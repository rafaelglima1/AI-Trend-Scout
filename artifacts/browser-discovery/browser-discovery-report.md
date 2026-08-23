# BROWSER DISCOVERY POC — FINAL REPORT

**Generated:** 2026-08-20
**Provider:** browser (Playwright + Chromium)
**Session:** instagram_session.json (3 auth cookies)

---

# STATUS

```text
STATUS: PASS
```

---

# SCENARIOS

| # | Scenario | URL | Status | Records |
|---|----------|-----|--------|---------|
| 1 | fitness | /explore/tags/fitness/ | REDIRECT | 0 |
| 2 | beleza | /explore/tags/beleza/ | SUCCESS | 21 |
| 3 | marketing | /explore/tags/marketing/ | SUCCESS | 21 |

---

# DATASET

- **Total records:** 42
- **Unique records:** 42
- **Unique creators:** N/A (not extracted from listing page)
- **Duplicate rate:** 0.0000

---

# METRICS

| Metric | Value |
|--------|-------|
| Freshness | N/A |
| Metadata Completeness | 0.2000 |
| Creator Diversity | 0.0000 |
| Timestamp Availability | 0.0000 |
| Hashtag Availability | 0.0000 |
| Author Availability | 0.0000 |
| Text Availability | 0.0000 |
| Like Count Availability | 0.0000 |
| Comment Count Availability | 0.0000 |
| View Count Availability | 0.0000 |
| Video Rate | 0.0000 |
| Reel Rate | 0.0000 |
| Scenario Success Rate | 0.6667 |
| Browser Duration | 30.00s |

---

# MEDIA COVERAGE

- **Video Rate:** 0.0000 (listing page does not show media type)
- **Reel Rate:** 0.0000

Note: Media type detection requires visiting each post individually.

---

# VIEW COUNT COVERAGE

- **View Count Availability:** 0.0000

Note: View count is not displayed on the hashtag listing page.

---

# BLOCKING CONDITIONS

- **Auth Required:** False (after session load)
- **Blocked:** False
- **CAPTCHA:** False

---

# SESSION

- **Cookies:** 11 total
- **Auth Cookies:** 3 (sessionid, ds_user_id, csrftoken)
- **Session Valid:** True

---

# PER-SCENARIO RESULTS

## fitness

- **Status:** REDIRECT
- **URL:** https://www.instagram.com/explore/search/keyword/?q=%23fitness
- **Records:** 0
- **Error:** Instagram redirected hashtag page to keyword search

## beleza

- **Status:** SUCCESS
- **URL:** https://www.instagram.com/explore/search/keyword/?q=%23beleza
- **Records:** 21
- **Post IDs:** DV3ylaTEbxr, DQE0xxMjbEF, Da-hcNgAgCD, ...

## marketing

- **Status:** SUCCESS
- **URL:** https://www.instagram.com/explore/search/keyword/?q=%23marketing
- **Records:** 21
- **Post IDs:** DbY9d23RBoh, DQun3DlkaDt, ...

---

# RAW RECORD COUNT

42

---

# UNIQUE RECORD COUNT

42

---

# CREATOR COUNT

N/A (author not extracted from listing page; would require visiting each post)

---

# DUPLICATE RATE

0.0000

---

# FRESHNESS

N/A (timestamps not available from listing page)

---

# METADATA COMPLETENESS

0.2000 (only id, url, media_type available from listing)

---

# CREATOR DIVERSITY

0.0000 (author not available from listing page)

---

# VIDEO RATE

0.0000

---

# REEL RATE

0.0000

---

# VIEW COUNT AVAILABILITY

0.0000

---

# ARTIFACTS

- artifacts/browser-discovery/browser-discovery.json
- artifacts/browser-discovery/browser-discovery-report.md
- artifacts/browser-discovery/raw/scenario_beleza.json (21 records)
- artifacts/browser-discovery/raw/scenario_marketing.json (21 records)
- artifacts/browser-discovery/cache/all_contents.json (42 records)
- artifacts/browser-discovery/cache/instagram_session.json (session)
- artifacts/browser-discovery/screenshots/ (post-login screenshots)

---

# LIMITATIONS

1. **Listing page metadata is minimal:** The hashtag listing page only shows post links, not full metadata (author, likes, comments, timestamps, media type).

2. **To get full metadata**, each post would need to be visited individually, which increases:
   - Time per scenario
   - Risk of rate limiting
   - Risk of triggering anti-bot measures

3. **Instagram redirected #fitness** to a keyword search page instead of the hashtag page.

4. **Session persistence:** The session cookies work for headless collection but may expire.

---

# DECISION

## VIABLE

Browser discovery is technically viable for collecting post URLs from Instagram's public hashtag pages.

**However:**
- Listing pages provide minimal metadata
- Full metadata requires per-post extraction (slower, riskier)
- Apify provides richer data (author, likes, comments, timestamps, media type) in a single request

**Recommendation:** Browser discovery can serve as a VALIDATION layer or fallback, but Apify remains superior as PRIMARY discovery provider for metadata richness.
