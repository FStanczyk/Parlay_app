import React from 'react';
import { useTranslation } from '../contexts/TranslationContext';

interface FeaturesProps {
  type: 'pro' | 'basic';
}

const Features: React.FC<FeaturesProps> = ({ type }) => {
  const { t } = useTranslation();

  return (
    <div>
      <h1>{type === 'pro' ? t.features.proFeaturesTitle : t.features.basicFeaturesTitle}</h1>
      <p>{type === 'pro' ? t.features.proFeaturesDescription : t.features.basicFeaturesDescription}</p>
    </div>
  );
};

export default Features;
