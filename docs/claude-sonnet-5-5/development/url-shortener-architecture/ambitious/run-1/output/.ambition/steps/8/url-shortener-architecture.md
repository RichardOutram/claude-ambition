# URL Shortener Architecture (10k req/s)

Written for a design review. Every number below is either derived from a stated assumption (marked **[A]**), measured, or cited to a source, and the scripts in Appendix A recompute the derived and measured ones.

## 1. Summary

- **Load:** 10k req/s peak ≈ 9.9k redirects/s + 99 creates/s, assuming 100:1 reads to writes.
- **Core design:** `Client → CDN → stateless Redirect Service → Redis → KV store`. Creates go through a separate Create Service. Click analytics are asynchronous and never on the redirect path.
- **The cache is an optimization, not a dependency.** The datastore is sized to take 100% of redirect reads (≈5k read units/s on DynamoDB, against a 40k default quota), so a cold or dead cache costs latency, not availability. The cache hit rate is highly sensitive to traffic skew (16%–92% in simulation with a cache holding 5% of links; 34–40% on a real page-view trace), so the design must not depend on it.
- **Short codes:** random 7-character base62 with a conditional insert (retry on conflict). Collision odds are 0.085% per insert at 3B links, so retries are rare, and there is no ID service to run.
- **Storage:** replicated key-value store (DynamoDB, Cassandra or Scylla). Sharded Postgres is the main alternative, and Section 3 says when it wins.
- **Redirect:** 302 with a 60 s `max-age`. The trade-off against 301 is in D1.
- **Stretch to 100k req/s:** the same architecture gets there, but the "DB can take 100% of reads" property breaks above ~80k reads/s on DynamoDB's default quota, Redis must shard, and instance count (12–34) depends on a load test (Section 8).
- **Abuse is designed in, not bolted on:** an attacker guessing 7-character codes can find ~736k live links a day, so unlisted links use 11 characters; analytics store keyed, rotating IP hashes (Section 6).

```
                 ┌──────────┐   miss   ┌───────────────┐
  Client ───────▶│ CDN/Edge │─────────▶│ L7 LB (TLS,   │
                 └──────────┘          │  rate limit)  │
                                       └───────┬───────┘
                          GET /{code}          │         POST /links
                     ┌─────────────────────────┴──────────────┐
              ┌──────▼───────┐                        ┌───────▼──────┐
              │ Redirect Svc │ (3+, stateless)        │  Create Svc  │ (2+)
              │ + in-proc LRU│                        │ validate,    │
              └──┬────────┬──┘                        │ random code, │
          hit    │        │ async, droppable          │ cond. insert │
        ┌────────▼──┐     │                           └───────┬──────┘
        │  Redis    │     ▼                                   │
        │ primary + │  ┌───────┐   ┌────────────┐             │
        │ replica   │  │ Kafka │──▶│ ClickHouse │             │
        └────┬──────┘  └───────┘   └────────────┘             │
          miss│                                                │
        ┌─────▼────────────────────────────────────────────────▼──┐
        │  KV store, RF=3, multi-AZ (sized for 100% of reads)     │
        └──────────────────────────────────────────────────────────┘
```

### Scope and non-goals

**In scope:** create, redirect, delete/disable, basic click counts, abuse controls, and the capacity and failure analysis for 10k req/s peak in a single region across three availability zones.

**Not decided here:** multi-region active-active (single region plus CDN is enough for the stated target; add regions only if the availability SLO or latency to distant users demands it), user accounts and billing, a web UI, custom domains, QR codes, link editing after creation, and the legal and retention policy for click data (the document gives a technical default and flags it for legal review).

## 2. Load model and numbers

Assumptions are marked **[A]**. Change them in `capacity.py` and re-run.

| Quantity | Value | Derivation |
|---|---|---|
| Peak total | 10,000 req/s | given |
| Read:write ratio **[A]** | 100:1 | read-heavy by nature of the product. No audited public figure exists; the only derivable one is ~14 lifetime clicks per link from an undated Bitly infographic (500M links, 7B clicks), which would mean ~14:1. See the sensitivity table below |
| Peak redirects | 9,901/s | 10,000 × 100/101 |
| Peak creates | 99/s | 10,000 − 9,901 |
| Peak:average **[A]** | 3:1 | a week of Wikipedia hourly totals shows only 1.33:1 for the daily cycle (A6); 3:1 leaves room for campaign bursts |
| Average creates | 33/s ≈ 1.04B/yr | 99 ÷ 3 × 86,400 × 365 |
| Links after 5 years | 5.2B average case, 15.6B if creates ran at peak all day | |
| Row size **[A]** | 500 B | code + URL (~200 B avg) + metadata + index |
| Storage after 5 years | 2.6 TB (average) to 7.8 TB (peak case), before replication; ×3 = 7.8–23 TB | |
| Key space | 62⁷ = 3.5 × 10¹² | 7 chars; 5y average case fills 0.15%, peak case 0.44% |
| DB reads if cache is dead | 9,901/s ≈ 4,950 read units/s | DynamoDB eventually-consistent read ≤4 KB = 0.5 unit; default quota is 40,000 per table |
| DB reads at various hit rates | 80%: 1,980/s · 90%: 990/s · 95%: 495/s · 99%: 99/s | 9,901 × (1 − hit) |
| Redis memory for 100M hot links **[A]** | 20 GB | ~200 B per entry |

**The read:write ratio moves the storage numbers more than anything else; the design survives it.** Re-running the model for other ratios (A6):

| Reads per create | Peak creates/s | Avg creates/s (÷3) | Links in 5y | Storage in 5y (500 B) | Key space used |
|---|---|---|---|---|---|
| 14:1 | 667 | 222 | 35B | 17.5 TB | 1.0% |
| 50:1 | 196 | 65 | 10.3B | 5.2 TB | 0.29% |
| **100:1** | 99 | 33 | 5.2B | 2.6 TB | 0.15% |
| 1000:1 | 10 | 3 | 0.5B | 0.3 TB | 0.01% |

At 14:1, storage is nearly 7× the base case and the Postgres-vs-KV decision (D3) tips even harder toward KV. Every other decision holds: conditional-insert collisions stay near 1% even at 35B links, 7-character codes still fit, and 667 creates/s is well within DynamoDB's per-table write quota. Get the real ratio from product data before capacity planning. Do not treat the 100:1 row as established.

**Cache hit rate is the least certain number in this document.** The simulation (Appendix A2) draws requests from a Zipf-like popularity distribution, where link *k* gets traffic proportional to 1/kˢ:

| Skew *s* | Cache = 1% of catalog (LRU) | Cache = 5% of catalog (LRU) |
|---|---|---|
| 0.6 | 5.8% | 16.2% |
| 0.8 | 23.1% | 38.5% |
| 1.0 | 58.3% | 70.9% |
| 1.2 | 87.3% | 91.7% |

Published web-request studies report exponents from about 0.6 to 1.0 (Appendix B). I found no published exponent for short-link traffic specifically. A 95% hit rate needs *s* ≈ 1.2 or higher, so I do not assume it.

**Check against a real trace (Appendix A4).** A4 fits one hour of Wikipedia page views (939k distinct pages, 2.76M views, 2026-10-01 12:00 UTC). It is real request-popularity data, but it is not short-link traffic, so treat it as a sanity check on the simulation, not as a measurement of this product:

