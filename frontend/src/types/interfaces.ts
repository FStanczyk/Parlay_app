export interface Sport {
  id: number;
  name: string;
}

export interface League {
  id: number;
  sport_id: number;
  name: string;
}

export interface Game {
  id: number;
  datetime: string;
  sport_id: number;
  league_id: number;
  home_team: string;
  away_team: string;
  sport?: Sport;
  league?: League;
}

export interface BetEvent {
  id: number;
  odds: number;
  game_id: number;
  event: string;
  game?: Game;
}

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
  subscription?: UserSubscription | null;
}

export interface SubscriptionPlan {
  id: number;
  name: string;
  price_monthly: number;
  price_yearly: number;
  features: Record<string, any>;
  is_active: boolean;
  sort_order: number;
  hierarchy_order: number; // 0 is lowest tier
}

export interface UserSubscription {
  id: number;
  user_id: number;
  plan_id: number;
  status: 'active' | 'cancelled' | 'expired' | 'trial';
  current_period_start: string;
  current_period_end: string;
  created_at?: string;
  updated_at?: string;
  plan?: SubscriptionPlan;
}

export interface UserCreate {
  email: string;
  password: string;
  full_name: string;
}

export interface UserResponse {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string; // email
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface BetRecommendation {
  id: number;
  bet_event_id: number;
  tipster_id: number;
}

export interface Tipster {
  id: number;
  user_id: number;
  appreciation: number;
  description: string;
}

export interface TipsterPublic {
  id: number;
  full_name: string | null;
  country: string | null;
  appreciation: number;
  description: string | null;
  is_verified: boolean;
  followers_count: number;
  recommendations_count: number;
}

export interface TipsterTier {
  id: number;
  tipster_id: number;
  level: number;
  name?: string;
  price_monthly?: number;
  features_description?: string;
}
