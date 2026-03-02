import { api } from './api';

export interface WishlistItemData {
  id: string;
  poi_name: string;
  city?: string;
  country?: string;
  category?: string;
  image_url?: string;
  description?: string;
  created_at: string;
}

export interface WishlistAddData {
  poi_name: string;
  city?: string;
  country?: string;
  category?: string;
  image_url?: string;
  description?: string;
}

export async function listWishlist(): Promise<WishlistItemData[]> {
  const { data } = await api.get('/api/v1/wishlist/');
  return data;
}

export async function addToWishlist(item: WishlistAddData): Promise<WishlistItemData> {
  const { data } = await api.post('/api/v1/wishlist/', item);
  return data;
}

export async function removeFromWishlist(id: string): Promise<void> {
  await api.delete(`/api/v1/wishlist/${id}`);
}

export async function checkWishlisted(poiName: string, city?: string): Promise<{ is_wishlisted: boolean; item_id?: string }> {
  const { data } = await api.get('/api/v1/wishlist/check', { params: { poi_name: poiName, city } });
  return data;
}
