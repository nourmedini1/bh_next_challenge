import React, { useState } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { BsShield, BsShieldCheck, BsEye, BsEyeSlash, BsChatDots, BsPersonFill } from 'react-icons/bs';
import { useAuth } from '../context/AuthContext';
import Navbar from '../components/Navbar';
import Logo from '../components/Logo';
import styles from '../styles/AuthPage.module.css';

const AuthPage = () => {
  const navigate = useNavigate();
  const { login, loginAsGuest } = useAuth();
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showGuestWarning, setShowGuestWarning] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://192.168.1.16:2002/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || 'Login failed');
      }

      // Use the auth context to handle login with Greta as the user name
      const userData = {
        ...data.user,
        name: 'Greta',
        email: formData.email,
        avatar: 'G'
      };
      await login(userData, data.token);

      // Redirect to chat
      navigate('/chat');
    } catch (err) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuestContinue = () => {
    // Use the auth context to handle guest login
    loginAsGuest();
    
    // Redirect to chat
    navigate('/chat');
  };

  const showGuestWarningModal = () => {
    setShowGuestWarning(true);
  };

  return (
    <div className={styles.authPage}>
      <Navbar />
      
      <Container className={styles.container}>
        <div className={styles.authCard}>
          <Row className="h-100 g-0">
            {/* Left Side - Features & Info */}
            <Col lg={6} className={`${styles.leftPanel} d-none d-lg-flex`}>
              <div className={styles.leftContent}>
                <div className={styles.logoSection}>
                  <Logo size={80} />
                  <h1 className={styles.brandTitle}>BH Assurance</h1>
                  <p className={styles.brandSubtitle}>Your Trusted Insurance Partner</p>
                </div>
                
                <div className={styles.featuresSection}>
                  <h3 className={styles.featuresTitle}>Why sign in?</h3>
                  <div className={styles.featuresList}>
                    <div className={styles.feature}>
                      <div className={styles.featureIcon}>
                        <BsChatDots size={20} />
                      </div>
                      <div className={styles.featureContent}>
                        <h4>Chat History</h4>
                        <p>Access all your previous conversations</p>
                      </div>
                    </div>
                    <div className={styles.feature}>
                      <div className={styles.featureIcon}>
                        <BsShieldCheck size={20} />
                      </div>
                      <div className={styles.featureContent}>
                        <h4>Personalized Assistance</h4>
                        <p>Get tailored insurance recommendations</p>
                      </div>
                    </div>
                    <div className={styles.feature}>
                      <div className={styles.featureIcon}>
                        <BsShield size={20} />
                      </div>
                      <div className={styles.featureContent}>
                        <h4>Secure Policy Access</h4>
                        <p>View policies and documents securely</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </Col>
            
            {/* Right Side - Auth Form */}
            <Col lg={6} xs={12} className={styles.rightPanel}>
              <div className={styles.authFormContainer}>
                {/* Mobile Logo */}
                <div className={styles.mobileLogoContainer}>
                  <Logo size={50} />
                  <h2 className={styles.mobileTitle}>BH Assurance</h2>
                </div>
                
                <div className={styles.formWrapper}>
                  <h2 className={styles.title}>Welcome Back</h2>
                  <p className={styles.subtitle}>Sign in to access your personalized assistant</p>
                  
                  {/* Error Alert */}
                  {error && (
                    <Alert variant="danger" className={styles.errorAlert}>
                      {error}
                    </Alert>
                  )}

                  {/* Guest Warning */}
                  {showGuestWarning && (
                    <Alert variant="warning" className={styles.guestWarning}>
                      <div className="d-flex align-items-start">
                        <BsShield size={18} className="me-2 mt-1 flex-shrink-0" />
                        <div>
                          <h6 className="mb-1">Limited Features as Guest</h6>
                          <p className="mb-2">You'll miss out on chat history, personalized recommendations, and policy access.</p>
                          <div className="d-flex gap-2">
                            <Button 
                              variant="outline-warning" 
                              size="sm"
                              onClick={() => setShowGuestWarning(false)}
                            >
                              Sign In Instead
                            </Button>
                            <Button 
                              variant="warning" 
                              size="sm"
                              onClick={handleGuestContinue}
                            >
                              Continue as Guest
                            </Button>
                          </div>
                        </div>
                      </div>
                    </Alert>
                  )}

                  {/* Login Form */}
                  <Form onSubmit={handleLogin} className={styles.loginForm}>
                    <Form.Group className="mb-3">
                      <Form.Label className={styles.label}>Email Address</Form.Label>
                      <Form.Control
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        placeholder="Enter your email"
                        required
                        className={styles.formInput}
                        disabled={isLoading}
                      />
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label className={styles.label}>Password</Form.Label>
                      <div className={styles.passwordWrapper}>
                        <Form.Control
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={formData.password}
                          onChange={handleInputChange}
                          placeholder="Enter your password"
                          required
                          className={styles.formInput}
                          disabled={isLoading}
                        />
                        <Button
                          variant="ghost"
                          className={styles.passwordToggle}
                          onClick={() => setShowPassword(!showPassword)}
                          type="button"
                          disabled={isLoading}
                        >
                          {showPassword ? <BsEyeSlash size={16} /> : <BsEye size={16} />}
                        </Button>
                      </div>
                    </Form.Group>

                    <Button
                      type="submit"
                      variant="primary"
                      className={styles.loginButton}
                      disabled={isLoading}
                    >
                      {isLoading ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          Signing In...
                        </>
                      ) : (
                        <>
                          <BsShieldCheck size={16} className="me-2" />
                          Sign In
                        </>
                      )}
                    </Button>
                  </Form>

                  {/* Divider */}
                  <div className={styles.divider}>
                    <span>or</span>
                  </div>

                  {/* Guest Access */}
                  <Button
                    variant="outline-secondary"
                    className={styles.guestButton}
                    onClick={showGuestWarningModal}
                    disabled={isLoading}
                  >
                    <BsPersonFill size={16} className="me-2" />
                    Continue as Guest
                  </Button>
                </div>
              </div>
            </Col>
          </Row>
        </div>
      </Container>
    </div>
  );
};

export default AuthPage;
