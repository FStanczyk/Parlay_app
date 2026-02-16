import { TipsterPublic } from '../types/interfaces';
import { apiGet, publicApiGet } from '../utils/api';

export interface TipsterFilters {
  followingOnly?: boolean;
  tagSearch?: string;
  sortBy?: 'followers' | 'appreciation' | 'recommendations';
}

export interface BetRecommendation {
  id: number;
  bet_event_id: number;
  tipster_id: number;
  tipster_tier_id?: number;
  tipster_description?: string;
  stake?: number;
  bet_event?: {
    id: number;
    odds: number;
    event: string;
    result?: 'WIN' | 'LOOSE' | 'TO_RESOLVE' | 'VOID' | 'UNKNOWN';
    game?: {
      id: number;
      datetime: string;
      home_team: string;
      away_team: string;
      league?: {
        id: number;
        name: string;
      };
    };
  };
  tipster_tier?: {
    id: number;
    level: number;
    name?: string;
  };
}

export const tipsterApi = {
  getAll: (filters?: TipsterFilters): Promise<TipsterPublic[]> => {
    const params = new URLSearchParams();
    if (filters?.followingOnly) {
      params.append('following_only', 'true');
    }
    if (filters?.tagSearch) {
      params.append('tag_search', filters.tagSearch);
    }
    if (filters?.sortBy) {
      params.append('sort_by', filters.sortBy);
    }
    const queryString = params.toString();
    return apiGet<TipsterPublic[]>(`/tipsters/${queryString ? `?${queryString}` : ''}`);
  },
  getById: (id: number): Promise<TipsterPublic> => {
    return publicApiGet<TipsterPublic>(`/tipsters/${id}`);
  },
  getRecommendations: (id: number): Promise<BetRecommendation[]> => {
    return publicApiGet<BetRecommendation[]>(`/tipsters/${id}/recommendations`);
  },
};
