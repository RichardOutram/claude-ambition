import * as SQLite from 'expo-sqlite';
import type { Pt } from './analyze';

const db = SQLite.openDatabaseSync('spike.db');
db.execSync(`
  CREATE TABLE IF NOT EXISTS pts (t INTEGER, lat REAL, lon REAL, acc REAL, speed REAL, recvAt INTEGER);
  CREATE TABLE IF NOT EXISTS ev (t INTEGER, kind TEXT, note TEXT);
`);

export const addPoint = (p: Pt) =>
  db.runSync('INSERT INTO pts VALUES (?,?,?,?,?,?)', [p.t, p.lat, p.lon, p.acc, p.speed, p.recvAt]);
export const addEvent = (kind: string, note = '') =>
  db.runSync('INSERT INTO ev VALUES (?,?,?)', [Date.now(), kind, note]);
export const allPoints = () => db.getAllSync<Pt>('SELECT * FROM pts ORDER BY t');
export const allEvents = () => db.getAllSync<{ t: number; kind: string; note: string }>('SELECT * FROM ev ORDER BY t');
export const clearAll = () => db.execSync('DELETE FROM pts; DELETE FROM ev;');
