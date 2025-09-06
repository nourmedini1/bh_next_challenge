import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Alert, Button } from 'react-bootstrap';
import { BsFileText, BsArrowClockwise, BsExclamationTriangle } from 'react-icons/bs';
import { useTheme } from '../contexts/ThemeContext';

// Simple Error Boundary to catch the actual error
class SimpleErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught:', error);
    console.error('Error info:', errorInfo);
    this.setState({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert variant="danger">
          <Alert.Heading>Component Error</Alert.Heading>
          <p><strong>Error:</strong> {this.state.error?.message}</p>
          <Button onClick={() => this.setState({ hasError: false, error: null })}>
            Reset
          </Button>
        </Alert>
      );
    }

    return this.props.children;
  }
}

// Lazy load the GuidelinesManager to catch import errors
const GuidelinesManager = React.lazy(() => 
  import('../components/admin/GuidelinesManager').catch(err => {
    console.error('Error loading GuidelinesManager:', err);
    return { default: () => <Alert variant="danger">Failed to load GuidelinesManager: {err.message}</Alert> };
  })
);

const Guidelines = () => {
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
      const response = await fetch(`${BASE_URL}/guidelines`);
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
                <BsFileText className="me-2" />
                Guidelines Management
              </h2>
              <p style={{ color: colors.textSecondary }} className="mb-0">
                Create and manage guidelines and business rules
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
      
      <SimpleErrorBoundary>
        <React.Suspense fallback={<div>Loading Guidelines Manager...</div>}>
          <GuidelinesManager baseUrl={BASE_URL} apiStatus={apiStatus} />
        </React.Suspense>
      </SimpleErrorBoundary>
    </Container>
  );
};

export default Guidelines;