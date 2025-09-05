import React, { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider = ({ children }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = !isDarkMode;
    setIsDarkMode(newTheme);
    localStorage.setItem('theme', newTheme ? 'dark' : 'light');
  };

  const theme = {
    colors: {
      primary: '#E32227',
      secondary: '#0C1E35',
      background: isDarkMode ? '#0C1E35' : '#ffffff',
      surface: isDarkMode ? '#1a2937' : '#f8f9fa',
      text: isDarkMode ? '#ffffff' : '#0C1E35',
      textSecondary: isDarkMode ? '#e9ecef' : '#6c757d',
      border: isDarkMode ? '#495057' : '#dee2e6',
      cardBg: isDarkMode ? '#1a2937' : '#ffffff',
    },
    isDarkMode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={theme}>
      {children}
    </ThemeContext.Provider>
  );
};
