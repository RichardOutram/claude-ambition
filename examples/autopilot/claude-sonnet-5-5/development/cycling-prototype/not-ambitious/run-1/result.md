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