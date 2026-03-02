import AsyncStorage from '@react-native-async-storage/async-storage';
import { api } from './api';

const DEMO_SEEDED_KEY = 'edt-demo-seeded';

/**
 * Seeds demo data on first launch (draft + wishlist items).
 * Checks AsyncStorage flag to avoid re-seeding.
 */
export async function seedDemoIfNeeded(): Promise<void> {
  try {
    const already = await AsyncStorage.getItem(DEMO_SEEDED_KEY);
    if (already) return;

    await api.post('/api/v1/demo/seed');
    await AsyncStorage.setItem(DEMO_SEEDED_KEY, 'true');
  } catch {
    // Silent fail — demo seed is best-effort
  }
}

/**
 * Resets all demo data and clears the seeded flag.
 */
export async function resetDemo(): Promise<void> {
  await api.post('/api/v1/demo/reset');
  await AsyncStorage.removeItem(DEMO_SEEDED_KEY);
}
