import { publicApiGet } from '../utils/api';

export interface Sport {
  id: number;
  name: string;
}

export interface League {
  id: number;
  sport_id: number;
  api_league_key: string;
  name: string;
  country_code: string;
  download: boolean;
}

export const sportsApi = {
  getAll: async (): Promise<Sport[]> => {
    return await publicApiGet<Sport[]>('/sports/');
  },

  getById: async (id: number): Promise<Sport> => {
    return await publicApiGet<Sport>(`/sports/${id}`);
  },
};

export const leaguesApi = {
  getAll: async (sportId?: number): Promise<League[]> => {
    const params = sportId ? `?sport_id=${sportId}` : '';
    return await publicApiGet<League[]>(`/leagues/${params}`);
  },

  getById: async (id: number): Promise<League> => {
    return await publicApiGet<League>(`/leagues/${id}`);
  },
};
