import React from 'react';
import { Navbar, Container, Button } from 'react-bootstrap';
import { BsSun, BsMoon, BsList } from 'react-icons/bs';
import { useTheme } from '../contexts/ThemeContext';

const Header = ({ onMobileMenuToggle, isMobile }) => {
  const { isDarkMode, toggleTheme, colors } = useTheme();

  const headerStyle = {
    backgroundColor: colors.cardBg,
    borderBottom: `1px solid ${colors.border}`,
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1020,
  };

  const logoStyle = {
    height: '40px',
    width: 'auto',
  };

  const toggleButtonStyle = {
    backgroundColor: 'transparent',
    border: `2px solid ${colors.primary}`,
    color: colors.primary,
    borderRadius: '8px',
    padding: '8px 12px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  };

  return (
    <Navbar style={headerStyle} className="py-3">
      <Container fluid>
        <Navbar.Brand href="#" className="d-flex align-items-center">
          <div 
            style={{
              ...logoStyle,
              backgroundColor: colors.primary,
              color: 'white',
              padding: '8px 16px',
              borderRadius: '4px',
              fontWeight: 'bold',
              fontSize: '18px'
            }}
          >
            ADMIN
          </div>
        </Navbar.Brand>
        
        <div className="d-flex align-items-center">
          {/* Mobile menu button */}
          {isMobile && (
            <Button
              variant="outline-primary"
              onClick={onMobileMenuToggle}
              style={{
                ...toggleButtonStyle,
                marginRight: '12px'
              }}
              className="d-flex align-items-center"
            >
              <BsList size={18} />
            </Button>
          )}
          
          <Button
            variant="outline-primary"
            onClick={toggleTheme}
            style={toggleButtonStyle}
            className="d-flex align-items-center"
          >
            {isDarkMode ? <BsSun size={18} /> : <BsMoon size={18} />}
            <span className="ms-2 d-none d-sm-inline">
              {isDarkMode ? 'Light' : 'Dark'}
            </span>
          </Button>
        </div>
      </Container>
    </Navbar>
  );
};

export default Header;
