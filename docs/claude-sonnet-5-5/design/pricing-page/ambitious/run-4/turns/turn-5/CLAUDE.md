# Pricing page

`pricing.html` is a single self-contained page: pricing for a freelancer invoicing app ("Ledgerly"). No build step or dependencies.

## Before launch: swap in real content
- Prices: the `PRICES` object in the script at the bottom (`[monthly, per-month-when-yearly]` per currency). The headline prices and "save" text come from it.
- Links: every `href="#"` (sign-up, log in, contact sales, footer).
- Policies and claims marked `PLACEHOLDER` (`grep PLACEHOLDER pricing.html`): the testimonial, the data-protection claim, and the billing strip (trial email timing, refund, 90-day read-only). Each must match real terms. Also edit the FAQ if they change.
- If the trial will take a card up front, edit the "No card needed" lines, the billing strip and the FAQ together.

## Check after any edit
`python3 -I check-pricing.py` runs the page in headless Chrome (set `CHROME` if Chrome is elsewhere). It must print only PASS lines. It checks: the four worries, "Best for" lines and plan buttons in the first screen on desktop (1280×800); the promises, plan rows and toggle in the first screen on a 390×700 phone; no horizontal overflow; prices and billing text in every currency and period; screen-reader text in the table; named controls; no unbacked headline numbers.

Last run: 11 of 11 PASS. Lighthouse accessibility, best practices and SEO were 100 on mobile and desktop (served over http; Lighthouse rejects `file://`).
