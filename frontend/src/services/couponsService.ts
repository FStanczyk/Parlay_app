import { apiGet, apiPost } from '../utils/api';
import { BetEvent } from '../types/interfaces';

export type CouponResult = 'WON' | 'LOST' | 'PENDING' | 'VOID';

export interface CouponCreate {
  name: string;
  bet_event_ids: number[];
}

export interface BetEventOnCoupon {
  id: number;
  coupon_id: number;
  bet_event_id: number;
  is_recommendation: boolean;
  bet_recommendation_id: number | null;
  bet_event?: BetEvent;
}

export interface Coupon {
  id: number;
  user_id: number;
  name: string;
  created_at: string;
  odds?: number | null;
  events?: number | null;
  result?: CouponResult | null;
  first_event_date?: string | null;
  last_event_date?: string | null;
  bet_events?: BetEventOnCoupon[];
}

export const couponsApi = {
  create: (couponData: CouponCreate): Promise<Coupon> => {
    return apiPost<Coupon>('/coupons/', couponData);
  },

  getMyCoupons: (): Promise<Coupon[]> => {
    return apiGet<Coupon[]>('/coupons/');
  },
};
