import { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  user: string | null;
  idToken: string | null;
  login: (email: string, token: string) => void;
  logout: () => void;
  setToken: (token: string) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<string | null>(null);
  const [idToken, setIdToken] = useState<string | null>(null);

  // Load token from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('firebase_id_token');
    if (token) {
      setIdToken(token);
      setIsAuthenticated(true);
    }
  }, []);

  const login = (email: string, token: string) => {
    setIsAuthenticated(true);
    setUser(email);
    setIdToken(token);
    localStorage.setItem('firebase_id_token', token);
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    setIdToken(null);
    localStorage.removeItem('firebase_id_token');
  };

  const setToken = (token: string) => {
    setIdToken(token);
    localStorage.setItem('firebase_id_token', token);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, idToken, login, logout, setToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};