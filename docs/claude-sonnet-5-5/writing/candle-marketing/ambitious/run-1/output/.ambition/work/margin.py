# Margin test: does the order-value lever raise PROFIT, or only revenue?
# Assumptions (all estimates, replace with real): COGS per 8oz jar $9, per mini $3.50,
# postage $8-12 (inference from published 1lb/5lb Ground Advantage figures), Etsy fees 6.5% + 3% of
# (item + shipping charged) + $0.20 listing + $0.25 processing; Offsite Ad fee 15% on attributed orders.
def profit(price, ship_charged, cogs, ship_cost, offsite=False):
    total = price + ship_charged
    fees = 0.095 * total + 0.45
    p = total - fees - cogs - ship_cost
    if offsite:
        p -= 0.15 * total
    return total, fees, p
cases = [
 ("A", "1 jar $28 + $7 shipping paid by buyer", 28, 7, 9.0, 9.0),
 ("B", "Jar + mini add-on, $38, free shipping", 38, 0, 12.5, 9.5),
 ("C", "2-jar set $52, free shipping", 52, 0, 18.0, 12.0),
 ("D", "3-mini set $38, free shipping", 38, 0, 10.5, 8.0),
 ("E", "2-jar set $38, free shipping", 38, 0, 18.0, 12.0),
]
for k, name, pr, sc, cg, sh in cases:
    t, f, p = profit(pr, sc, cg, sh)
    _, _, po = profit(pr, sc, cg, sh, True)
    print(f"{k} | {name} | order ${t:.0f} | fees ${f:.2f} | profit ${p:.2f} | with offsite ${po:.2f}")
print("price floor, 2-jar set, free ship, profit>=12:", (12+12+0.45+18-18+18-18)/1)  # placeholder, recomputed below
# price at which a 2-jar set (COGS 18, ship 12) clears $12 profit: P*(1-0.095) - 0.45 - 18 - 12 = 12
print("floor P =", round((12 + 0.45 + 18 + 12) / 0.905, 2))
print("spring A gross profit range:", round(75*11.94), round(75*16.61))
print("baseline gross profit (37 x A):", round(37*13.23))
