import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../contexts/TranslationContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireSubscription?: boolean;
  requirePlan?: number;
  requireFeature?: string;
  requireAdmin?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireSubscription = false,
  requirePlan,
  requireFeature,
  requireAdmin = false,
}) => {
  const { t } = useTranslation();
  const { isAuthenticated, isAdmin, loading, hasSubscription, hasFeature } = useAuth();

  if (loading) {
    return (
      <div className="protected-route__loading">
        <div className="protected-route__spinner"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  if (requireSubscription && !hasSubscription()) {
    return <Navigate to="/" replace />;
  }

  if (requirePlan && !hasSubscription(requirePlan)) {
    return <Navigate to="/" replace />;
  }

  if (requireFeature && !hasFeature(requireFeature)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
