# threejs/neon-implosion · not-ambitious

### User

Create a vivid neon art solar system particle implosion, a 10 second looping animation in three.js, as a single web page.

**→ Write** `{"file_path": "<workspace>/neon-solar-implosion.html", "content": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"UTF-8\" />\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n<title>Neon Solar Implosion \u2014 10s Loop</title>\n<style>\n  html, body { margin: 0; height: 100%; background: #02000a; overflow: hidden; }\n  canvas { display: block; }\n  #hud {\n … [14008 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/neon-solar-implosion.html (file state is current in your context — no need to Read it back)
```

</details>

**→ Bash** `{"command": "python3 - <<'EOF'\nf='neon-solar-implosion.html'; s=open(f).read()\nrep=[\n(\"uScale * 0.06 / -mv.z\",\"uScale * 0.4 / -mv.z\"),\n(\"\"\"  const f = p < IMPLODE_END ? charge * charge * 0.6 : boom;\n  flash.material.opacity = Math.min(1, f * 1.2 + 0.15 * (1 - charge));\"\"\",\n\"\"\"  // punch: rises through the collapse, relaxes after detonation (continuous, 0 at loop seam)\n  const p … [883 more chars]`

<details><summary>result</summary>

```
Exit code 2
```

</details>

**→ Bash** `{"command": "grep -c \"punch\" neon-solar-implosion.html; which node && python3 -c \"\nimport re;s=open('neon-solar-implosion.html').read();open('/tmp/m.mjs','w').write(re.search(r'<script type=\\\"module\\\">(.*)</script>',s,re.S).group(1))\" && node --check /tmp/m.mjs && echo OK", "description": "Confirm edits and syntax-check the module script"}`

<details><summary>result</summary>

```
7
/usr/bin/node
OK
```

</details>

### Assistant

I built the animation as one HTML file: **`<workspace>/neon-solar-implosion.html`**. Open it in a browser. It loads three.js from a CDN, so it needs an internet connection.

The JavaScript passes a syntax check, but there was no browser here to run it, so I haven't actually watched it play. The particle sizes, flash brightness and timing are set from calculation and may need tuning once you see it.

**What happens in each 10-second loop:**

| Time | Phase | What you see |
|---|---|---|
| 0–1.6s | **Orbit** | A neon sun made of about 18,000 particles, 8 glowing planets on orbit trails, an asteroid belt, and a ringed planet. The camera drifts slowly. |
| 1.6–5.75s | **Collapse** | All particles spiral inward, flattening into a disk and heating up to white-hot. The camera pushes in and the bloom glow builds. |
| 5.75–7s | **Detonation** | A blinding flash, three shockwave rings (cyan, magenta and yellow) at different angles, and some camera shake. The particles blow out into a nebula that shifts between magenta and cyan. |
| 7–10s | **Rebirth** | The particles curl back into their exact orbits, so the loop restarts without a visible jump. |

**How it works:**
- About 108,000 particles are moved entirely by a vertex shader. Each particle's position is calculated from where it is in the 10-second cycle, so every loop plays identically.
- Each planet completes a whole number of orbits per loop. The camera, glow, flash and twinkle values all start and end at the same value, so nothing jumps when the loop restarts.
- The glow comes from additive blending plus a bloom effect that gets stronger during the collapse and the explosion.
- A small label at the bottom shows the current phase, with a progress bar.
