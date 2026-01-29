import React, { useState } from 'react';
import { apiCall } from '../../utils/api';
import Modal from '../Modal';

interface ExpertPlanProps {
  id: number;
  level: number;
  name?: string;
  priceMonthly?: number;
  featuresDescription?: string;
  onUpdate?: () => void;
}

const ExpertPlan: React.FC<ExpertPlanProps> = ({
  id,
  level,
  name,
  priceMonthly,
  featuresDescription,
  onUpdate
}) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    level,
    name: name || '',
    priceMonthly: priceMonthly || '',
    featuresDescription: featuresDescription || ''
  });

  const isFreeTier = Number(formData.level) === 0;

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const isFormValid = () => {
    if (!formData.name.trim()) return false;
    if (!isFreeTier && (!formData.priceMonthly || Number(formData.priceMonthly) <= 0)) return false;
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isFormValid()) return;
    setSaving(true);
    try {
      await apiCall(`/tipsters/me/tiers/${id}`, {
        method: 'PATCH',
        body: JSON.stringify({
          level: Number(formData.level),
          name: formData.name,
          price_monthly: isFreeTier ? 0 : Number(formData.priceMonthly),
          features_description: formData.featuresDescription || null
        })
      });
      setIsModalOpen(false);
      onUpdate?.();
    } catch (error) {
      console.error('Failed to update tier:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <div className="expert-plan-card wide__small__text">
        {level === 0 && <span className="expert-plan-card__free-badge wide__small__text">FREE</span>}
        <div className="expert-plan-card__row">
          <span className="expert-plan-card__label">Level</span>
          <span className="expert-plan-card__value">{level}</span>
        </div>
        <div className="expert-plan-card__row">
          <span className="expert-plan-card__label">Name</span>
          <span className="expert-plan-card__value">{name || '—'}</span>
        </div>
        <div className="expert-plan-card__row">
          <span className="expert-plan-card__label">Price</span>
          <span className="expert-plan-card__value">
            {level === 0 ? 'FREE' : `$${priceMonthly}/mo`}
          </span>
        </div>
        <div className="expert-plan-card__row" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: 'var(--spacing-xs)', borderBottom: 'none', paddingBottom: 0 }}>
          <span className="expert-plan-card__label">Description</span>
          <span className="expert-plan-card__value">{featuresDescription || '—'}</span>
        </div>
        <button
          className="button_primary"
          onClick={() => setIsModalOpen(true)}
          type="button"
        >
          Edit Plan
        </button>
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Edit Plan">
        <form className="expert-plan-form" onSubmit={handleSubmit}>
          <div className="expert-plan-form__field">
            <label>Level</label>
            <input
              type="number"
              name="level"
              className="expert-plan-form__input"
              value={formData.level}
              onChange={handleChange}
              min={0}
            />
          </div>
          <div className="expert-plan-form__field">
            <label>Name *</label>
            <input
              type="text"
              name="name"
              className="expert-plan-form__input"
              value={formData.name}
              onChange={handleChange}
              placeholder="e.g. Basic, Pro, Elite"
              required
            />
          </div>
          <div className="expert-plan-form__field">
            <label>Price ($/month) {!isFreeTier && '*'}</label>
            {isFreeTier ? (
              <div className="expert-plan-form__free-badge">FREE</div>
            ) : (
              <input
                type="number"
                name="priceMonthly"
                className="expert-plan-form__input"
                value={formData.priceMonthly}
                onChange={handleChange}
                min={0.01}
                step={0.01}
                placeholder="0.00"
                required
              />
            )}
          </div>
          <div className="expert-plan-form__field">
            <label>Description</label>
            <textarea
              name="featuresDescription"
              className="expert-plan-form__textarea"
              value={formData.featuresDescription}
              onChange={handleChange}
              placeholder="Describe the features of this plan..."
              rows={4}
            />
          </div>
          <div className="expert-plan-form__actions">
            <button type="button" className="button_secondary" onClick={() => setIsModalOpen(false)} disabled={saving}>
              Cancel
            </button>
            <button type="submit" className="button_primary" disabled={saving || !isFormValid()}>
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </Modal>
    </>
  );
};

export default ExpertPlan;
