import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { BsChatDots } from 'react-icons/bs';
import Navbar from '../components/Navbar';
import Logo from '../components/Logo';
import styles from '../styles/LandingPage.module.css';

const LoginPage = () => {
  const navigate = useNavigate();

  const handleChatClick = () => {
    navigate('/chat');
  };

  return (
    <div className={styles.landingPage}>
      <Navbar />
      
      <Container className={styles.container}>
        <Row className="justify-content-center align-items-center min-vh-100">
          <Col lg={8} md={10} sm={12} className="text-center">
            <div className={styles.logoContainer}>
              <Logo size={120} />
            </div>
            
            <h1 className={styles.title}>BH Assurance</h1>
            <h2 className={styles.subtitle}>Your Trusted Insurance Partner</h2>
            
            <p className={styles.description}>
              Welcome to BH Assurance, where we provide comprehensive insurance solutions 
              tailored to your needs. Our intelligent chatbot is available 24/7 to help 
              you find the perfect coverage, answer your questions, and guide you through 
              the insurance process.
            </p>
            
            <div className={styles.features}>
              <Row className="g-4 mb-5">
                <Col md={4}>
                  <div className={styles.featureCard}>
                    <h5>Instant Support</h5>
                    <p>Get immediate answers to your insurance questions</p>
                  </div>
                </Col>
                <Col md={4}>
                  <div className={styles.featureCard}>
                    <h5>Personalized Quotes</h5>
                    <p>Receive customized insurance quotes in minutes</p>
                  </div>
                </Col>
                <Col md={4}>
                  <div className={styles.featureCard}>
                    <h5>Expert Guidance</h5>
                    <p>Get professional advice from our AI assistant</p>
                  </div>
                </Col>
              </Row>
            </div>
            
            <Button 
              size="lg" 
              className={styles.ctaButton}
              onClick={handleChatClick}
            >
              <BsChatDots className="me-2" />
              Talk to Our Chatbot
            </Button>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default LoginPage;
