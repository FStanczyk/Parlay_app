import React, { useState } from 'react';
import { Coupon } from '../services/couponsService';
import { useTranslation } from '../contexts/TranslationContext';
import Modal from './Modal';
import BetEventPanel from './BetEventPanel';

interface CouponRowProps {
  coupon: Coupon;
}

const CouponRow: React.FC<CouponRowProps> = ({ coupon }) => {
  const { t } = useTranslation();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const calculateTotalOdds = () => {
    if (!coupon.bet_events || coupon.bet_events.length === 0) return 1;
    return coupon.bet_events.reduce((total, betEventOnCoupon) => {
      return total * (betEventOnCoupon.bet_event?.odds || 1);
    }, 1);
  };

  const getFirstAndLastEventDates = () => {
    if (!coupon.bet_events || coupon.bet_events.length === 0) {
      return { first: null, last: null };
    }

    const dates = coupon.bet_events
      .map((betEventOnCoupon) => betEventOnCoupon.bet_event?.game?.datetime)
      .filter((date): date is string => date !== undefined)
      .sort();

    if (dates.length === 0) {
      return { first: null, last: null };
    }

    return {
      first: dates[0],
      last: dates[dates.length - 1],
    };
  };

  const totalOdds = calculateTotalOdds();
  const { first, last } = getFirstAndLastEventDates();

  const handleRowClick = () => {
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
  };

  const handleLockToggle = () => {
    // No-op for view-only mode
  };

  return (
    <>
      <div className="coupon-row card" onClick={handleRowClick}>
      <div className="coupon-row__name">
        <h3 className="coupon-row__title italic-title">{coupon.name}</h3>
      </div>

      <div className="coupon-row__total-odds">
        <span className="coupon-row__total-odds-label">{t.parlaySummary.odds}:</span>
        <span className="coupon-row__total-odds-value">{totalOdds.toFixed(2)}</span>
      </div>

      <div className="coupon-row__events-count">
        {coupon.bet_events?.length || 0} {coupon.bet_events?.length === 1 ? t.myParlays.event : t.myParlays.events}
      </div>

      {first && last && (
        <div className="coupon-row__dates">
          <span className="coupon-row__date">{formatDate(first)}</span>
          <span className="coupon-row__date-separator">/</span>
          <span className="coupon-row__date">{formatDate(last)}</span>
        </div>
      )}
      </div>

    <Modal
      isOpen={isModalOpen}
      onClose={handleModalClose}
      title={coupon.name}
      size="large"
    >
      <div className="coupon-details-modal">
        {coupon.bet_events && coupon.bet_events.length > 0 ? (
          <div className="coupon-details-modal__events">
            {coupon.bet_events.map((betEventOnCoupon) => {
              const betEvent = betEventOnCoupon.bet_event;
              if (!betEvent) return null;

              return (
                <BetEventPanel
                  key={betEventOnCoupon.id}
                  betEvent={betEvent}
                  isLocked={false}
                  onLockToggle={handleLockToggle}
                  disabled={true}
                />
              );
            })}
          </div>
        ) : (
          <div className="coupon-details-modal__empty">
            <p>No events found.</p>
          </div>
        )}
      </div>
    </Modal>
    </>
  );
};

export default CouponRow;
