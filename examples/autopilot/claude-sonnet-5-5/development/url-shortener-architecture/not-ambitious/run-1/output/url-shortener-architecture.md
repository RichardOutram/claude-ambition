# URL Shortener — Architecture (10k req/s)

## 1. Requirements

### Functional
- Create a short URL from a long URL (optional custom alias, optional expiry).
- Redirect short URL → long URL (HTTP 301/302).
- Basic click analytics (async, non-blocking).
- Delete/disable links.

### Non-functional
| Attribute | Target |
|---|---|
| Peak throughput | 10,000 req/s total |
| Read:write ratio | ~100:1 → ~9,900 redirects/s, ~100 creates/s |
| Redirect latency | p99 < 50 ms (server side) |
| Availability | 99.99% for redirects; creates may degrade |
| Durability | No loss of created links |
| Short code | 7 chars, base62 → 62^7 ≈ 3.5 trillion codes |

## 2. Capacity Estimates

- Writes: 100/s × 86,400 ≈ 8.6M/day ≈ 3.1B/year. Plan for 5 years ≈ 15B links worst case (typical far lower).
- Record size ≈ 500 B (code, long URL, user, timestamps, flags) → ~1.5 TB/year at worst case, ~7.5 TB over 5 years before replication.
- Reads: 10k/s peak. With a ≥90% cache hit rate, only ~1k/s reach the database.
- Bandwidth: redirect response ≈ 500 B → ~5 MB/s egress. Trivial.
- Cache: Pareto-style traffic; caching the hottest 20% of daily-active links ≈ tens of GB → a small Redis cluster.
- Analytics events: ~10k/s × ~200 B = ~2 MB/s into the event stream (~170 GB/day raw).

Conclusion: 10k req/s is modest. The design goal is **simplicity, horizontal scalability, and cache-first reads**, not exotic infrastructure.

## 3. High-Level Architecture

```
                    ┌──────────────┐
   Client ─────────▶│ CDN / Edge   │── cache hit ──▶ 301/302
                    └──────┬───────┘
                           │ miss
                    ┌──────▼───────┐
                    │ L7 Load      │  (TLS termination, rate limiting, WAF)
                    │ Balancer     │
                    └──┬────────┬──┘
                       │        │
          GET /{code}  │        │  POST /api/v1/urls
              ┌────────▼──┐  ┌──▼─────────┐
              │ Redirect  │  │  Create    │
              │ Service   │  │  Service   │
              │ (stateless│  │ (stateless)│
              └──┬─────┬──┘  └──┬──────┬──┘
                 │     │        │      │
         ┌───────▼──┐  │   ┌────▼───┐  │
         │ Redis    │  │   │ Key    │  │
         │ Cache    │  │   │ Alloc. │  │
         └───────┬──┘  │   └────────┘  │
          miss   │     │ click event   │
         ┌───────▼─────▼───┐      ┌────▼────────────┐
         │  Primary Store  │◀─────┤ write            │
         │ (sharded KV/DB) │      └──────────────────┘
         └─────────────────┘
                 │ async
         ┌───────▼──────┐    ┌────────────┐    ┌───────────────┐
         │ Kafka        │───▶│ Stream     │───▶│ Analytics DB  │
         │ (click events)│   │ Consumers  │    │ (ClickHouse)  │
         └──────────────┘    └────────────┘    └───────────────┘
```

Redirect and create paths are deployed as **separate services** so the 99% read path scales and fails independently of the write path.

## 4. API

```
POST   /api/v1/urls
  body: { "long_url": "...", "custom_alias?": "...", "expires_at?": "..." }
  201:  { "short_url": "https://sho.rt/aZ3k9Qx", "code": "aZ3k9Qx" }

GET    /{code}            → 301/302 Location: <long_url>   (404 / 410 if missing / expired)
DELETE /api/v1/urls/{code}
GET    /api/v1/urls/{code}/stats
```

