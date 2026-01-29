import React from 'react';
import { useTranslation } from '../contexts/TranslationContext';

interface FeaturePanelProps {
  name: string;
  description: string;
  icon: React.ReactNode;
}

const FeaturePanel: React.FC<FeaturePanelProps> = ({ name, description, icon }) => {
    const { t } = useTranslation();
    return (
        <div className="feature-panel">
            <div className="feature-panel__icon">
                {icon}
            </div>
            <h4 className="feature-panel__name">{name}</h4>
            {description && <p className="feature-panel__description">{description}</p>}
        </div>
    );
};

export default FeaturePanel;
