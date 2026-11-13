# dev/cycling-prototype · not-ambitious

### User

Build a clickable prototype of the app in plan.md that I can open as a single html file

**→ Bash** `{"command": "cd \"<workspace>\" && ls -la && cat plan.md"}`

<details><summary>result</summary>

```
total 18
drwxr-xr-x@ 3 admin  staff    96 12 Nov 22:40 .
drwxr-xr-x  1 admin  staff     0  1 Jan  1970 ..
-rw-r--r--@ 1 admin  staff  8439 12 Nov 22:40 plan.md
# Cycling Social Fitness App (React Native + Expo) — Plan

## Context
Build a social, gamified fitness tracker for cyclists. Existing apps (Strava) are social but shallow on game mechanics; gamified apps (Zwift) are indoor-focused. Opportunity: outdoor-first ride tracking with territory/segment games, streaks, challenges, and club-based social features. Greenfield project (working dir has no existing code), so no reuse constraints.

## Product Scope

### MVP (v1)
1. **Auth & profile**: email/Apple/Google sign-in, bike garage, avatar, level/XP.
2. **Ride recording**: GPS tracking (foreground + background), live stats (speed, distance, elevation, time), auto-pause, offline-safe recording, save as route.
3. **Ride feed**: followed riders' rides, kudos, comments, map thumbnail, photos.
4. **Gamification core**:
   - XP and levels from distance, elevation, consistency
   - Streaks (weekly ride streak, with "freeze" tokens)
   - Badges/achievements (first 100 km, Everesting progress, early bird, etc.)
   - Weekly challenges (distance, climb, rides count) + personal goals
5. **Segments & leaderboards**: user-defined climb/sprint segments, KOM/QOM, friends/club/local leaderboards.
6. **Clubs**: create/join, club feed, club-vs-club monthly challenges.
7. **Push notifications**: kudos, challenge progress, streak-at-risk, segment beaten.

### v2
Territory capture ("claim" map hexes by riding through them), group rides with live location, Apple Health / Health Connect / Garmin / Bluetooth sensors (HR, power, cadence), route planner, seasons with cosmetic rewards, safety features (crash detection, live share).

## Tech Stack
- **App**: Expo SDK (latest) + TypeScript, **Expo Router** (file-based nav), dev builds via **EAS Build** (needed for background location, BLE).
- **State/data**: TanStack Query (server state), Zustan … [6565 more chars]
```

</details>

**→ Write** `{"file_path": "<workspace>/prototype.html", "content": "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n<title>Cycling Social Fitness \u2014 Prototype</title>\n<style>\n:root{--bg:#0f1115;--card:#1a1d24;--card2:#232732;--txt:#f2f4f8;--mut:#8b93a5;--acc:#ff5a1f;--acc2:#ffb020;--ok:#2ecc71;--blue:#3b82f6; … [23892 more chars]`

<details><summary>result</summary>

```
File created successfully at: <workspace>/prototype.html (file state is current in your context — no need to Read it back)
```

</details>

### Assistant

I've built the prototype as one self-contained file: `<workspace>/prototype.html`. Double-click it to open it in a browser. I haven't opened it in a browser yet, so I haven't clicked through it to check for bugs.

It shows a phone-sized frame on desktop and goes full-screen on a phone. The data is fake and nothing is saved, so a reload resets it.

**What you can click through**
- **Sign-in:** any button signs you in, then a location-permission prompt appears.
- **Feed:**
  - Give kudos to rides.
  - Open a ride to read and post comments.
  - Open a segment and switch its leaderboard between friends, club and local.
  - See the weekly streak card and the Pro-locked power and climb analysis.
- **Record:**
  - Start, pause and resume a ride with a live timer, distance, speed and elevation.
  - Finish to get a summary with XP earned and a matched segment.
  - Save the ride and it shows up at the top of your feed, with a badge-unlocked celebration and extra progress on your weekly distance challenge.
- **Challenges:**
  - See your level and XP bar, streak and freeze token.
  - Switch between your challenges and Discover, and join new ones.
  - Joining a Pro-only challenge opens the paywall.
