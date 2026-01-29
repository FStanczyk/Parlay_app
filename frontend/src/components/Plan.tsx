import React from 'react';
import { useTranslation } from '../contexts/TranslationContext';

interface PlanProps {
  id: string;
  name: string;
  price: string;
  description?: string;
}

const Plan: React.FC<PlanProps> = ({ id, name, price, description }) => {
    const { t } = useTranslation();
    return (
        <div className="plan card">
            <p className="plan__mini-name">{t.home.plan.miniText} {id}</p>
            <h2 className="plan__name">{name}</h2>
            <p className="plan__price">{price}</p>
            {description && <p className="plan__description">{description}</p>}

            <button
                className="button_primary plan__button"
                onClick={()=>{}}
                type="button"
            >
            {t.common.subscribe}
          </button>
        </div>
    );
};

export default Plan;
