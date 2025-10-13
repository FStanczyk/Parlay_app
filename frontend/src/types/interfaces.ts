// TypeScript interfaces for the application

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
  full_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
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
}
