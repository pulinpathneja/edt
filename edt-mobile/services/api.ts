import axios from 'axios';
import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as Crypto from 'expo-crypto';

const DEVICE_ID_KEY = 'edt-device-id';

let cachedDeviceId: string | null = null;

export async function getDeviceId(): Promise<string> {
  if (cachedDeviceId) return cachedDeviceId;

  let id = await AsyncStorage.getItem(DEVICE_ID_KEY);
  if (!id) {
    id = Crypto.randomUUID();
    await AsyncStorage.setItem(DEVICE_ID_KEY, id);
  }
  cachedDeviceId = id;
  return id;
}

const getBaseURL = () => {
  // Always use Cloud Run backend (works in both dev and prod)
  return 'https://edt-api-724289610112.us-central1.run.app';
};

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach X-Device-ID header to every request
api.interceptors.request.use(async (config) => {
  const deviceId = await getDeviceId();
  config.headers['X-Device-ID'] = deviceId;
  return config;
});

export async function registerSession(platform?: string, appVersion?: string): Promise<void> {
  try {
    await api.post('/api/v1/sessions/register', { platform, app_version: appVersion });
  } catch {
    // Silent fail — session registration is best-effort
  }
}