| Measured on the trace | Result |
|---|---|
| Zipf exponent, ranks 100–100,000 | *s* = 0.56–0.59 (about 1.0 only for the top 100 pages) |
| Share of views on the top 1% / 5% / 20% of pages | 23.5% / 40.0% / 65.4% |
| Cache = the previous hour's top 1% / 5% of pages, serving the next hour | 22.3% / 34.3% hit rate (the ideal for the same hour is 23.5% / 40.0%, so a stale cache loses about 1–6 points) |

This agrees with the simulation at *s* = 0.6–0.8 and says the realistic hit rate with a small cache (a few percent of the active set) is **roughly 20–40%, not 95%**. A cache holding most of the active set does much better; that costs memory, not throughput (D4). Two caveats: shortener traffic may be more bursty (new links spike then fade), which this trace does not capture, and its tail is probably longer. Measure *s* from real click logs in the first weeks and size Redis from that.

**Throughput is not the hard part.** Redis docs show non-pipelined runs of roughly 72k–180k ops/s on one instance (Appendix B), so 10k/s uses a fraction of one core. Redis is here for latency and DB load, not capacity. A5 measures a bare redirect hot path ( Node, 1M-entry in-process map, one process, `ab` over localhost on a 4-core laptop): **15.3k–16.6k req/s per process**. That supports the **[A]** ≥5k req/s per instance as a floor for the bare path. It excludes TLS (terminated at the LB), logging, the Redis hop, and Kafka emit, and `ab` shares the machine's CPU, so a production instance must be load-tested before this is relied on. Instance counts below come from availability (N+1 across 3 AZs), not CPU.

**Concurrency and headroom (queueing arithmetic, A7).** By Little's law, requests in flight = arrival rate × time in system: 9,901/s × 5 ms ≈ **50 concurrent** on the cache-hit path, and 9,901/s × 30 ms ≈ **297 concurrent** if every read goes to the database (178 at a 60% miss rate). With one AZ lost, two instances carry that, so each needs a datastore client pool allowing about 150 concurrent requests (check this against the client library's default limit). On headroom: in the simplest queueing model (M/M/1), mean waiting time is ρ/(1−ρ) times the service time, which is 1.5× at 60% utilisation, 4× at 80% and 9× at 90%. That is why the autoscale trigger is CPU > 60%. M/M/1 assumes highly variable service times, so it overstates delay for a uniform service like this one; treat it as a conservative guide and confirm with the load test.

## 3. Decisions and rejected alternatives

### D1. Redirect status: 302 with `Cache-Control: max-age=60`
| Option | For | Against |
|---|---|---|
| 301 | Browsers and CDNs cache indefinitely; least origin load | Clicks become invisible to analytics; delete/disable/edit cannot take effect for clients that cached it |
| **302 + max-age=60** | Edits and takedowns propagate within ~60 s; CDN can still absorb hot links | Some repeat clicks from the same browser skip analytics; origin sees more traffic than with 301 |
| 302, no cache | Exact analytics, instant takedown | CDN gives no relief; all 9.9k/s hits origin |

**Check the CDN before relying on this:** always send an explicit `Cache-Control` on the 302. Cloudflare's docs say it caches 302s for 20 minutes when no header is present and otherwise follows the header; Google Cloud CDN's docs list 302 as cacheable. I could not confirm CloudFront's behaviour for 302 from its documentation, so test the chosen CDN with a real request. Browsers may also cache a 302 that carries `max-age`, which is the analytics gap noted above.

**Flips to 301** if analytics are not a product requirement and links are immutable. **Flips to no-cache** if instant takedown (abuse, legal) outweighs origin load. The cold-cache analysis in Section 2 shows origin can take that load.

### D2. Short code generation: random 7-char base62, conditional insert
| Option | Collision behaviour (from `id_check.py`) | Cost | Verdict |
|---|---|---|---|
| **Random code + conditional insert, retry** | 0.085% per insert at 3B links, 0.28% at 10B, 2.8% at 100B; expected attempts 1.0009 at 3B | Needs a store with cheap conditional put (DynamoDB `attribute_not_exists`, SQL unique key, Cassandra `IF NOT EXISTS`). At 99 creates/s even Cassandra's slower conditional writes are fine | **Chosen** |
| Counter range leases + Feistel scramble | 0 collisions (2M IDs tested, all unique and invertible) | Needs a central counter (etcd/ZooKeeper/DB sequence), lease logic, and a secret key; if the scramble key leaks, codes become enumerable | Rejected: solves a collision problem that is rare at this scale, and adds a coordinator |
| Truncated hash of the URL | A 7-char truncation collides *somewhere* with certainty at 3B links (birthday bound) and needs the same conflict handling as random | Bonus: same URL gives the same code (dedup). But dedup conflicts with per-user links, expiries, and analytics | Rejected unless global dedup is a requirement |
| Plain sequential counter | None | Trivially enumerable: anyone can walk every link | Rejected |

**Flips to counter+scramble** if the store lacks a cheap conditional write, or if the table approaches ~10% of key space (≈3.5 × 10¹¹ links, ~20–70× the 5-year projection), where retries stop being negligible. The cheaper escape at that point is to move to 8 characters (62⁸ = 2.2 × 10¹⁴).

**Code hygiene.** Random codes are not neutral strings. 2.2% of random 7-character codes (lowercased) contain a 4+ letter English dictionary word (A6; the macOS word list, which is not a profanity list). At the base case's ~1B creates per year, that is ~22M codes a year containing real words. Some will be offensive, and codes appear under your brand's domain. The fix costs nothing because the create path already retries: reject any generated code that matches a blocklist after case-folding and common character substitutions, and generate again. About half of all codes (51%) contain a look-alike character (`0 O o 1 l I`), which matters if codes are ever read aloud or printed. Dropping those characters leaves a 56-character alphabet (56⁷ = 1.7 × 10¹²) and doubles the collision rate to ~0.17% at 3B links, which is still negligible. Decide this with the product team: yes for printed or spoken links, no otherwise.

**Guessability is a privacy decision, not a footnote (red team, Section 6).** A 7-character code is dense: at 3B links, 0.085% of random guesses hit a live link. An attacker making 10,000 guesses/s spread across many IPs finds ~8.5 live links/s, about **736,000 a day** (A7). 8 characters cut that to ~12,000 a day, and 11 characters (62¹¹ = 5 × 10¹⁹) to effectively none. People do shorten URLs that embed secrets (signed links, reset tokens, private documents), and those links are exposed by enumeration. Decision: public links use 7 characters; links the creator marks *unlisted* use 11, and the product states plainly that 7-character links are public by construction. **Flips to 11 characters for everything** if the product positions links as private. The cost is four extra characters in every URL.

Custom aliases use the same conditional insert; a conflict returns `409`. Reserve a blocklist (`api`, `admin`, etc.) so aliases cannot shadow routes.

### D3. Datastore: replicated KV store over sharded SQL
Access pattern: point lookup by `code`, append-mostly writes, no joins, a secondary lookup by `owner_id`.

| Option | For | Against |
|---|---|---|
| **KV / wide-column (DynamoDB, Cassandra, Scylla)** | Partition-by-key scaling and multi-AZ replication are built in; native TTL for expiry; 5.2B rows is routine | Weaker ad-hoc queries; the owner listing needs a GSI/separate table; eventual consistency on replicas |
| Single Postgres + read replicas | Familiar; strong consistency; ad-hoc SQL | 2.6–7.8 TB over 5y with 5.2B+ rows in one primary strains backup, vacuum, and failover; writes at 99/s are easy, the size is the issue |
| Sharded Postgres (Citus/Vitess-style) | SQL tooling plus scale | You run the sharding layer yourself |

