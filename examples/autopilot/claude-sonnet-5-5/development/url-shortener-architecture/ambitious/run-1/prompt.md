# dev/url-shortener-architecture · ambitious

## Before the prompt

/be-ambitious

(blocked by the plugin's hook before Claude sees it; it arms the session)

## Prompt

Design the architecture for a URL shortener that handles 10k requests a second, as a Markdown file

## Client reply 1

Push it further.

## Client reply 2

B. It's for a design review, so I'll need to defend it in front of other engineers. The trade-offs and the alternatives I rejected (e.g. key generation approaches, SQL vs NoSQL, cache strategy) matter most, and the numbers should be sound enough to back those choices up.

## Client reply 3

I'd go with A and B together, with D as the framing.

A matters most to me. In a design review, people will challenge each choice, so I want to see what each one was weighed against and what would make it flip. B backs that up: the key numbers (QPS, cache hit rate, storage growth, ID runway) should show their working and assumptions, so nobody can wave them away.

D matters too. Open with a short summary and one clear diagram so I can follow the argument quickly. I don't need the full list of 10 to 15 hard questions in C, but cover the obvious ones, like what happens when the cache or database goes down.

## Client reply 4

C. I'd want the scripts so I can re-run the capacity and cache numbers myself, and I'd want the public figures so the assumptions aren't just yours. Keep it light, though: a few small scripts and a short sources list in the Markdown file, not a separate report.

## Client reply 5

Confirmed, this restatement serves what I asked for. Putting the scripts and sources in a short appendix of the same file is fine, and I'd rather you follow the numbers than defend your first draft. Please proceed and finish the work without stopping.
