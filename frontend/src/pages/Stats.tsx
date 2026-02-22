import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { tipsterApi } from '../services/tipsterService';

const Stats: React.FC = () => {
  const { isExpert } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!isExpert) {
      setError(true);
      return;
    }
    tipsterApi.getMe()
      .then((tipster) => {
        navigate(`/experts/${tipster.id}/stats`, { replace: true });
      })
      .catch(() => setError(true));
  }, [isExpert, navigate]);

  if (error) {
    return (
      <div className="expert-stats" style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--color-text-secondary)' }}>
          No stats available. Become an expert to track your performance.
        </p>
      </div>
    );
  }

  return null;
};

export default Stats;
