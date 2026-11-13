"""Capacity model. Edit ASSUMPTIONS, re-run: python3 capacity.py"""
PEAK_RPS      = 10_000   # total peak requests/s (given)
READ_PER_WRITE = 100     # redirects per create (assumption; see sources)
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
print(f"ID range lasts {ID_RANGE/writes:.0f}s at peak write rate per single instance (worst case)")
for hit in (0.80, 0.90, 0.95, 0.99):
    print(f"origin DB reads/s at edge+cache hit {hit:.0%}: {reads*(1-hit):,.0f}")
print(f"Redis memory for 100M hot links: {100e6*REDIS_BYTES/1e9:.0f} GB")
