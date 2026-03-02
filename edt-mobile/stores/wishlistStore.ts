import { create } from 'zustand';
import * as wishlistApi from '@/services/wishlistApi';
import type { WishlistItemData, WishlistAddData } from '@/services/wishlistApi';

interface WishlistState {
  items: WishlistItemData[];
  wishlistedKeys: Set<string>;
  isLoading: boolean;

  loadWishlist: () => Promise<void>;
  toggleWishlist: (item: WishlistAddData) => Promise<void>;
  isWishlisted: (poiName: string, city?: string) => boolean;
  removeItem: (id: string) => Promise<void>;
}

function makeKey(poiName: string, city?: string): string {
  return `${poiName}::${city ?? ''}`;
}

export const useWishlistStore = create<WishlistState>((set, get) => ({
  items: [],
  wishlistedKeys: new Set(),
  isLoading: false,

  loadWishlist: async () => {
    set({ isLoading: true });
    try {
      const items = await wishlistApi.listWishlist();
      const keys = new Set(items.map((i) => makeKey(i.poi_name, i.city)));
      set({ items, wishlistedKeys: keys, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  toggleWishlist: async (item) => {
    const key = makeKey(item.poi_name, item.city);
    const { items, wishlistedKeys } = get();

    if (wishlistedKeys.has(key)) {
      // Remove
      const existing = items.find((i) => makeKey(i.poi_name, i.city) === key);
      if (existing) {
        const newItems = items.filter((i) => i.id !== existing.id);
        const newKeys = new Set(wishlistedKeys);
        newKeys.delete(key);
        set({ items: newItems, wishlistedKeys: newKeys });
        try {
          await wishlistApi.removeFromWishlist(existing.id);
        } catch {
          // Revert on failure
          set({ items, wishlistedKeys });
        }
      }
    } else {
      // Add (optimistic)
      const tempItem: WishlistItemData = {
        id: `temp-${Date.now()}`,
        poi_name: item.poi_name,
        city: item.city,
        country: item.country,
        category: item.category,
        image_url: item.image_url,
        description: item.description,
        created_at: new Date().toISOString(),
      };
      const newKeys = new Set(wishlistedKeys);
      newKeys.add(key);
      set({ items: [...items, tempItem], wishlistedKeys: newKeys });
      try {
        const saved = await wishlistApi.addToWishlist(item);
        // Replace temp with server item
        set((state) => ({
          items: state.items.map((i) => (i.id === tempItem.id ? saved : i)),
        }));
      } catch {
        // Revert on failure
        set({ items, wishlistedKeys });
      }
    }
  },

  isWishlisted: (poiName, city) => {
    return get().wishlistedKeys.has(makeKey(poiName, city));
  },

  removeItem: async (id) => {
    const { items, wishlistedKeys } = get();
    const item = items.find((i) => i.id === id);
    if (!item) return;

    const key = makeKey(item.poi_name, item.city);
    const newItems = items.filter((i) => i.id !== id);
    const newKeys = new Set(wishlistedKeys);
    newKeys.delete(key);
    set({ items: newItems, wishlistedKeys: newKeys });

    try {
      await wishlistApi.removeFromWishlist(id);
    } catch {
      // Revert
      set({ items, wishlistedKeys });
    }
  },
}));