**Flips to Postgres** if the 5-year horizon is under ~1B links (≈500 GB, fits one primary with replicas comfortably) and the team's operational skill is SQL. At 10k/s, 5 TB+ is where the KV store earns its place. Replica read capacity for PK lookups at 10k/s on Postgres is plausible but I have no sourced figure, so benchmark before relying on it.

Schema (`links`): `code` (partition key), `long_url` (≤2048 chars), `owner_id`, `created_at`, `expires_at` (native TTL), `status` (active/disabled/blocked). Replication factor 3; reads from a local replica; writes at quorum.

### D4. Cache strategy: cache-aside, with the DB sized for no cache
- **Layers:** CDN (60 s on hot links) → in-process LRU (~10k entries, 5–10 s TTL) → Redis → DB.
- **Pattern:** cache-aside on read; warm on create; delete on disable/edit. Write-through is rejected because 99 writes/s gives nothing to optimize and a dual write adds a consistency hazard.
- **Redis topology:** one primary + one replica (no cluster mode). 10k ops/s is far below single-instance limits; the only reason to shard is memory (>~64 GB working set).
- **TTL:** 24 h ±10% jitter to avoid synchronized expiry. Negative-cache unknown codes for 30 s so scans cannot bypass the cache to hammer the DB.
- **Stampede control:** single-flight per key inside each instance, so one miss produces one DB read per instance.
- **Sizing rule:** size Redis to hold the *active set* (links clicked within the TTL), not a percentage of all links ever created. Memory is cheap relative to the hit rate it buys: 1M entries ≈ 200 MB and 100M ≈ 20 GB at ~200 B per entry, so one 32 GB node holds ~150M links. Past that point the remaining misses are first-touch misses, which no cache removes. The active-set size is unknown until real traffic arrives, so start at 32 GB and resize from the measured hit ratio.
- **Rejected: no Redis at all** (DB + in-process LRU only). It is viable at this scale, because the DB can take 100% of reads. Redis is kept for p99 latency (sub-millisecond-plus-network instead of a DB read) and to cut per-read DB cost, not for throughput. **Flips to no-Redis** if the measured hit ratio stays under ~30% even with the active set fully cached, where the added moving part buys little. The Wikipedia check suggests a small cache lands near that line (20–40%), which is why the sizing rule above matters.
- **Rejected: sizing Redis for a 95% hit rate.** Neither the simulation nor the real trace supports it unless the active set fits in memory.

### D5. Separation of paths
- Redirect and Create are separate deployments, so a create-side bug or spike cannot take down redirects.
- Click events go to Kafka from a bounded in-memory buffer; if full, **drop events, not redirects**. Analytics (ClickHouse) is eventually consistent and its outage is invisible to users.

## 4. Request flows

**Redirect** `GET /{code}`: in-process LRU → Redis → DB. Unknown → 404; expired/disabled → 410. Budget: cache ≤5 ms, DB ≤30 ms, else 503. Emit click event asynchronously.

**Create** `POST /api/v1/links` (with `Idempotency-Key`; optional `unlisted: true` for an 11-character code, see D2): validate (http/https only, length cap, blocklist/Safe Browsing check, reject loops back to the shortener) → generate random code → conditional insert, retry on conflict (max 5) → warm cache → `201`. Alias conflict → `409`; blocked URL → `422`; limit → `429`.

Other endpoints: `DELETE /api/v1/links/{code}` (204, invalidates cache), `GET /api/v1/links/{code}/stats`.

## 5. Failure modes

| Failure | Effect | Response |
|---|---|---|
| Redis down | Latency rises; all reads hit DB (≈4,950 read units/s on DynamoDB, 12% of the default per-table quota) | Circuit breaker to DB; in-process LRU shields hot keys; **no outage if the DB is sized as in Section 2 and no single key exceeds the per-partition limit (next row)** |
| Cache cold start / deploy | Same as above for a short time | Single-flight; ramp traffic |
| DB node/AZ down | RF=3 quorum continues | Multi-AZ; alert on replica lag |
| DB fully unavailable | Cached links still redirect (in-process, Redis, CDN); new links and misses fail | Serve stale on error for hot links for a bounded window (e.g. 10 min `stale-if-error`); creates return 503. A link blocked for abuse is purged from the CDN at block time, so stale serving only risks links flagged during the outage itself |
| Kafka/ClickHouse down | Lost or delayed click counts only | Bounded buffer, drop on overflow |
| Hot-key storm (one viral link) | With Redis down, one key's reads land on one DB partition. DynamoDB allows ~3,000 read units/s per partition, ≈6,000 eventually-consistent reads/s of one key. On a real trace the top page carries 3.7% of views (≈370/s at 9.9k/s), so the limit needs ~61% of all traffic on one link. A viral link can still do that | CDN absorbs with the 60 s TTL; the in-process LRU (5–10 s TTL) bounds DB reads of one key to about one per instance per TTL, whatever the request rate; alert on single-key share >20% of traffic |
| Create Svc down | No new links; redirects unaffected | Separate deployment |
| URL scanner / Safe Browsing check unavailable | New destinations cannot be vetted; redirects unaffected | Fail closed for anonymous creates (`503`); trusted accounts may create and be scanned asynchronously, with auto-disable on a later hit |
| Code scanning/enumeration | Cache misses hit the DB, and live links leak (D2) | Negative cache; per-IP and per-network rate limits; challenge clients with a high 404 ratio; 11-character unlisted tier (D2) |
| ID service down | Not applicable | Eliminated by D2 |

Redirect Service: 3 instances across 3 AZs, so any 2 can carry peak (see assumption in Section 2), autoscaling at CPU > 60% (Section 2, queueing). Create Service: 2 instances.

## 6. Abuse, harm and security

Each row is an attack, who it harms, the evidence, and the design's response.

