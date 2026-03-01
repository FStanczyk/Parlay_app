import React from 'react';
import { useNavigate } from 'react-router-dom';
import iconSpinVideo from '../assets/branding/icon_spin.mp4';
import xTwitterIcon from '../assets/icons/x_twitter.svg';
import rinkImage from '../assets/images/rink.jpg';
import GeneratorComponent from '../components/Generator';
import GoogleSignInButton from '../components/GoogleSignInButton';
import AnimationText from '../components/TextCarousel';
import { ROUTES } from '../constants';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../contexts/TranslationContext';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { isAuthenticated, isAdmin } = useAuth();

  React.useEffect(() => {
    if (isAuthenticated && isAdmin) {
      navigate('/hub');
    }
  }, [isAuthenticated, isAdmin, navigate]);

  return (
    <div className="home">
      <section className="home__hero">
        <div className="home__hero-content">
          <a
            className="home__hero-eyebrow"
            href="https://x.com/Philip_snat"
            target="_blank"
            rel="noopener noreferrer"
          >
            <img src={xTwitterIcon} alt="" className="home__hero-x-icon" aria-hidden="true" />
            <span>@Philip_snat</span>
          </a>
          <h1 className="home__hero-headline">
            <span className="home__hero-headline-static">{t.home.title1}</span>
            <br />
            <span className="home__hero-headline-for">{t.home.title2}&nbsp;</span>
            <span className="home__hero-carousel">
              <AnimationText texts={t.home.textCarousel} />
            </span>
          </h1>
          <p className="home__hero-sub">
            Providing predictions for NHL and KHL calculated by original neural network models. Try generator to create your own parlay out of all other available games.
          </p>
          <div className="home__hero-nav-links">
            <button
              className="home__hero-nav-btn"
              onClick={() => navigate('/philip-snat-models')}
            >
              Philip Snat Models
            </button>
            <button
              className="home__hero-nav-btn"
              onClick={() => navigate(ROUTES.GENERATOR)}
            >
              Generator
            </button>
          </div>
          <div className="home__hero-actions">
            <GoogleSignInButton className="home__google-button" />
          </div>
        </div>
        <div className="home__hero-visual">
          <div className="home__hero-video-wrap">
            <video
              className="home__hero-video"
              src={iconSpinVideo}
              autoPlay
              loop
              muted
              playsInline
            />
          </div>
        </div>
      </section>

      <div className="home__banner">
        <img src={rinkImage} alt="Sports arena" className="home__banner-image" />
        <div className="home__banner-overlay" />
      </div>

      <section className="home__demo">
        <div className="home__demo-label">Try the generator</div>
        <GeneratorComponent isDemo={true} maxEvents={4} defaultEvents={4} />
      </section>
    </div>
  );
};

export default Home;
