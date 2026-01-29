import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../contexts/TranslationContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireSubscription?: boolean;
  requirePlan?: number;
  requireFeature?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireSubscription = false,
  requirePlan,
  requireFeature,
}) => {
  const { t } = useTranslation();
  const { isAuthenticated, loading, hasSubscription, hasFeature } = useAuth();

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

  if (requireSubscription && !hasSubscription()) {
    return <Navigate to="/hub" replace />;
  }

  if (requirePlan && !hasSubscription(requirePlan)) {
    return <Navigate to="/hub" replace />;
  }

  if (requireFeature && !hasFeature(requireFeature)) {
    return <Navigate to="/hub" replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
