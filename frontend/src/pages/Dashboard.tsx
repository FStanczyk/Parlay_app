import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../contexts/TranslationContext';

const Dashboard: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user, logout, hasSubscription, isExpert } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="dashboard">
      <div className="dashboard__container">
        <div className="dashboard__header">
          <h1 className="dashboard__title italic-title">{t.dashboard.title}</h1>
          <button className="dashboard__logout" onClick={handleLogout}>
            {t.dashboard.logout}
          </button>
        </div>

        <div className="dashboard__grid">
          <div className="dashboard__card card">
            <h2 className="dashboard__card-title italic-title">
              {t.dashboard.welcome}, {user?.full_name || user?.email || t.common.user}!
            </h2>
            <p className="dashboard__card-text">
              {t.dashboard.email}: {user?.email}
            </p>
            {user?.subscription && (
              <div className="dashboard__subscription-info">
                <span className="dashboard__chip">
                  {user.subscription.plan?.name || 'Free'} {t.dashboard.plan}
                </span>
                <p className="dashboard__card-text">
                  {t.dashboard.status}: {user.subscription.status}
                </p>
              </div>
            )}
          </div>

          <div className="dashboard__card card">
            <div className="dashboard__card-header">
              <h2 className="dashboard__card-title italic-title">{t.dashboard.subscriptionStatus}</h2>
              {isExpert && (
                <span className="dashboard__expert-tag">{t.dashboard.expert}</span>
              )}
            </div>
            {hasSubscription() ? (
              <>
                <p className="dashboard__card-text">
                  {t.dashboard.plan}: {user?.subscription?.plan?.name}
                </p>
                <p className="dashboard__card-text">
                  {t.dashboard.expires}: {user?.subscription?.current_period_end ?
                    new Date(user.subscription.current_period_end).toLocaleDateString() :
                    t.parlaySummary.na}
                </p>
                {hasSubscription(1) && (
                  <div className="dashboard__alert dashboard__alert--success">
                    {t.dashboard.proFeaturesAccess}
                  </div>
                )}
                {hasSubscription(2) && (
                  <div className="dashboard__alert dashboard__alert--success">
                    {t.dashboard.fullFeaturesAccess}
                  </div>
                )}
              </>
            ) : (
              <p className="dashboard__card-text">
                {t.dashboard.noActiveSubscription}
              </p>
            )}
          </div>

          <div className="dashboard__card card">
            <h2 className="dashboard__card-title  italic-title">{t.dashboard.quickStats}</h2>
            <p className="dashboard__card-text">
              {t.dashboard.totalParlays}: 0
            </p>
            <p className="dashboard__card-text">
              {t.dashboard.winRate}: 0%
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
