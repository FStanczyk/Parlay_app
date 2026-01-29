import React, { useEffect, useState } from 'react';
import ExpertListRow from '../../components/searchExpertsComponents/expertPlan';
import { tipsterApi } from '../../services/tipsterService';
import { TipsterPublic } from '../../types/interfaces';

const SearchExperts: React.FC = () => {
  const [tipsters, setTipsters] = useState<TipsterPublic[]>([]);

  useEffect(() => {
    tipsterApi.getAll().then((response) => {
      setTipsters(response);
    });
  }, []);

  return (
    <div className="search-experts">
      <h1 className='italic-title'>Search Experts</h1>
      {tipsters.map((tipster) => (
        <ExpertListRow key={tipster.id} tipster={tipster} />
      ))}
    </div>
  );
};

export default SearchExperts;
