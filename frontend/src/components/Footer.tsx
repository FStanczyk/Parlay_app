import React from 'react';
import { useNavigate } from 'react-router-dom';
import { APP_NAME } from '../constants';
import { useTranslation } from '../contexts/TranslationContext';

const Footer: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer__container">
        <div className="footer__content">
          <p className="footer__copyright">
            © {currentYear} {APP_NAME}. {t.footer.rights}
          </p>
          <nav className="footer__nav">
            <button
              className="footer__link"
              onClick={() => navigate('/generator')}
            >
              {t.nav.generator}
            </button>
          </nav>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
