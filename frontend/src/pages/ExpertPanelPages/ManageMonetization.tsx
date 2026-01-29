import React, { useCallback, useEffect, useState } from 'react';
import ExpertPlan from '../../components/expertComponents/expertPlan';
import Modal from '../../components/Modal';
import { useTranslation } from '../../contexts/TranslationContext';
import { TipsterTier } from '../../types/interfaces';
import { apiGet, apiPost } from '../../utils/api';

const ManageMonetization: React.FC = () => {
  const { t } = useTranslation();
  const [tiers, setTiers] = useState<TipsterTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newPlanForm, setNewPlanForm] = useState({
    level: 0,
    name: '',
    priceMonthly: '',
    featuresDescription: ''
  });

  const fetchTiers = useCallback(async () => {
    try {
      const data = await apiGet<TipsterTier[]>('/tipsters/me/tiers');
      setTiers(data);
    } catch (error) {
      console.error('Failed to fetch tiers:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTiers();
  }, [fetchTiers]);

  const isFreeTier = Number(newPlanForm.level) === 0;

  const handleNewPlanChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setNewPlanForm(prev => ({ ...prev, [name]: value }));
  };

  const isFormValid = () => {
    if (!newPlanForm.name.trim()) return false;
    if (!isFreeTier && (!newPlanForm.priceMonthly || Number(newPlanForm.priceMonthly) <= 0)) return false;
    return true;
  };

  const handleAddPlan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isFormValid()) return;
    setSaving(true);
    try {
      await apiPost('/tipsters/me/tiers', {
        level: Number(newPlanForm.level),
        name: newPlanForm.name,
        price_monthly: isFreeTier ? 0 : Number(newPlanForm.priceMonthly),
        features_description: newPlanForm.featuresDescription || null
      });
      setIsAddModalOpen(false);
      setNewPlanForm({ level: 0, name: '', priceMonthly: '', featuresDescription: '' });
      fetchTiers();
    } catch (error) {
      console.error('Failed to create tier:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="expert-panel">
      <div className="expert-panel__container">
        <section className="manage-monetization__section monetization__current-plans">
          <h2 className="manage-monetization__section-title italic-title">{t.manageMonetization.currentPlans}</h2>
          <button className='button_primary' onClick={() => setIsAddModalOpen(true)}>
            {t.manageMonetization.addNew} +
          </button>
          <div className="manage-monetization__current-plans-grid">
            {loading ? (
              <p>{t.common.loading}</p>
            ) : tiers.length > 0 ? (
              tiers.map((tier) => (
                <ExpertPlan
                  key={tier.id}
                  id={tier.id}
                  level={tier.level}
                  name={tier.name}
                  priceMonthly={tier.price_monthly}
                  featuresDescription={tier.features_description}
                  onUpdate={fetchTiers}
                />
              ))
            ) : (
              <p>{t.manageMonetization.noPlans}</p>
            )}
          </div>
        </section>
      </div>

      <Modal isOpen={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} title={t.manageMonetization.addNew}>
        <form className="expert-plan-form" onSubmit={handleAddPlan}>
          <div className="expert-plan-form__field">
            <label>Level</label>
            <input
              type="number"
              name="level"
              className="expert-plan-form__input"
              value={newPlanForm.level}
              onChange={handleNewPlanChange}
              min={0}
            />
          </div>
          <div className="expert-plan-form__field">
            <label>Name *</label>
            <input
              type="text"
              name="name"
              className="expert-plan-form__input"
              value={newPlanForm.name}
              onChange={handleNewPlanChange}
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
                value={newPlanForm.priceMonthly}
                onChange={handleNewPlanChange}
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
              value={newPlanForm.featuresDescription}
              onChange={handleNewPlanChange}
              placeholder="Describe the features of this plan..."
              rows={4}
            />
          </div>
          <div className="expert-plan-form__actions">
            <button type="button" className="button_secondary" onClick={() => setIsAddModalOpen(false)} disabled={saving}>
              {t.common.cancel}
            </button>
            <button type="submit" className="button_primary" disabled={saving || !isFormValid()}>
              {saving ? t.common.loading : t.manageMonetization.addNew}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default ManageMonetization;
