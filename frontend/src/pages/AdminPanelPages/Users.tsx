import React, { useEffect, useState } from 'react';
import { apiGet } from '../../utils/api';
import '../../styles/users.scss';

interface User {
  id: number;
  email: string;
  full_name: string | null;
  country: string | null;
  birthdate: string | null;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

interface PaginatedUsersResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

const Users: React.FC = () => {
  const [users, setUsers] = useState<PaginatedUsersResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);

  useEffect(() => {
    const fetchUsers = async () => {
      setLoading(true);
      try {
        const data = await apiGet<PaginatedUsersResponse>(
          `/admin/users?page=${currentPage}&page_size=25`
        );
        setUsers(data);
      } catch (err) {
        console.error('Failed to fetch users:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUsers();
  }, [currentPage]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="users">
        <div className="users__container">
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="users">
      <div className="users__container">
        <h1 className="users__title">Users</h1>

        {users && (
          <>
            <div className="users__list">
              <div className="users__header">
                <div className="users__header-cell">ID</div>
                <div className="users__header-cell">Email</div>
                <div className="users__header-cell">Full Name</div>
                <div className="users__header-cell">Country</div>
                <div className="users__header-cell">Admin</div>
                <div className="users__header-cell">Active</div>
                <div className="users__header-cell">Created</div>
              </div>

              {users.users.map((user) => (
                <div key={user.id} className="users__row">
                  <div className="users__cell">{user.id}</div>
                  <div className="users__cell">{user.email}</div>
                  <div className="users__cell">{user.full_name || '-'}</div>
                  <div className="users__cell">{user.country || '-'}</div>
                  <div className="users__cell">
                    {user.is_admin ? 'Yes' : 'No'}
                  </div>
                  <div className="users__cell">
                    {user.is_active ? 'Yes' : 'No'}
                  </div>
                  <div className="users__cell">{formatDate(user.created_at)}</div>
                </div>
              ))}
            </div>

            {users.total_pages > 1 && (
              <div className="users__pagination">
                <button
                  className="button_secondary users__pagination-button"
                  onClick={() => setCurrentPage(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  Previous
                </button>
                <span className="users__pagination-info">
                  Page {currentPage} of {users.total_pages} ({users.total} total)
                </span>
                <button
                  className="button_secondary users__pagination-button"
                  onClick={() => setCurrentPage(currentPage + 1)}
                  disabled={currentPage === users.total_pages}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Users;
