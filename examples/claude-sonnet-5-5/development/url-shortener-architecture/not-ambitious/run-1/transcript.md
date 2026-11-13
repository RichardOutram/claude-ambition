# dev/url-shortener-architecture · not-ambitious

### User

Design the architecture for a URL shortener that handles 10k requests a second, as a Markdown file

**→ Write** `{"file_path": "<workspace>/url-shortener-architecture.md", "content": "# URL Shortener \u2014 Architecture (10k req/s)\n\n## 1. Requirements\n\n### Functional\n- Create a short URL from a long URL (optional custom alias, optional expiry).\n- Redirect short URL \u2192 long URL (HTTP 301/302).\n- Basic click analytics (async, non-blocking).\n- Delete/disable links.\n\n### Non-functional\n| Attribute … [13809 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/url-shortener-architecture.md (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I wrote the design to `<workspace>/url-shortener-architecture.md`. I haven't load-tested it or run any of it, so the sizing numbers are estimates.

The main decisions in it:

- **Load assumption:** about 100:1 reads to writes, so roughly 9,900 redirects/s and 100 creates/s. At that scale the design is mostly about keeping reads off the database.
- **Read path:** CDN, then an in-process cache, then Redis, then the database. This should serve over 95% of redirects from cache, with negative caching to absorb scans for codes that don't exist.
- **Redirect type:** it defaults to 302 with a short `max-age`, so clicks still get counted and links can still be edited or disabled. 301 is an opt-in.
- **Short codes:** each Create instance gets a block of IDs, scrambles them with a reversible keyed function, and encodes them as 7-character base62. That avoids collisions and per-write coordination, and the codes aren't guessable. Custom aliases use a conditional insert.
- **Storage:** a partitioned key-value store such as DynamoDB, Cassandra or Scylla, since every lookup is by code. Sharded Postgres or MySQL is listed as an alternative.
- **Analytics:** click events go asynchronously through Kafka into ClickHouse, so the redirect never waits on them.
- **Services:** redirect and create run as separate stateless services, so each scales and fails independently.
- **Sizing:** the plan covers about 3× headroom (30k req/s), with instance counts per component.

The file also covers capacity estimates, the API, failure handling, abuse prevention, monitoring, a test plan and future extensions.

### User

Push it further.

### Assistant

I'll extend the document with a second part that goes deeper on the parts the first pass skimmed: failure modes, consistency edge cases, the code-generation internals, hot keys, multi-region, schemas and rollout.

**→ Edit** `{"replace_all": false, "file_path": "<workspace>/url-shortener-architecture.md", "old_string": "- Edge compute (Workers/Lambda@Edge) serving redirects from replicated edge KV for global sub-20 ms latency.\n", "new_string": "- Edge compute (Workers/Lambda@Edge) serving redirects from replicated edge KV for global sub-20 ms latency.\n\n---\n\n# Part II \u2014 Deep Dives\n\n## 17. Latency Budget (p99 … [20203 more chars]`

<details><summary>result</summary>

```
The file <workspace>/url-shortener-architecture.md has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

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
