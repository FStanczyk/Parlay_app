import { apiGet, apiPost, apiDelete } from '../utils/api';

export const followApi = {
  getFollowedIds: (): Promise<number[]> => {
    return apiGet<number[]>('/tipsters/following/ids');
  },
  follow: (tipsterId: number): Promise<{ detail: string }> => {
    return apiPost<{ detail: string }>(`/tipsters/${tipsterId}/follow`);
  },
  unfollow: (tipsterId: number): Promise<{ detail: string }> => {
    return apiDelete<{ detail: string }>(`/tipsters/${tipsterId}/follow`);
  },
};