- **Clubs:**
  - Join or leave clubs.
  - Open a club to see the club-vs-club monthly race, its feed and the Pro admin tools tease.
- **Profile:**
  - Stats tab with a blurred Pro training-load card.
  - Badges tab with earned and locked badges.
  - Garage tab with bikes, the privacy zone setting and sign-out.
- **Paywall:** a fake subscribe button unlocks Pro and removes the locks. The plan's "recording and core features stay free" rule is stated on the paywall.

**Left out**
- Real maps (routes are drawn as simple line sketches).
- Notifications.
- The v2 features: territory capture, group rides, sensors and the route planner.
- The Road/Gravel toggle on the Record screen is only decorative.

### User

Push it further.

**→ Bash** `{"command": "cd \"<workspace>\" && python3 - <<'EOF'\np='prototype.html'\ns=open(p).read()\ndef rep(a,b):\n    global s\n    assert s.count(a)==1,a[:60]\n    s=s.replace(a,b)\n\n# CSS\nrep(\"</style>\",\"\"\"\n.bell{position:relative;font-size:22px;cursor:pointer;padding:4px}.bell b{position:absolute;top:0;right:0;background:var(--acc);font-size:10px;border-radius:10px;padding:1px 5px}\n.dots{disp … [18729 more chars]`

<details><summary>result</summary>

```
syntax ok
```

</details>

**→ Bash** `{"command": "cd /tmp && ls node_modules/jsdom >/dev/null 2>&1 || npm i jsdom --silent 2>&1 | tail -1; node -e \"\nconst {JSDOM}=require('jsdom');const fs=require('fs');\nconst d=new JSDOM(fs.readFileSync('<workspace>/prototype.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true});\nconst w=d.window;w.SVGElement.prototype.getPointAtLength=()=>({x:1,y:1});w.SVGElement.prototype.getTotalLe … [612 more chars]`

<details><summary>result</summary>

```
ok 7 3
Shell cwd was reset to <workspace>
```

</details>

### Assistant

I've extended `prototype.html` (same file, same way of opening it). A scripted smoke test in jsdom, a simulated browser with no real layout, ran every screen and the record, finish and save flow without errors. I haven't looked at it in a real browser, so layout and the animations are unchecked.

**What's new**
- **Onboarding:** after sign-in there are three steps. You pick road or gravel, set a weekly distance goal (which renames and resizes your weekly challenge), then follow suggested riders and grant location access.
- **Notifications:**
  - The Feed has a 🔔 with an unread count.
  - The inbox covers streak at risk, segment beaten and challenge progress. Tapping an item jumps to the relevant screen.
  - There are working push-setting toggles.
  - Saving a ride later triggers live toasts: kudos from Maya after about 5 seconds, and a segment rank-up after about 12.
- **Social:**
  - Tap any avatar for a rider profile with a Follow/Unfollow button. Unfollowing removes that rider's rides from your feed.
  - A Suggested riders section appears in the feed.
- **Segments:**
  - The Feed now has Rides and Segments tabs, with your rank on each segment.
  - You can create a segment from the feed, or from a ride summary after you finish.
  - The friends, club and local leaderboards now show different results.
- **Recording:**
  - The Road/Gravel toggle now works and is saved on the ride.
  - A dot moves along the route while you ride.
  - Segment-ahead and segment-started alerts appear mid-ride.
- **Gamification:** XP now carries over into real levels. Level-ups get confetti and an XP bar animation, and each saved ride unlocks the next locked badge. Challenge progress goes up from your ride's distance, climb and ride count.
- **Pro:** the stats card is now a real chart of weekly distance with a fitness trend line. It's blurred until you unlock Pro.
- **Labs tab (v2 preview):** a hex territory map on your Profile. Tap hexes to claim neutral ones or capture rival ones for XP. It also lists the other v2 features.

If you meant something else by "further", say which direction. Options include a real map using Leaflet tiles, light mode, a Pro-only club admin dashboard, or a guided demo that walks through the main flow.
