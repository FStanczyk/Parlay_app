import React from 'react';
import { useTranslation } from '../../contexts/TranslationContext';

const Statistics: React.FC = () => {
  const { t } = useTranslation();

  return (
    <div className="expert-panel">
      <div className="expert-panel__container">
        <h1 className="expert-panel__title italic-title">{t.expertPanel.statistics}</h1>
      </div>
    </div>
  );
};

export default Statistics;
