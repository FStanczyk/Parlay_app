import React, { useState } from 'react';
import { FiChevronDown, FiChevronRight } from 'react-icons/fi';
import { useLocation, useNavigate } from 'react-router-dom';
import { Icon } from '../utils/Icon';

export interface NavItem {
  label: string;
  route?: string;
  items?: NavItem[];
}

interface AdminSideNavProps {
  items: NavItem[];
}

const AdminSideNav: React.FC<AdminSideNavProps> = ({ items }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [openItems, setOpenItems] = useState<Set<string>>(new Set());

  const toggleItem = (label: string) => {
    const newOpenItems = new Set(openItems);
    if (newOpenItems.has(label)) {
      newOpenItems.delete(label);
    } else {
      newOpenItems.add(label);
    }
    setOpenItems(newOpenItems);
  };

  const handleItemClick = (item: NavItem) => {
    if (item.items && item.items.length > 0) {
      toggleItem(item.label);
    } else if (item.route) {
      navigate(item.route);
    }
  };

  const isActive = (route?: string): boolean => {
    if (!route) return false;
    return location.pathname === route;
  };

  const renderItem = (item: NavItem, level: number = 0): React.ReactNode => {
    const hasChildren = item.items && item.items.length > 0;
    const isOpen = openItems.has(item.label);
    const active = isActive(item.route);
    const levelClass = level > 0 ? `admin-side-nav__button--level-${level}` : '';

    return (
      <li key={item.label} className="admin-side-nav__item">
        <button
          className={`admin-side-nav__button ${active ? 'admin-side-nav__button--active' : ''} ${levelClass}`}
          onClick={() => handleItemClick(item)}
        >
          {hasChildren && (
            <Icon
              component={isOpen ? FiChevronDown : FiChevronRight}
              className="admin-side-nav__chevron"
            />
          )}
          <span className="admin-side-nav__label">{item.label}</span>
        </button>
        {hasChildren && isOpen && (
          <ul className="admin-side-nav__submenu">
            {item.items?.map((subItem) => renderItem(subItem, level + 1))}
          </ul>
        )}
      </li>
    );
  };

  return (
    <nav className="admin-side-nav">
      <ul className="admin-side-nav__list">
        {items.map((item) => renderItem(item))}
      </ul>
    </nav>
  );
};

export default AdminSideNav;
