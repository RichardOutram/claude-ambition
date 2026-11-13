# URL Shortener Architecture (10k req/s)

## 1. Requirements

### Functional
- Create a short URL from a long URL (optional custom alias, optional expiry).
- Redirect a short URL to the original URL.
- Basic click analytics (async, non-blocking).
- Delete/disable links.

### Non-functional
| Attribute | Target |
|---|---|
| Throughput | 10k req/s peak total |
| Read:write ratio | ~100:1 → ~9.9k redirects/s, ~100 creates/s |
| Redirect latency | p99 < 50 ms (server side) |
| Availability | 99.95%+ for redirects; creates may degrade first |
| Durability | No loss of created links |
| Scale horizon | ~3B links over 5 years |

## 2. Capacity Estimates

- **Writes:** 100/s × 86,400 ≈ 8.6M/day ≈ 3.1B/year.
- **Storage:** ~500 B/record (short code, long URL up to 2 KB avg ~200 B, metadata) → ~1.5 TB/year; ~8 TB over 5 years before replication.
- **Key space:** base62, 7 chars = 62⁷ ≈ 3.5 trillion — ample headroom.
- **Read bandwidth:** 10k × ~500 B response ≈ 5 MB/s — trivial; the bottleneck is lookup latency, not bandwidth.
- **Cache:** Traffic is heavily skewed (Zipf). Caching the hottest ~20% of daily-active links (~a few GB) gives a >95% hit rate. A 3-node Redis cluster at 16–32 GB each is ample.

10k req/s is modest. A handful of stateless app nodes plus a cache absorbs it; the design focuses on **simplicity, cache-first reads, and failure isolation** rather than exotic scaling.

## 3. High-Level Architecture

```
                   ┌───────────────┐
 Client ──────────▶│  CDN / Edge   │  (cache 301/302 for hot links)
                   └──────┬────────┘
                          │ miss
                   ┌──────▼────────┐
                   │ L7 Load Bal.  │  (TLS termination, rate limiting)
                   └──────┬────────┘
              ┌───────────┴───────────┐
       ┌──────▼──────┐         ┌──────▼──────┐
       │ Redirect Svc│  (x N)  │  Create Svc │ (x M)
       └──────┬──────┘         └──────┬──────┘
              │                       │
       ┌──────▼──────┐         ┌──────▼──────┐
       │ Redis Cache │◀────────│ ID Generator│
       │  (cluster)  │         │ (range alloc)│
       └──────┬──────┘         └──────┬──────┘
              │ miss                  │
       ┌──────▼───────────────────────▼──────┐
       │   Primary DB (sharded, replicated)  │
       └──────────────────────────────────────┘
              │
   Redirect Svc ──async──▶ Kafka ──▶ Analytics Consumer ──▶ ClickHouse
```

Redirect and Create are **separate deployable services** so a write spike or bug cannot degrade the read path.

## 4. Components

### 4.1 Edge / CDN
- Cache redirect responses for hot links with short TTL (e.g. 60 s).
- Use **302** if per-click analytics must hit origin; **301** for max cacheability (browsers cache it, so clicks become invisible and link edits/deletes propagate slowly). Default: **302 with `Cache-Control: max-age=60`**, which balances both.
- Absorbs DDoS and traffic bursts before they reach origin.

### 4.2 Load Balancer / API Gateway
- TLS termination, HTTP/2, health checks.
- Per-IP and per-API-key rate limiting (token bucket in Redis) — stricter on `POST /links`.

### 4.3 Redirect Service (hot path)
1. Parse code from path `GET /{code}`.
2. Check in-process LRU (tiny, ~10k entries, 5–10 s TTL) to absorb extreme hot keys.
3. Check Redis. On hit → respond.
4. On miss → read DB replica, populate Redis (with TTL + jitter), respond.
5. Negative-cache unknown codes (short TTL, ~30 s) to block enumeration/penetration attacks.
6. Emit click event to Kafka **asynchronously** (fire-and-forget, bounded buffer; drop on overflow rather than block the redirect).

Stateless; autoscale on CPU/RPS. ~6–10 instances comfortably handle peak with headroom (each instance can serve several thousand cached req/s).

### 4.4 Create Service
- Validates URL (scheme allowlist, length limit, blocklist / Safe Browsing check, reject self-referential loops).
- Obtains a unique ID, base62-encodes it, writes to DB, warms cache.
- Idempotency key support so client retries don't create duplicates.
- Custom aliases: insert with unique constraint; conflict → `409`.

### 4.5 ID Generation
Options considered:

| Approach | Pros | Cons |
|---|---|---|
| Hash (MD5/SHA of URL) truncated | Stateless, dedup-friendly | Collisions need retry loops; predictable |
| Random 7-char + retry on conflict | Simple, unguessable | Collision rate rises with fill; extra DB round trip |
| **Counter ranges + base62** | No collisions, no coordination per request | Sequential → guessable unless scrambled |
| Snowflake IDs | Decentralized | Longer codes (~11 chars) |

**Chosen:** a central counter (ZooKeeper/etcd or a DB sequence) hands out **ranges of 10,000 IDs** to each Create instance, which then issues them locally from memory. Coordination happens ~once per 100 s per instance at 100 creates/s. To avoid guessable/enumerable codes, pass the integer through a **reversible bijective scramble** (e.g. Feistel network / format-preserving permutation keyed with a secret) before base62 encoding. A crashed instance wastes at most one range — acceptable given 3.5T key space.

### 4.6 Data Store

**Access pattern:** pure key-value lookup by `code`; writes are append-mostly; no joins.

