import React, { useState, useEffect } from 'react';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
// import ErrorBoundary from './components/ErrorBoundary'; // Temporarily comment this out
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import WelcomeToast from './components/WelcomeToast';
import VectorStores from './pages/VectorStores';
import Analytics from './pages/Analytics';
import Agents from './pages/Agents';
import Tags from './pages/Tags';
import Terms from './pages/Terms';
import Guidelines from './pages/Guidelines';
import Journeys from './pages/Journeys';
import Settings from './pages/Settings';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

// Temporary working Error Boundary
class TempErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error);
    console.error('Error info:', errorInfo);
    
    // Safely set the state
    this.setState({
      error: error,
      errorInfo: errorInfo // This might be null, and that's OK
    });
  }

  render() {
    if (this.state.hasError) {
      // Safe access with null checking
      const componentStack = this.state.errorInfo?.componentStack || 'Component stack not available';
      const errorMessage = this.state.error?.message || 'An unknown error occurred';

      return (
        <div style={{ padding: '20px' }}>
          <div className="alert alert-danger">
            <h4>Something went wrong</h4>
            <p><strong>Error:</strong> {errorMessage}</p>
            <button 
              className="btn btn-outline-danger"
              onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
            >
              Try Again
            </button>
            <button 
              className="btn btn-outline-secondary ms-2"
              onClick={() => window.location.reload()}
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

const AppContent = () => {
  const [activeSection, setActiveSection] = useState('vector-stores');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const { colors } = useTheme();

  // Handle responsive behavior
  useEffect(() => {
    const handleResize = () => {
      const mobile = window.innerWidth <= 768;
      setIsMobile(mobile);
      if (mobile) {
        setSidebarCollapsed(true);
      } else {
        setSidebarCollapsed(false);
      }
    };

    window.addEventListener('resize', handleResize);
    handleResize(); // Check initial size

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeydown = (e) => {
      if (e.altKey) {
        switch (e.key) {
          case '1':
            e.preventDefault();
            setActiveSection('vector-stores');
            break;
          case '2':
            e.preventDefault();
            setActiveSection('analytics');
            break;
          case '3':
            e.preventDefault();
            setActiveSection('agents');
            break;
          case '4':
            e.preventDefault();
            setActiveSection('tags');
            break;
          case '5':
            e.preventDefault();
            setActiveSection('terms');
            break;
          case '6':
            e.preventDefault();
            setActiveSection('guidelines');
            break;
          case '7':
            e.preventDefault();
            setActiveSection('journeys');
            break;
          case '8':
            e.preventDefault();
            setActiveSection('settings');
            break;
          default:
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeydown);
    return () => window.removeEventListener('keydown', handleKeydown);
  }, []);

  const handleMobileMenuToggle = () => {
    if (isMobile) {
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };

  const mainStyle = {
    backgroundColor: colors.background,
    minHeight: '100vh',
    paddingLeft: isMobile ? '0' : (sidebarCollapsed ? '60px' : '250px'),
    paddingTop: '76px',
    transition: 'padding-left 0.3s ease',
    overflowX: 'hidden',
  };

  const contentStyle = {
    height: 'calc(100vh - 76px)',
    overflowY: 'auto',
    overflowX: 'hidden',
  };

  const renderContent = () => {
    switch (activeSection) {
      case 'vector-stores':
        return <VectorStores />;
      case 'analytics':
        return <Analytics />;
      case 'agents':
        return <Agents />;
      case 'tags':
        return <Tags />;
      case 'terms':
        return <Terms />;
      case 'guidelines':
        return <Guidelines />;
      case 'journeys':
        return <Journeys />;
      case 'settings':
        return <Settings />;
      default:
        return <VectorStores />;
    }
  };

  return (
    <div style={{ backgroundColor: colors.background, minHeight: '100vh' }}>
      <Header 
        onMobileMenuToggle={handleMobileMenuToggle}
        isMobile={isMobile}
      />
      
      {/* Mobile backdrop */}
      {isMobile && !sidebarCollapsed && (
        <div 
          className="mobile-sidebar-backdrop show"
          onClick={() => setSidebarCollapsed(true)}
        />
      )}
      
      <Sidebar 
        activeSection={activeSection} 
        setActiveSection={setActiveSection}
        isCollapsed={sidebarCollapsed}
        setIsCollapsed={setSidebarCollapsed}
        isMobile={isMobile}
      />
      <main style={mainStyle}>
        <div style={contentStyle}>
          {renderContent()}
        </div>
      </main>
      <WelcomeToast />
    </div>
  );
};

function App() {
  return (
    <TempErrorBoundary>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </TempErrorBoundary>
  );
}

export default App;