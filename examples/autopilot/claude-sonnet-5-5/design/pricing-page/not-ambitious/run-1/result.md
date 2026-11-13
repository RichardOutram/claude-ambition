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