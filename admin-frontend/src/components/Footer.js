import React from 'react';
import { Container } from 'react-bootstrap';
import { useTheme } from '../contexts/ThemeContext';

const Footer = () => {
  const { colors } = useTheme();

  const footerStyle = {
    backgroundColor: colors.cardBg,
    borderTop: `1px solid ${colors.border}`,
    padding: '1rem 0',
    marginTop: 'auto',
  };

  return (
    <footer style={footerStyle}>
      <Container fluid>
        <div className="d-flex justify-content-between align-items-center">
          <small style={{ color: colors.textSecondary }}>
            © 2025 Admin Dashboard. All rights reserved.
          </small>
          <small style={{ color: colors.textSecondary }}>
            Version 2.1.3 | Built with React & Bootstrap
          </small>
        </div>
      </Container>
    </footer>
  );
};

export default Footer;