**Choice:** a horizontally scalable KV/wide-column store (DynamoDB, Cassandra, or ScyllaDB). Sharded PostgreSQL/Vitess is an acceptable alternative if the team prefers relational tooling. At this scale (~100 writes/s, ~500 uncached reads/s) even a single replicated Postgres primary would work for years; the KV store is chosen for headroom and operational simplicity of sharding.

Schema (`links`):
| Column | Type | Notes |
|---|---|---|
| `code` | string (PK, partition key) | 7–10 chars base62 |
| `long_url` | string | ≤ 2048 chars |
| `owner_id` | string | nullable for anonymous |
| `created_at` | timestamp | |
| `expires_at` | timestamp | nullable; also use native TTL |
| `status` | enum | active / disabled / blocked |

Secondary index (or separate table) on `owner_id` for "my links" listing. Replication factor 3, quorum writes, read from local replica (eventual consistency is fine; read-your-writes on create is satisfied by cache warming).

### 4.7 Cache (Redis Cluster)
- Key: `code` → `long_url|status|expires_at` (compact).
- Policy: `allkeys-lru`, TTL 24 h with ±10% jitter to avoid synchronized expiry.
- Cache-aside for reads; write-through warm on create.
- Stampede protection: single-flight per key in the service + short lock on miss.
- Invalidate (delete) on disable/update.
- 3 primaries + 3 replicas; if Redis is down, services fall back to DB with a circuit breaker and tighter rate limits.

### 4.8 Analytics Pipeline
- Redirect Service → **Kafka** (`click-events`, partitioned by `code`).
- Consumers aggregate and write to **ClickHouse** (or a Druid/BigQuery equivalent): clicks per code per minute, geo, referrer, device.
- Event payload: `code, ts, ip_hash, user_agent, referrer, country`. Hash/truncate IPs for privacy.
- Fully decoupled: analytics outage never affects redirects.

### 4.9 Background Jobs
- Expiry sweeper (backup to native TTL).
- Malicious URL rescans; auto-disable flagged links and purge cache.
- Key-range replenishment monitoring.

## 5. API

```
POST /api/v1/links
  Headers: Authorization, Idempotency-Key
  Body:    { "url": "...", "alias": "optional", "expires_at": "optional" }
  201:     { "short_url": "https://sho.rt/aZ3kP9q", "code": "aZ3kP9q" }
  409:     alias taken        422: invalid/blocked URL     429: rate limited

GET /{code}
  302 Location: <long_url>
  404 unknown / 410 expired or disabled

DELETE /api/v1/links/{code}      -> 204
GET    /api/v1/links/{code}/stats -> aggregated analytics
```

## 6. Scaling & Capacity Plan

| Tier | Sizing at 10k req/s | Scale trigger |
|---|---|---|
| CDN | absorbs maybe 30–60% of hot traffic | — |
| Redirect Svc | 8 instances (4 vCPU) ≈ 2x headroom | CPU > 60% or p99 > 30 ms |
| Create Svc | 3 instances | CPU / RPS |
| Redis | 3 shards × (1 primary + 1 replica) | memory > 70%, ops/s |
| DB | 6 nodes, RF=3 | storage > 60%, read latency |
| Kafka | 3 brokers, 12 partitions | consumer lag |

Headroom goal: handle **3× peak (30k req/s)** by adding stateless nodes only; no re-architecture needed. Beyond that, add CDN cache TTL and more Redis shards.

## 7. Availability & Failure Handling

- **Multi-AZ** everywhere; optionally **multi-region active-active** for redirects (DB with cross-region replication, regional Redis). Creates can be routed to a home region.
- **Redis down:** fall back to DB with circuit breaker; in-process LRU shields hottest keys.
- **DB node down:** quorum reads/writes continue with RF=3.
- **Kafka down:** drop/buffer click events locally; redirects unaffected.
- **ID service down:** instances keep issuing from their pre-allocated range (≥100 s runway at normal load); allocate larger ranges for more buffer.
- Timeouts, retries with jitter, and load shedding on every network hop. Redirect path has strict budget: cache ≤ 5 ms, DB ≤ 30 ms, else `503`.

## 8. Security & Abuse

- Rate limiting + CAPTCHA/auth for creation; API keys for programmatic use.
- Validate scheme (`http/https` only); block `javascript:`, `data:`, private IP ranges/localhost (SSRF if any URL fetching is done).
- Malware/phishing screening at creation and periodically after.
- Unguessable codes (scrambled IDs); negative caching against enumeration.
- Optional interstitial page for flagged/unknown destinations.
- HTTPS only with HSTS; WAF at edge.

## 9. Observability

- **Metrics:** redirect RPS, p50/p95/p99 latency, cache hit ratio (target >95%), DB read latency, 4xx/5xx rates, Kafka lag, ID-range remaining.
- **Logs:** structured, sampled on the hot path.
- **Tracing:** OpenTelemetry, sampled 1%.
- **SLOs / alerts:** redirect availability 99.95%, p99 < 50 ms; page on burn-rate alerts.
- Synthetic probes from multiple regions.

## 10. Trade-offs & Decisions Summary

| Decision | Choice | Rationale |
|---|---|---|
| Redirect code | 302 + short max-age | Keeps analytics and edit/delete workable while still cacheable |
| ID generation | Range-allocated counter + scramble | Zero collisions, no per-request coordination, not enumerable |
| Storage | Replicated KV store | Pure key lookups, easy horizontal scale |
| Consistency | Eventual for reads | Links are immutable-ish; stale window of seconds is acceptable |
| Analytics | Async via Kafka | Never on the critical path |
| Service split | Separate read/write services | Independent scaling and failure isolation |

## 11. Possible Future Extensions
- Per-link QR codes, custom domains (domain → tenant mapping in cache).
- A/B and geo-targeted redirects (rule evaluation at the edge).
- Link editing with versioned cache invalidation.
- Tiered storage: archive cold/expired links to object storage.
