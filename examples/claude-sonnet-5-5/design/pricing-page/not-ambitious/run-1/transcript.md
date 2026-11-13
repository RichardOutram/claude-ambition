# design/pricing-page · not-ambitious

### User

Design a pricing page for an invoicing app for freelancers, as a single web page

**→ Write** `{"file_path": "<workspace>/pricing.html", "content": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>Quillbill \u2014 Pricing for freelancers</title>\n<meta name=\"description\" content=\"Simple invoicing for freelancers. Start free, upgrade when you're busy. No hidden fees.\">\n<style>\n  :roo … [16217 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/pricing.html (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I built the pricing page as one self-contained HTML file with no dependencies: `<workspace>/pricing.html`. I haven't opened it in a browser, so the layout and the billing toggle are untested.

**What's on the page**
- **Hero and billing toggle:** a headline and a Monthly/Annual switch. Choosing Annual updates the prices and the "billed" text, and the annual option is labelled "2 months free".
- **Three plans:**
  - **Starter** is free: 3 clients, 5 invoices a month.
  - **Freelancer** costs $12 a month ($10 on the annual plan). It's highlighted as "Most popular" and has unlimited invoices, reminders, recurring invoices and multi-currency.
  - **Studio** costs $29 a month ($24 on the annual plan). It adds a team, a client portal, reports and an API.
- **Reassurance:** a line under the plans says payment processing fees are charged by the processor, with nothing added on top. A trust strip below lists "Cancel anytime", "No per-invoice fees" and similar.
- **Comparison table:** it groups features by invoicing, getting paid, work and team, and support. It scrolls sideways on small screens.
- **Testimonial, FAQ and closing sign-up button:** the FAQ covers the free-trial card, plan limits, cancelling, fees, discounts and refunds.

**Design choices**
- A calm green and cream palette, with a dark theme that follows the system setting.
- On mobile the plans stack, with the featured plan first.
- The toggle is keyboard-accessible, there are visible focus outlines, and animations switch off for people who prefer reduced motion.

The product name (Quillbill), the prices, the plan limits, the testimonial and the discount and refund terms are all placeholders I made up. Replace them with your real details. To preview the page, run `open "<workspace>/pricing.html"`.

### User

Push it further.

**→ Write** `{"file_path": "<workspace>/pricing.html", "content": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>Quillbill \u2014 Pricing for freelancers</title>\n<meta name=\"description\" content=\"Simple invoicing for freelancers. Start free, upgrade when you're busy. No hidden fees.\">\n<style>\n  :roo … [28922 more chars]`

<details><summary>result</summary>

```
The file <workspace>/pricing.html has been updated successfully. (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I rewrote `<workspace>/pricing.html` with a lot more in it. I haven't opened it in a browser, so the animations, the calculator and the layout are untested.

**New**
- **Hero invoice:** a tilted mock invoice whose "PAID" stamp slams down a moment after load. It shows the product's payoff right at the top of the page.
- **Currency switcher (USD, EUR, GBP):** prices and the yearly totals update with it. The numbers also count up when you flip monthly/annual.
- **"Does it pay for itself?" calculator:**
  - **Inputs:** two sliders, for invoices per month and your hourly rate.
  - **Output:** it shows the monthly value of admin time you'd get back, and highlights the plan that fits.
  - **Starter case:** at 5 invoices a month or fewer, it says Starter covers you.
  - **Paid case:** above that, it says how many times Freelancer would pay for itself.
  - **Assumptions:** it assumes about 20 minutes of admin per invoice by hand versus 3 with the app, and the page says so.
- **Stats strip:** the numbers count up as it scrolls into view.
- **Comparison table:** the Freelancer column is tinted so it stands out.
- **Polish:**
  - **Background:** a soft gradient glow behind the hero.
  - **Plan cards:** they lift on hover.
  - **Sections:** each fades in on scroll.
  - **Mobile:** a sticky "Start free trial" bar appears once the plans scroll off screen.
  - **Reduced motion:** every animation turns off.

**Placeholders to replace**
- The usage stats (48,000+ freelancers, $2.1B invoiced, 9 days faster) are made up. I put an "illustrative figures" footnote at the bottom, which you should remove once the numbers are real.
- The EUR and GBP prices are hand-picked round numbers, not converted rates.
- Everything from the first version is still a placeholder: the Quillbill name, the plan limits, the testimonial and the discount and refund terms.

Next I could add a plan-finder quiz, a "Contact sales" tier for agencies, or a version split into components for a real codebase. Tell me which you want.
