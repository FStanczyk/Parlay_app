import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useTranslation } from '../../contexts/TranslationContext';

const EditProfile: React.FC = () => {
  const { t } = useTranslation();
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTipster = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:8000/api/v1/tipsters/me', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setDescription(response.data.description || '');
      } catch (err) {
        console.error('Failed to fetch tipster data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTipster();
  }, []);

  const handleSave = async () => {
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      const token = localStorage.getItem('token');
      await axios.patch(
        'http://localhost:8000/api/v1/tipsters/me',
        { description },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuccess(t.expertPanel.saveSuccess);
    } catch (err) {
      setError(t.expertPanel.saveError);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="expert-panel">
        <div className="expert-panel__container">
          <div className="expert-panel__loading">{t.common.loading}</div>
        </div>
      </div>
    );
  }

  return (
    <div className="expert-panel">
      <div className="expert-panel__container">
        <h1 className="expert-panel__title italic-title">{t.expertPanel.editProfile}</h1>

        {error && <div className="expert-panel__error">{error}</div>}
        {success && <div className="expert-panel__success">{success}</div>}

        <div className="expert-panel__field">
          <label htmlFor="description" className="expert-panel__label wide__small__text">
            {t.expertPanel.setDescription}
          </label>
          <textarea
            id="description"
            className="expert-panel__textarea"
            rows={6}
            placeholder={t.expertPanel.descriptionPlaceholder}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <div className="expert-panel__sublabel">*{t.expertPanel.descriptionSublabel}</div>
        </div>

        <button
          className="expert-panel__save button_primary"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? t.expertPanel.saving : t.expertPanel.save}
        </button>
      </div>
    </div>
  );
};

export default EditProfile;
