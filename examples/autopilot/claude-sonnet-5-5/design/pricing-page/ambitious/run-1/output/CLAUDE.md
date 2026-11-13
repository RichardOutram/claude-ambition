# Pricing page

`pricing.html` is one self-contained file (no build, no dependencies).

## Check it
`cd checks && npm install && npm run check` (needs Google Chrome at /Applications). Or run `/check-pricing`.
- `accept.mjs`: 39 checks in real Chrome: plan structure, objection answers inside each plan card, price/fee/table arithmetic, toggle + selector + signup links, no overflow 320-1280px, axe-core 0 violations in light and dark, no-JS fallback.
- `stretch.mjs`: first screen must show the Solo button at 375x667 and all three objection lines at 1366x640.
Last run: 39/39 and stretch met. Re-run after any copy, price or layout edit.

## Before launch
Price, fee and policy numbers are placeholders (see FAQ and plan cards). Replace the `/signup` links.
