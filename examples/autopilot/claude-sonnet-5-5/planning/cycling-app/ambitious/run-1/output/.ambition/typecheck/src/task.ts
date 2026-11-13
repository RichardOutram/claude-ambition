// Imported at the top of App.tsx so defineTask runs at module load (required by expo-task-manager).
import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
import { addEvent, addPoint } from './db';

export const TASK = 'spike-gps-task';

// Tune these between rides if the first ride shows dropouts (note the values in the log).
export const CONFIG: Location.LocationTaskOptions = {
  accuracy: Location.Accuracy.BestForNavigation,
  distanceInterval: 10, // metres (both OSes)
  timeInterval: 5000, // ms (Android only)
  activityType: Location.ActivityType.Fitness,
  pausesUpdatesAutomatically: false,
  showsBackgroundLocationIndicator: true,
  foregroundService: { notificationTitle: 'Spike recording', notificationBody: 'Logging GPS' },
};

TaskManager.defineTask(TASK, async ({ data, error }: any) => {
  if (error) {
    addEvent('task_error', String(error.message ?? error));
    return;
  }
  const now = Date.now();
  for (const l of (data?.locations ?? []) as Location.LocationObject[]) {
    addPoint({
      t: l.timestamp, lat: l.coords.latitude, lon: l.coords.longitude,
      acc: l.coords.accuracy ?? -1, speed: l.coords.speed ?? -1, recvAt: now,
    });
  }
});

export async function startRecording(): Promise<string> {
  const fg = await Location.requestForegroundPermissionsAsync();
  if (fg.status !== 'granted') return 'foreground permission denied';
  const bg = await Location.requestBackgroundPermissionsAsync();
  if (bg.status !== 'granted') return 'background ("Always") permission denied';
  await Location.startLocationUpdatesAsync(TASK, CONFIG);
  addEvent('start', JSON.stringify({ ...CONFIG, accuracy: 'BestForNavigation' }));
  return 'recording';
}

export async function stopRecording() {
  if (await Location.hasStartedLocationUpdatesAsync(TASK)) await Location.stopLocationUpdatesAsync(TASK);
  addEvent('stop');
}
