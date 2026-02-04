import React from 'react';
import { FaChartLine, FaDollarSign, FaFileLines, FaUsers } from 'react-icons/fa6';
import { useNavigate } from 'react-router-dom';
import rinkImage from '../assets/images/rink.jpg';
import FeaturePanel from '../components/FeaturePanel';
import GeneratorComponent from '../components/Generator';
import GoogleSignInButton from '../components/GoogleSignInButton';
import ImagePanel from '../components/ImagePanel';
import Plan from '../components/Plan';
import AnimationText from '../components/TextCarousel';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../contexts/TranslationContext';
import { Icon } from '../utils/Icon';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/hub');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="home">
      <div className="home__container">
        <section className="home__hero">
          <div className="home__title-text-top">{t.home.title1}</div>
          <div className="home__title-text-bottom">{t.home.title2}</div>
          <div className="home__text-carousel">
            <AnimationText texts={t.home.textCarousel} />
          </div>
          <GoogleSignInButton className="home__google-button" />
      </section>
      <ImagePanel path={rinkImage} />
      <section className="home__features">
        <FeaturePanel
          name="Automated slips"
          description="Build ready-to-play slips autoomatically based on your preferences"
          icon={<Icon component={FaFileLines} aria-hidden={true} />}
        />
        <FeaturePanel
          name="Expert Network"
          description="Browse bet recommendations, search for new experts and play along with analysts"
          icon={<Icon component={FaUsers} aria-hidden={true} />}
        />
        <FeaturePanel
          name="Simulated portfolio"
          description="Simulate and manage your betting portfoliio with technical precision"
          icon={<Icon component={FaChartLine} aria-hidden={true} />}
        />
        <FeaturePanel
          name="Expert monetization"
          description="Share your knowledge and earn with our monetization platform"
          icon={<Icon component={FaDollarSign} aria-hidden={true} />}
        />
      </section>
      <section className="home__demo">
        <GeneratorComponent isDemo={true} maxEvents={4} defaultEvents={4} />
      </section>
      <section className="home__plans">
        <Plan id="01" name="Free" price="0$" description="Basic features" />
        <Plan id="02" name="Pro" price="10.99$" description="Pro features" />
        <Plan id="03" name="Elite" price="20.99$" description="Elite features" />
      </section>
      </div>
    </div>
  );
};

export default Home;
