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
        <div className="feature-panel card">
            <div className="feature-panel__header">
                <div className="feature-panel__icon">
                    {icon}
                </div>
                <div className="feature-panel__name">{name}</div>
            </div>
            {description && <p className="feature-panel__description">{description}</p>}
        </div>
    );
};

export default FeaturePanel;
