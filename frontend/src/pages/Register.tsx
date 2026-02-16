import axios from 'axios';
import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { useNavigate } from 'react-router-dom';
import GoogleSignInButton from '../components/GoogleSignInButton';
import { API_BASE_URL } from '../constants';
import { useTranslation } from '../contexts/TranslationContext';

const COUNTRIES = [
  { code: 'AF', name: 'Afghanistan' },
  { code: 'AL', name: 'Albania' },
  { code: 'DZ', name: 'Algeria' },
  { code: 'AR', name: 'Argentina' },
  { code: 'AU', name: 'Australia' },
  { code: 'AT', name: 'Austria' },
  { code: 'BD', name: 'Bangladesh' },
  { code: 'BE', name: 'Belgium' },
  { code: 'BR', name: 'Brazil' },
  { code: 'BG', name: 'Bulgaria' },
  { code: 'CA', name: 'Canada' },
  { code: 'CL', name: 'Chile' },
  { code: 'CN', name: 'China' },
  { code: 'CO', name: 'Colombia' },
  { code: 'HR', name: 'Croatia' },
  { code: 'CZ', name: 'Czech Republic' },
  { code: 'DK', name: 'Denmark' },
  { code: 'EG', name: 'Egypt' },
  { code: 'EE', name: 'Estonia' },
  { code: 'FI', name: 'Finland' },
  { code: 'FR', name: 'France' },
  { code: 'DE', name: 'Germany' },
  { code: 'GR', name: 'Greece' },
  { code: 'HU', name: 'Hungary' },
  { code: 'IS', name: 'Iceland' },
  { code: 'IN', name: 'India' },
  { code: 'ID', name: 'Indonesia' },
  { code: 'IE', name: 'Ireland' },
  { code: 'IL', name: 'Israel' },
  { code: 'IT', name: 'Italy' },
  { code: 'JP', name: 'Japan' },
  { code: 'KE', name: 'Kenya' },
  { code: 'LV', name: 'Latvia' },
  { code: 'LT', name: 'Lithuania' },
  { code: 'MY', name: 'Malaysia' },
  { code: 'MX', name: 'Mexico' },
  { code: 'NL', name: 'Netherlands' },
  { code: 'NZ', name: 'New Zealand' },
  { code: 'NG', name: 'Nigeria' },
  { code: 'NO', name: 'Norway' },
  { code: 'PK', name: 'Pakistan' },
  { code: 'PE', name: 'Peru' },
  { code: 'PH', name: 'Philippines' },
  { code: 'PL', name: 'Poland' },
  { code: 'PT', name: 'Portugal' },
  { code: 'RO', name: 'Romania' },
  { code: 'RU', name: 'Russia' },
  { code: 'SA', name: 'Saudi Arabia' },
  { code: 'RS', name: 'Serbia' },
  { code: 'SG', name: 'Singapore' },
  { code: 'SK', name: 'Slovakia' },
  { code: 'SI', name: 'Slovenia' },
  { code: 'ZA', name: 'South Africa' },
  { code: 'KR', name: 'South Korea' },
  { code: 'ES', name: 'Spain' },
  { code: 'SE', name: 'Sweden' },
  { code: 'CH', name: 'Switzerland' },
  { code: 'TH', name: 'Thailand' },
  { code: 'TR', name: 'Turkey' },
  { code: 'UA', name: 'Ukraine' },
  { code: 'AE', name: 'United Arab Emirates' },
  { code: 'GB', name: 'United Kingdom' },
  { code: 'US', name: 'United States' },
  { code: 'VE', name: 'Venezuela' },
  { code: 'VN', name: 'Vietnam' },
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
      await axios.post(`${API_BASE_URL}/users/`, {
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
                  <option key={c.code} value={c.code}>{c.name}</option>
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
