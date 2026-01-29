import React, { useEffect, useState } from 'react';
import CouponRow from '../components/CouponRow';
import { useTranslation } from '../contexts/TranslationContext';
import { Coupon, couponsApi } from '../services/couponsService';

const MyParlays: React.FC = () => {
  const { t } = useTranslation();
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCoupons = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await couponsApi.getMyCoupons();
        setCoupons(data);
      } catch (err) {
        console.error('Error fetching coupons:', err);
        setError(err instanceof Error ? err.message : t.errors.genericError);
      } finally {
        setLoading(false);
      }
    };

    fetchCoupons();
  }, [t.errors.genericError]);

  return (
    <div className="my-parlays">
      <div className="my-parlays__container">
        <h1 className="my-parlays__title italic-title">{t.nav.myParlays}</h1>

        {loading && (
          <div className="my-parlays__loading">
            <div className="my-parlays__spinner"></div>
            <p>{t.common.loading}</p>
          </div>
        )}

        {error && (
          <div className="my-parlays__error">
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && coupons.length === 0 && (
          <div className="my-parlays__empty">
            <p>{t.myParlays.noParlays}</p>
          </div>
        )}

        {!loading && !error && coupons.length > 0 && (
          <div className="my-parlays__list">
            {coupons.map((coupon) => (
              <CouponRow key={coupon.id} coupon={coupon} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyParlays;
