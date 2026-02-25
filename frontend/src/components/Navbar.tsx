import React, { useEffect, useState } from 'react';
import { FiChevronDown, FiMenu, FiX } from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';
import { APP_NAME, ROUTES } from '../constants';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from '../contexts/TranslationContext';
import { availableLanguages } from '../translations';
import { Icon } from '../utils/Icon';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [expertsDropdownOpen, setExpertsDropdownOpen] = useState(false);
  const [profileDropdownOpen, setProfileDropdownOpen] = useState(false);
  const { isAuthenticated, isAdmin, user, logout, isExpert } = useAuth();
  const { t, language, setLanguage } = useTranslation();

  useEffect(() => {
    const mediaQuery = window.matchMedia('(max-width: 767px)');
    const handleChange = (event: MediaQueryListEvent | MediaQueryList) => {
      setIsMobile(event.matches);
    };

    handleChange(mediaQuery);
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
    mediaQuery.addListener(handleChange);
    return () => mediaQuery.removeListener(handleChange);
  }, []);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (route?: string, action?: string) => {
    if (action === 'logout') {
      handleLogout();
    } else if (route) {
      navigate(route);
      setMobileOpen(false);
      setExpertsDropdownOpen(false);
      setProfileDropdownOpen(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate(ROUTES.HOME);
    setMobileOpen(false);
  };

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      // Don't close if clicking on dropdown elements
      if (!target.closest('.navbar__dropdown') && !target.closest('.navbar__dropdown-menu')) {
        setExpertsDropdownOpen(false);
        setProfileDropdownOpen(false);
      }
    };

    if (expertsDropdownOpen || profileDropdownOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [expertsDropdownOpen, profileDropdownOpen]);

  const handleDropdownToggle = (dropdown: 'experts' | 'profile') => {
    if (dropdown === 'experts') {
      setExpertsDropdownOpen(!expertsDropdownOpen);
      setProfileDropdownOpen(false);
    } else {
      setProfileDropdownOpen(!profileDropdownOpen);
      setExpertsDropdownOpen(false);
    }
  };

  const getNavigationItems = (): Array<{
    label: string;
    route?: string;
    action?: string;
    dropdown?: boolean;
    items?: Array<{ label: string; route?: string; action?: string }>;
  }> => {
    const philipSnatModelsItem = { label: t.nav.philipSnatModels, route: ROUTES.PHILIP_SNAT_MODELS };

    if (!isAuthenticated) {
      return [
        philipSnatModelsItem,
        { label: t.nav.generator, route: ROUTES.GENERATOR },
        { label: t.nav.login, route: ROUTES.LOGIN },
        { label: t.nav.register, route: ROUTES.REGISTER },
      ];
    }

    if (!isAdmin) {
      return [
        philipSnatModelsItem,
        { label: t.nav.generator, route: ROUTES.GENERATOR },
        { label: t.nav.logout, action: 'logout' },
      ];
    }

    const profileItems = [
      { label: t.nav.dashboard, route: ROUTES.PROFILE_DASHBOARD },
      { label: t.nav.myParlays, route: ROUTES.PROFILE_PARLAYS },
      { label: t.nav.stats, route: ROUTES.PROFILE_STATS },
      { label: t.nav.settings, route: ROUTES.PROFILE_SETTINGS },
      ...(!isExpert ? [{ label: t.nav.becomeExpert, route: ROUTES.BECOME_EXPERT }] : []),
      { label: t.nav.logout, action: 'logout' },
    ];

    const navItems = [
      philipSnatModelsItem,
      { label: t.nav.hub, route: ROUTES.HUB },
      { label: t.nav.generator, route: ROUTES.GENERATOR },
      {
        label: t.nav.experts,
        dropdown: true,
        items: [
          { label: t.nav.searchExperts, route: ROUTES.EXPERTS_SEARCH },
          { label: t.nav.following, route: ROUTES.EXPERTS_FOLLOWING },
          { label: t.nav.recommendations, route: ROUTES.EXPERTS_RECOMMENDATIONS },
        ]
      },
      { label: t.nav.simulator, route: ROUTES.SIMULATOR },
      ...(isExpert ? [{ label: t.nav.expertPanel, route: ROUTES.EXPERT_PANEL }] : []),
      ...(user?.is_admin ? [{ label: t.nav.adminPanel, route: ROUTES.ADMIN_PANEL }] : []),
      {
        label: t.nav.profile,
        dropdown: true,
        items: profileItems
      },
    ];

    return navItems;
  };

  const navigationItems = getNavigationItems();
  const languageSwitcher = (
    <div className="navbar__language-switcher">
      {availableLanguages.map((lang) => (
        <button
          key={lang}
          className={`navbar__language-button ${language === lang ? 'navbar__language-button--active' : ''}`}
          onClick={() => setLanguage(lang)}
          aria-label={`Switch to ${lang.toUpperCase()}`}
        >
          {lang.toUpperCase()}
        </button>
      ))}
    </div>
  );

  return (
    <>
      <nav className="navbar">
        <div className="navbar__toolbar">
          <div className="navbar__desktop-part navbar__logo" onClick={() => navigate(ROUTES.HOME)}>
            {APP_NAME}
          </div>

          {!isMobile ? (
            <div className="navbar__desktop-part navbar__desktop-menu">
              {navigationItems.map((item) => {
                if (item.dropdown) {
                  const isExpertsDropdown = item.label === t.nav.experts;
                  const isOpen = isExpertsDropdown ? expertsDropdownOpen : profileDropdownOpen;

                  return (
                    <div key={item.label} className="navbar__dropdown">
                      <button
                        className="navbar__button navbar__dropdown-toggle"
                        onClick={(event) => {
                          event.stopPropagation();
                          handleDropdownToggle(isExpertsDropdown ? 'experts' : 'profile');
                        }}
                      >
                        {item.label}
                        <Icon component={FiChevronDown} aria-hidden={true} />
                      </button>
                      {isAuthenticated && isOpen && (
                        <div className="navbar__dropdown-menu">
                          {item.items?.map((subItem) => (
                            <button
                              key={subItem.label}
                              className="navbar__dropdown-item"
                              onClick={(event) => {
                                event.stopPropagation();
                                handleNavigation(subItem.route, subItem.action);
                              }}
                            >
                              {subItem.label}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                }

                return (
                  <button
                    key={item.label}
                    className="navbar__button"
                    onClick={() => handleNavigation(item.route, item.action)}
                  >
                    {item.label}
                  </button>
                );
              })}
              {languageSwitcher}
            </div>
          ) : (
            <button
              className="navbar__menu-button"
              aria-label="open drawer"
              onClick={handleDrawerToggle}
            >
              <Icon component={FiMenu} aria-hidden={true} />
            </button>
          )}
        </div>
      </nav>

      {mobileOpen && (
        <div className="navbar__drawer-overlay" onClick={handleDrawerToggle}>
          <div className="navbar__drawer" onClick={(e) => e.stopPropagation()}>
            <div className="navbar__drawer-header">
              <button
                className="navbar__drawer-close"
                onClick={handleDrawerToggle}
                aria-label="close drawer"
              >
                <Icon component={FiX} aria-hidden={true} />
              </button>
            </div>
            <ul className="navbar__drawer-list">
              {navigationItems.map((item) => {
                if (item.dropdown) {
                  return (
                    <li key={item.label} className="navbar__drawer-item">
                      <div className="navbar__drawer-dropdown">
                        <button className="navbar__button navbar__drawer-button">
                          {item.label}
                        </button>
                        <ul className="navbar__drawer-submenu">
                          {item.items?.map((subItem) => (
                            <li key={subItem.label}>
                              <button
                                className="navbar__drawer-submenu-item"
                                onClick={() => handleNavigation(subItem.route, subItem.action)}
                              >
                                {subItem.label}
                              </button>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </li>
                  );
                }

                return (
                  <li key={item.label} className="navbar__drawer-item">
                    <button
                      className="navbar__button navbar__drawer-button"
                      onClick={() => handleNavigation(item.route, item.action)}
                    >
                      {item.label}
                    </button>
                  </li>
                );
              })}
              <li className="navbar__drawer-item">{languageSwitcher}</li>
            </ul>
          </div>
        </div>
      )}
    </>
  );
};

export default Navbar;
