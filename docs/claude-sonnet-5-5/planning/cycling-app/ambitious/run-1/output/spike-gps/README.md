# GPS background-recording spike (throwaway)

Goal: show whether Expo's background location holds up on a real ride. Pass criteria are in
section 3 of `PLAN.md`.

## Set up (needs Xcode + Android Studio; see "Toolchain" below)
```sh
cd "/Volumes/My Shared Files/work/spike-gps"
npx create-expo-app@latest app --template blank-typescript
cd app
npx expo install expo-location expo-task-manager expo-sqlite expo-battery
cp -R ../src ./src && cp ../App.tsx ./App.tsx
```
Add to `app/app.json` inside `"expo"` (use your own bundle id / package):
```json
"ios": { "bundleIdentifier": "com.yourname.gpsspike" },
"android": { "package": "com.yourname.gpsspike" },
"plugins": [["expo-location", {
  "isIosBackgroundLocationEnabled": true,
  "isAndroidBackgroundLocationEnabled": true,
  "isAndroidForegroundServiceEnabled": true,
  "locationAlwaysAndWhenInUsePermission": "Spike test: records your ride in the background."
}]]
```
Build onto each phone (free Apple provisioning lasts 7 days):
```sh
npx expo run:ios --device
npx expo run:android --device
```

## Run the test (each phone, ideally the same ride carried together)
1. Open the app, tap **Start**, allow location, choose **Always**. Lock the screen, put the phone in a jersey pocket or bag.
2. Ride 45+ minutes with some stops. Start a reference recorder too (Apple Fitness / Strava / bike computer) and note its distance.
3. Optional kill test: mid-ride, force-quit the app, reopen, and note what happens. Tap Start again if needed.
4. Tap **Stop**, then **Show summary** (check `passGaps`, `dropoutPct`, `longestMovingGapS`), then **Share log** and send it to yourself.
5. Note battery start/stop (the log records both) and the reference distance.

Send the shared text back; the plan's results table (section 10) gets filled from it.

## Toolchain (found 2026-11-13 on this Mac)
- `xcodebuild` points at Command Line Tools, not full Xcode. If Xcode is installed: `sudo xcode-select -s /Applications/Xcode.app/Contents/Developer`.
- No Android SDK at `~/Library/Android/sdk` and `adb` is not on PATH. Set `ANDROID_HOME` and add `platform-tools` to PATH (Android Studio > SDK Manager shows the path).
- This spike app has not been built or run. Only `src/analyze.ts` has been tested (below).

## Analyzer test
`node --experimental-strip-types test-analyze.mjs` from this folder.
