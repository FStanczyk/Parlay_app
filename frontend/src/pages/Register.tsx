import axios from 'axios';
import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { useNavigate } from 'react-router-dom';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { useTranslation } from '../contexts/TranslationContext';

const COUNTRIES = [
  'Afghanistan', 'Albania', 'Algeria', 'Argentina', 'Australia', 'Austria',
  'Bangladesh', 'Belgium', 'Brazil', 'Bulgaria', 'Canada', 'Chile', 'China',
  'Colombia', 'Croatia', 'Czech Republic', 'Denmark', 'Egypt', 'Estonia',
  'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'India',
  'Indonesia', 'Ireland', 'Israel', 'Italy', 'Japan', 'Kenya', 'Latvia',
  'Lithuania', 'Malaysia', 'Mexico', 'Netherlands', 'New Zealand', 'Nigeria',
  'Norway', 'Pakistan', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Romania',
  'Russia', 'Saudi Arabia', 'Serbia', 'Singapore', 'Slovakia', 'Slovenia',
  'South Africa', 'South Korea', 'Spain', 'Sweden', 'Switzerland', 'Thailand',
  'Turkey', 'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States',
  'Venezuela', 'Vietnam'
];

const Register: React.FC = () => {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [country, setCountry] = useState('');
  const [birthdate, setBirthdate] = useState<Date | null>(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await axios.post('http://localhost:8000/api/v1/users/', {
        email,
        password,
        full_name: fullName,
        country: country || null,
        birthdate: birthdate ? birthdate.toISOString().split('T')[0] : null,
      });

      setSuccess(t.register.success);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      const errorData = err.response?.data;
      if (errorData?.detail) {
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map((e: any) =>
            `${e.loc?.join('.')}: ${e.msg}`
          ).join(', ');
          setError(errorMessages || t.register.validationError);
        } else {
          setError(errorData.detail);
        }
      } else {
        setError(t.register.registrationFailed);
      }
    }
  };

  return (
    <div className="register">
      <div className="register__container">
        <div className="register__card">
          <h1 className="register__title italic-title">{t.register.title}</h1>

          {error && (
            <div className="register__error">
              {error}
            </div>
          )}

          {success && (
            <div className="register__success">
              {success}
            </div>
          )}

          <form className="register__form" onSubmit={handleSubmit}>
            <div className="register__field">
              <label htmlFor="fullName" className="register__label">{t.register.fullName}</label>
              <input
                id="fullName"
                className="register__input"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
              />
            </div>
            <div className="register__field">
              <label htmlFor="email" className="register__label">{t.register.email}</label>
              <input
                id="email"
                className="register__input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="register__field">
              <label htmlFor="password" className="register__label">{t.register.password}</label>
              <input
                id="password"
                className="register__input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="register__field">
              <label htmlFor="country" className="register__label">{t.register.country}</label>
              <select
                id="country"
                className="register__input register__select"
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                required
              >
                <option value="">{t.register.selectCountry}</option>
                {COUNTRIES.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div className="register__field">
              <label htmlFor="birthdate" className="register__label">{t.register.birthdate}</label>
              <DatePicker
                id="birthdate"
                selected={birthdate}
                onChange={(date: Date | null) => setBirthdate(date)}
                dateFormat="yyyy-MM-dd"
                className="register__datepicker"
                wrapperClassName="register__datepicker-wrapper"
                showYearDropdown
                showMonthDropdown
                dropdownMode="select"
                maxDate={new Date()}
                required
              />
            </div>
            <button
              type="submit"
              className="register__submit button_primary"
            >
              {t.register.submit}
            </button>
            <GoogleSignInButton className="home__google-button" />
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register;
