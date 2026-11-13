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