- **301 vs 302**: 301 is cached by browsers (less load, but clicks go uncounted and links can't be changed). Default to **302** with a short `Cache-Control: max-age` (e.g. 60 s) so analytics stay accurate while still offloading the CDN/browser. Offer 301 as an opt-in.
- Authenticate creates via API key / OAuth; redirects are public.
- Rate limit creates per key/IP (token bucket in Redis).

## 5. Short Code Generation

Options considered:

| Approach | Pros | Cons |
|---|---|---|
| Hash (MD5/SHA of URL) truncated | Stateless, dedup-friendly | Collisions; needs retry/check |
| Random 7-char base62 | Unguessable | Collision checks on insert |
| Global counter + base62 | No collisions | Sequential/guessable; single point of contention |
| **Pre-allocated ID ranges + base62 (chosen)** | No collisions, no per-write coordination | Needs obfuscation if guessability matters |

**Chosen design: range allocation.**
1. A small coordination service (ZooKeeper/etcd, or a DB row with atomic increment) hands out blocks of, e.g., 100,000 IDs to each Create Service instance.
2. Each instance consumes its block locally in memory (zero network cost per create) and requests a new block when ~80% used.
3. The numeric ID is passed through a reversible bijective scramble (e.g. Feistel network / format-preserving encryption with a secret key), then base62-encoded to 7 chars. This yields unique, non-sequential, non-enumerable codes.
4. If an instance crashes, its unused block is simply lost (acceptable: 3.5T space).

Custom aliases: insert with a conditional write (`IF NOT EXISTS`); on conflict return 409. Reserve a namespace/denylist for system routes and abusive words.

## 6. Data Model & Storage

### Primary table `urls`
| Field | Type | Notes |
|---|---|---|
| `code` | string (PK / partition key) | 7–10 chars |
| `long_url` | string | up to 2 KB |
| `user_id` | string | nullable |
| `created_at` | timestamp | |
| `expires_at` | timestamp | nullable, TTL |
| `status` | enum | active / disabled / blocked |

Access pattern is **pure key-value lookup by `code`** — no joins, no range scans on the hot path.

### Store choice
- **Recommended:** a horizontally scalable KV/wide-column store (DynamoDB, Cassandra, ScyllaDB). Partition by `code` hash; native TTL for expiry; multi-AZ replication.
- **Alternative:** PostgreSQL/MySQL sharded by `hash(code)` (e.g. 16–64 logical shards, mapped to a few physical nodes) with read replicas. Fine at this scale and operationally familiar.
- A secondary index on `user_id` (or separate table `urls_by_user`) supports listing a user's links; it is off the hot path.

### Duplicate long URLs
Don't dedupe by default (each link gets its own analytics and owner). Optional dedup via a `hash(long_url, user_id)` index.

## 7. Read Path (the 99%)

1. **CDN/edge cache** keyed on path; short TTL (30–300 s). Absorbs most viral traffic.
2. **Redirect service in-process cache** (small LRU, ~100k entries, TTL 60 s) — absorbs hot keys without a network hop.
3. **Redis cluster** (cache-aside): `GET code` → on miss read DB, then `SET code long_url EX 24h`.
4. **Negative caching**: cache "not found" for ~30–60 s to defend against enumeration/scan traffic.
5. **Bloom filter** of valid codes (optional) to reject nonexistent codes without touching the DB.
6. Emit a click event **asynchronously** (fire-and-forget to Kafka; never block the redirect on it).

Cache stampede protection: request coalescing (single-flight) per key and jittered TTLs.

Expected: CDN + local + Redis serve >95% of reads; DB sees < 500 reads/s.

## 8. Write Path

1. Validate URL (scheme allowlist http/https, length, parse), run it against a malware/phishing blocklist (e.g. Safe Browsing) — async re-scan afterward.
2. Obtain an ID from the local block, scramble + encode to a code.
3. Write to the primary store (quorum write for durability).
4. Optionally warm the cache.
5. Return the short URL.

~100 writes/s is trivial for any of the stores above.

## 9. Analytics Pipeline

- Redirect service publishes `{code, ts, ip_hash, user_agent, referrer, country}` to **Kafka** (batched, async, `acks=1`; loss of a few events is acceptable).
- Consumers aggregate into **ClickHouse** (or Druid/BigQuery): raw events plus rollups per code per minute/hour/day.
- Stats API reads from the rollups. Counters are eventually consistent (seconds to minutes).
- Never increment a click counter in the primary DB on the hot path (hot-row contention).

## 10. Scaling & Capacity Plan

| Component | Sizing at 10k req/s (with ~3× headroom for 30k) |
|---|---|
| Edge/CDN | Managed; handles all |
| Load balancers | 2+ in multi-AZ (managed ALB/NLB) |
| Redirect service | Each node can do ~5–10k simple req/s (Go/Rust/Java NIO). Run **6–10 instances** across 3 AZs |
| Create service | 3 instances (HA, not capacity) |
| Redis | 3 shards × (1 primary + 1 replica); ~50k–100k ops/s each → ample |
| Primary store | 6+ nodes, RF=3, across 3 AZs |
| Kafka | 3 brokers, ~12 partitions for click topic |
| ClickHouse | 2–3 nodes (replicated) |

Autoscale redirect pods on CPU and RPS. Stateless services make this trivial.

## 11. Reliability & Availability

- **Multi-AZ everywhere**; optional multi-region active-active for redirects (read-only data replicated, writes homed or via a globally replicated KV like DynamoDB Global Tables).
- **Degradation order:** analytics down → redirects unaffected; create service down → redirects unaffected; Redis down → fall back to DB with rate protection (circuit breaker + local cache); DB read replica lag → acceptable for redirects.
- Timeouts, retries with jitter, circuit breakers on all downstream calls.
- Health checks and graceful draining at the load balancer.
- Backups: continuous/point-in-time recovery for the primary store; periodic restore drills.
- Expired-link cleanup through native TTL or a background sweeper (never in the request path).

## 12. Security & Abuse

- HTTPS only; HSTS.
- Validate and canonicalise input; block `javascript:`, `data:`, internal IPs (SSRF if previews/validation fetch the target).
- Malicious-URL detection on create and periodic re-scan; ability to disable codes instantly (status flag + cache invalidation/CDN purge).
- Rate limiting and per-account quotas; CAPTCHA for anonymous creates.
- Non-sequential codes prevent enumeration; negative caching and rate limits blunt scanning.
- Hash IPs in analytics; comply with privacy regulations (GDPR retention, deletion).

## 13. Observability

- **Metrics:** redirect RPS, p50/p95/p99 latency, cache hit ratios (CDN / local / Redis), DB latency, error rates, Kafka lag, ID-block allocation rate.
- **Tracing:** sample 1% of requests end-to-end.
- **Logging:** structured, sampled on the hot path.
- **Alerts:** p99 > 100 ms, 5xx > 0.1%, cache hit ratio drop, Kafka consumer lag, remaining-ID-space and disk growth.
- **SLOs:** 99.99% redirect availability; p99 latency < 50 ms server-side.

## 14. Testing & Rollout

- Load test to 30k req/s (k6/Gatling) with a Zipfian key distribution, plus a hot-key scenario (single code at 5k req/s).
- Chaos tests: kill a Redis shard, a DB node, an AZ.
- Canary deploys; blue/green for the redirect service; feature flags for 301 vs 302 behaviour.

## 15. Key Trade-offs & Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Redirect code | 302 + short max-age | Keeps analytics and edit/disable ability |
| Code generation | Range-allocated IDs + scramble | No collisions, no per-write coordination, non-guessable |
| Storage | Partitioned KV store | Pure key lookups, easy horizontal scale, TTL support |
| Caching | CDN → local → Redis | 95%+ offload; DB is nearly idle |
| Analytics | Async via Kafka | Redirect latency and availability independent of analytics |
| Service split | Redirect vs Create | Different scaling and failure profiles |
| Consistency | Eventual for stats and caches; strong for create | Users see their link work immediately after creation |

## 16. Future Extensions

- Custom domains per tenant.
- Link-in-bio pages, QR code generation.
- Geo/device-based routing rules (evaluated at edge).
- A/B destination rotation.
- Edge compute (Workers/Lambda@Edge) serving redirects from replicated edge KV for global sub-20 ms latency.

---

# Part II — Deep Dives

## 17. Latency Budget (p99 < 50 ms server-side)

| Hop | Budget | Notes |
|---|---|---|
| LB → redirect pod | 1–2 ms | same AZ preferred (zone-aware routing) |
| Local LRU lookup | < 0.05 ms | in-process, lock-striped |
| Redis GET (local AZ) | 0.5–2 ms | pipelined connection pool, no per-request connects |
| DB point read (miss path) | 5–15 ms | single-partition read, LOCAL_QUORUM |
| Kafka produce | 0 ms on hot path | async batched buffer; drop on overflow |
| Response write | < 1 ms | tiny headers-only response |

Typical request: local hit → ~2 ms total. Redis hit → ~5 ms. Full miss → ~20 ms. The 50 ms p99 leaves room for GC pauses and one retry. Use hedged reads (send a second Redis/DB request after the p95 latency elapses) to trim tail latency.

## 18. Redirect Handler (reference logic)

```
handle(GET /{code}):
  if !valid_format(code):            return 404            # reject before any I/O
  e = local_cache.get(code)
  if e == null:
    e = singleflight(code, () ->                           # coalesce concurrent misses
          redis.get(code) ?? db.get(code) ?? NOT_FOUND)
    if e is NOT_FOUND:  local_cache.put(code, NEG, ttl=30s ± jitter); return 404
    local_cache.put(code, e, ttl=60s ± jitter)
    redis.set(code, e, ex=24h ± jitter)                    # only if it came from the DB
  if e == NEG:                       return 404
  if e.status != ACTIVE:             return 410            # disabled/blocked
  if e.expires_at < now:             return 410
  click_buffer.offer(event(code, now, request))            # non-blocking, drops if full
  return 302, Location: e.long_url, Cache-Control: public, max-age=60
```

Key properties: no I/O before format validation; one in-flight backend call per key per pod; analytics can never block or fail the response; every TTL is jittered so entries don't expire in lockstep.

## 19. Short Code Internals

### Why Feistel, and the exact parameters
- 62^7 ≈ 3.52 × 10^12 > 2^41. Use a **40-bit** domain (≈ 1.1 × 10^12 codes) so a balanced Feistel (20 + 20 bits) maps `[0, 2^40)` onto itself bijectively, and every output fits in 7 base62 characters. No cycle-walking needed.
- Round function: truncated HMAC-SHA256 over (round index ‖ half) with a secret key; **4+ rounds** (use 6 for margin).
- Left-pad to 7 chars so length leaks nothing about the counter.
- 1.1T codes versus a worst-case ~15B links over 5 years = ~1.4% utilisation, so random-looking codes remain very hard to guess by probing. Expect scanners; that's what the negative cache and rate limits are for.
- If you need more headroom, step to 8 chars (44-bit domain → 62^8 ≈ 2.2 × 10^14) with no architectural change; old 7-char codes keep working because lookup is by exact string.

### Do not rotate the Feistel key
Rotating changes the counter→code mapping. A future counter value could then map to a code already issued under the old key → collision. Therefore:
1. Treat the key as long-lived; store it in a KMS/HSM-backed secret.
2. If it ever leaks, the exposure is only *predictability of future codes*, not data access. Mitigation is to move to a new code length/prefix namespace, not to re-key in place.
3. **Defence in depth regardless:** every create is a conditional insert (`IF NOT EXISTS`). On the (theoretically impossible) conflict, draw the next ID from the block and retry, and raise an alert.

### ID block leasing
```
table id_blocks(block_start BIGINT PRIMARY KEY, owner TEXT, lease_expires TIMESTAMP)
```
- Allocator does `UPDATE next_block SET v = v + 100000 RETURNING v` (single-row, atomic, ~1 call per 100k creates per instance → effectively zero contention).
- Instances prefetch the next block at 80% consumption in a background task, so creates never wait on the allocator.
- Allocator unavailable: instances keep creating until their block (+ prefetched block) runs out. At 100 creates/s over 3 instances, one 100k block lasts ~50 minutes per instance, giving a large buffer to fix the allocator.
- Lost blocks on crash: ≤ 100k IDs per crash, negligible against 1.1T.
- Multi-region: give each region a disjoint counter range (high bits = region ID) so regions allocate fully independently.

### Custom aliases
- Separate namespace rule: aliases must differ structurally from generated codes (e.g. generated codes are exactly 7 chars from base62; aliases must be 4–32 chars and contain at least one `-` or `_`, or be ≠ 7 chars). This guarantees an alias can never collide with a future generated code.
- Denylist: reserved routes (`api`, `admin`, `health`, `static`), offensive terms, brand impersonation list.

## 20. Consistency Edge Cases

| Scenario | Risk | Handling |
|---|---|---|
| Create, then immediate click | Cache miss + read replica lag → spurious 404 | Create path does **write-through** to Redis *and* deletes any negative-cache entry; DB read at LOCAL_QUORUM (or primary) on cache miss for codes < 60 s old |
| Alias requested right after someone probed it | Negative-cache entry (30 s) hides new link | Create explicitly deletes `neg:{code}` in Redis and publishes an invalidation to pods |
| Disable/takedown | Stale entries in CDN, Redis, local LRUs | Write DB status → delete Redis key → publish invalidation on pub/sub (pods drop local entry) → CDN purge by surrogate key. Worst-case staleness bounded by TTLs: local 60 s, CDN ≤ 60 s. Emergency takedown SLO: **< 60 s global** |
| Update destination | Same as above | Same path; prefer disallowing edits on 301 links (browsers cache them forever) |
| Redis failover loses recent writes | Entries missing | Harmless; cache-aside repopulates from DB |
| Expiry | Entry served after `expires_at` | Handler checks `expires_at` itself; TTL on the cache entry is `min(24h, expires_at − now)` |
| Duplicate create (client retry) | Two codes for one request | Idempotency-Key header → stored for 24 h → returns the original response |

## 21. Hot Keys & Traffic Spikes

A viral link might get 5k–8k req/s on one code. Defence layers, in order:
1. **CDN**: a 60 s TTL collapses this to roughly (#edge POPs ÷ 60) origin requests per second.
2. **Per-pod local cache**: one origin fetch per pod per TTL. Redis never sees the key at high rate.
3. **Request coalescing** inside each pod.
4. **Redis hot-key mitigation** (if the above ever fails): replicate hot entries under suffixed keys (`code#0..#7`) and read a random suffix. Detect via Redis `--hotkeys`/client-side counters.
5. **Load shedding**: if redirect pod concurrency exceeds a threshold, return 503 with `Retry-After` for *uncached, unknown codes first*, preserving capacity for valid hot traffic.

Cold-start / cache-flush stampede: if all of Redis is lost, 10k req/s of mostly-distinct keys hit the DB. Provision the DB to sustain ~3k reads/s (the local caches and CDN absorb the rest), plus circuit breakers and per-pod concurrency caps on DB calls. Re-warm by replaying the top-N codes from the last 24 h of click events.

## 22. Multi-Region Design

```
            Global DNS / Anycast (latency-based, health-checked)
        ┌──────────────────┬───────────────────┐
   Region A (primary)   Region B             Region C
   redirect + create    redirect (+create)   redirect
   Redis, KV replica    Redis, KV replica    Redis, KV replica
        └──── async multi-master / global-table replication ────┘
```

- **Reads** are served in the nearest region from the local replica. Replication lag (typically < 1 s) only matters for brand-new links; the fallback is a cross-region read on local miss for codes with the region-prefix of another region (see ID ranges above, which also tells you *where a code was created*).
- **Writes**: simplest correct option is to home creates in the user's nearest region, with disjoint ID ranges (no cross-region coordination) and conditional insert for aliases. Aliases are the only globally-unique-by-choice resource; route alias creates to a single "alias authority" region, or use a globally consistent store for the alias index only.
- **Disable/takedown** is a high-priority replicated write, followed by a global pub/sub fan-out and CDN purge.
- **Region failure**: DNS withdraws it; other regions already hold the data. RPO ≈ replication lag (≈ seconds) for newly created links; RTO ≈ DNS/health-check propagation (≈ 30–60 s).
- Capacity rule: each region sized to carry 50% of global peak so the loss of one of three regions needs no scale-up.

## 23. Concrete Schemas

### Cassandra/Scylla
```sql
CREATE TABLE urls (
  code        text PRIMARY KEY,
  long_url    text,
  owner_id    text,
  status      tinyint,          -- 0 active, 1 disabled, 2 blocked
  created_at  timestamp,
  expires_at  timestamp
) WITH default_time_to_live = 0
  AND compaction = {'class': 'LeveledCompactionStrategy'};

-- expiry via per-row TTL on insert (USING TTL <seconds>)

CREATE TABLE urls_by_owner (
  owner_id   text,
  created_at timeuuid,
  code       text,
  PRIMARY KEY (owner_id, created_at)
) WITH CLUSTERING ORDER BY (created_at DESC);
```
Writes: `INSERT ... IF NOT EXISTS` (lightweight transaction, ~100/s is fine) at LOCAL_QUORUM. Reads: `LOCAL_ONE`/`LOCAL_QUORUM` by partition key. Lightweight transactions are used **only on create**, never on the read path.

### PostgreSQL alternative
```sql
CREATE TABLE urls (
  code        char(7) PRIMARY KEY,   -- or varchar(32) to allow aliases
  long_url    text NOT NULL,
  owner_id    bigint,
  status      smallint NOT NULL DEFAULT 0,
  created_at  timestamptz NOT NULL DEFAULT now(),
  expires_at  timestamptz
);
CREATE INDEX ON urls (owner_id, created_at DESC);
CREATE INDEX ON urls (expires_at) WHERE expires_at IS NOT NULL;  -- sweeper
```
Shard by `hash(code) mod 64` logical shards across 4–8 physical nodes so shards can move between nodes without re-hashing keys.

### ClickHouse
```sql
CREATE TABLE clicks (
  ts DateTime, code String, country LowCardinality(String),
  device LowCardinality(String), referrer_host String, ip_hash UInt64
) ENGINE = MergeTree PARTITION BY toYYYYMMDD(ts) ORDER BY (code, ts)
TTL ts + INTERVAL 13 MONTH;

CREATE MATERIALIZED VIEW clicks_hourly ... ENGINE = SummingMergeTree
  ORDER BY (code, hour) AS SELECT code, toStartOfHour(ts) AS hour, count() AS clicks FROM clicks GROUP BY code, hour;
```
Kafka keyed by `code` keeps one code's events in one partition (ordered, and cheap for dedup). For hot codes, add a random salt to the key to avoid a hot partition; the rollup sums across it anyway.

## 24. Failure Mode Analysis

| Failure | Detection | User impact | Automatic response | Recovery |
|---|---|---|---|---|
| One redirect pod dies | LB health check (2–3 s) | None | Traffic reroutes, HPA replaces | Self-healing |
| Whole AZ lost | Multi-signal health | None if ≥ 1/3 headroom per AZ | LB drains AZ; DB/Redis quorum survives (RF=3) | Scale up in remaining AZs |
| Redis shard lost | Sentinel/cluster failover | Latency bump for 1/3 of keys | Replica promoted (~10–30 s); misses fall to DB with caps | Cache re-warms |
| Redis fully down | Error-rate alert | p99 rises to ~20–30 ms | Circuit opens; local cache + DB with concurrency cap | Restore, re-warm |
| DB node lost | Gossip / health | None (RF=3, quorum) | Coordinator reroutes | Replace node, stream data |
| DB overloaded | Latency/queue alerts | Some 503s on cold keys | Load shedding on unknown codes | Add nodes, raise cache TTL temporarily |
| Kafka down | Producer error rate | None for redirects; stats delayed | Buffer in memory, drop oldest on overflow (counted) | Consumers catch up |
| Create service down | Alert | No new links; redirects fine | Autoscale/restart | — |
| ID allocator down | Alert | None for ~50 min of buffer | Use prefetched block | Restore allocator |
| Bad deploy | Canary error/latency SLO | Limited to canary slice | Automated rollback | Fix forward |
| Poisoned/malicious link | Blocklist feed, reports | Phishing exposure | Status=blocked + invalidation + purge < 60 s | Post-incident review |
| Expired TLS cert | Cert monitor (30/14/7 days) | Total outage | — | Automated renewal (ACME), two independent alert paths |
| DNS provider outage | External probes | Total outage | Secondary DNS provider | Failover NS |

**Error budget:** 99.99% ≈ **4.3 min/month**. A 30 s cache-failover blip uses ~12% of the monthly budget, which is why local caches and the CDN matter: they make single-component incidents invisible.

## 25. Security Threat Model (STRIDE-lite)

| Threat | Vector | Mitigation |
|---|---|---|
| Phishing/malware via short links (abuse) | Attackers hide destinations | Create-time blocklist check; periodic re-scan; user reporting; optional interstitial for unverified anonymous links; reputation scoring on creating accounts/IPs |
| Enumeration/scraping | Brute-force codes | 1.1T space, scrambled IDs, per-IP rate limit on 404s, negative cache, Bloom filter, CDN WAF bot rules |
| SSRF | Server fetches target URL for title/validation | Fetch via egress proxy, deny RFC1918/link-local/metadata IPs (169.254.169.254), resolve-then-connect pinning, timeouts and size caps |
| Open redirect used in attacks on others | Service is a redirector by design | Scheme allowlist, no redirect chains to other shorteners (detect and reject), abuse monitoring |
| Cache poisoning | Crafted Host/path variants | CDN cache key = normalised path only; ignore unknown query params; strict `Host` allowlist |
| Header injection | `\r\n` in long URL | Reject control chars; percent-encode on output |
| Credential/key theft | Leaked API keys | Hashed key storage, scopes, rotation, per-key quotas |
| DoS on create | Mass link creation | Auth + token bucket per key/IP + CAPTCHA + global write cap |
| Privacy | Click logs identify users | Truncate/hash IPs with a rotating salt, honour DNT/consent, retention TTL (13 months), deletion API |
| Insider/supply chain | Dependencies, CI | Signed images, SBOM, least-privilege IAM, secret manager (no env-file secrets), audit logs |

## 26. Observability — Concrete Signals

- **Golden signals per service:** rate, errors, latency (histograms with buckets at 1/2/5/10/25/50/100/250 ms), saturation (pod CPU, goroutine/thread pool, connection pool use).
- **Cache effectiveness:** `hit_ratio{layer=cdn|local|redis}` — alert if local+Redis combined < 90% for 10 min.
- **Business canaries:** a synthetic probe creates a link and follows it every 30 s from 3 regions (end-to-end check, including read-after-write).
- **Analytics integrity:** compare redirect count (LB) vs events ingested; alert on > 2% divergence for > 15 min.
- **Burn-rate alerts:** page on 14.4× burn over 1 h (fast) and 6× over 6 h (slow) for the availability SLO.
- **Dashboards:** one for the on-call (traffic, errors, latency, cache, DB, Kafka lag), one for capacity (growth of rows, storage, ID space consumed %), one for abuse (blocked links, report rate, 404 rate by source).

## 27. Capacity Headroom Table

| Resource | Steady (10k/s) | Peak design (30k/s) | Limit that matters |
|---|---|---|---|
| Redirect pods (≈ 4k req/s/pod conservative) | 4 needed → run 8 | 8 needed → run 12 | CPU, TLS handshakes (terminate at LB) |
| Redis ops/s | ~1–2k (after CDN + local) | ~5k | Memory, not ops (hot set ≈ 30 GB at 100M entries × ~300 B) |
| DB reads/s | ~500 | ~1.5k (3k in cache-flush drill) | Per-node IOPS |
| DB writes/s | ~100 | ~300 | trivial |
| Kafka MB/s | ~2 | ~6 | trivial |
| Storage growth | ~4 GB/day (links), ~170 GB/day raw clicks (~10× less after compression/columnar) | — | Click retention is the cost driver |

**Largest cost drivers** (in order): CDN egress/requests, click-event storage and compute, multi-region replication traffic, then the stateless compute. The core redirect service itself is cheap.

## 28. Operations

- **Runbooks** (each with detection, diagnosis commands, mitigation, escalation): cache failover, DB node replacement, emergency takedown, region evacuation, Kafka lag, ID allocator recovery, certificate renewal failure.
- **Deploys:** canary 1% → 10% → 50% → 100%, auto-gated on error rate and p99; never deploy to all AZs at once; deploys frozen during the Kafka/DB maintenance windows.
- **Schema/data migrations:** expand → backfill → contract; the redirect path must tolerate both the old and new column sets for one release.
- **Resharding:** logical shards (64+) moved between physical nodes with dual-write + verification; no key rehashing.
- **Disaster recovery drills:** quarterly restore from backup into an isolated environment; verify RPO/RTO; game-day an AZ loss yearly.
- **Data lifecycle:** expired links tombstoned for 30 days (grace for accidental expiry), then hard-deleted; code reuse of deleted links is **disallowed** to prevent hijacking of old printed URLs.

## 29. Alternatives Considered and Rejected

| Alternative | Why not |
|---|---|
| Single Postgres + Redis | Works at 10k/s today, but single-primary write ceiling and storage growth force sharding later; acceptable as an MVP stage (see §30) |
| Random codes with collision retry | Needs a DB round trip per create to check; ranges avoid this, though random is simpler if write rate stays ≈ 100/s |
| Hash of long URL as code | Collisions + same URL for every user + no per-link analytics/ownership |
| Snowflake-style IDs | 64-bit IDs → 11 base62 chars; needlessly long for a *short* URL |
| 301 by default | Browser caching hides clicks and makes takedown ineffective |
| Counter in the DB per click | Hot row contention; async event pipeline is strictly better |
| Serverless-only (Lambda + DynamoDB) | Legitimate for this scale and cheaper to operate; cold starts and per-request pricing at 10k/s sustained make containers cheaper, but see §30 for when it wins |

## 30. Phased Rollout Plan

| Phase | Scope | Exit criteria |
|---|---|---|
| **0 — MVP** | Monolith (create + redirect), one Postgres primary + replica, one Redis, CDN in front; 302 only | Load test at 10k req/s passes with ≥ 90% cache hit |
| **1 — Production-ready** | Split redirect/create services, multi-AZ, Feistel codes with ID blocks, Kafka → ClickHouse analytics, observability + alerts, abuse screening | 99.95% over 30 days, runbooks tested |
| **2 — Scale & resilience** | Sharded/partitioned KV store, Redis cluster, burn-rate alerting, chaos testing, takedown < 60 s proven | AZ-loss game day passes with no user-visible errors |
| **3 — Global** | Multi-region active-active reads, regional ID ranges, alias authority, edge KV for redirects | Region-evacuation drill passes; p99 < 30 ms in all target regions |

Build Phase 0–1 first: at 10k req/s the boring design (Postgres + Redis + CDN) is genuinely sufficient, and the stages above add complexity only when a measured need appears.

## 31. Open Questions (to resolve before building)

1. Are anonymous creates allowed? (Drives abuse-handling cost more than any scaling concern.)
2. Required analytics freshness: seconds (streaming aggregates) or hours (batch)?
3. Custom domains per tenant? (Changes the key to `(domain, code)` and the CDN/TLS strategy.)
4. Link edit support? (Rules out 301 and tightens cache invalidation.)
5. Regulatory scope (GDPR/CCPA) for click data and retention.
6. Is 99.99% required globally or per region? (Determines whether multi-region is Phase 2 or Phase 3.)
7. Budget: managed services (DynamoDB, MSK, ElastiCache) versus self-hosted. Managed removes most of §28's operational load.
