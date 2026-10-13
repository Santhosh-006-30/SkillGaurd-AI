import React, { createContext, useContext, useState, useEffect } from 'react';

export type UserRole = 'ADMIN' | 'MONITOR' | 'INSPECTOR' | 'CENTRE_OPERATOR';

export interface User {
  id: number;
  username: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  created_at?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, userData: User) => void;
  logout: () => void;
  authHeader: () => Record<string, string>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('skillguard_token'));
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('skillguard_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (token) {
      // Validate session with backend
      fetch('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then((res) => {
          if (!res.ok) {
            throw new Error('Session invalid');
          }
          return res.json();
        })
        .then((data) => {
          if (data.success && data.data) {
            setUser(data.data);
            localStorage.setItem('skillguard_user', JSON.stringify(data.data));
          } else {
            logout();
          }
        })
        .catch(() => {
          logout();
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, [token]);

  const login = (newToken: string, userData: User) => {
    setToken(newToken);
    setUser(userData);
    localStorage.setItem('skillguard_token', newToken);
    localStorage.setItem('skillguard_user', JSON.stringify(userData));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('skillguard_token');
    localStorage.removeItem('skillguard_user');
  };

  const authHeader = (): Record<string, string> => {
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
        authHeader,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
