import React from 'react';
import { Card } from 'react-bootstrap';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { useTheme } from '../../contexts/ThemeContext';

const TimeSeriesChart = ({ data }) => {
  const { colors } = useTheme();

  if (!data || data.length === 0) {
    return (
      <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <Card.Body className="text-center py-5">
          <div style={{ color: colors.textSecondary }}>No timeseries data available</div>
        </Card.Body>
      </Card>
    );
  }

  // Format data for chart
  const chartData = data.map(item => ({
    time: new Date(item.bucket).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }),
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
    <Card style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
      <Card.Header style={{ backgroundColor: colors.cardBg, borderColor: colors.border }}>
        <h5 style={{ color: colors.text }} className="mb-0">
          Request Timeline
        </h5>
      </Card.Header>
      <Card.Body>
        <ResponsiveContainer width="100%" height={400}>
          <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke={colors.border} />
            <XAxis 
              dataKey="time" 
              stroke={colors.textSecondary}
              fontSize={12}
            />
            <YAxis stroke={colors.textSecondary} />
            <Tooltip content={<CustomTooltip />} />
            <Legend />
            <Bar dataKey="requests" fill="#007bff" name="Total Requests" />
            <Bar dataKey="success" fill="#28a745" name="Success" />
            <Bar dataKey="errors" fill="#dc3545" name="Errors" />
          </BarChart>
        </ResponsiveContainer>
      </Card.Body>
    </Card>
  );
};

export default TimeSeriesChart;
