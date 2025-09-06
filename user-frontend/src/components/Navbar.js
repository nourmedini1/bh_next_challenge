import React from 'react';
import { Navbar as BSNavbar, Container, Dropdown } from 'react-bootstrap';
import { useLocation, useNavigate } from 'react-router-dom';
import { IoArrowBack } from 'react-icons/io5';
import { BsPersonCircle, BsBoxArrowRight, BsShieldCheck, BsPersonFill, BsCircle } from 'react-icons/bs';
import { useAuth } from '../context/AuthContext';
import Logo from './Logo';
import ThemeToggle from './ThemeToggle';
import styles from '../styles/Navbar.module.css';

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { isAuthenticated, isGuest, user, logout } = useAuth();
  const isHomePage = location.pathname === '/';
  const isAuthPage = location.pathname === '/auth';

  const handleBackClick = () => {
    navigate('/');
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const handleLogin = () => {
    navigate('/auth');
  };

  return (
    <BSNavbar className={styles.navbar} fixed="top" expand="lg">
      <Container fluid className={styles.navContainer}>
        <div className={styles.navLeft}>
          {!isHomePage && (
            <button
              className={styles.backButton}
              onClick={handleBackClick}
              aria-label="Go back to home"
            >
              <IoArrowBack size={20} />
            </button>
          )}
          <BSNavbar.Brand className={styles.brand}>
            <Logo size={40} />
            <span className={styles.brandText}>BH Assurance</span>
          </BSNavbar.Brand>
        </div>
        
        <div className={styles.navRight}>
          {/* User Profile / Auth Section */}
          {!isAuthPage && (
            <div className={styles.authSection}>
                            {isAuthenticated ? (
                <Dropdown align="end">
                  <Dropdown.Toggle variant="ghost" className={styles.userDropdown}>
                    <div className={styles.userAvatarIcon}>
                      <BsCircle size={24} className={styles.circleIcon} />
                      <span className={styles.avatarLetter}>G</span>
                    </div>
                    <span className={styles.userName}>
                      Greta
                    </span>
                  </Dropdown.Toggle>
                  <Dropdown.Menu className={styles.dropdownMenu}>
                    <Dropdown.Item className={styles.dropdownItem} disabled>
                      <div className={styles.userAvatarIconSmall}>
                        <BsCircle size={16} className={styles.circleIconSmall} />
                        <span className={styles.avatarLetterSmall}>G</span>
                      </div>
                      Signed in as Greta
                    </Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item className={styles.dropdownItem} onClick={handleLogout}>
                      <BsBoxArrowRight size={16} className="me-2" />
                      Sign Out
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              ) : isGuest ? (
                <Dropdown align="end">
                  <Dropdown.Toggle variant="ghost" className={styles.guestDropdown}>
                    <BsPersonFill size={18} className="me-2" />
                    <span className={styles.guestText}>Guest</span>
                  </Dropdown.Toggle>
                  <Dropdown.Menu className={styles.dropdownMenu}>
                    <Dropdown.Item className={styles.dropdownItem} disabled>
                      <BsPersonFill size={16} className="me-2" />
                      Limited Features Active
                    </Dropdown.Item>
                    <Dropdown.Divider />
                    <Dropdown.Item className={styles.dropdownItem} onClick={handleLogin}>
                      <BsShieldCheck size={16} className="me-2" />
                      Sign In for Full Access
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              ) : null}
            </div>
          )}
          
          <ThemeToggle />
        </div>
      </Container>
    </BSNavbar>
  );
};

export default Navbar;
