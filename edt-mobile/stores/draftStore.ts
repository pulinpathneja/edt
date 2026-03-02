import { create } from 'zustand';
import * as draftApi from '@/services/draftApi';
import type { DraftData } from '@/services/draftApi';

interface DraftState {
  activeDraft: DraftData | null;
  isLoading: boolean;

  loadActiveDraft: () => Promise<void>;
  saveDraft: (data: DraftData) => Promise<void>;
  updateDraft: (data: Partial<DraftData>) => Promise<void>;
  discardDraft: () => Promise<void>;
  markCompleted: () => Promise<void>;
}

export const useDraftStore = create<DraftState>((set, get) => ({
  activeDraft: null,
  isLoading: false,

  loadActiveDraft: async () => {
    set({ isLoading: true });
    try {
      const draft = await draftApi.getActiveDraft();
      set({ activeDraft: draft, isLoading: false });
    } catch {
      set({ activeDraft: null, isLoading: false });
    }
  },

  saveDraft: async (data) => {
    try {
      const { activeDraft } = get();
      if (activeDraft?.id) {
        const updated = await draftApi.updateDraft(activeDraft.id, data);
        set({ activeDraft: updated });
      } else {
        const created = await draftApi.createDraft(data);
        set({ activeDraft: created });
      }
    } catch {
      // Silently fail — draft save is best-effort
    }
  },

  updateDraft: async (data) => {
    try {
      const { activeDraft } = get();
      if (!activeDraft?.id) return;
      const updated = await draftApi.updateDraft(activeDraft.id, data);
      set({ activeDraft: updated });
    } catch {
      // Silently fail
    }
  },

  discardDraft: async () => {
    try {
      const { activeDraft } = get();
      if (activeDraft?.id) {
        await draftApi.deleteDraft(activeDraft.id);
      }
      set({ activeDraft: null });
    } catch {
      set({ activeDraft: null });
    }
  },

  markCompleted: async () => {
    try {
      const { activeDraft } = get();
      if (activeDraft?.id) {
        await draftApi.updateDraft(activeDraft.id, { status: 'completed' });
      }
      set({ activeDraft: null });
    } catch {
      set({ activeDraft: null });
    }
  },
}));
