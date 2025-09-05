import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Tabs, Tab, Alert, Button, Spinner } from 'react-bootstrap';
import { BsGraphUp, BsArrowClockwise, BsExclamationTriangle } from 'react-icons/bs';
import { useTheme } from '../contexts/ThemeContext';
import OverviewMetrics from '../components/analytics/OverviewMetrics';
import TimeSeriesChart from '../components/analytics/TimeSeriesChart';
import ToolUsageTable from '../components/analytics/ToolUsageTable';
import HeatmapChart from '../components/analytics/HeatmapChart';
import LatencyDistribution from '../components/analytics/LatencyDistribution';
import ErrorBreakdown from '../components/analytics/ErrorBreakdown';
import SearchAnalytics from '../components/analytics/SearchAnalytics';
import LLMInsights from '../components/analytics/LLMInsights';

const Analytics = () => {
  const { colors } = useTheme();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState('unknown');
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      // Replace with your actual endpoint
      const response = await fetch('http://192.168.1.16:6002/analytics');

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: Failed to fetch analytics data`);
      }
      
      const analyticsData = await response.json();
      setData(analyticsData);
      setError(null);
      setApiStatus('connected');
    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError(`Failed to connect to analytics API: ${err.message}`);
      setApiStatus('disconnected');
      setData(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Container fluid className="py-4">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" size="lg" />
          <div style={{ color: colors.textSecondary }} className="mt-3">
            Loading analytics data...
          </div>
        </div>
      </Container>
    );
  }

  return (
    <Container fluid className="py-4">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h2 style={{ color: colors.text }} className="mb-1">
                <BsGraphUp className="me-2" />
                Analytics Dashboard
              </h2>
              <p style={{ color: colors.textSecondary }} className="mb-0">
                Tool usage analytics and performance insights
              </p>
            </div>
            <Button 
              variant="outline-secondary" 
              onClick={fetchAnalyticsData}
              disabled={loading}
              className="d-flex align-items-center"
            >
              <BsArrowClockwise className={`me-2 ${loading ? 'spin' : ''}`} />
              Refresh
            </Button>
          </div>

          {error && (
            <Alert variant="warning" className="d-flex align-items-center mb-3">
              <BsExclamationTriangle className="me-2" />
              {error}
            </Alert>
          )}

          {/* API Status */}
          <div className="d-flex align-items-center mb-4">
            <small style={{ color: colors.textSecondary }} className="me-2">API Status:</small>
            <span className={`badge bg-${apiStatus === 'connected' ? 'success' : 'danger'}`}>
              {apiStatus === 'connected' ? '🟢 Connected' : '🔴 Disconnected'}
            </span>
            <small style={{ color: colors.textSecondary }} className="ms-2">
              Last updated: {data?.metadata?.generated_at ? new Date(data.metadata.generated_at).toLocaleString() : 'N/A'}
            </small>
          </div>
        </Col>
      </Row>

      <Tabs activeKey={activeTab} onSelect={(k) => setActiveTab(k)} className="mb-4">
        <Tab eventKey="overview" title="Overview">
          <Row>
            <Col xs={12}>
              <OverviewMetrics data={data} />
            </Col>
          </Row>
          <Row className="mt-4">
            <Col xs={12}>
              <TimeSeriesChart data={data?.timeseries || []} />
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="tools" title="Tool Usage">
          <Row>
            <Col xs={12}>
              <ToolUsageTable data={data?.usage_by_tool || []} />
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="performance" title="Performance">
          <Row>
            <Col md={6}>
              <LatencyDistribution data={data?.latency_distribution || []} />
            </Col>
            <Col md={6}>
              <ErrorBreakdown data={data?.error_breakdown || []} />
            </Col>
          </Row>
          <Row className="mt-4">
            <Col xs={12}>
              <HeatmapChart data={data?.heatmap || []} />
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="search" title="Search Analytics">
          <Row>
            <Col xs={12}>
              <SearchAnalytics data={data?.search || {}} />
            </Col>
          </Row>
        </Tab>

        <Tab eventKey="insights" title="AI Insights">
          <Row>
            <Col xs={12}>
              <LLMInsights data={data?.llm_insights || {}} />
            </Col>
          </Row>
        </Tab>
      </Tabs>
    </Container>
  );
};

export default Analytics;
