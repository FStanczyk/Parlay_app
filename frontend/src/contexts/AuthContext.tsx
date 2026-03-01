import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../constants';

export interface SubscriptionPlan {
  id: number;
  name: string;
  price_monthly: number;
  price_yearly: number;
  features: Record<string, any>;
  is_active: boolean;
  sort_order: number;
  hierarchy_order: number;
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

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_admin: boolean;
  is_expert: boolean;
  created_at: string;
  subscription?: UserSubscription | null;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isExpert: boolean;
  hasSubscription: (hierarchyOrder?: number) => boolean;
  hasFeature: (featureName: string) => boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/subscriptions/me`, {
        withCredentials: true,
      });
      setUser(response.data);
    } catch (error: any) {
      if (error.response?.status === 401) {
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUser();
  }, []);

  const login = async () => {
    await fetchUser();
  };

  const logout = async () => {
    try {
      await axios.post(`${API_BASE_URL}/auth/logout`, {}, { withCredentials: true });
    } catch {
    } finally {
      setUser(null);
    }
  };

  const refreshUser = async () => {
    await fetchUser();
  };

  const hasSubscription = (hierarchyOrder?: number): boolean => {
    if (!user?.subscription) return false;
    if (user.subscription.status !== 'active') return false;

    if (hierarchyOrder === undefined) {
      return true;
    }

    const userHierarchyOrder = user.subscription.plan?.hierarchy_order ?? -1;

    return userHierarchyOrder >= hierarchyOrder;
  };

  const hasFeature = (featureName: string): boolean => {
    if (!user?.subscription?.plan?.features) return false;
    return user.subscription.plan.features[featureName] === true;
  };

  const value: AuthContextType = {
    user,
    loading,
    isAuthenticated: !!user,
    isAdmin: user?.is_admin ?? false,
    isExpert: user?.is_expert ?? false,
    hasSubscription,
    hasFeature,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
