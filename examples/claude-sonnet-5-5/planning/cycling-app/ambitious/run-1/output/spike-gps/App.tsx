import { useState } from 'react';
import { Button, ScrollView, Share, Text, View } from 'react-native';
import * as Battery from 'expo-battery';
import { stopRecording, startRecording } from './src/task';
import { addEvent, allEvents, allPoints, clearAll } from './src/db';
import { analyze } from './src/analyze';

async function batteryNote() {
  return `battery=${(await Battery.getBatteryLevelAsync()).toFixed(3)}`;
}

export default function App() {
  const [out, setOut] = useState('Idle');
  const summary = () => JSON.stringify(analyze(allPoints()), null, 2);
  return (
    <ScrollView contentContainerStyle={{ padding: 24, paddingTop: 72, gap: 12 }}>
      <Text style={{ fontSize: 20, fontWeight: '600' }}>GPS spike</Text>
      <Button title="Start" onPress={async () => { addEvent('battery_start', await batteryNote()); setOut(await startRecording()); }} />
      <Button title="Stop" onPress={async () => { await stopRecording(); addEvent('battery_stop', await batteryNote()); setOut('stopped'); }} />
      <Button title="Show summary" onPress={() => setOut(summary())} />
      <Button title="Share log (summary + CSV + events)" onPress={() => {
        const csv = ['t,lat,lon,acc,speed,recvAt', ...allPoints().map(p => `${p.t},${p.lat},${p.lon},${p.acc},${p.speed},${p.recvAt}`)].join('\n');
        const ev = allEvents().map(e => `${new Date(e.t).toISOString()} ${e.kind} ${e.note}`).join('\n');
        Share.share({ message: `${summary()}\n\nEVENTS\n${ev}\n\nCSV\n${csv}` });
      }} />
      <Button title="Clear log" color="red" onPress={() => { clearAll(); setOut('cleared'); }} />
      <View><Text selectable style={{ fontFamily: 'Courier' }}>{out}</Text></View>
    </ScrollView>
  );
}
