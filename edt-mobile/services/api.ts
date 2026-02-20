import axios from 'axios';
import { Platform } from 'react-native';

const getBaseURL = () => {
  if (__DEV__) {
    // Android emulator uses 10.0.2.2 for host loopback; iOS simulator uses localhost
    return Platform.OS === 'android'
      ? 'http://10.0.2.2:8000'
      : 'http://localhost:8000';
  }
  // Production: Cloud Run URL
  return 'https://edt-api-724289610112.us-central1.run.app';
};

export const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});
