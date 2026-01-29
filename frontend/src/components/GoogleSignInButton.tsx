import React from 'react';
import { ReactComponent as GoogleIcon } from '../assets/icons/google.svg';
import { API_BASE_URL } from '../constants';
import { useTranslation } from '../contexts/TranslationContext';

interface GoogleSignInButtonProps {
  className?: string;
}

const GoogleSignInButton: React.FC<GoogleSignInButtonProps> = ({ className = '' }) => {
  const { t } = useTranslation();

  const handleGoogleSignIn = () => {
    window.location.href = `${API_BASE_URL}/api/v1/auth/google`;
  };

  return (
    <button
      className={`button_primary google-signin-button ${className}`.trim()}
      onClick={handleGoogleSignIn}
      type="button"
    >
      <GoogleIcon className="google-icon" aria-hidden="true" />
      {t.home.googleSignIn}
    </button>
  );
};

export default GoogleSignInButton;
