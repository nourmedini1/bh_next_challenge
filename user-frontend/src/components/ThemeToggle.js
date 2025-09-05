import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import { BsSun, BsMoon } from 'react-icons/bs';
import { useTheme } from '../context/ThemeContext';
import styles from '../styles/ThemeToggle.module.css';

const ThemeToggle = () => {
  const { isDarkMode, toggleTheme } = useTheme();
  const [isHovered, setIsHovered] = useState(false);

  const getIcon = () => {
    if (isHovered) {
      // Show next state on hover
      return isDarkMode ? <BsSun size={18} /> : <BsMoon size={18} />;
    }
    // Show current state normally
    return isDarkMode ? <BsMoon size={18} /> : <BsSun size={18} />;
  };

  return (
    <Button
      variant="outline-secondary"
      className={styles.themeToggle}
      onClick={toggleTheme}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
    >
      {getIcon()}
    </Button>
  );
};

export default ThemeToggle;
