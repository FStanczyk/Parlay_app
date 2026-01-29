import React from 'react';
import { Outlet } from 'react-router-dom';
import AdminSideNav from '../components/AdminSideNav';
import { ROUTES } from '../constants';
import type { NavItem } from '../components/AdminSideNav';

const AdminPanel: React.FC = () => {
  const navItems: NavItem[] = [
    {
      label: 'Add AI predictions',
      route: ROUTES.ADMIN_ADD_AI_PREDICTIONS,
    },
    {
      label: 'Users',
      route: ROUTES.ADMIN_USERS,
    },
  ];

  return (
    <div className="admin-panel">
      <div className="admin-panel__container">
        <AdminSideNav items={navItems} />
        <main className="admin-panel__content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminPanel;
