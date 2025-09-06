import React from 'react';
import { Alert, Button, Container } from 'react-bootstrap';
import { BsExclamationTriangle } from 'react-icons/bs';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <Container className="mt-5">
          <Alert variant="danger" className="text-center">
            <BsExclamationTriangle size={48} className="mb-3" />
            <h4>Oops! Something went wrong</h4>
            <p>We're sorry, but something unexpected happened.</p>
            {process.env.NODE_ENV === 'development' && (
              <details style={{ whiteSpace: 'pre-wrap', textAlign: 'left' }}>
                {this.state.error && this.state.error.toString()}
                <br />
                {this.state.errorInfo.componentStack}
              </details>
            )}
            <Button 
              variant="primary" 
              className="mt-3"
              onClick={() => window.location.reload()}
            >
              Reload Page
            </Button>
          </Alert>
        </Container>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
