import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isGuest, setIsGuest] = useState(false);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check authentication status on app load
  useEffect(() => {
    const checkAuthStatus = () => {
      try {
        const storedToken = localStorage.getItem('authToken');
        const storedUser = localStorage.getItem('userData');
        const storedIsAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
        const storedIsGuest = localStorage.getItem('isGuest') === 'true';

        if (storedToken && storedIsAuthenticated) {
          setToken(storedToken);
          setUser(storedUser ? JSON.parse(storedUser) : null);
          setIsAuthenticated(true);
          setIsGuest(false);
        } else if (storedIsGuest) {
          setIsGuest(true);
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Error checking auth status:', error);
        // Clear potentially corrupted data
        logout();
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = (userData, authToken) => {
    try {
      localStorage.setItem('authToken', authToken);
      localStorage.setItem('userData', JSON.stringify(userData));
      localStorage.setItem('isAuthenticated', 'true');
      localStorage.removeItem('isGuest');
      
      setToken(authToken);
      setUser(userData);
      setIsAuthenticated(true);
      setIsGuest(false);
    } catch (error) {
      console.error('Error during login:', error);
      throw new Error('Failed to save authentication data');
    }
  };

  const loginAsGuest = () => {
    try {
      localStorage.setItem('isGuest', 'true');
      localStorage.setItem('isAuthenticated', 'false');
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      
      setIsGuest(true);
      setIsAuthenticated(false);
      setToken(null);
      setUser(null);
    } catch (error) {
      console.error('Error during guest login:', error);
    }
  };

  const logout = () => {
    try {
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      localStorage.removeItem('isAuthenticated');
      localStorage.removeItem('isGuest');
      
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
      setIsGuest(false);
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  const hasFeatureAccess = (feature) => {
    if (!isAuthenticated && isGuest) {
      // Define which features are available to guests
      const guestFeatures = ['basic_chat', 'general_info'];
      return guestFeatures.includes(feature);
    }
    return isAuthenticated; // Authenticated users have access to all features
  };

  const getAuthHeaders = () => {
    if (token && isAuthenticated) {
      return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      };
    }
    return {
      'Content-Type': 'application/json'
    };
  };

  const value = {
    isAuthenticated,
    isGuest,
    user,
    token,
    loading,
    login,
    loginAsGuest,
    logout,
    hasFeatureAccess,
    getAuthHeaders
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
