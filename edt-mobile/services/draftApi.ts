import { api } from './api';

export interface DraftData {
  id?: string;
  current_step?: number;
  country_id?: string;
  country_name?: string;
  start_date?: string;
  end_date?: string;
  group_type?: string;
  group_size?: number;
  vibes?: string[];
  budget_level?: number;
  pacing?: string;
  selected_allocation?: any;
  status?: string;
}

export async function getActiveDraft(): Promise<DraftData | null> {
  const { data } = await api.get('/api/v1/drafts/active');
  return data;
}

export async function createDraft(draft: DraftData): Promise<DraftData> {
  const { data } = await api.post('/api/v1/drafts/', draft);
  return data;
}

export async function updateDraft(id: string, draft: Partial<DraftData>): Promise<DraftData> {
  const { data } = await api.patch(`/api/v1/drafts/${id}`, draft);
  return data;
}

export async function deleteDraft(id: string): Promise<void> {
  await api.delete(`/api/v1/drafts/${id}`);
}
