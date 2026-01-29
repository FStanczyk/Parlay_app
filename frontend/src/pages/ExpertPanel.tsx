import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ROUTES } from '../constants';
import { useTranslation } from '../contexts/TranslationContext';

const ExpertPanel: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="expert-panel">
      <div className="expert-panel__container">
        <h1 className="expert-panel__title italic-title">{t.expertPanel.title}</h1>
        <div className="expert-panel__options--grid">
          <div
            className="expert-panel__option"
            onClick={() => navigate(ROUTES.EXPERT_EDIT_PROFILE)}
          >
            {t.expertPanel.editProfile}
          </div>
          <div
            className="expert-panel__option"
            onClick={() => navigate(ROUTES.EXPERT_RECOMMENDATIONS)}
          >
            {t.expertPanel.manageRecommendations}
          </div>
          <div
            className="expert-panel__option"
            onClick={() => navigate(ROUTES.EXPERT_MONETIZATION)}
          >
            {t.expertPanel.manageMonetization}
          </div>
          <div
            className="expert-panel__option"
            onClick={() => navigate(ROUTES.EXPERT_STATISTICS)}
          >
            {t.expertPanel.statistics}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExpertPanel;
