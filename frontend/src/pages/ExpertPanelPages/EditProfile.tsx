import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useTranslation } from '../../contexts/TranslationContext';
import { API_BASE_URL } from '../../constants';

const EditProfile: React.FC = () => {
  const { t } = useTranslation();
  const [description, setDescription] = useState('');
  const [tag1, setTag1] = useState('');
  const [tag2, setTag2] = useState('');
  const [tag3, setTag3] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchTipster = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_BASE_URL}/tipsters/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setDescription(response.data.description || '');
        setTag1(response.data.tag_1 || '');
        setTag2(response.data.tag_2 || '');
        setTag3(response.data.tag_3 || '');
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
        `${API_BASE_URL}/tipsters/me`,
        {
          description,
          tag_1: tag1,
          tag_2: tag2,
          tag_3: tag3
        },
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

        <div className="expert-panel__field">
          <label htmlFor="tag1" className="expert-panel__label wide__small__text">
            Tag 1
          </label>
          <input
            id="tag1"
            type="text"
            className="expert-panel__input"
            maxLength={20}
            placeholder="e.g. Soccer"
            value={tag1}
            onChange={(e) => setTag1(e.target.value)}
          />
        </div>

        <div className="expert-panel__field">
          <label htmlFor="tag2" className="expert-panel__label wide__small__text">
            Tag 2
          </label>
          <input
            id="tag2"
            type="text"
            className="expert-panel__input"
            maxLength={20}
            placeholder="e.g. NBA"
            value={tag2}
            onChange={(e) => setTag2(e.target.value)}
          />
        </div>

        <div className="expert-panel__field">
          <label htmlFor="tag3" className="expert-panel__label wide__small__text">
            Tag 3
          </label>
          <input
            id="tag3"
            type="text"
            className="expert-panel__input"
            maxLength={20}
            placeholder="e.g. High odds"
            value={tag3}
            onChange={(e) => setTag3(e.target.value)}
          />
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
