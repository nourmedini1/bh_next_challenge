import React from 'react';
import { Spinner } from 'react-bootstrap';
import { useTheme } from '../contexts/ThemeContext';

const LoadingSpinner = ({ size = 'lg', message = 'Loading...' }) => {
  const { colors } = useTheme();

  return (
    <div 
      className="d-flex flex-column align-items-center justify-content-center"
      style={{ 
        height: '200px',
        color: colors.textSecondary 
      }}
    >
      <Spinner 
        animation="border" 
        variant="primary" 
        size={size}
        style={{ color: colors.primary }}
      />
      {message && (
        <p className="mt-3 mb-0" style={{ color: colors.textSecondary }}>
          {message}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;
