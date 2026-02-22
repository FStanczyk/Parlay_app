import { TipsterPublic } from '../types/interfaces';
import { apiGet, publicApiGet } from '../utils/api';

export interface TipsterStats {
  total_picks: number;
  total_picks_won: number;
  sum_stake: number;
  total_return: number;
  sum_odds: number;
  picks_with_description: number;
}

export interface TopExpert {
  id: number;
  full_name: string | null;
  country: string | null;
  is_verified: boolean;
  tag_1: string | null;
  tag_2: string | null;
  tag_3: string | null;
  total_picks: number;
  total_picks_won: number;
  roi: number;
}

export interface TopPick {
  tipster_id: number;
  tipster_name: string | null;
  tipster_verified: boolean;
  event: string;
  odds: number;
  home_team: string;
  away_team: string;
  game_datetime: string;
}

export interface TipsterMe {
  id: number;
  user_id: number;
  description: string | null;
  appreciation: number;
  is_verified: boolean;
  tag_1: string | null;
  tag_2: string | null;
  tag_3: string | null;
}

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
  getStats: (id: number): Promise<TipsterStats> => {
    return publicApiGet<TipsterStats>(`/tipsters/${id}/stats`);
  },
  getMe: (): Promise<TipsterMe> => {
    return apiGet<TipsterMe>('/tipsters/me');
  },
  getLeaderboard: (limit = 10): Promise<TopExpert[]> => {
    return publicApiGet<TopExpert[]>(`/tipsters/leaderboard?limit=${limit}`);
  },
  getTopPicks: (limit = 10, days = 3): Promise<TopPick[]> => {
    return publicApiGet<TopPick[]>(`/tipsters/top-picks?limit=${limit}&days=${days}`);
  },
};
