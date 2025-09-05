import React from 'react';
import styles from '../styles/Logo.module.css';

const Logo = ({ size = 60, className = '' }) => {
  return (
    <div className={`${styles.logo} ${className}`}>
      <img 
        src="/images/bh-logo.png" 
        alt="BH Assurance" 
        className={styles.logoImage}
        style={{ height: size }}
      />
    </div>
  );
};

export default Logo;
