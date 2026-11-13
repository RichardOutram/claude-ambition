I added a Part II (sections 17–31) to `<workspace>/url-shortener-architecture.md`. It covers the areas the first version skimmed. Nothing has been load-tested; the throughput and latency numbers are estimates.

**What's new**
- **Latency budget and handler logic (§17–18):** a per-hop budget for the 50 ms p99 target, and pseudocode for the redirect handler with request coalescing, jittered TTLs and non-blocking analytics.
- **Code generation (§19):**
  - A 40-bit, 20+20 Feistel network maps counter values onto 7-character codes. That gives about 1.1T codes, so the worst case of ~15B links uses roughly 1.4% of the space.
  - ID block leasing keeps working for about 50 minutes if the allocator goes down.
  - Aliases are kept structurally distinct from generated codes, so they can never collide.
- **Key rotation:** changing the Feistel key would remap future counters onto codes already issued, causing collisions. The doc says never to rotate it, and keeps a conditional insert on every create as a backstop.
- **Consistency edge cases (§20):**
  - A create-then-click race, where a stale negative-cache entry would 404 a brand-new alias, is handled by write-through plus negative-cache deletion.
  - Takedown propagates through every cache layer, with a worst case under 60 seconds.
- **Hot keys and stampedes (§21):** five layers of defence for a viral link, plus a plan for a full Redis loss.
- **Multi-region (§22):** disjoint ID ranges per region, a single alias authority, and per-region capacity sized so losing one of three regions needs no scale-up.
- **Schemas (§23):** concrete Cassandra, Postgres and ClickHouse definitions.
- **Failure and security analysis (§24–25):**
  - A failure-mode table covers detection, impact, automatic response and recovery.
  - The 99.99% target works out to a 4.3 minute monthly error budget.
  - A threat model covers abuse, SSRF and enumeration.
- **Operations and decisions (§26–31):**
  - Burn-rate alerts and synthetic probes, a headroom table with the main cost drivers, and runbooks, deploys and resharding.
  - Alternatives that were rejected, and a four-phase rollout.
  - Seven open questions to settle before building.

The doc says plainly that Postgres, Redis and a CDN are enough at 10k req/s. The partitioned store and multi-region work are later phases, added only when a measured need appears.