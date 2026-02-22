import React from 'react';
import TopExpertsSection from '../components/TopExpertsSection';
import TopPicksSection from '../components/TopPicksSection';
import '../styles/hub.scss';

const Hub: React.FC = () => {
  return (
    <div className="hub">
      <div className="hub__container">
        <div className="hub__sections">
          <TopExpertsSection />
          <TopPicksSection />
        </div>
      </div>
    </div>
  );
};

export default Hub;
