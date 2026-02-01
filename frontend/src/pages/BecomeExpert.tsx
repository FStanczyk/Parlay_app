import axios from 'axios';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from '../contexts/TranslationContext';
import { API_BASE_URL } from '../constants';

const BecomeExpert: React.FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [description, setDescription] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_BASE_URL}/tipsters/`,
        { description },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuccess(t.becomeExpert.success);
      setTimeout(() => {
        navigate('/profile/dashboard');
      }, 2000);
    } catch (err: any) {
      const errorData = err.response?.data;
      if (errorData?.detail === 'User is already a tipster') {
        setError(t.becomeExpert.alreadyExpert);
      } else {
        setError(t.becomeExpert.error);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="become-expert">
      <div className="become-expert__container">
        <div className="become-expert__card">
          <h1 className="become-expert__title italic-title">{t.becomeExpert.title}</h1>
          <p className="become-expert__subtitle">{t.becomeExpert.subtitle}</p>

          {error && (
            <div className="become-expert__error">
              {error}
            </div>
          )}

          {success && (
            <div className="become-expert__success">
              {success}
            </div>
          )}

          <form className="become-expert__form" onSubmit={handleSubmit}>
            <div className="become-expert__field">
              <label htmlFor="description" className="become-expert__label">
                {t.becomeExpert.description}
              </label>
              <textarea
                id="description"
                className="become-expert__textarea"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={t.becomeExpert.descriptionPlaceholder}
                rows={6}
              />
            </div>

            <button
              type="submit"
              className="become-expert__submit button_primary"
              disabled={loading}
            >
              {loading ? '...' : t.becomeExpert.submit}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default BecomeExpert;
