# Stretch model: $6,000 in April 2027. All inputs are estimates; replace with real figures.
W = 4.345
def fees(total): return 0.095 * total + 0.45

# --- revenue route ---
retail_visits, retail_conv, retail_aov = 3200, 0.025, 45.0
retail_orders = round(retail_visits * retail_conv)
retail_rev = retail_orders * retail_aov
bulk_orders, bulk_price, bulk_ship = 6, 400.0, 30.0       # 50 mini tins at $8, postage passed through
bulk_rev = bulk_orders * bulk_price
print("retail", retail_orders, "orders", retail_rev, "| bulk", bulk_rev, "| total", retail_rev + bulk_rev)
print("run-rate per week: $3,000 ->", round(3000 / W), "| $4,100 ->", round(4100 / W), "| $6,000 ->", round(6000 / W))

# --- profit ---
bulk_total = bulk_price + bulk_ship
bulk_profit = bulk_total - fees(bulk_total) - 50 * 3.5 - bulk_ship
print("bulk order profit: fees %.2f profit %.2f" % (fees(bulk_total), bulk_profit))
retail_profit_each = 13.0
print("gross profit stretch: retail %.0f + bulk %.0f = %.0f" % (retail_orders * retail_profit_each, bulk_orders * bulk_profit,
      retail_orders * retail_profit_each + bulk_orders * bulk_profit))
print("gross profit fallback: 75 x 13 =", 75 * 13)

# --- making + packing hours ---
JAR_PER_H, MINI_PER_H = 8, 20
def hours(retail_orders, bulk_orders, bulk_tins=50):
    candles = retail_orders * 1.4
    jars, minis = candles * 0.75, candles * 0.25
    make = jars / JAR_PER_H + (minis + bulk_orders * bulk_tins) / MINI_PER_H
    pack = retail_orders * 10 / 60 + bulk_orders * 45 / 60
    return candles + bulk_orders * bulk_tins, make, pack, make + pack
for name, ro, bo in (("fallback", 75, 0), ("stretch", 80, 6)):
    c, m, p, t = hours(ro, bo)
    print(f"{name}: {c:.0f} candles, make {m:.1f} h, pack {p:.1f} h, total {t:.1f} h/month = {t/W:.1f} h/week")
# --- expected landing (bulk orders per month is the unknown) ---
for label, rr, bo in (("low", 3000, 1), ("mid", 3600, 2), ("high", 3600, 4)):
    print(label, rr + bo * bulk_price)
# outreach funnel
for contacts, reply, close in ((60, 0.10, 0.15), (60, 0.20, 0.15), (60, 0.20, 0.30)):
    print("outreach", contacts, reply, close, "->", round(contacts * reply * close, 1), "orders")
print("inquiries needed for 6 orders at 15% close:", round(6 / 0.15))
