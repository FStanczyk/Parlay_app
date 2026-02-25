import axios from 'axios';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../contexts/TranslationContext';
import { API_BASE_URL } from '../constants';

const Login: React.FC = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { isAuthenticated, isAdmin, login } = useAuth();

  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      navigate('/hub');
    }
  }, [isAuthenticated, isAdmin, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post(
        `${API_BASE_URL}/auth/login`,
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          },
        }
      );

      await login(response.data.access_token);
    } catch (err: any) {
      const errorData = err.response?.data;
      if (errorData?.detail) {
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map((e: any) =>
            `${e.loc?.join('.')}: ${e.msg}`
          ).join(', ');
          setError(errorMessages || t.login.validationError);
        } else {
          setError(errorData.detail);
        }
      } else {
        setError(t.login.loginFailed);
      }
    }
  };

  return (
    <div className="login">
      <div className="login__container">
        <div className="login__card">
          <h1 className="login__title italic-title">{t.login.title}</h1>

          {error && (
            <div className="login__error">
              {error}
            </div>
          )}

          <form className="login__form" onSubmit={handleSubmit}>
            <div className="login__field">
              <label htmlFor="email" className="login__label">{t.login.email}</label>
              <input
                id="email"
                className="login__input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="login__field">
              <label htmlFor="password" className="login__label">{t.login.password}</label>
              <input
                id="password"
                className="login__input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <button
              type="submit"
              className="login__submit button_primary"
            >
              {t.login.submit}
            </button>
            <GoogleSignInButton className="home__google-button" />
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
