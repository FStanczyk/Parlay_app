import { apiGet, apiPost, publicApiGet } from '../utils/api';
import { BetEvent } from '../types/interfaces';

export const betEventsApi = {
  // Get all bet events (public - no auth required)
  getAll: (): Promise<BetEvent[]> => {
    return publicApiGet<BetEvent[]>('/bet-events/');
  },

  // Get bet events filtered by sport_id and/or league_id (public - no auth required)
  getFiltered: (sportId?: number, leagueId?: number): Promise<BetEvent[]> => {
    const params = new URLSearchParams();
    if (sportId !== undefined) params.append('sport_id', sportId.toString());
    if (leagueId !== undefined) params.append('league_id', leagueId.toString());
    
    const queryString = params.toString();
    const endpoint = queryString ? `/bet-events/filter?${queryString}` : '/bet-events/filter';
    
    return publicApiGet<BetEvent[]>(endpoint);
  },

  // Get specific bet event by ID (public - no auth required)
  getById: (id: number): Promise<BetEvent> => {
    return publicApiGet<BetEvent>(`/bet-events/${id}`);
  },

  // Get N random bet events (public - no auth required)
  getRandom: (limit: number = 10, sportId?: number, leagueId?: number, excludeIds?: number[], minOdds?: number, maxOdds?: number): Promise<BetEvent[]> => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (sportId !== undefined) params.append('sport_id', sportId.toString());
    if (leagueId !== undefined) params.append('league_id', leagueId.toString());
    if (excludeIds && excludeIds.length > 0) params.append('exclude_ids', excludeIds.join(','));
    if (minOdds !== undefined) params.append('min_odds', minOdds.toString());
    if (maxOdds !== undefined) params.append('max_odds', maxOdds.toString());
    
    const queryString = params.toString();
    const endpoint = `/bet-events/random?${queryString}`;
    
    return publicApiGet<BetEvent[]>(endpoint);
  },

  // Create new bet event (requires authentication)
  create: (betEvent: Omit<BetEvent, 'id'>): Promise<BetEvent> => {
    return apiPost<BetEvent>('/bet-events/', betEvent);
  },

  // Export bet events to CSV (requires authentication)
  exportCsv: (sportId?: number, leagueId?: number): Promise<Blob> => {
    const params = new URLSearchParams();
    if (sportId !== undefined) params.append('sport_id', sportId.toString());
    if (leagueId !== undefined) params.append('league_id', leagueId.toString());
    
    const queryString = params.toString();
    const endpoint = queryString ? `/bet-events/export/csv?${queryString}` : '/bet-events/export/csv';
    
    return apiGet<Blob>(endpoint);
  },
};
