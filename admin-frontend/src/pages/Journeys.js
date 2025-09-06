import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Alert, Button } from 'react-bootstrap';
import { BsMap, BsArrowClockwise, BsExclamationTriangle } from 'react-icons/bs';
import { useTheme } from '../contexts/ThemeContext';
import JourneysManager from '../components/admin/JourneysManager';

const Journeys = () => {
  const { colors } = useTheme();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('unknown');

  const BASE_URL = 'http://localhost:6001';

  useEffect(() => {
    checkApiStatus();
  }, []);

  const checkApiStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BASE_URL}/journeys`);
      
      if (response.ok) {
        setApiStatus('connected');
        setError(null);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (err) {
      console.error('Error checking API status:', err);
      setError(`Failed to connect to Admin API: ${err.message}`);
      setApiStatus('disconnected');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h2 style={{ color: colors.text }} className="mb-1">
                <BsMap className="me-2" />
                Journeys Management
              </h2>
              <p style={{ color: colors.textSecondary }} className="mb-0">
                Design and manage user journeys and workflows
              </p>
            </div>
            <Button 
              variant="outline-secondary" 
              onClick={checkApiStatus}
              disabled={loading}
              className="d-flex align-items-center"
            >
              <BsArrowClockwise className={`me-2 ${loading ? 'spin' : ''}`} />
              Check API
            </Button>
          </div>

          {error && (
            <Alert variant="warning" className="d-flex align-items-center mb-3">
              <BsExclamationTriangle className="me-2" />
              {error}
            </Alert>
          )}

          <div className="d-flex align-items-center mb-4">
            <small style={{ color: colors.textSecondary }} className="me-2">API Status:</small>
            <span className={`badge bg-${apiStatus === 'connected' ? 'success' : 'danger'}`}>
              {apiStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
            <small style={{ color: colors.textSecondary }} className="ms-2">
              {BASE_URL}
            </small>
          </div>
        </Col>
      </Row>

      <JourneysManager baseUrl={BASE_URL} apiStatus={apiStatus} />
    </Container>
  );
};

export default Journeys;