| Attack / misuse | Who is harmed | Finding | Design response |
|---|---|---|---|
| **Phishing and malware relay.** The shortener's domain hides the destination and lends it trust | Link recipients | A scan at creation checks only the destination of that moment; the destination can be swapped to a malicious page afterwards | Scan at creation and re-scan on a schedule and on abuse reports; no destination editing for anonymous links; auto-disable and purge the CDN on a hit; abuse-report endpoint with a time-to-takedown target |
| **Shortener chaining and open-redirect laundering** (our link to another shortener's link) | Recipients; reputation of the domain | Chains defeat destination scanning | Reject other shorteners' domains and our own as destinations; follow at most one redirect when scanning |
| **Header injection.** The user-supplied URL becomes the `Location` header | Recipients; cache integrity | A URL with CR/LF or control characters can split the response | Parse and re-serialise the URL, percent-encode, reject control characters and over-length input before storing |
| **Enumeration of unlisted links** | Creators whose URLs contain secrets | See D2: ~736k live links/day for a distributed attacker at 7 characters | 11-character unlisted tier; 404-ratio challenge; per-network limits |
| **Click-log de-anonymisation.** Analytics keep IP hashes | Link recipients | An unsalted hash of an IPv4 address is reversible by brute force: the 2³² addresses take ~0.5 h on one CPU core in pure Python, seconds on a GPU (A7) | Store a keyed hash (HMAC with a secret that is rotated daily), or truncate the address; discard raw IPs at ingest; set a retention limit (technical default: raw events 30 days, aggregates longer; confirm with legal) |
| **Storage and quota exhaustion** (mass creation) | Operators; honest users via throttling | A per-IP cap alone is easy to evade with many addresses | Per-account and per-network create quotas, CAPTCHA for anonymous creation, alert on create-rate anomalies |
| **Takedown latency** | Anyone being attacked by a live malicious link | A 302 can be cached by browsers for `max-age` and by CDNs for their default TTL if the header is missing (Cloudflare: 20 min) | Always send explicit `max-age=60`; purge CDN on block; accept ≤60 s browser tail |
| **Tracking of link recipients** | Link recipients | Click analytics record who clicked what | Disclose in the privacy policy; no cross-link identifiers; honour deletion requests |

Baseline controls: rate limiting at the LB, scheme allowlist (`http`/`https`), private-IP blocking if the scanner fetches URLs (SSRF), HTTPS only with HSTS, WAF at the edge.

## 7. Observability

- **SLOs:** redirect availability 99.95% (a budget of 21.6 minutes of downtime per 30 days); p99 server-side latency <50 ms.
- **Availability budget (A7).** Availabilities of components in series multiply. The redirect path has **four hard dependencies**: DNS/CDN, the load balancer, the Redirect Service, and the datastore (on a miss). Each must reach about 99.987% (≤5.4 min/month) for the product to reach 99.95%. A path with six dependencies at a typical 99.9% each gives 99.40% (259 min/month, 12× the budget). That is why Redis, Kafka, ClickHouse, the Create Service and the URL scanner are deliberately **soft**: none of them is allowed to fail a redirect, so none draws on this budget.
- **Metrics:** redirect RPS and latency percentiles, cache hit ratio, DB read latency and throttles, 4xx/5xx rate, Kafka lag, conditional-insert retry rate (should stay ~0.1%).
- **Alert on** burn rate of the availability SLO, DB throttling, and cache hit ratio falling sharply (a sign of a hot scan or a deploy problem).
- Synthetic probes from multiple regions.

## 8. Stretch: the same architecture at 100k req/s (10×)

Sections 1–7 are the design for the 10k req/s target. This section shows how far the same design stretches to **100k req/s peak** at the same SLOs (99.95% availability, p99 <50 ms), and where it stops. All figures are from A8 and use the Section 2 assumptions.

| Component | At 10k | At 100k | What changes |
|---|---|---|---|
| Redirects / creates (peak) | 9,901 / 99 per s | 99,010 / 990 per s | |
| Links after 5 years (average case) | 5.2B | 52B (26 TB; 78 TB peak case, before ×3) | KV store is the only sensible choice (D3); key space used 1.5% |
| Code collisions at 5 years | 0.15% per insert | 1.5% per insert | Still negligible; D2 unchanged |
| DB reads at 100% miss | 4,950 read units/s (12% of default quota) | **49,505/s (124% of the default 40k quota)** | **Breaks the "DB can take everything" property, see below** |
| Redis | 1 primary + replica | **3 shards** (33k ops/s each, 46% of the ~72k reference) | One instance would be at 138% of the documented reference figure |
| Redirect instances (60% CPU target) | 3 | **12–34** (18–51 with one AZ lost) | Range spans the measured 15k/s bare path and the 5k/s floor; the load test decides |
| Requests in flight | 50 hit / 297 miss | 495 hit / 2,970 miss | Spread over many more instances, so each pool stays at roughly 90–370 |
| Hottest key (trace-like skew) | ~370 reads/s (6% of the ~6,000/s partition ceiling) | ~3,700/s (**62%**) | Margin nearly gone |
| Click events | 10k/s | 99k/s ≈ 20 MB/s | Aggregate in-process (below) |

**Where it breaks first, in order:**

1. **The cache becomes a dependency.** At 100% miss the datastore needs 49.5k read units/s, 124% of the default per-table quota (40k). The quota is documented as adjustable (Appendix B), so the first move is to request a raise before launch. Otherwise the cache must hit at least 19% just to stay at the quota, and at least 43% to keep 30% headroom, and Redis then joins the hard-dependency chain: five hard dependencies instead of four, each needing 99.990% for the 99.95% SLO (R1). I have not confirmed that AWS would grant a raise to the needed level; treat it as a launch blocker to resolve with the provider. Cassandra or Scylla clusters have no such quota but need roughly 10× the nodes, which I have not sized.
2. **Redis must shard.** Three primaries with replicas, hash-slot cluster mode. Losing one shard sends a third of reads (~33k/s, ~16.5k read units/s) to the datastore, which is within the quota.
3. **Instance count depends on a number I could not measure.** 12 instances if production hot-path throughput is near the 15k req/s bare-path spike, 34 if it is the 5k floor. I could not test beyond ~15k req/s: the local load generator and servers saturate a 4-core laptop (a two-process run gave 14.8k vs 15.1k for one, which shows the test machine's limit, not the code's). Load test on separate machines before sizing.
4. **The hottest key sits at 62% of a partition's ceiling** even with typical skew. The in-process LRU (D4) stops being a nice-to-have: it is what bounds one key's database reads. Lower the single-key alert from 20% to 10% of traffic.
5. **Analytics volume.** 99k events/s is 20 MB/s, which Kafka handles, but ClickHouse ingestion at that rate is unsourced here. The cheaper design is to aggregate in-process: each instance counts clicks per code in memory and flushes every 10 s, so the event volume depends on distinct codes per window, not on request rate. Keep a 1-in-100 sample of full events for geo, device and referrer breakdowns. The cost is that per-click records are not stored.

**Verdict.** The architecture reaches 100k req/s without a redesign (same components, same decisions D1–D5), but not with the same configuration, and not for free: one external blocker (the datastore quota), one structural change (Redis sharding), and one unmeasured sizing input (instance throughput). If only 10k is required, nothing in Sections 1–7 changes.

## 9. Open decisions and next checks

Owners are proposed roles; replace them with names. Dates are proposed from 2026-11-13.

### Decisions

| # | Decision | Options | For / against | Pick | Owner | Decide by |
|---|---|---|---|---|---|---|
| 1 | Datastore | DynamoDB · Cassandra/Scylla · sharded Postgres | DynamoDB: managed, but a quota raise is needed at 100k and it ties you to AWS. Cassandra/Scylla: no quota, but you run the cluster and conditional writes are slower. Postgres: SQL tooling, but 2.6–7.8 TB strains a single primary (D3) | Managed KV (DynamoDB on AWS, otherwise Scylla) | Platform lead | 2026-11-27 |
| 2 | Link privacy | 7 characters for all · 7 public + 11 unlisted · 11 for all | 7 for all: shortest URLs, but ~736k live links/day can be enumerated (D2). 11 for all: safest, four extra characters everywhere. Split: needs an opt-in the creator must understand | 7 public + 11 unlisted | Product, Security lead | 2026-11-27 |
| 3 | Redirect status | 302 + 60 s · 301 · 302 uncached | 302 + 60 s: analytics and ~60 s takedown, some CDN relief. 301: least load, but clicks and takedowns are invisible. Uncached: exact, no relief (D1) | 302 + `max-age=60` | Product | 2026-11-20 |
| 4 | Code alphabet | 62 characters + blocklist · 56 characters (no look-alikes) + blocklist | 62: shorter space cost, but `0/O/1/l/I` are ambiguous when read aloud or printed. 56: unambiguous, collision rate doubles to ~0.17% at 3B links (D2) | 62 + blocklist; 56 only if links are printed or spoken | Product | 2026-12-04 |
| 5 | Click-data retention | Keyed daily-rotating IP hash, raw events 30 days · truncated IP only · no per-click data | Keyed hash: supports geo and abuse analysis. Truncation: weaker analysis, less personal data. None: simplest, no breakdowns (Section 6) | Keyed hash, 30-day raw retention | Legal, Security lead | 2026-12-04 |
| 6 | Plan for 100k | Request the datastore quota raise now · wait until traffic is proven | Now: avoids a launch blocker (Section 8), costs a provider conversation for traffic that may not come. Wait: no wasted effort, risks a quota-throttled launch | Request the raise once product confirms 100k is plausible within 12 months | Platform lead | 2026-12-11 |

### Next checks

| Check | What it settles | Owner | Date |
|---|---|---|---|
| Real read:write ratio and peak:average from product data | Storage and creation-rate numbers (Section 2) | Product, Data | 2026-11-20 |
| Request a 302 with `max-age` and a purge through the chosen CDN | D1 caching and takedown behaviour | Platform lead | 2026-11-27 |
| Load test the real Redirect Service (TLS at the LB, Redis hop, Kafka emit, logging) from separate load generators | The ≥5k req/s per-instance floor and the instance count (Sections 2 and 8) | Platform lead | 2026-12-04 |
| Datastore read test at 100% miss, 10k req/s, plus a cold start | The "DB can take everything" property (Section 5) | Platform lead | 2026-12-04 |
| Fit the Zipf exponent and active-set size from two weeks of click logs, then re-run A2 and A4 | Redis size and the 30% keep-or-drop-Redis line (D4) | Platform lead, Data | launch + 14 days |

---

## Appendix A. Scripts (A1–A4, A6–A8 pure Python 3 with no dependencies; A5 Node.js)

Run each with `python3 -I <file>`. Outputs shown are from an actual run (Python 3, macOS).

### A1. `capacity.py`
```python
"""Capacity model. Edit ASSUMPTIONS, re-run: python3 capacity.py"""
PEAK_RPS      = 10_000   # total peak requests/s (given)
READ_PER_WRITE = 100     # redirects per create (assumption)
PEAK_TO_AVG   = 3        # peak/average traffic ratio (assumption)
RECORD_BYTES  = 500      # DB row incl. index overhead (assumption)
REDIS_BYTES   = 200      # per cached entry: key+url+overhead (assumption)
YEARS         = 5
REPLICAS      = 3
ID_RANGE      = 10_000   # IDs handed to an instance per lease

reads  = PEAK_RPS * READ_PER_WRITE / (READ_PER_WRITE + 1)
writes = PEAK_RPS - reads
avg_writes = writes / PEAK_TO_AVG
per_year = avg_writes * 86_400 * 365
total = per_year * YEARS
print(f"peak reads/s={reads:,.0f} writes/s={writes:,.0f}")
print(f"avg writes/s={avg_writes:,.0f} -> {per_year/1e9:.2f}B links/yr, {total/1e9:.2f}B in {YEARS}y")
print(f"storage/yr={per_year*RECORD_BYTES/1e12:.2f} TB, {YEARS}y={total*RECORD_BYTES/1e12:.2f} TB, "
      f"x{REPLICAS} replicas={total*RECORD_BYTES*REPLICAS/1e12:.1f} TB")
print(f"keyspace 62^7={62**7:.2e}; used after {YEARS}y = {total/62**7:.3%}")
for hit in (0.80, 0.90, 0.95, 0.99):
    print(f"origin DB reads/s at edge+cache hit {hit:.0%}: {reads*(1-hit):,.0f}")
print(f"Redis memory for 100M hot links: {100e6*REDIS_BYTES/1e9:.0f} GB")
```
Output:
```
peak reads/s=9,901 writes/s=99
avg writes/s=33 -> 1.04B links/yr, 5.20B in 5y
storage/yr=0.52 TB, 5y=2.60 TB, x3 replicas=7.8 TB
keyspace 62^7=3.52e+12; used after 5y = 0.148%
origin DB reads/s at edge+cache hit 80%: 1,980
origin DB reads/s at edge+cache hit 90%: 990
origin DB reads/s at edge+cache hit 95%: 495
origin DB reads/s at edge+cache hit 99%: 99
Redis memory for 100M hot links: 20 GB
```

### A2. `cache_sim.py` (~7 s)
```python
"""Zipf cache simulation: python3 cache_sim.py
Links ranked 1..N, P(rank k) ~ 1/k^s. Reports hit rate of
 (a) ideal static cache holding the top-C links (upper bound), and
 (b) a real LRU, simulated with random requests."""
import bisect, itertools, random
from collections import OrderedDict

def cdf(n, s):
    w = [1 / k**s for k in range(1, n + 1)]
    tot = sum(w)
    return [x / tot for x in itertools.accumulate(w)]

N = 1_000_000          # catalog simulated (results depend on C/N)
REQS = 1_000_000
random.seed(1)
print(f"{'s':>5} {'cache%':>7} {'ideal':>7} {'LRU':>7}")
for s in (0.6, 0.8, 1.0, 1.2):
    c = cdf(N, s)
    for pct in (0.1, 1, 5, 20):
        C = int(N * pct / 100)
        ideal = c[C - 1]
        lru, hits = OrderedDict(), 0
        for _ in range(REQS):
            k = bisect.bisect_left(c, random.random())
            if k in lru:
                hits += 1
                lru.move_to_end(k)
            else:
                lru[k] = 1
                if len(lru) > C:
                    lru.popitem(last=False)
        print(f"{s:>5} {pct:>6}% {ideal:>7.1%} {hits/REQS:>7.1%}")
```
Output:
```
    s  cache%   ideal     LRU
  0.6    0.1%    6.0%    1.1%
  0.6      1%   15.6%    5.8%
  0.6      5%   30.0%   16.2%
  0.6     20%   52.4%   35.6%
  0.8    0.1%   20.7%   10.0%
  0.8      1%   36.2%   23.1%
  0.8      5%   52.3%   38.5%
  0.8     20%   70.8%   55.8%
  1.0    0.1%   52.0%   40.3%
  1.0      1%   68.0%   58.3%
  1.0      5%   79.2%   70.9%
  1.0     20%   88.8%   78.2%
  1.2    0.1%   82.2%   75.9%
  1.2      1%   91.0%   87.3%
  1.2      5%   95.1%   91.7%
  1.2     20%   97.7%   92.1%
```
Caveats: requests are independent draws (no temporal locality); the catalog is 1M links, not billions, and hit rate depends on cache size as a fraction of the catalog, which is an approximation at larger N.

### A3. `id_check.py`
```python
"""ID scheme checks: python3 id_check.py"""
import hashlib, math

ALPHA = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
KEY = b"demo-secret"
HALF = 20                      # 2 x 20 bits = 40-bit domain (1.1e12 < 62^7)
MASK = (1 << HALF) - 1

def f(x, r):
    h = hashlib.blake2b(x.to_bytes(3, "big") + bytes([r]), key=KEY, digest_size=3)
    return int.from_bytes(h.digest(), "big") & MASK

def enc(n):
    l, r = n >> HALF, n & MASK
    for i in range(4):
        l, r = r, l ^ f(r, i)
    return (l << HALF) | r

def dec(n):
    l, r = n >> HALF, n & MASK
    for i in reversed(range(4)):
        l, r = r ^ f(l, i), l
    return (l << HALF) | r

def b62(n):
    s = ""
    while n:
        n, d = divmod(n, 62)
        s = ALPHA[d] + s
    return s.rjust(7, "0")

# 1. Feistel is a bijection: sequential IDs -> unique codes, invertible
N = 2_000_000
codes = set()
for i in range(N):
    e = enc(i)
    assert dec(e) == i
    codes.add(b62(e))
print(f"1. {N:,} sequential IDs -> {len(codes):,} unique 7-char codes")

# 2. Random-code + retry: expected attempts as the table fills
SPACE = 62**7
for filled in (1e9, 3e9, 1e10, 1e11):
    p = filled / SPACE
    print(f"2. {filled:.0e} links: P(collision)={p:.3%}, expected attempts={1/(1-p):.4f}")

# 3. Truncated hash (birthday bound)
n = 3e9
p = 1 - math.exp(-n * (n - 1) / (2 * SPACE))
print(f"3. hash-truncate, {n:.0e} links: P(>=1 collision)={p:.4f}")
```
Output:
```
1. 2,000,000 sequential IDs -> 2,000,000 unique 7-char codes
2. 1e+09 links: P(collision)=0.028%, expected attempts=1.0003
2. 3e+09 links: P(collision)=0.085%, expected attempts=1.0009
2. 1e+10 links: P(collision)=0.284%, expected attempts=1.0028
2. 1e+11 links: P(collision)=2.840%, expected attempts=1.0292
3. hash-truncate, 3e+09 links: P(>=1 collision)=1.0000
```
Limit: the Feistel test checks 2M IDs, not the full 2⁴⁰ domain; a Feistel network is a bijection by construction.

### A4. `trace_fit.py` (real trace; ~4 s)
Input: two consecutive hourly files from the [Wikimedia pageviews dump](https://dumps.wikimedia.org/other/pageviews/) (`pageviews-20261001-120000.gz`, `...-130000.gz`, about 50 MB each). Download them into their own empty directory and treat them as untrusted data. Any "name count" hourly click file works with a one-line parser change.
```python
"""Fit Zipf exponent and measure hour-to-hour working-set stability on a real
request-popularity trace (Wikimedia hourly pageviews, en.wikipedia desktop+mobile).
usage: python3 -I trace_fit.py <hourA.gz> <hourB.gz>"""
import gzip, math, sys

def load(path):
    c = {}
    with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            p = line.split(" ")
            if len(p) >= 3 and p[0] == "en" and p[2].isdigit():   # domain code "en" = en.wikipedia desktop
                c[p[1]] = c.get(p[1], 0) + int(p[2])
    return c

a, b = load(sys.argv[1]), load(sys.argv[2])
cnt = sorted(a.values(), reverse=True)
tot = sum(cnt)
print(f"hour A: {len(cnt):,} distinct pages, {tot:,} views")

# Least-squares slope of log(freq) vs log(rank), over rank windows
def slope(lo, hi):
    xs = [math.log(r) for r in range(lo, min(hi, len(cnt)))]
    ys = [math.log(cnt[r - 1]) for r in range(lo, min(hi, len(cnt)))]
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    return -sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
for lo, hi in ((1, 100), (100, 10_000), (10_000, 100_000), (1, 100_000)):
    print(f"zipf exponent, ranks {lo:,}-{hi:,}: s={slope(lo, hi):.2f}")

# Ideal static cache hit rate = share of views on top-C pages (computed on the empirical counts)
cum = 0; marks = {}
for i, v in enumerate(cnt, 1):
    cum += v
    marks[i] = cum / tot
for pct in (0.1, 1, 5, 20):
    C = max(1, int(len(cnt) * pct / 100))
    print(f"top {pct}% of pages ({C:,}) carry {marks[C]:.1%} of views")

# Stability: cache filled with hour A's top-C, serving hour B's traffic (cold start excluded)
top = sorted(a, key=a.get, reverse=True)
tb = sum(b.values())
for pct in (0.1, 1, 5):
    C = max(1, int(len(a) * pct / 100))
    s = set(top[:C])
    hit = sum(v for k, v in b.items() if k in s) / tb
    print(f"cache = hour A's top {pct}% ({C:,}); hit rate on hour B = {hit:.1%}")
```
Output:
```
hour A: 939,188 distinct pages, 2,759,213 views
zipf exponent, ranks 1-100: s=1.00
zipf exponent, ranks 100-10,000: s=0.59
zipf exponent, ranks 10,000-100,000: s=0.56
zipf exponent, ranks 1-100,000: s=0.58
top 0.1% of pages (939) carry 12.4% of views
top 1% of pages (9,391) carry 23.5% of views
top 5% of pages (46,959) carry 40.0% of views
top 20% of pages (187,837) carry 65.4% of views
cache = hour A's top 0.1% (939); hit rate on hour B = 11.7%
cache = hour A's top 1% (9,391); hit rate on hour B = 22.3%
cache = hour A's top 5% (46,959); hit rate on hour B = 34.3%
```
Limits: this is Wikipedia page views (the `en` desktop rows), not short-link clicks; one hour of one day; hourly aggregates carry no request order, so burstiness within the hour is not captured; "% of pages" is a share of pages viewed that hour.

### A5. `redirect_bench.js` (bare hot-path throughput)
```js
// Minimal redirect hot path: parse code, in-process Map lookup, 302. One process = one core.
// usage: node redirect_bench.js   (listens on 8099)
const http = require('http');
const cache = new Map();
for (let i = 0; i < 1_000_000; i++) cache.set('c' + i, 'https://example.com/long/path/' + i + '?utm=' + 'x'.repeat(100));
http.createServer((req, res) => {
  const url = cache.get(req.url.slice(1));
  if (url) { res.writeHead(302, { Location: url, 'Cache-Control': 'max-age=60' }); res.end(); }
  else { res.writeHead(404); res.end(); }
}).listen(8099, () => console.log('ready'));
```
Run: `node redirect_bench.js`, then `ab -k -n 200000 -c 64 http://127.0.0.1:8099/c1234` (three runs). Result: **16,564 / 15,454 / 15,309 req/s**, 0 failed requests. Limits: one request path repeated (a cache hit every time), localhost, no TLS, `ab` competing for the same 4 cores, and p99 under this closed-loop saturation (~230 ms at 64 connections) is queueing delay, not service latency, so it should not be read as a latency figure.

### A6. `challenge_checks.py` (assumption tests)
Inputs: the hourly file from A4 and a week of hourly totals from the Wikimedia API (`https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/en.wikipedia/all-access/user/hourly/2026101000/2026101623`, saved as `hourly.json`). Uses the macOS word list at `/usr/share/dict/words`.
```python
"""Challenge checks. usage: python3 -I challenge_checks.py <hourly.json> <hourA.gz>
 C1 peak:average from a week of real hourly totals
 C2 hot-key share from a real trace vs DynamoDB per-partition read limit
 C3 read:write sensitivity
 C4 how often random base62 codes spell dictionary words"""
import gzip, json, random, sys

# C1
v = [i["views"] for i in json.load(open(sys.argv[1]))["items"]]
print(f"C1 {len(v)} hourly totals: peak/mean = {max(v)/(sum(v)/len(v)):.2f}, min/mean = {min(v)/(sum(v)/len(v)):.2f}")

# C2
c = {}
with gzip.open(sys.argv[2], "rt", encoding="utf-8", errors="replace") as f:
    for line in f:
        p = line.split(" ")
        if len(p) >= 3 and p[0] == "en" and p[2].isdigit():
            c[p[1]] = c.get(p[1], 0) + int(p[2])
cnt = sorted(c.values(), reverse=True); tot = sum(cnt)
RPS = 9901; PART = 6000      # 3,000 RRU/partition / 0.5 per eventually-consistent 4KB read
for k in (1, 10, 100):
    sh = sum(cnt[:k]) / tot
    print(f"C2 top-{k} pages carry {sh:.2%} of views -> at {RPS:,} redirects/s the hottest key sees ~{cnt[0]/tot*RPS:,.0f}/s"
          if k == 1 else f"C2 top-{k} pages carry {sh:.2%} of views")
print(f"   per-partition ceiling ~{PART:,} reads/s (eventually consistent). Hot key needs {PART/RPS:.0%} of all traffic to hit it.")

# C3
print("C3 read:write  writes/s(peak)  avg writes/s  links in 5y  storage 5y @500B")
for r in (10, 14, 50, 100, 1000):
    w = 10000 / (r + 1); a = w / 3
    n = a * 86400 * 365 * 5
    print(f"   {r:>5}:1 {w:>14,.0f} {a:>13,.0f} {n/1e9:>11.1f}B {n*500/1e12:>9.1f} TB  keyspace used {n/62**7:.2%}")

# C4
words = {w.strip().lower() for w in open("/usr/share/dict/words") if w.strip().isalpha() and len(w.strip()) >= 4}
A = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
random.seed(7); N = 200_000; hit = 0
for _ in range(N):
    s = "".join(random.choice(A) for _ in range(7)).lower()
    if any(s[i:i+L] in words for L in (4, 5, 6, 7) for i in range(0, 8 - L)): hit += 1
print(f"C4 {hit/N:.2%} of random 7-char codes contain a 4+ letter dictionary word ({len(words):,} words); "
      f"share of codes with look-alike chars (0 O o 1 l I): {1-(56/62)**7:.1%}")
```
Output:
```
C1 168 hourly totals: peak/mean = 1.33, min/mean = 0.71
C2 top-1 pages carry 3.74% of views -> at 9,901 redirects/s the hottest key sees ~370/s
C2 top-10 pages carry 6.05% of views
C2 top-100 pages carry 8.13% of views
   per-partition ceiling ~6,000 reads/s (eventually consistent). Hot key needs 61% of all traffic to hit it.
C3 read:write  writes/s(peak)  avg writes/s  links in 5y  storage 5y @500B
      10:1            909           303        47.8B      23.9 TB  keyspace used 1.36%
      14:1            667           222        35.0B      17.5 TB  keyspace used 0.99%
      50:1            196            65        10.3B       5.2 TB  keyspace used 0.29%
     100:1             99            33         5.2B       2.6 TB  keyspace used 0.15%
    1000:1             10             3         0.5B       0.3 TB  keyspace used 0.01%
C4 2.19% of random 7-char codes contain a 4+ letter dictionary word (232,989 words); share of codes with look-alike chars (0 O o 1 l I): 51.0%
```
Limits: C1 is one week of global English-Wikipedia traffic (daily cycle only, no bursts); C2 uses one hour of Wikipedia, not shortener traffic; C4 counts any English word, not offensive ones, because I had no profanity list.

### A7. `range_checks.py` (availability, queueing, guessing, hash reversal)
```python
"""Range checks: python3 range_checks.py
 R1 availability budget  R2 queueing/Little's law  R3 guessing exposure  R4 hashed-IP reversibility"""
import hashlib, time

# R1: 99.95% monthly availability budget
SLO = 0.9995
print(f"R1 99.95% over 30 days = {30*24*60*(1-SLO):.1f} min downtime budget")
for n in (3, 4, 5, 6):
    print(f"   {n} hard serial dependencies -> each needs >= {SLO**(1/n):.5f} ({30*24*60*(1-SLO**(1/n)):.1f} min/month each)")
print(f"   same 6 dependencies each at 99.9%: product = {0.999**6:.5f} -> {30*24*60*(1-0.999**6):.0f} min/month")

# R2: Little's law and M/M/1 queueing factor
R = 9901
for name, lat, frac in (("cache-hit path (5 ms budget)", 0.005, 1.0), ("DB-miss path, 100% miss (30 ms)", 0.030, 1.0),
                        ("DB-miss path, 60% miss (30 ms)", 0.030, 0.6)):
    print(f"R2 {name}: in flight = {R*frac:,.0f}/s x {lat*1000:.0f} ms = {R*frac*lat:,.0f} concurrent")
for rho in (0.5, 0.6, 0.7, 0.8, 0.9):
    print(f"   utilisation {rho:.0%}: mean queueing delay = {rho/(1-rho):.1f} x service time")

# R3: guessing exposure at 3B live links, attacker at 10,000 guesses/s (distributed)
LIVE, G = 3e9, 10_000
for chars, alpha in ((7, 62), (8, 62), (11, 62)):
    p = LIVE / alpha**chars
    print(f"R3 {chars}-char codes: P(guess hits a live link)={p:.3e}; at {G:,} guesses/s -> {G*p:.4f} links/s, {G*p*86400:,.0f} links/day")

# R4: how long does it take to reverse an unsalted SHA-256 of an IPv4 address?
N = 300_000; t = time.time()
for i in range(N):
    hashlib.sha256(b"%d.%d.%d.%d" % (i >> 24 & 255, i >> 16 & 255, i >> 8 & 255, i & 255)).digest()
rate = N / (time.time() - t)
print(f"R4 pure-Python SHA-256: {rate:,.0f} hashes/s -> all 2^32 IPv4 addresses in {2**32/rate/3600:.1f} h on one core "
      f"(a GPU does billions/s: seconds)")
```
Output (the R4 rate is from one run on a laptop and varies by machine):
```
R1 99.95% over 30 days = 21.6 min downtime budget
   3 hard serial dependencies -> each needs >= 0.99983 (7.2 min/month each)
   4 hard serial dependencies -> each needs >= 0.99987 (5.4 min/month each)
   5 hard serial dependencies -> each needs >= 0.99990 (4.3 min/month each)
   6 hard serial dependencies -> each needs >= 0.99992 (3.6 min/month each)
   same 6 dependencies each at 99.9%: product = 0.99401 -> 259 min/month
R2 cache-hit path (5 ms budget): in flight = 9,901/s x 5 ms = 50 concurrent
R2 DB-miss path, 100% miss (30 ms): in flight = 9,901/s x 30 ms = 297 concurrent
R2 DB-miss path, 60% miss (30 ms): in flight = 5,941/s x 30 ms = 178 concurrent
   utilisation 50%: mean queueing delay = 1.0 x service time
   utilisation 60%: mean queueing delay = 1.5 x service time
   utilisation 70%: mean queueing delay = 2.3 x service time
   utilisation 80%: mean queueing delay = 4.0 x service time
   utilisation 90%: mean queueing delay = 9.0 x service time
R3 7-char codes: P(guess hits a live link)=8.519e-04; at 10,000 guesses/s -> 8.5188 links/s, 736,026 links/day
R3 8-char codes: P(guess hits a live link)=1.374e-05; at 10,000 guesses/s -> 0.1374 links/s, 11,871 links/day
R3 11-char codes: P(guess hits a live link)=5.765e-11; at 10,000 guesses/s -> 0.0000 links/s, 0 links/day
R4 pure-Python SHA-256: 2,608,766 hashes/s -> all 2^32 IPv4 addresses in 0.5 h on one core (a GPU does billions/s: seconds)
```
Limits: R1 treats failures as independent and ignores partial degradation; R2 uses M/M/1, a simplification; R3 assumes the attacker's guesses are uniform over the code space and that 3B links are live; R4 times one CPU core, and the GPU remark is general knowledge, not measured here.

### A8. `stretch_checks.py` (100k req/s)
```python
"""Stretch: what changes at 100k req/s peak? python3 stretch_checks.py"""
import math
PEAK, RATIO, P2A = 100_000, 100, 3
reads = PEAK * RATIO / (RATIO + 1); writes = PEAK - reads
avg_w = writes / P2A; yr = avg_w * 86400 * 365; n5 = yr * 5
print(f"S1 reads={reads:,.0f}/s writes={writes:,.0f}/s | avg writes {avg_w:,.0f}/s -> {yr/1e9:.1f}B/yr, {n5/1e9:.0f}B in 5y, "
      f"{n5*500/1e12:.0f} TB (peak case {writes*86400*365*5*500/1e12:.0f} TB) | key space used {n5/62**7:.2%}, "
      f"collision/insert at {n5/1e9:.0f}B = {n5/62**7:.2%}")
QUOTA, RRU = 40_000, 0.5
need = reads * RRU
print(f"S2 DB at 100% miss: {need:,.0f} read units/s vs default table quota {QUOTA:,} -> {need/QUOTA:.0%} of quota")
for target in (0.7, 1.0):
    h = max(0, 1 - (QUOTA * target) / need)
    print(f"   to stay under {target:.0%} of the default quota the cache must hit >= {h:.0%}")
print(f"S3 Redis at {reads:,.0f} ops/s vs ~72k (docs, non-pipelined): single instance = {reads/72_000:.0%} of that reference; "
      f"3 shards -> {reads/3:,.0f} ops/s each = {reads/3/72_000:.0%}")
for per, label in ((5_000, "floor 5k/s"), (15_000, "bare path 15k/s")):
    n = math.ceil(reads / (per * 0.6))
    print(f"S4 Redirect instances at 60% CPU target, {label}: {n}; with 1 of 3 AZs lost: {math.ceil(n * 3 / 2)}")
for lat, name in ((0.005, "hit 5 ms"), (0.030, "miss 30 ms")):
    print(f"S5 in flight, {name}: {reads*lat:,.0f} concurrent")
top1 = 0.0374
print(f"S6 hottest key at trace-like skew: {reads*top1:,.0f} reads/s vs ~6,000/s partition ceiling = {reads*top1/6000:.0%}")
print(f"S7 click events: {reads:,.0f}/s x 200 B = {reads*200/1e6:.0f} MB/s; sampling 1-in-10 -> {reads/10:,.0f} events/s")
```
Output:
```
S1 reads=99,010/s writes=990/s | avg writes 330/s -> 10.4B/yr, 52B in 5y, 26 TB (peak case 78 TB) | key space used 1.48%, collision/insert at 52B = 1.48%
S2 DB at 100% miss: 49,505 read units/s vs default table quota 40,000 -> 124% of quota
   to stay under 70% of the default quota the cache must hit >= 43%
   to stay under 100% of the default quota the cache must hit >= 19%
S3 Redis at 99,010 ops/s vs ~72k (docs, non-pipelined): single instance = 138% of that reference; 3 shards -> 33,003 ops/s each = 46%
S4 Redirect instances at 60% CPU target, floor 5k/s: 34; with 1 of 3 AZs lost: 51
S4 Redirect instances at 60% CPU target, bare path 15k/s: 12; with 1 of 3 AZs lost: 18
S5 in flight, hit 5 ms: 495 concurrent
S5 in flight, miss 30 ms: 2,970 concurrent
S6 hottest key at trace-like skew: 3,703 reads/s vs ~6,000/s partition ceiling = 62%
S7 click events: 99,010/s x 200 B = 20 MB/s; sampling 1-in-10 -> 9,901 events/s
```
Limits: the instance counts use the 5k/s floor and the 15k/s bare-path spike as bounds, not a production measurement; the 72k ops/s Redis figure is the reference example from the docs, not a measurement on your hardware.

## Appendix B. Sources for assumptions

- **Redis single-instance throughput:** [Redis benchmarks](https://redis.io/docs/latest/operate/oss_and_stack/management/optimization/benchmarks/). The docs show non-pipelined runs around 72k ops/s and SET at ~180k ops/s on example hardware, and warn that results depend heavily on hardware and pipelining. Used only to show 10k ops/s is well below one instance's limit; benchmark your own hardware.
- **DynamoDB limits:** [Quotas in Amazon DynamoDB](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/ServiceQuotas.html). Default on-demand quota of 40,000 read and 40,000 write request units per table, adjustable. Per-partition limits of 3,000 read units or 1,000 write units per second apply. AWS pages differ on whether the quota is per-table or account-wide; confirm in your account's Service Quotas console. The 0.5-unit cost of an eventually-consistent read of ≤4 KB is confirmed by [DynamoDB read and write operations](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/read-write-operations.html) (strongly consistent = 1, transactional = 2).
- **Real trace used in A4:** [Wikimedia pageviews dumps](https://dumps.wikimedia.org/other/pageviews/), hourly view counts per page (open data from the Wikimedia Foundation).
- **Web request popularity (Zipf-like):** [Breslau et al., "Web Caching and Zipf-like Distributions"](https://pages.cs.wisc.edu/~cao/papers/zipf-implications.html) (exponent varies by trace, commonly cited 0.6–0.8) and [arXiv cs/0404010](https://arxiv.org/abs/cs/0404010) (website popularity exponent ~1.0). **Gap:** I found no published popularity exponent for short-link click traffic, so the range 0.6–1.2 in Section 2 is an assumption; A4 checks it against a different kind of real traffic. The 100:1 read ratio has no public source; the only derivable figure (~14 clicks per link, from an undated [Adweek Bitly infographic](https://www.adweek.com/?p=372217) mixing figures that may be from different periods) points much lower, hence the sensitivity table. The 3:1 peak:average is an assumption; a week of [Wikimedia hourly view totals](https://wikimedia.org/api/rest_v1/metrics/pageviews/aggregate/en.wikipedia/all-access/user/hourly/2026101000/2026101623) shows 1.33:1 for the daily cycle.
- **CDN caching of 302s:** [Cloudflare default cache behavior](https://developers.cloudflare.com/cache/concepts/default-cache-behavior) (302 default TTL 20 minutes; explicit headers followed) and [Google Cloud CDN caching overview](https://docs.cloud.google.com/cdn/docs/caching) (302 listed as cacheable). CloudFront not confirmed from its documentation.
