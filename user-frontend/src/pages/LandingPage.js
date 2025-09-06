import React from 'react';
import { Container, Row, Col, Button } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import { 
  BsChatDots, 
  BsShieldCheck, 
  BsLightning, 
  BsPerson, 
  BsStars,
  BsArrowRight,
  BsHeadset
} from 'react-icons/bs';
import Navbar from '../components/Navbar';
import Logo from '../components/Logo';
import styles from '../styles/LandingPage.module.css';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleChatClick = () => {
    navigate('/auth');
  };

  return (
    <div className={styles.landingPage}>
      <Navbar />
      
      <Container className={styles.container}>
        <Row className="h-100 align-items-center">
          {/* Left Side - Content */}
          <Col lg={6} md={6} className="h-100 d-flex flex-column justify-content-center">
            <div className={styles.leftContent}>
              <div className={styles.titleSection}>

                <h1 className={styles.title}>Insurance Made Simple</h1>
              </div>
              
              <h2 className={styles.subtitle}>Discover, Compare, and Secure Your Future</h2>
              
              <p className={styles.description}>
                Experience insurance like never before. Our AI-powered assistant makes finding 
                the right coverage effortless and instant.
              </p>
              
              <div className={styles.ctaSection}>
                <Button 
                  size="lg" 
                  className={styles.ctaButton}
                  onClick={handleChatClick}
                >
                  <BsStars className="me-2" />
                  Start Your Journey
                  <BsArrowRight className="ms-2" />
                </Button>
                <p className={styles.ctaSubtext}>
                  Join thousands who've simplified their insurance experience
                </p>
              </div>
            </div>
          </Col>
          
          {/* Right Side - Features */}
          <Col lg={6} md={6} className="h-100 d-flex align-items-center">
            <div className={styles.rightContent}>
              <div className={styles.features}>
                <div className={styles.featureCard}>
                  <div className={styles.featureIcon}>
                    <BsLightning size={28} />
                  </div>
                  <div className={styles.featureContent}>
                    <h5>Lightning Fast Quotes</h5>
                    <p>Get personalized insurance quotes in under 60 seconds</p>
                  </div>
                </div>
                
                <div className={styles.featureCard}>
                  <div className={styles.featureIcon}>
                    <BsHeadset size={28} />
                  </div>
                  <div className={styles.featureContent}>
                    <h5>24/7 Smart Support</h5>
                    <p>AI-powered assistance available around the clock</p>
                  </div>
                </div>
                
                <div className={styles.featureCard}>
                  <div className={styles.featureIcon}>
                    <BsShieldCheck size={28} />
                  </div>
                  <div className={styles.featureContent}>
                    <h5>Trusted Protection</h5>
                    <p>Comprehensive coverage backed by industry expertise</p>
                  </div>
                </div>
              </div>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  );
};

export default LandingPage;
