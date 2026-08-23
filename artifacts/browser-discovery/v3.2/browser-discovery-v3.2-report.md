# V3.2 — LIKE RELIABILITY INVESTIGATION REPORT

| Metric | Value |
|---|---|
| timestamp | 2026-08-23T04:57:12.350200+00:00 |
| total_posts | 50 |
| beleza | 25 |
| marketing | 25 |
| v2_available | 49 |
| v3_available | 43 |
| v2_availability | 0.98 |
| v3_availability | 0.86 |
| exact_match | 24 |
| v2_only | 7 |
| v3_only | 1 |
| disagreement | 18 |
| both_null | 0 |
| mean_abs_diff | 862.4047619047619 |
| median_abs_diff | 0.0 |
| max_abs_diff | 25062 |
| v2_source | {'TEXT_OG': 24, 'VISIBLE_TEXT': 25, 'UNKNOWN': 1} |
| v3_source | {'TEXT_OG': 43, 'UNKNOWN': 7} |
| dis_source_same | 0 |
| dis_source_diff | 18 |
| total_duration | 206.98 |
| average_seconds_per_post | 4.14 |
| nav_errors | 0 |
| timeouts | 0 |
| auth_required | 0 |
| captcha | 0 |
| external_provider_cost | 0 |

## Key Findings

1. V2 availability 98%% (49/50) vs V3 availability 86%% (43/50).
2. Exact match only 48%% (24/50) - low agreement between extractors.
3. All 18 disagreements: V2 source=VISIBLE_TEXT (DOM), V3 source=TEXT_OG (og:description).
4. V2 VISIBLE_TEXT values are false positives - grab arbitrary small numbers from unrelated DOM content, NOT the post real like count.
5. V3 TEXT_OG values match og:description but have a K-scaling bug (16K parsed as 16, not 16000).

## Conclusion
The V2=90%% vs V3=80%% gap was NOT a real V3 regression. V2 produced false-positive like values from DOM visible text. V3 og:description extraction is more reliable for detection but has a K-scaling value bug.