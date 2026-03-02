import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface PreferencesState {
  groupType: string;
  groupSize: number;
  vibes: string[];
  budgetLevel: number;
  pacing: string;

  setPreferences: (prefs: Partial<Pick<PreferencesState, 'groupType' | 'groupSize' | 'vibes' | 'budgetLevel' | 'pacing'>>) => void;
  clear: () => void;
}

const defaultPrefs = {
  groupType: '',
  groupSize: 2,
  vibes: [] as string[],
  budgetLevel: 3,
  pacing: 'moderate',
};

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      ...defaultPrefs,

      setPreferences: (prefs) => set((state) => ({ ...state, ...prefs })),

      clear: () => set(defaultPrefs),
    }),
    {
      name: 'edt-preferences',
      storage: createJSONStorage(() => AsyncStorage),
    },
  ),
);
