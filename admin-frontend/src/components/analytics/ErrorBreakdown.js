import React from 'react';
import { Card, Table, Badge, Alert } from 'react-bootstrap';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { useTheme } from '../../contexts/ThemeContext';

const ErrorBreakdown = ({ data }) => {
  const { colors } = useTheme();

  if (!data || data.length === 0) {
    return (
      <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <Card.Body className="text-center py-5">
          <div style={{ color: colors.textSecondary }}>No error data available</div>
        </Card.Body>
      </Card>
    );
  }

  // Prepare data for pie chart
  const chartData = data.map((item, index) => ({
    name: item.tool_name.replace(/^tool_/, '').replace(/_/g, ' '),
    value: item.count,
    error: item.error,
    fullName: item.tool_name
  }));

  const totalErrors = chartData.reduce((sum, item) => sum + item.value, 0);

  // Colors for pie chart
  const COLORS = ['#dc3545', '#fd7e14', '#ffc107', '#6f42c1', '#e83e8c', '#20c997'];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div style={{
          backgroundColor: colors.cardBg,
          border: `1px solid ${colors.border}`,
          borderRadius: '8px',
          padding: '10px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <p style={{ color: colors.text, margin: '0 0 5px 0', fontWeight: 'bold' }}>
            {data.name}
          </p>
          <p style={{ color: colors.text, margin: 0 }}>
            Errors: {data.value} ({((data.value / totalErrors) * 100).toFixed(1)}%)
          </p>
          <p style={{ color: colors.textSecondary, margin: 0, fontSize: '12px' }}>
            {data.error}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
      <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <h5 style={{ color: colors.text }} className="mb-0">
          Error Breakdown
        </h5>
        <small style={{ color: colors.textSecondary }}>
          {totalErrors} total errors
        </small>
      </Card.Header>
      <Card.Body>
        {totalErrors > 0 ? (
          <>
            {/* Pie Chart */}
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                  fontSize={10}
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>

            {/* Error Details Table */}
            <div className="mt-3">
              <Table size="sm" style={{ color: colors.text }}>
                <thead>
                  <tr style={{ borderColor: colors.border }}>
                    <th style={{ color: colors.text, borderColor: colors.border }}>Tool</th>
                    <th style={{ color: colors.text, borderColor: colors.border }}>Error</th>
                    <th style={{ color: colors.text, borderColor: colors.border }}>Count</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((error, index) => (
                    <tr key={index} style={{ borderColor: colors.border }}>
                      <td style={{ color: colors.text, borderColor: colors.border }}>
                        <div style={{ fontSize: '12px' }}>
                          {error.tool_name.replace(/^tool_/, '').replace(/_/g, ' ')}
                        </div>
                      </td>
                      <td style={{ color: colors.text, borderColor: colors.border }}>
                        <small style={{ color: colors.textSecondary }}>
                          {error.error}
                        </small>
                      </td>
                      <td style={{ color: colors.text, borderColor: colors.border }}>
                        <Badge bg="danger">{error.count}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>

            {/* Most Common Error Alert */}
            {data.length > 0 && (
              <Alert variant="warning" className="mt-3 mb-0">
                <strong>Most Common Error:</strong> {data[0].error} 
                <br />
                <small>Affects {data.filter(e => e.error === data[0].error).length} tool(s)</small>
              </Alert>
            )}
          </>
        ) : (
          <div className="text-center py-4">
            <div style={{ color: colors.textSecondary }}>
              🎉 No errors recorded!
            </div>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default ErrorBreakdown;
