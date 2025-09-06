import React from 'react';
import { Row, Col, Card, Table, Badge, Alert } from 'react-bootstrap';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useTheme } from '../../contexts/ThemeContext';

const SearchAnalytics = ({ data }) => {
  const { colors } = useTheme();

  if (!data || Object.keys(data).length === 0) {
    return (
      <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <Card.Body className="text-center py-5">
          <div style={{ color: colors.textSecondary }}>No search analytics data available</div>
        </Card.Body>
      </Card>
    );
  }

  const { by_category = [], top_errors = [], latency = [] } = data;

  // Prepare data for category chart
  const categoryData = by_category.map(item => ({
    name: item.tool_name.replace('search_', '').replace(/_documents$/, '').replace(/_/g, ' '),
    requests: item.requests,
    success: item.success,
    errors: item.errors,
    successRate: item.requests > 0 ? ((item.success / item.requests) * 100).toFixed(1) : 0
  }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: colors.cardBg,
          border: `1px solid ${colors.border}`,
          borderRadius: '8px',
          padding: '10px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <p style={{ color: colors.text, margin: '0 0 5px 0', fontWeight: 'bold' }}>
            {label}
          </p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color, margin: 0 }}>
              {`${entry.dataKey}: ${entry.value}${entry.dataKey === 'successRate' ? '%' : ''}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div>
      <Row>
        {/* Search by Category */}
        <Col md={8}>
          <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
            <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
              <h5 style={{ color: colors.text }} className="mb-0">
                Search by Category
              </h5>
            </Card.Header>
            <Card.Body>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
                  <XAxis 
                    dataKey="name" 
                    stroke={colors.textSecondary}
                    fontSize={10}
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis stroke={colors.textSecondary} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="requests" fill="#007bff" name="Total Requests" />
                  <Bar dataKey="success" fill="#28a745" name="Success" />
                  <Bar dataKey="errors" fill="#dc3545" name="Errors" />
                </BarChart>
              </ResponsiveContainer>
            </Card.Body>
          </Card>
        </Col>

        {/* Top Errors */}
        <Col md={4}>
          <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
            <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
              <h5 style={{ color: colors.text }} className="mb-0">
                Top Search Errors
              </h5>
            </Card.Header>
            <Card.Body>
              {top_errors.length > 0 ? (
                <div>
                  {top_errors.map((error, index) => (
                    <Alert 
                      key={index} 
                      variant="danger" 
                      className="d-flex justify-content-between align-items-center py-2"
                    >
                      <div>
                        <strong>{error.error}</strong>
                      </div>
                      <Badge bg="danger">{error.count}</Badge>
                    </Alert>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <div style={{ color: colors.textSecondary }}>
                    🎉 No search errors!
                  </div>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row className="mt-4">
        {/* Search Latency Table */}
        <Col xs={12}>
          <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
            <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
              <h5 style={{ color: colors.text }} className="mb-0">
                Search Performance by Category
              </h5>
            </Card.Header>
            <Card.Body className="p-0">
              <Table responsive hover style={{ color: colors.text, margin: 0 }}>
                <thead style={{ backgroundColor: colors.background }}>
                  <tr>
                    <th style={{ color: colors.text, borderColor: colors.border }}>Category</th>
                    <th style={{ color: colors.text, borderColor: colors.border }}>Requests</th>
                    <th style={{ color: colors.text, borderColor: colors.border }}>Success Rate</th>
                    <th style={{ color: colors.text, borderColor: colors.border }}>Avg Latency</th>
                    <th style={{ color: colors.text, borderColor: colors.border }}>P95 Latency</th>
                    <th style={{ color: colors.text, borderColor: colors.border }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {by_category.map((category, index) => {
                    const successRate = category.requests > 0 ? ((category.success / category.requests) * 100).toFixed(1) : 0;
                    const latencyInfo = latency.find(l => l.tool_name === category.tool_name);
                    
                    return (
                      <tr key={index} style={{ borderColor: colors.border }}>
                        <td style={{ color: colors.text }}>
                          <div>
                            <strong>
                              {category.tool_name.replace('search_', '').replace(/_documents$/, '').replace(/_/g, ' ')}
                            </strong>
                            <br />
                            <small style={{ color: colors.textSecondary }}>
                              {category.tool_name}
                            </small>
                          </div>
                        </td>
                        <td style={{ color: colors.text }}>
                          <Badge bg="primary">{category.requests}</Badge>
                        </td>
                        <td>
                          <Badge bg={successRate >= 80 ? 'success' : successRate >= 50 ? 'warning' : 'danger'}>
                            {successRate}%
                          </Badge>
                        </td>
                        <td style={{ color: colors.text }}>
                          {latencyInfo ? `${latencyInfo.avg_latency_ms.toFixed(0)}ms` : 'N/A'}
                        </td>
                        <td style={{ color: colors.textSecondary }}>
                          {latencyInfo ? `${latencyInfo.p95_latency_ms.toFixed(0)}ms` : 'N/A'}
                        </td>
                        <td>
                          <Badge bg={category.errors === 0 ? 'success' : 'warning'}>
                            {category.errors === 0 ? 'Healthy' : `${category.errors} errors`}
                          </Badge>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SearchAnalytics;
